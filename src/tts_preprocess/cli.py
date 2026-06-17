from __future__ import annotations

import argparse
from pathlib import Path

from tts_preprocess.pipeline import PrepareOptions, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prepare-for-audiobook",
        description="Prepare selected PDF pages for audiobook generation.",
    )

    parser.add_argument(
        "input_pdf",
        type=Path,
        help="Path to the input PDF.",
    )

    parser.add_argument(
        "--pages",
        required=True,
        help='Pages to extract, for example "12-18" or "1,3-5".',
    )

    parser.add_argument(
        "--start",
        help="Phrase where the output text should begin.",
    )

    parser.add_argument(
        "--end",
        help="Phrase where the output text should stop.",
    )

    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Match --start and --end without caring about capitalization.",
    )

    parser.add_argument(
        "--include-end",
        action="store_true",
        help="Keep the --end phrase in the output text.",
    )

    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip text cleanup and write the extracted/trimmed text as-is.",
    )

    parser.add_argument(
        "--keep-page-numbers",
        action="store_true",
        help="Do not remove standalone page numbers during cleanup.",
    )

    parser.add_argument(
        "--keep-line-breaks",
        action="store_true",
        help="Do not unwrap PDF line breaks into paragraphs during cleanup.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("audio-ready-book.txt"),
        help="Output text file path.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    options = PrepareOptions(
        input_pdf=args.input_pdf,
        pages=args.pages,
        output=args.output,
        start=args.start,
        end=args.end,
        ignore_case=args.ignore_case,
        include_end=args.include_end,
        clean=not args.no_clean,
        remove_page_numbers=not args.keep_page_numbers,
        unwrap=not args.keep_line_breaks,
    )

    try:
        result = run_pipeline(options)
    except ValueError as error:
        parser.error(str(error))
    except FileNotFoundError as error:
        parser.error(str(error))

    print(f"Input PDF: {result.input_pdf}")
    print(f"Pages: {result.pages}")
    print(f"Output: {result.output}")
    print(f"Cleanup: {'enabled' if result.cleanup_enabled else 'disabled'}")
    print(f"Characters written: {result.characters_written}")
    print(f"Words written: {result.words_written}")

    return 0
