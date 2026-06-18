from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GenerationOptions:
    input_text: Path
    output_mp3: Path | None = None
    command: str = "make-audiobook"
    engine: str | None = None
    voice: str | None = None
    speed: float | None = None
    length_scale: float | None = None
    random_voice: bool = False
    random_quality: str | None = None
    extra_args: tuple[str, ...] = ()
    dry_run: bool = False
    overwrite: bool = False


@dataclass(frozen=True)
class GenerationResult:
    input_text: Path
    expected_mp3: Path
    output_mp3: Path
    command: tuple[str, ...]
    dry_run: bool

    @property
    def command_text(self) -> str:
        return " ".join(self.command)


def generate_audio(options: GenerationOptions) -> GenerationResult:
    """
    Generate an MP3 from a prepared text file by calling make-audiobook.

    make-audiobook writes INPUT_STEM.mp3 next to the input file.
    If output_mp3 is provided, we move that generated file afterward.
    """
    input_text = options.input_text.expanduser().resolve()

    if not input_text.exists():
        raise FileNotFoundError(f"Input text file not found: {input_text}")

    if not input_text.is_file():
        raise ValueError(f"Input path is not a file: {input_text}")

    if input_text.suffix.lower() != ".txt":
        raise ValueError(
            f"Expected a .txt file from tts_preprocess, got: {input_text.name}"
        )

    resolved_command = resolve_command(options.command)

    expected_mp3 = input_text.with_suffix(".mp3")

    output_mp3 = (
        options.output_mp3.expanduser().resolve()
        if options.output_mp3 is not None
        else expected_mp3
    )

    command = build_make_audiobook_command(options, input_text, resolved_command)

    result = GenerationResult(
        input_text=input_text,
        expected_mp3=expected_mp3,
        output_mp3=output_mp3,
        command=tuple(command),
        dry_run=options.dry_run,
    )

    if options.dry_run:
        return result

    if output_mp3.exists() and not options.overwrite:
        raise FileExistsError(
            f"Output already exists: {output_mp3}. Use --overwrite to replace it."
        )

    if expected_mp3.exists() and expected_mp3 != output_mp3 and not options.overwrite:
        raise FileExistsError(
            f"make-audiobook output already exists: {expected_mp3}. "
            "Use --overwrite to replace it."
        )

    completed = subprocess.run(command, check=False)

    if completed.returncode != 0:
        raise RuntimeError(
            f"Audio generation failed with exit code {completed.returncode}."
        )

    if not expected_mp3.exists():
        raise FileNotFoundError(
            f"Expected output was not created: {expected_mp3}"
        )

    if output_mp3 != expected_mp3:
        output_mp3.parent.mkdir(parents=True, exist_ok=True)

        if output_mp3.exists() and options.overwrite:
            output_mp3.unlink()

        shutil.move(str(expected_mp3), str(output_mp3))

    return result


def build_make_audiobook_command(
    options: GenerationOptions,
    input_text: Path,
    resolved_command: str | None = None,
) -> list[str]:
    command = [
        resolved_command or options.command,
        str(input_text),
    ]

    if options.engine:
        command.append(f"--engine={options.engine}")

    if options.voice:
        command.append(f"--voice={options.voice}")

    if options.speed is not None:
        command.append(f"--speed={options.speed}")

    if options.length_scale is not None:
        command.append(f"--length_scale={options.length_scale}")

    if options.random_voice:
        command.append("--random-voice")

    if options.random_quality:
        command.append(f"--random={options.random_quality}")

    command.extend(options.extra_args)

    return command


def resolve_command(command: str) -> str:
    """
    Resolve a command name or explicit executable path.

    Examples:
        "make-audiobook"
        "/home/augdp/projects/make-audiobook/.venv/bin/make-audiobook"
        "~/projects/make-audiobook/.venv/bin/make-audiobook"
    """
    expanded = Path(command).expanduser()

    if expanded.parent != Path("."):
        if not expanded.exists():
            raise FileNotFoundError(f"Command not found: {expanded}")

        if not expanded.is_file():
            raise ValueError(f"Command path is not a file: {expanded}")

        return str(expanded.resolve())

    resolved = shutil.which(command)

    if resolved is None:
        raise FileNotFoundError(
            f"Could not find {command!r} on PATH. "
            "Install make-audiobook, add it to PATH, or pass --command."
        )

    return resolved
