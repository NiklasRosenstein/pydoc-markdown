from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor

from . import assert_processor_result


def test__CrossrefProcessor__does_not_disrupt_local_markdown_anchor_references() -> None:
    assert_processor_result(
        CrossrefProcessor(),
        """
        Refer to [flowchart](#flowchart), [another](help.md#charts) and check out the #Chart class.
        """,
        """
        Refer to [flowchart](#flowchart), [another](help.md#charts) and check out the `Chart` class.
        """,
    )
