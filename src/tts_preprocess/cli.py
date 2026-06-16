from __future__ import annotations

import argparse
from pathlib import Path

from tts_preprocess.extract import extract_pages
from tts_preprocess.pages import parse_page_range
from tts_preprocess.trim import trim_to_markers


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

    try:
        page_indexes = parse_page_range(args.pages)

        text = extract_pages(args.input_pdf, page_indexes)

        text = trim_to_markers(
            text,
            start=args.start,
            end=args.end,
            ignore_case=args.ignore_case,
            include_end=args.include_end,
        )

    except ValueError as error:
        parser.error(str(error))
    except FileNotFoundError as error:
        parser.error(str(error))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")

    print(f"Input PDF: {args.input_pdf}")
    print(f"Pages: {args.pages}")
    print(f"Output: {args.output}")
    print(f"Characters written: {len(text)}")

    return 0
