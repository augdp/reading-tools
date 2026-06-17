from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tts_preprocess.clean import clean_text
from tts_preprocess.extract import extract_pages_with_numbers
from tts_preprocess.page_clean import (
    join_extracted_pages,
    remove_repeated_marginal_lines,
    remove_repeated_marginal_lines_by_parity,
)
from tts_preprocess.pages import parse_page_range
from tts_preprocess.trim import trim_to_markers


@dataclass(frozen=True)
class PrepareOptions:
    input_pdf: Path
    pages: str
    output: Path
    start: str | None = None
    end: str | None = None
    ignore_case: bool = False
    include_end: bool = False
    clean: bool = True
    remove_page_numbers: bool = True
    unwrap: bool = True
    remove_headers_footers: bool = True
    remove_parity_headers_footers: bool = True
    header_footer_top_lines: int = 3
    header_footer_bottom_lines: int = 3


@dataclass(frozen=True)
class PrepareResult:
    input_pdf: Path
    output: Path
    pages: str
    page_indexes: tuple[int, ...]
    text: str
    cleanup_enabled: bool
    header_footer_cleanup_enabled: bool
    parity_header_footer_cleanup_enabled: bool

    @property
    def characters_written(self) -> int:
        return len(self.text)

    @property
    def words_written(self) -> int:
        return len(self.text.split())


def run_pipeline(options: PrepareOptions) -> PrepareResult:
    """
    Run the full PDF-to-clean-text pipeline and write the output file.
    """
    result = prepare_text(options)
    write_prepared_text(result)
    return result


def prepare_text(options: PrepareOptions) -> PrepareResult:
    """
    Prepare audiobook-friendly text from a PDF without writing it yet.

    Pipeline:
    1. parse page range
    2. extract selected pages
    3. remove repeated page headers/footers
    4. join pages into one text
    5. trim start/end markers
    6. clean text for TTS
    """
    page_indexes = tuple(parse_page_range(options.pages))

    extracted_pages = extract_pages_with_numbers(
        options.input_pdf,
        list(page_indexes),
    )

    if options.remove_headers_footers:
        extracted_pages = remove_repeated_marginal_lines(
            extracted_pages,
            top_lines=options.header_footer_top_lines,
            bottom_lines=options.header_footer_bottom_lines,
        )

    if options.remove_parity_headers_footers:
        extracted_pages = remove_repeated_marginal_lines_by_parity(
            extracted_pages,
            top_lines=options.header_footer_top_lines,
            bottom_lines=options.header_footer_bottom_lines,
        )

    text = join_extracted_pages(extracted_pages)

    text = trim_to_markers(
        text,
        start=options.start,
        end=options.end,
        ignore_case=options.ignore_case,
        include_end=options.include_end,
    )

    if options.clean:
        text = clean_text(
            text,
            remove_page_numbers=options.remove_page_numbers,
            unwrap=options.unwrap,
        )

    return PrepareResult(
        input_pdf=options.input_pdf,
        output=options.output,
        pages=options.pages,
        page_indexes=page_indexes,
        text=text,
        cleanup_enabled=options.clean,
        header_footer_cleanup_enabled=options.remove_headers_footers,
        parity_header_footer_cleanup_enabled=options.remove_parity_headers_footers,
    )


def write_prepared_text(result: PrepareResult) -> None:
    """
    Write prepared text to disk.
    """
    result.output.parent.mkdir(parents=True, exist_ok=True)
    result.output.write_text(result.text, encoding="utf-8")
