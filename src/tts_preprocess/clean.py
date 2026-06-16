from __future__ import annotations

import re


def clean_text(
    text: str,
    *,
    remove_page_numbers: bool = True,
    unwrap: bool = True,
) -> str:
    """
    Clean extracted PDF text so it is better for text-to-speech.

    This is intentionally conservative. It does not rewrite the author's text;
    it only fixes common PDF extraction artifacts.
    """
    if not text:
        return text

    cleaned = normalize_newlines(text)
    cleaned = fix_hyphenated_line_breaks(cleaned)
    cleaned = normalize_spaces(cleaned)

    if remove_page_numbers:
        cleaned = remove_standalone_page_numbers(cleaned)

    if unwrap:
        cleaned = unwrap_line_breaks(cleaned)

    cleaned = collapse_blank_lines(cleaned)

    return cleaned.strip() + "\n"


def normalize_newlines(text: str) -> str:
    """Convert Windows/Mac line endings into Unix-style newlines."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def fix_hyphenated_line_breaks(text: str) -> str:
    """
    Join words split across lines.

    Example:
        "hyphen-\\nated" -> "hyphenated"
    """
    return re.sub(r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)", "", text)


def normalize_spaces(text: str) -> str:
    """
    Normalize tabs and repeated spaces line-by-line.
    """
    lines = []

    for line in text.splitlines():
        line = line.replace("\t", " ")
        line = re.sub(r"[ ]{2,}", " ", line)
        lines.append(line.strip())

    return "\n".join(lines)


def remove_standalone_page_numbers(text: str) -> str:
    """
    Remove lines that are only page numbers.

    Example:
        "Some text\\n42\\nMore text" -> "Some text\\nMore text"
    """
    lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if re.fullmatch(r"\d{1,4}", stripped):
            continue

        lines.append(line)

    return "\n".join(lines)


def unwrap_line_breaks(text: str) -> str:
    """
    Convert hard-wrapped PDF lines into paragraphs.

    Blank lines are treated as paragraph breaks.

    Example:
        "This is a\\nwrapped sentence." -> "This is a wrapped sentence."
    """
    blocks = re.split(r"\n\s*\n", text.strip())
    cleaned_blocks: list[str] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]

        if not lines:
            continue

        if _looks_like_list(lines):
            cleaned_blocks.append("\n".join(lines))
        else:
            cleaned_blocks.append(" ".join(lines))

    return "\n\n".join(cleaned_blocks)


def collapse_blank_lines(text: str) -> str:
    """Collapse 3+ newlines into 2 newlines."""
    return re.sub(r"\n{3,}", "\n\n", text)


def _looks_like_list(lines: list[str]) -> bool:
    """
    Preserve line breaks for simple bullet or numbered lists.
    """
    list_marker = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")

    return any(list_marker.match(line) for line in lines)
