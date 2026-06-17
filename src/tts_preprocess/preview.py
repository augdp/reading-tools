from __future__ import annotations


def render_preview(text: str, *, max_chars: int = 1000) -> str:
    """
    Render a readable terminal preview of prepared text.

    If the text is shorter than max_chars, show all of it.
    If it is longer, show the beginning and end with a separator.
    """
    if max_chars < 100:
        raise ValueError("Preview length must be at least 100 characters.")

    normalized = text.strip()

    if not normalized:
        return _wrap_preview("[No text extracted.]")

    if len(normalized) <= max_chars:
        return _wrap_preview(normalized)

    half = max_chars // 2

    beginning = normalized[:half].rstrip()
    ending = normalized[-half:].lstrip()

    preview = f"{beginning}\n\n[...]\n\n{ending}"

    return _wrap_preview(preview)


def _wrap_preview(text: str) -> str:
    line = "-" * 60

    return f"Preview:\n{line}\n{text}\n{line}"
