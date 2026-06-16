import pytest

from tts_preprocess.pages import parse_page_range


def test_single_page() -> None:
    assert parse_page_range("4") == [3]


def test_simple_range() -> None:
    assert parse_page_range("4-6") == [3, 4, 5]


def test_mixed_pages_and_ranges() -> None:
    assert parse_page_range("1,3-5,8") == [0, 2, 3, 4, 7]


def test_duplicate_pages_are_removed() -> None:
    assert parse_page_range("1,1,2-3,3") == [0, 1, 2]


def test_empty_page_range_fails() -> None:
    with pytest.raises(ValueError):
        parse_page_range("")


def test_zero_page_fails() -> None:
    with pytest.raises(ValueError):
        parse_page_range("0")


def test_backwards_range_fails() -> None:
    with pytest.raises(ValueError):
        parse_page_range("8-3")


def test_non_numeric_page_fails() -> None:
    with pytest.raises(ValueError):
        parse_page_range("abc")
