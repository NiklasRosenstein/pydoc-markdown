# Example Django Model code. Source:
# https://github.com/AuHau/toggl-cli/blob/master/toggl/api/models.py

import json
import logging
import typing
from copy import copy
from urllib.parse import quote_plus
from validate_email import validate_email

import pendulum

from . import base
from . import fields
from .. import utils
from .. import exceptions

logger = logging.getLogger('toggl.api.models')


# Workspace entity
class Workspace(base.TogglEntity):
    _can_create = False
    _can_delete = False

    name = fields.StringField(required=True)
    premium = fields.BooleanField()
    admin = fields.BooleanField()
    only_admins_may_create_projects = fields.BooleanField()
    only_admins_see_billable_rates = fields.BooleanField()
    rounding = fields.IntegerField()
    rounding_minutes = fields.IntegerField()
    default_hourly_rate = fields.FloatField()

    # As TogglEntityMeta is by default adding WorkspaceTogglSet to TogglEntity,
    # but we want vanilla TogglSet so defining it here explicitly.
    objects = base.TogglSet()

    def invite(self, *emails):  # type: (*str) -> None
        """
        Invites users defined by email addresses. The users does not have to have account in Toggl, in that case after
        accepting the invitation, they will go through process of creating the account in the Toggl web.

        :param emails: List of emails to invite.
        :return: None
        """
        for email in emails:
            if not validate_email(email):
                raise exceptions.TogglValidationException('Supplied email \'{}\' is not valid email!'.format(email))

        emails_json = json.dumps({'emails': emails})
        data = utils.toggl("/workspaces/{}/invite".format(self.id), "post", emails_json, config=self._config)

        if 'notifications' in data and data['notifications']:
            raise exceptions.TogglException(data['notifications'])


class WorkspaceEntity(base.TogglEntity):
    workspace = fields.MappingField(Workspace, 'wid', is_read_only=True,
                                    default=lambda config: config.default_workspace)  # type: Workspace


# Premium Entity
class PremiumEntity(WorkspaceEntity):
    """
    Abstract entity that enforces that linked Workspace is premium (paid).
    """

    def save(self, config=None):  # type: (utils.Config) -> None
        if not self.workspace.premium:
            raise exceptions.TogglPremiumException('The entity {} requires to be associated with Premium workspace!')

        super().save(config)


# ----------------------------------------------------------------------------
# Entities definitions
# ----------------------------------------------------------------------------
class Client(WorkspaceEntity):
    name = fields.StringField(required=True)
    notes = fields.StringField()


class Project(WorkspaceEntity):
    name = fields.StringField(required=True)
    client = fields.MappingField(Client, 'cid')  # type: Client
    active = fields.BooleanField(default=True)
    is_private = fields.BooleanField(default=True)
    billable = fields.BooleanField(premium=True)
    auto_estimates = fields.BooleanField(default=False, premium=True)
    estimated_hours = fields.IntegerField(premium=True)
    color = fields.IntegerField()
    rate = fields.FloatField(premium=True)

    def add_user(self, user, manager=False, rate=None):  # type: (User, bool, typing.Optional[float]) -> ProjectUser
        project_user = ProjectUser(project=self, user=user, workspace=self.workspace, manager=manager, rate=rate)
        project_user.save()

        return project_user


class UserSet(base.WorkspaceTogglSet):

    def current_user(self, config=None):  # type: (utils.Config) -> User
        """
        Fetches details about the current user.
        """
        fetched_entity = utils.toggl('/me', 'get', config=config)
        return self.entity_cls.deserialize(config=config, **fetched_entity['data'])


