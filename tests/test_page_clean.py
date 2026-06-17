from tts_preprocess.extract import ExtractedPage
from tts_preprocess.page_clean import (
    join_extracted_pages,
    remove_repeated_marginal_lines,
    remove_repeated_marginal_lines_by_parity,
)


def test_remove_repeated_header() -> None:
    pages = [
        ExtractedPage(
            page_number=1,
            text="BOOK TITLE\nReal text from page one.",
        ),
        ExtractedPage(
            page_number=2,
            text="BOOK TITLE\nReal text from page two.",
        ),
    ]

    result = remove_repeated_marginal_lines(pages)

    assert "BOOK TITLE" not in result[0].text
    assert "BOOK TITLE" not in result[1].text
    assert "Real text from page one." in result[0].text
    assert "Real text from page two." in result[1].text


def test_remove_repeated_footer() -> None:
    pages = [
        ExtractedPage(
            page_number=1,
            text="Real text from page one.\nCHAPTER 1",
        ),
        ExtractedPage(
            page_number=2,
            text="Real text from page two.\nCHAPTER 1",
        ),
    ]

    result = remove_repeated_marginal_lines(pages)

    assert "CHAPTER 1" not in result[0].text
    assert "CHAPTER 1" not in result[1].text
    assert "Real text from page one." in result[0].text
    assert "Real text from page two." in result[1].text


def test_does_not_remove_repeated_body_text() -> None:
    pages = [
        ExtractedPage(
            page_number=1,
            text="Header one\nImportant repeated phrase.\nBottom one",
        ),
        ExtractedPage(
            page_number=2,
            text="Header two\nImportant repeated phrase.\nBottom two",
        ),
    ]

    result = remove_repeated_marginal_lines(
        pages,
        top_lines=1,
        bottom_lines=1,
    )

    assert "Important repeated phrase." in result[0].text
    assert "Important repeated phrase." in result[1].text


def test_remove_repeated_headers_by_parity() -> None:
    pages = [
        ExtractedPage(page_number=1, text="ODD BOOK TITLE\nPage one text."),
        ExtractedPage(page_number=2, text="EVEN AUTHOR NAME\nPage two text."),
        ExtractedPage(page_number=3, text="ODD BOOK TITLE\nPage three text."),
        ExtractedPage(page_number=4, text="EVEN AUTHOR NAME\nPage four text."),
    ]

    result = remove_repeated_marginal_lines_by_parity(pages)

    assert "ODD BOOK TITLE" not in result[0].text
    assert "ODD BOOK TITLE" not in result[2].text
    assert "EVEN AUTHOR NAME" not in result[1].text
    assert "EVEN AUTHOR NAME" not in result[3].text

    assert "Page one text." in result[0].text
    assert "Page two text." in result[1].text
    assert "Page three text." in result[2].text
    assert "Page four text." in result[3].text


def test_remove_numbered_headers_by_parity() -> None:
    pages = [
        ExtractedPage(page_number=1, text="BOOK TITLE 13\nPage one text."),
        ExtractedPage(page_number=3, text="BOOK TITLE 15\nPage three text."),
        ExtractedPage(page_number=5, text="BOOK TITLE 17\nPage five text."),
    ]

    result = remove_repeated_marginal_lines_by_parity(pages)

    assert "BOOK TITLE 13" not in result[0].text
    assert "BOOK TITLE 15" not in result[1].text
    assert "BOOK TITLE 17" not in result[2].text

    assert "Page one text." in result[0].text
    assert "Page three text." in result[1].text
    assert "Page five text." in result[2].text


def test_remove_numbered_headers_with_different_order_by_parity() -> None:
    pages = [
        ExtractedPage(page_number=2, text="14 AUTHOR NAME\nPage two text."),
        ExtractedPage(page_number=4, text="16 AUTHOR NAME\nPage four text."),
        ExtractedPage(page_number=6, text="18 AUTHOR NAME\nPage six text."),
    ]

    result = remove_repeated_marginal_lines_by_parity(pages)

    assert "14 AUTHOR NAME" not in result[0].text
    assert "16 AUTHOR NAME" not in result[1].text
    assert "18 AUTHOR NAME" not in result[2].text

    assert "Page two text." in result[0].text
    assert "Page four text." in result[1].text
    assert "Page six text." in result[2].text


def test_parity_cleanup_does_not_cross_odd_even_groups() -> None:
    pages = [
        ExtractedPage(page_number=1, text="ONLY ONCE ODD\nPage one text."),
        ExtractedPage(page_number=2, text="ONLY ONCE EVEN\nPage two text."),
    ]

    result = remove_repeated_marginal_lines_by_parity(pages)

    assert "ONLY ONCE ODD" in result[0].text
    assert "ONLY ONCE EVEN" in result[1].text


def test_normalizes_spacing_and_case_when_matching() -> None:
    pages = [
        ExtractedPage(
            page_number=1,
            text="Book    Title\nReal text one.",
        ),
        ExtractedPage(
            page_number=2,
            text="book title\nReal text two.",
        ),
    ]

    result = remove_repeated_marginal_lines(pages)

    assert "Book    Title" not in result[0].text
    assert "book title" not in result[1].text


def test_does_nothing_with_one_page() -> None:
    pages = [
        ExtractedPage(
            page_number=1,
            text="BOOK TITLE\nReal text.",
        ),
    ]

    result = remove_repeated_marginal_lines(pages)

    assert result == pages


def test_join_extracted_pages() -> None:
    pages = [
        ExtractedPage(page_number=1, text="Page one text."),
        ExtractedPage(page_number=2, text="Page two text."),
    ]

    result = join_extracted_pages(pages)

    assert result == "Page one text.\n\nPage two text.\n"
