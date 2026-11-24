from watchdog.events import FileModifiedEvent, FileMovedEvent, FileSystemEvent

from pydoc_markdown.util.watchdog import _CallbackEventHandler


def test__CallbackEventHandler__matches_source_and_destination_paths() -> None:
    events: list[FileSystemEvent] = []
    handler = _CallbackEventHandler(events.append, ["watched.md"])

    modified = FileModifiedEvent("watched.md")
    moved_to_watched = FileMovedEvent("temporary.md", "watched.md")
    moved_elsewhere = FileMovedEvent("temporary.md", "other.md")

    handler.on_any_event(modified)
    handler.on_any_event(moved_to_watched)
    handler.on_any_event(moved_elsewhere)

    # Compare by identity: watchdog < 4 does not give non-move events a `dest_path` attribute,
    # while watchdog >= 4 sets it to an empty string, so asserting on event attributes is version-dependent.
    assert len(events) == 2
    assert events[0] is modified
    assert events[1] is moved_to_watched
