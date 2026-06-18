from __future__ import annotations

import argparse
from pathlib import Path

from tts_generation.generation import GenerationOptions, generate_audio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate-audiobook",
        description="Generate an MP3 audiobook from prepared text.",
    )

    parser.add_argument(
        "input_text",
        type=Path,
        help="Prepared .txt file, usually created by prepare-for-audiobook.",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output MP3 path. Defaults to INPUT.mp3 next to the text file.",
    )

    parser.add_argument(
        "--command",
        default="make-audiobook",
        help="Audiobook command to run. Default: make-audiobook.",
    )

    parser.add_argument(
        "--engine",
        choices=["kokoro", "piper", "whisperspeech"],
        help="TTS engine to pass to make-audiobook.",
    )

    parser.add_argument(
        "--voice",
        help="Voice name to pass to make-audiobook, for example af_bella.",
    )

    parser.add_argument(
        "--speed",
        type=float,
        help="Kokoro speed multiplier. Example: 1.2.",
    )

    parser.add_argument(
        "--length-scale",
        type=float,
        help="Piper length scale. Higher is slower.",
    )

    parser.add_argument(
        "--random-voice",
        action="store_true",
        help="Ask make-audiobook to use a random voice.",
    )

    parser.add_argument(
        "--random-quality",
        choices=["high", "medium", "low"],
        help="Ask make-audiobook to use a random voice filtered by quality.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing output MP3.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the make-audiobook command without running it.",
    )

    parser.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help=(
            "Extra args passed to make-audiobook after '--'. "
            "Example: generate-audiobook file.txt -- --some-option"
        ),
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    extra_args = tuple(args.extra_args)

    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]

    options = GenerationOptions(
        input_text=args.input_text,
        output_mp3=args.output,
        command=args.command,
        engine=args.engine,
        voice=args.voice,
        speed=args.speed,
        length_scale=args.length_scale,
        random_voice=args.random_voice,
        random_quality=args.random_quality,
        extra_args=extra_args,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )

    try:
        result = generate_audio(options)
    except (
        ValueError,
        FileNotFoundError,
        FileExistsError,
        RuntimeError,
    ) as error:
        parser.error(str(error))

    print(f"Input text: {result.input_text}")
    print(f"Expected make-audiobook output: {result.expected_mp3}")
    print(f"Final MP3: {result.output_mp3}")
    print(f"Command: {result.command_text}")

    if result.dry_run:
        print("Dry run: no audio was generated.")
    else:
        print("Audio generation complete.")

    return 0
