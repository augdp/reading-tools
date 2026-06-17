import pytest

from tts_preprocess.preview import render_preview


def test_render_preview_short_text() -> None:
    result = render_preview("Short text.", max_chars=100)

    assert "Preview:" in result
    assert "Short text." in result
    assert "[...]" not in result


def test_render_preview_long_text() -> None:
    text = "A" * 120 + " middle " + "B" * 120

    result = render_preview(text, max_chars=120)

    assert "Preview:" in result
    assert "[...]" in result
    assert "A" * 20 in result
    assert "B" * 20 in result


def test_render_preview_empty_text() -> None:
    result = render_preview("", max_chars=100)

    assert "[No text extracted.]" in result


def test_preview_chars_must_be_at_least_100() -> None:
    with pytest.raises(ValueError):
        render_preview("Some text.", max_chars=50)
