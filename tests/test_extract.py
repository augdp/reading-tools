from pathlib import Path

import fitz

from tts_preprocess.extract import extract_pages


def make_test_pdf(path: Path) -> None:
    document = fitz.open()

    page_1 = document.new_page()
    page_1.insert_text((72, 72), "This is page one.")

    page_2 = document.new_page()
    page_2.insert_text((72, 72), "This is page two.")

    page_3 = document.new_page()
    page_3.insert_text((72, 72), "This is page three.")

    document.save(path)
    document.close()


def test_extract_single_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    make_test_pdf(pdf_path)

    text = extract_pages(pdf_path, [0])

    assert "This is page one." in text
    assert "This is page two." not in text


def test_extract_multiple_pages(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    make_test_pdf(pdf_path)

    text = extract_pages(pdf_path, [0, 2])

    assert "This is page one." in text
    assert "This is page two." not in text
    assert "This is page three." in text
