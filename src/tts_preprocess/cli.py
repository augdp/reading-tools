from __future__ import annotations

import argparse
from pathlib import Path

from tts_preprocess.pages import parse_page_range


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
    except ValueError as error:
        parser.error(str(error))

    print(f"Input PDF: {args.input_pdf}")
    print(f"Output: {args.output}")
    print(f"Zero-based page indexes: {page_indexes}")

    return 0
