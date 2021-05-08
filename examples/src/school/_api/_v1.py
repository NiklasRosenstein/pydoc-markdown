
import typing as t

if t.TYPE_CHECKING:
  from .._class import Class
  from .._pupil import Pupil
  from .._school import School
  from .._teacher import Teacher


class SchoolApiV1:
  """
  Interface for getting school data.
  """

  def get_class(self) -> 'Class':
    pass

  def get_pupil(self) -> 'Pupil':
    pass

  def get_school(self) -> 'School':
    pass

  def get_teacher(self) -> 'Teacher':
    pass