class User(WorkspaceEntity):
    _can_create = False
    _can_update = False
    _can_delete = False
    _can_get_detail = False

    api_token = fields.StringField()
    send_timer_notifications = fields.BooleanField()
    openid_enabled = fields.BooleanField()
    default_workspace = fields.MappingField(Workspace, 'default_wid')  # type: Workspace
    email = fields.EmailField()
    fullname = fields.StringField()
    store_start_and_stop_time = fields.BooleanField()
    beginning_of_week = fields.ChoiceField({
        '0': 'Sunday',
        '1': 'Monday',
        '2': 'Tuesday',
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday',
        '6': 'Saturday'
    })
    language = fields.StringField()
    image_url = fields.StringField()
    timezone = fields.StringField()

    objects = UserSet()

    @classmethod
    def signup(cls, email, password, timezone=None, created_with='TogglCLI',
               config=None):  # type: (str, str, str, str, utils.Config) -> User
        """
        Creates brand new user. After creation confirmation email is sent to him.

        :param email: Valid email of the new user.
        :param password: Password of the new user.
        :param timezone: Timezone to be associated with the user. If empty, than timezone from config is used.
        :param created_with: Name of application that created the user.
        :param config:
        :return:
        """
        if config is None:
            config = utils.Config.factory()

        if timezone is None:
            timezone = config.timezone

        if not validate_email(email):
            raise exceptions.TogglValidationException('Supplied email \'{}\' is not valid email!'.format(email))

        user_json = json.dumps({'user': {
            'email': email,
            'password': password,
            'timezone': timezone,
            'created_with': created_with
        }})
        data = utils.toggl("/signups", "post", user_json, config=config)
        return cls.deserialize(config=config, **data['data'])

    def is_admin(self, workspace):
        wid = workspace.id if isinstance(workspace, Workspace) else workspace

        workspace_user = WorkspaceUser.objects.get(wid=wid, uid=self.id)
        return workspace_user.admin

    def __str__(self):
        return '{} (#{})'.format(self.fullname, self.id)


class WorkspaceUser(WorkspaceEntity):
    _can_get_detail = False
    _can_create = False

    email = fields.EmailField(is_read_only=True)
    active = fields.BooleanField()
    admin = fields.BooleanField(admin_only=True)
    user = fields.MappingField(User, 'uid', is_read_only=True)  # type: User

    def __str__(self):
        return '{} (#{})'.format(self.email, self.id)


class ProjectUser(WorkspaceEntity):
    _can_get_detail = False

    rate = fields.FloatField(admin_only=True)
    manager = fields.BooleanField(default=False)
    project = fields.MappingField(Project, 'pid', is_read_only=True)  # type: Project
    user = fields.MappingField(User, 'uid', is_read_only=True)  # type: User

    def __str__(self):
        return '{}/{} (#{})'.format(self.project.name, self.user.email, self.id)


class Task(PremiumEntity):
    name = fields.StringField(required=True)
    project = fields.MappingField(Project, 'pid', required=True)  # type: Project
    user = fields.MappingField(User, 'uid')  # type: User
    estimated_seconds = fields.IntegerField()
    active = fields.BooleanField(default=True)
    tracked_seconds = fields.IntegerField(is_read_only=True)


# Time Entry entity


class TimeEntryDateTimeField(fields.DateTimeField):
    """
    Special extension of DateTimeField which handles better way of formatting the datetime for CLI use-case.
    """

    def format(self, value, config=None, instance=None, display_running=False,
               only_time_for_same_day=None):  # type: (typing.Any, utils.Config, base.Entity, bool, pendulum.DateTime) -> typing.Any
        if not display_running and not only_time_for_same_day:
            return super().format(value, config)

        if value is None and display_running:
            return 'running'

        if instance is not None and only_time_for_same_day:
            config = config or utils.Config.factory()

            if value.in_timezone(config.timezone).to_date_string() == only_time_for_same_day.in_timezone(
                    config.timezone).to_date_string():
                return value.in_timezone(config.timezone).format(config.time_format)

        return super().format(value, config)


def get_duration(name, instance):  # type: (str, base.Entity) -> int
    """
    Getter for Duration Property field.

    Handles correctly the conversion of of negative running duration (for more refer to the Toggl API doc).
    """
    if instance.is_running:
        return instance.start.int_timestamp * -1

    return int((instance.stop - instance.start).in_seconds())


def set_duration(name, instance, value, init=False):  # type: (str, base.Entity, typing.Any, bool) -> bool
    """
    Setter for Duration Property field.
    """
    if value is None:
        return

    if value > 0:
        instance.is_running = False
        instance.stop = instance.start + pendulum.duration(seconds=value)
    else:
        instance.is_running = True
        instance.stop = None

    return True  # Any change will result in updated instance's state.


def format_duration(value, config=None):  # type: (typing.Any, utils.Config) -> str
    """
    Formatting the duration into HOURS:MINUTES:SECOND format.
    """
    if value < 0:
        value = pendulum.now().int_timestamp + value

    hours = value // 3600
    minutes = (value - hours * 3600) // 60
    seconds = (value - hours * 3600 - minutes * 60) % 60

    return '{}:{:02d}:{:02d}'.format(hours, minutes, seconds)


