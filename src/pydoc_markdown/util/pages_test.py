import io

import pytest
from docspec_python import parse_python_module

from pydoc_markdown.util.pages import GenericPage, Page


def _load_test_module():
    return parse_python_module(
        io.StringIO(
            """
def keep():
    pass

def drop():
    pass

class Container:
    def keep(self):
        pass

    def drop(self):
        pass
"""
        ),
        "<string>",
        "package.module",
    )


def test__Pages__is_still_subscriptable_for_backwards_compatibility() -> None:
    """
    In Pydoc-markdown 4.8.1, we renamed the `Page` type to `GenericPage` and made the `Page` type a concrete
    specialized version of it to fix the deserialization issue described in [#291]. To avoid breaking code
    that uses the `Page` type and subscripts it, we keep it runtime compatible with it's old version.

    [#291]: https://github.com/NiklasRosenstein/pydoc-markdown/issues/291
    """

    class CustomPage(Page["CustomPage"]):  # type: ignore[type-arg]
        pass

    assert Page[CustomPage] == GenericPage[CustomPage]  # type: ignore[misc]


def test__GenericPage__exclude_does_not_change_positional_arguments() -> None:
    children = [Page("Child")]

    page = Page("API", "api", None, None, ["package.*"], children)  # type: ignore[misc,arg-type]

    assert page.children is children
    assert page.exclude is None


def test__GenericPage__filtered_modules__applies_exclusions_and_retains_ancestors() -> None:
    module = _load_test_module()
    page = Page(
        title="API",
        contents=["package.module.keep", "package.module.drop", "package.module.Container.*"],
        exclude=["package.module.drop", "package.module.Container.drop"],
    )

    result = page.filtered_modules([module])

    assert result[0] is not module
    assert [member.name for member in result[0].members] == ["keep", "Container"]
    assert [member.name for member in result[0].members[1].members] == ["keep"]  # type: ignore[union-attr]
    assert [member.name for member in module.members] == ["keep", "drop", "Container"]
    assert [member.name for member in module.members[2].members] == ["keep", "drop"]  # type: ignore[union-attr]


def test__GenericPage__filtered_modules__exclusion_wins_over_contents(
    caplog: pytest.LogCaptureFixture,
) -> None:
    module = _load_test_module()
    page = Page(
        title="API",
        contents=["package.module.keep", "package.module.Container.*"],
        exclude=["package.module.Container", "package.missing"],
    )

    result = page.filtered_modules([module])

    assert [member.name for member in result[0].members] == ["keep"]
    assert "contents has unmatched elements" not in caplog.text


def test__GenericPage__filtered_modules__can_exclude_a_module_and_its_members() -> None:
    module = _load_test_module()
    page = Page(
        title="API",
        contents=["package.module.*"],
        exclude=["package.module"],
    )

    assert page.filtered_modules([module]) == []
