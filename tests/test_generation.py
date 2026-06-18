from pathlib import Path

from tts_generation.generation import (
    GenerationOptions,
    build_make_audiobook_command,
)


def test_build_basic_command(tmp_path: Path) -> None:
    input_text = tmp_path / "section.txt"

    options = GenerationOptions(input_text=input_text)

    command = build_make_audiobook_command(options, input_text)

    assert command == ["make-audiobook", str(input_text)]


def test_build_command_with_engine_voice_and_speed(tmp_path: Path) -> None:
    input_text = tmp_path / "section.txt"

    options = GenerationOptions(
        input_text=input_text,
        engine="kokoro",
        voice="af_bella",
        speed=1.2,
    )

    command = build_make_audiobook_command(options, input_text)

    assert command == [
        "make-audiobook",
        str(input_text),
        "--engine=kokoro",
        "--voice=af_bella",
        "--speed=1.2",
    ]


def test_build_command_with_piper_length_scale(tmp_path: Path) -> None:
    input_text = tmp_path / "section.txt"

    options = GenerationOptions(
        input_text=input_text,
        engine="piper",
        length_scale=1.8,
    )

    command = build_make_audiobook_command(options, input_text)

    assert command == [
        "make-audiobook",
        str(input_text),
        "--engine=piper",
        "--length_scale=1.8",
    ]


def test_build_command_with_random_quality(tmp_path: Path) -> None:
    input_text = tmp_path / "section.txt"

    options = GenerationOptions(
        input_text=input_text,
        random_quality="high",
    )

    command = build_make_audiobook_command(options, input_text)

    assert command == [
        "make-audiobook",
        str(input_text),
        "--random=high",
    ]


def test_build_command_with_extra_args(tmp_path: Path) -> None:
    input_text = tmp_path / "section.txt"

    options = GenerationOptions(
        input_text=input_text,
        extra_args=("--some-option", "value"),
    )

    command = build_make_audiobook_command(options, input_text)

    assert command == [
        "make-audiobook",
        str(input_text),
        "--some-option",
        "value",
    ]
