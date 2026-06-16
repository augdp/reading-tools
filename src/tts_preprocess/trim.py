from __future__ import annotations


def trim_to_markers(
    text: str,
    *,
    start: str | None = None,
    end: str | None = None,
    ignore_case: bool = False,
    include_end: bool = False,
) -> str:
    """
    Trim text using optional start and end markers.

    Rules:
    - If start is provided, output begins at the start marker.
    - If end is provided, output stops at the end marker.
    - By default, the end marker is not included.
    - If include_end=True, the end marker is kept.

    Example:
        trim_to_markers("aaa START keep this END bbb", start="START", end="END")
        -> "START keep this"
    """
    if not text:
        return text

    trimmed = text

    if start:
        start_index = _find_marker(trimmed, start, ignore_case=ignore_case)

        if start_index == -1:
            raise ValueError(f"Start marker not found: {start!r}")

        trimmed = trimmed[start_index:]

    if end:
        end_index = _find_marker(trimmed, end, ignore_case=ignore_case)

        if end_index == -1:
            raise ValueError(f"End marker not found: {end!r}")

        if include_end:
            end_index = end_index + len(end)

        trimmed = trimmed[:end_index]

    return trimmed.strip() + "\n"


def _find_marker(text: str, marker: str, *, ignore_case: bool) -> int:
    marker = marker.strip()

    if not marker:
        raise ValueError("Marker cannot be empty.")

    if ignore_case:
        return text.casefold().find(marker.casefold())

    return text.find(marker)
