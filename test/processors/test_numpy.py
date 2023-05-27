import pytest

from pydoc_markdown.contrib.processors.numpy import NumpyProcessor

from . import assert_processor_result

docstring_a = """
    Generate ordinary dialogue.
    
    Extended Summary
    ----------------
    This function generates ordinary dialogue so that users can fully enjoy how efficient the code is.
    
    Parameters
    ----------
    lines : int
        The number of lines of dialogue to generate.
    
    Returns
    -------
    list[str]
        The generated lines of dialogue.
    
    Raises
    ------
    ValueError
        If *lines* is not a positive integer.
    
    Examples
    --------
    >>> ordinary_dialogue(5)
    ["You should just read this manga as is.",
    "Why would anyone want to make an anime adaptation?",
    "This is a dialogue-heavy piece with hardly any action.",
    "Not to mention most of it takes place in a dressing room.",
    "So why would anyone turn a manga like this into an anime?"]
    """

md_docstring_a = """
    Generate ordinary dialogue.
    
    This function generates ordinary dialogue so that users can fully enjoy how efficient the code is.
    
    **Arguments**
    
    * **lines** (`int`): The number of lines of dialogue to generate.
    
    **Returns**
    
    * `list[str]`: The generated lines of dialogue.
    
    **Raises**
    
    * `ValueError`: If *lines* is not a positive integer.
    
    **Examples**
    
    ```python
    >>> ordinary_dialogue(5)
    ["You should just read this manga as is.",
    "Why would anyone want to make an anime adaptation?",
    "This is a dialogue-heavy piece with hardly any action.",
    "Not to mention most of it takes place in a dressing room.",
    "So why would anyone turn a manga like this into an anime?"]
    ```
    """

docstring_b = """
    Shout "You fool!".
    
    Notes
    -----
    The average "You fool!" travels at 340 m/s[1]_.
    
    References
    ----------
    .. [1] Tsutomu Mizushima (Director). (2012, July 5). Normal Dialogue / Different Clothes / Shouting Instructions 
    (No. 1). In Joshiraku. Mainichi Broadcasting System.
    
    Examples
    --------
    >>> you_fool()
    "You fool!"
    
    See Also
    --------
    :func:`bakayarou`
        The same function but in Japanese for no reason in particular.
    """

md_docstring_b = """
    Shout "You fool!".
    
    **Notes**
    
    The average "You fool!" travels at 340 m/s<sup>1</sup>.
    
    **References**
    
    1. Tsutomu Mizushima (Director). (2012, July 5). Normal Dialogue / Different Clothes / Shouting Instructions
    (No. 1). In Joshiraku. Mainichi Broadcasting System.
    
    **Examples**
    
    ```python
    >>> you_fool()
    "You fool!"
    ``` 
    
    **See Also**
    
    * :func:`bakayarou`: The same function but in Japanese for no reason in particular.
    """


@pytest.mark.parametrize("processor", [NumpyProcessor()])
def test_numpy_processor(processor):
    assert_processor_result(processor or NumpyProcessor(), docstring_a, md_docstring_a)
    assert_processor_result(processor or NumpyProcessor(), docstring_b, md_docstring_b)
