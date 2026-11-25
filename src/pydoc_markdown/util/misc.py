import html
import re


def escape_except_blockquotes(string: str) -> str:
    """
    Html-escape a string, except the content in markdown blockquotes.
    """

    # Define regex patterns to match blockquotes
    single_quote_pattern = r"`[^`]*`"
    triple_quote_pattern = r"```[\s\S]*?```"

    # Find all blockquotes in the string
    blockquote_matches = re.findall(f"({triple_quote_pattern}|{single_quote_pattern})", string)

    # Replace all blockquotes with placeholder tokens to preserve their contents
    for i, match in enumerate(blockquote_matches):
        string = string.replace(match, f"BLOCKQUOTE_TOKEN_{i}_END")

    # Escape the remaining string
    escaped_string = html.escape(string)

    # Replace the placeholder tokens with their original contents
    for i, match in enumerate(blockquote_matches):
        escaped_string = escaped_string.replace(f"BLOCKQUOTE_TOKEN_{i}_END", match)

    return escaped_string


#: Matches fenced code blocks (backtick or tilde fences) and inline code spans (any number of backticks).
_MARKDOWN_CODE_RE = re.compile(
    r"^[ \t]*(?P<fence>`{3,}|~{3,})[^\n]*\n[\s\S]*?^[ \t]*(?P=fence)[ \t]*$"
    r"|(?P<ticks>`+)[\s\S]*?(?<!`)(?P=ticks)(?!`)",
    re.MULTILINE,
)

#: Matches a curly brace that is not already escaped with a backslash.
_UNESCAPED_CURLY_BRACE_RE = re.compile(r"(?<!\\)([{}])")


def escape_curly_brackets(string: str) -> str:
    """
    Escape `{` and `}` with a backslash, except inside fenced code blocks and inline code, and except where they are
    already escaped. MDX (v2 and later) otherwise parses them as JavaScript expressions.
    """

    parts = []
    position = 0
    for match in _MARKDOWN_CODE_RE.finditer(string):
        parts.append(_UNESCAPED_CURLY_BRACE_RE.sub(r"\\\1", string[position : match.start()]))
        parts.append(match.group())
        position = match.end()
    parts.append(_UNESCAPED_CURLY_BRACE_RE.sub(r"\\\1", string[position:]))
    return "".join(parts)
