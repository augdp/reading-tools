from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable

from tts_preprocess.extract import ExtractedPage


LineNormalizer = Callable[[str], str]


def remove_repeated_marginal_lines(
    pages: list[ExtractedPage],
    *,
    top_lines: int = 3,
    bottom_lines: int = 3,
    min_occurrences: int = 2,
) -> list[ExtractedPage]:
    """
    Remove repeated header/footer-like lines from extracted pages.

    This is the global pass. It checks all selected pages together.
    """
    return _remove_repeated_marginal_lines_with_normalizer(
        pages,
        top_lines=top_lines,
        bottom_lines=bottom_lines,
        min_occurrences=min_occurrences,
        normalize_line=_normalize_line,
    )


def remove_repeated_marginal_lines_by_parity(
    pages: list[ExtractedPage],
    *,
    top_lines: int = 3,
    bottom_lines: int = 3,
    min_occurrences: int = 2,
) -> list[ExtractedPage]:
    """
    Remove repeated marginal lines separately for odd and even pages.

    This catches book-layout patterns where odd pages and even pages have
    different running headers/footers.

    It also treats page-like numbers as placeholders while matching, so these
    can be recognized as the same repeated header/footer pattern:

        BOOK TITLE 13
        BOOK TITLE 15
        BOOK TITLE 17

    Matching signature:

        book title <num>
    """
    if not pages:
        return pages

    cleaned_by_index: dict[int, ExtractedPage] = {
        index: page
        for index, page in enumerate(pages)
    }

    for parity in (0, 1):
        indexed_group = [
            (index, page)
            for index, page in enumerate(pages)
            if page.page_number % 2 == parity
        ]

        group_pages = [page for _, page in indexed_group]

        cleaned_group = _remove_repeated_marginal_lines_with_normalizer(
            group_pages,
            top_lines=top_lines,
            bottom_lines=bottom_lines,
            min_occurrences=min_occurrences,
            normalize_line=_normalize_line_with_number_placeholders,
        )

        for (original_index, _), cleaned_page in zip(indexed_group, cleaned_group):
            cleaned_by_index[original_index] = cleaned_page

    return [
        cleaned_by_index[index]
        for index in range(len(pages))
    ]


def join_extracted_pages(pages: list[ExtractedPage]) -> str:
    """
    Join extracted page texts into one text string.

    Pages are separated by blank lines so later cleanup can still detect
    paragraph boundaries.
    """
    chunks = []

    for page in pages:
        text = page.text.strip()

        if text:
            chunks.append(text)

    if not chunks:
        return ""

    return "\n\n".join(chunks).strip() + "\n"


def _remove_repeated_marginal_lines_with_normalizer(
    pages: list[ExtractedPage],
    *,
    top_lines: int,
    bottom_lines: int,
    min_occurrences: int,
    normalize_line: LineNormalizer,
) -> list[ExtractedPage]:
    if not pages:
        return pages

    if len(pages) < min_occurrences:
        return pages

    repeated_lines = _find_repeated_marginal_lines(
        pages,
        top_lines=top_lines,
        bottom_lines=bottom_lines,
        min_occurrences=min_occurrences,
        normalize_line=normalize_line,
    )

    if not repeated_lines:
        return pages

    cleaned_pages: list[ExtractedPage] = []

    for page in pages:
        lines = page.text.splitlines()
        removable_indexes = _marginal_line_indexes(
            lines,
            top_lines=top_lines,
            bottom_lines=bottom_lines,
        )

        kept_lines = []

        for index, line in enumerate(lines):
            normalized = normalize_line(line)

            if index in removable_indexes and normalized in repeated_lines:
                continue

            kept_lines.append(line)

        cleaned_text = "\n".join(kept_lines).strip()

        cleaned_pages.append(
            ExtractedPage(
                page_number=page.page_number,
                text=cleaned_text,
            )
        )

    return cleaned_pages


def _find_repeated_marginal_lines(
    pages: list[ExtractedPage],
    *,
    top_lines: int,
    bottom_lines: int,
    min_occurrences: int,
    normalize_line: LineNormalizer,
) -> set[str]:
    counts: Counter[str] = Counter()

    for page in pages:
        lines = page.text.splitlines()
        candidate_indexes = _marginal_line_indexes(
            lines,
            top_lines=top_lines,
            bottom_lines=bottom_lines,
        )

        seen_on_this_page: set[str] = set()

        for index in candidate_indexes:
            normalized = normalize_line(lines[index])

            if normalized:
                seen_on_this_page.add(normalized)

        counts.update(seen_on_this_page)

    return {
        line
        for line, count in counts.items()
        if count >= min_occurrences
    }


def _marginal_line_indexes(
    lines: list[str],
    *,
    top_lines: int,
    bottom_lines: int,
) -> set[int]:
    non_empty_indexes = [
        index
        for index, line in enumerate(lines)
        if line.strip()
    ]

    top_indexes = non_empty_indexes[:top_lines] if top_lines > 0 else []
    bottom_indexes = non_empty_indexes[-bottom_lines:] if bottom_lines > 0 else []

    return set(top_indexes) | set(bottom_indexes)


def _normalize_line(line: str) -> str:
    return " ".join(line.split()).casefold()


def _normalize_line_with_number_placeholders(line: str) -> str:
    normalized = _normalize_line(line)

    return re.sub(r"\b\d{1,4}\b", "<num>", normalized)
