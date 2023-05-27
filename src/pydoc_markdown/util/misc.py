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
        string = string.replace(match, f"BLOCKQUOTE_TOKEN_{i}")

    # Escape the remaining string
    escaped_string = html.escape(string)

    # Replace the placeholder tokens with their original contents
    for i, match in enumerate(blockquote_matches):
        escaped_string = escaped_string.replace(f"BLOCKQUOTE_TOKEN_{i}", match)

    return escaped_string
