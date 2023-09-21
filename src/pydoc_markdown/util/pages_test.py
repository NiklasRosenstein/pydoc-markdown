from pydoc_markdown.util.pages import GenericPage, Page


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
