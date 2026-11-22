from watchdog.events import FileModifiedEvent, FileMovedEvent, FileSystemEvent

from pydoc_markdown.util.watchdog import _CallbackEventHandler


def test__CallbackEventHandler__matches_source_and_destination_paths() -> None:
    events: list[FileSystemEvent] = []
    handler = _CallbackEventHandler(events.append, ["watched.md"])

    handler.on_any_event(FileModifiedEvent("watched.md"))
    handler.on_any_event(FileMovedEvent("temporary.md", "watched.md"))
    handler.on_any_event(FileMovedEvent("temporary.md", "other.md"))

    assert [(event.src_path, getattr(event, "dest_path", None)) for event in events] == [
        ("watched.md", ""),
        ("temporary.md", "watched.md"),
    ]
