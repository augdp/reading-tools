from tts_preprocess.clean import (
    clean_text,
    fix_hyphenated_line_breaks,
    normalize_spaces,
    remove_standalone_page_numbers,
    unwrap_line_breaks,
)


def test_fix_hyphenated_line_breaks() -> None:
    text = "This is hyphen-\nated text."

    result = fix_hyphenated_line_breaks(text)

    assert result == "This is hyphenated text."


def test_normalize_spaces() -> None:
    text = "This   has    spaces.\nThis\thas\ttabs."

    result = normalize_spaces(text)

    assert result == "This has spaces.\nThis has tabs."


def test_remove_standalone_page_numbers() -> None:
    text = "First paragraph.\n\n42\n\nSecond paragraph."

    result = remove_standalone_page_numbers(text)

    assert result == "First paragraph.\n\n\nSecond paragraph."


def test_unwrap_line_breaks() -> None:
    text = "This is a line\nthat should become one paragraph."

    result = unwrap_line_breaks(text)

    assert result == "This is a line that should become one paragraph."


def test_unwrap_preserves_simple_lists() -> None:
    text = "- first item\n- second item"

    result = unwrap_line_breaks(text)

    assert result == "- first item\n- second item"


def test_clean_text() -> None:
    text = "This is hyphen-\nated text.\n\n42\n\nAnother   paragraph."

    result = clean_text(text)

    assert result == "This is hyphenated text.\n\nAnother paragraph.\n"


def test_clean_text_can_keep_page_numbers() -> None:
    text = "First paragraph.\n\n42\n\nSecond paragraph."

    result = clean_text(text, remove_page_numbers=False)

    assert result == "First paragraph.\n\n42\n\nSecond paragraph.\n"


def test_clean_text_can_keep_line_breaks() -> None:
    text = "This is a line\nthat should stay broken."

    result = clean_text(text, unwrap=False)

    assert result == "This is a line\nthat should stay broken.\n"
