import pytest

from tts_preprocess.trim import trim_to_markers


def test_trim_start_marker() -> None:
    text = "Remove this. START Keep this."

    result = trim_to_markers(text, start="START")

    assert result == "START Keep this.\n"


def test_trim_end_marker_excludes_end_by_default() -> None:
    text = "Keep this. END Remove this."

    result = trim_to_markers(text, end="END")

    assert result == "Keep this.\n"


def test_trim_end_marker_can_be_included() -> None:
    text = "Keep this. END Remove this."

    result = trim_to_markers(text, end="END", include_end=True)

    assert result == "Keep this. END\n"


def test_trim_start_and_end_markers() -> None:
    text = "Remove this. START Keep this. END Remove this too."

    result = trim_to_markers(text, start="START", end="END")

    assert result == "START Keep this.\n"


def test_trim_ignores_case_when_requested() -> None:
    text = "Remove this. Start Keep this. End Remove this."

    result = trim_to_markers(
        text,
        start="start",
        end="end",
        ignore_case=True,
    )

    assert result == "Start Keep this.\n"


def test_missing_start_marker_fails() -> None:
    with pytest.raises(ValueError):
        trim_to_markers("Some text.", start="NOT HERE")


def test_missing_end_marker_fails() -> None:
    with pytest.raises(ValueError):
        trim_to_markers("Some text.", end="NOT HERE")


def test_empty_marker_fails() -> None:
    with pytest.raises(ValueError):
        trim_to_markers("Some text.", start="   ")