class TimeEntrySet(base.TogglSet):
    """
    TogglSet which is extended by current() method which returns the currently running TimeEntry.
    Moreover it extends the filtrating mechanism by native filtering according start and/or stop time.
    """

    def build_list_url(self, caller, config, conditions):  # type: (str, utils.Config, typing.Dict) -> str
        url = '/{}'.format(self.base_url)

        if caller == 'filter':
            start = conditions.pop('start', None)
            stop = conditions.pop('stop', None)

            if start is not None or stop is not None:
                url += '?'

            if start is not None:
                url += 'start_date={}&'.format(quote_plus(start.isoformat()))

            if stop is not None:
                url += 'end_date={}&'.format(quote_plus(stop.isoformat()))

        return url

    def current(self, config=None):  # type: (utils.Config) -> TimeEntry
        config = config or utils.Config.factory()
        fetched_entity = utils.toggl('/time_entries/current', 'get', config=config)

        if fetched_entity.get('data') is None:
            return None

        return self.entity_cls.deserialize(config=config, **fetched_entity['data'])


class TimeEntry(WorkspaceEntity):
    description = fields.StringField()
    project = fields.MappingField(Project, 'pid')  # type: Project
    task = fields.MappingField(Task, 'tid', premium=True)  # type: Task
    billable = fields.BooleanField(default=False, premium=True)
    start = TimeEntryDateTimeField(required=True)
    stop = TimeEntryDateTimeField()
    duration = fields.PropertyField(get_duration, set_duration, formatter=format_duration)
    created_with = fields.StringField(required=True, default='TogglCLI')
    tags = fields.SetField()

    objects = TimeEntrySet()

    def __init__(self, start, stop=None, duration=None, **kwargs):
        if stop is None and duration is None:
            raise ValueError(
                'You can create only finished time entries through this way! '
                'You must supply either \'stop\' or \'duration\' parameter!'
            )

        self.is_running = False

        super().__init__(start=start, stop=stop, duration=duration, **kwargs)

    @classmethod
    def get_url(cls):
        return 'time_entries'

    def to_dict(self, serialized=False, changes_only=False):
        # Enforcing serialize duration when start or stop changes
        if changes_only and (self.__change_dict__.get('start') or self.__change_dict__.get('stop')):
            self.__change_dict__['duration'] = None

        return super().to_dict(serialized=serialized, changes_only=changes_only)

    @classmethod
    def start_and_save(cls, start=None, config=None,
                       **kwargs):  # type: (pendulum.DateTime, utils.Config, **typing.Any) -> TimeEntry
        """
        Creates a new running entry.

        If there is another running time entry in the time of calling this method, then the running entry is stopped.
        This is handled by Toggl's backend.

        :param start: The DateTime object representing start of the new TimeEntry. If None than current time is used.
        :param config:
        :param kwargs: Other parameters for creating the new TimeEntry
        :return: New running TimeEntry
        """
        config = config or utils.Config.factory()

        if start is None:
            start = pendulum.now(config.timezone)

        if 'stop' in kwargs or 'duration' in kwargs:
            raise RuntimeError('With start_and_save() method you can not create finished entries!')

        instance = cls.__new__(cls)
        instance.__change_dict__ = {}
        instance.is_running = True
        instance._config = config
        instance.start = start

        for key, value in kwargs.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def stop_and_save(self=None, stop=None):
        """
        Stops running the entry. It has to be running entry.

        :param stop: DateTime which should be set as stop time. If None, then current time is used.
        :return: Self
        """
        if self is None:
            # noinspection PyMethodFirstArgAssignment
            self = TimeEntry.objects.current()
            if self is None:
                raise exceptions.TogglValidationException('There is no running entry to be stoped!')

        if not self.is_running:
            raise exceptions.TogglValidationException('You can\'t stop not running entry!')

        config = self._config or utils.Config.factory()

        if stop is None:
            stop = pendulum.now(config.timezone)

        self.stop = stop
        self.is_running = False
        self.save(config=config)

        return self

    def continue_and_save(self, start=None):
        """
        Creates new time entry with same description as the self entry and starts running it.

        :param start: The DateTime object representing start of the new TimeEntry. If None than current time is used.
        :return: The new TimeEntry.
        """
        if self.is_running:
            logger.warning('Trying to continue time entry {} which is already running!'.format(self))

        config = self._config or utils.Config.factory()

        if start is None:
            start = pendulum.now(config.timezone)

        new_entry = copy(self)
        new_entry.start = start
        new_entry.stop = None
        new_entry.is_running = True

        new_entry.save(config=config)

        return new_entry

    def __str__(self):
        return '{} (#{})'.format(getattr(self, 'description', ''), self.id)
