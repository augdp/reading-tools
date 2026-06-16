from __future__ import annotations


def parse_page_range(value: str) -> list[int]:
    """
    Convert a human page range into zero-based page indexes.

    Examples:
        "4"     -> [3]
        "4-6"   -> [3, 4, 5]
        "1,3-5" -> [0, 2, 3, 4]
    """
    value = value.strip()

    if not value:
        raise ValueError("Page range cannot be empty.")

    pages: list[int] = []

    for part in value.split(","):
        part = part.strip()

        if not part:
            raise ValueError(f"Invalid page range: {value!r}")

        if "-" in part:
            start_text, end_text = part.split("-", maxsplit=1)
            start = _parse_positive_int(start_text)
            end = _parse_positive_int(end_text)

            if end < start:
                raise ValueError(
                    f"Invalid page range {part!r}: end page is before start page."
                )

            pages.extend(range(start - 1, end))
        else:
            page = _parse_positive_int(part)
            pages.append(page - 1)

    return _dedupe_preserve_order(pages)


def _parse_positive_int(value: str) -> int:
    value = value.strip()

    if not value.isdigit():
        raise ValueError(f"Expected a positive page number, got {value!r}.")

    number = int(value)

    if number < 1:
        raise ValueError(f"Page numbers start at 1, got {number}.")

    return number


def _dedupe_preserve_order(values: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result
