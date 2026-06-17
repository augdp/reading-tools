from pathlib import Path

from tts_preprocess.extract import ExtractedPage
from tts_preprocess.pipeline import PrepareOptions, prepare_text, run_pipeline


def test_prepare_text_runs_pipeline_steps(monkeypatch, tmp_path: Path) -> None:
    def fake_extract_pages_with_numbers(
        pdf_path: Path,
        page_indexes: list[int],
    ) -> list[ExtractedPage]:
        assert pdf_path == tmp_path / "book.pdf"
        assert page_indexes == [0, 1]

        return [
            ExtractedPage(
                page_number=1,
                text="BOOK TITLE\nRemove this. START This is hyphen-\nated.\n\n42",
            ),
            ExtractedPage(
                page_number=2,
                text="BOOK TITLE\n\nEND Remove this too.\n\n43",
            ),
        ]

    monkeypatch.setattr(
        "tts_preprocess.pipeline.extract_pages_with_numbers",
        fake_extract_pages_with_numbers,
    )

    options = PrepareOptions(
        input_pdf=tmp_path / "book.pdf",
        pages="1-2",
        output=tmp_path / "section.txt",
        start="START",
        end="END",
    )

    result = prepare_text(options)

    assert result.page_indexes == (0, 1)
    assert result.text == "START This is hyphenated.\n"
    assert result.characters_written == len("START This is hyphenated.\n")
    assert result.words_written == 4
    assert result.header_footer_cleanup_enabled is True


def test_run_pipeline_writes_output(monkeypatch, tmp_path: Path) -> None:
    def fake_extract_pages_with_numbers(
        pdf_path: Path,
        page_indexes: list[int],
    ) -> list[ExtractedPage]:
        return [
            ExtractedPage(
                page_number=1,
                text="This is extracted text.",
            )
        ]

    monkeypatch.setattr(
        "tts_preprocess.pipeline.extract_pages_with_numbers",
        fake_extract_pages_with_numbers,
    )

    output = tmp_path / "out" / "section.txt"

    options = PrepareOptions(
        input_pdf=tmp_path / "book.pdf",
        pages="1",
        output=output,
    )

    result = run_pipeline(options)

    assert output.exists()
    assert output.read_text(encoding="utf-8") == "This is extracted text.\n"
    assert result.output == output


def test_pipeline_can_keep_headers_and_footers(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def fake_extract_pages_with_numbers(
        pdf_path: Path,
        page_indexes: list[int],
    ) -> list[ExtractedPage]:
        return [
            ExtractedPage(
                page_number=1,
                text="BOOK TITLE\nPage one text.",
            ),
            ExtractedPage(
                page_number=2,
                text="BOOK TITLE\nPage two text.",
            ),
        ]

    monkeypatch.setattr(
        "tts_preprocess.pipeline.extract_pages_with_numbers",
        fake_extract_pages_with_numbers,
    )

    options = PrepareOptions(
        input_pdf=tmp_path / "book.pdf",
        pages="1-2",
        output=tmp_path / "section.txt",
        remove_headers_footers=False,
    )

    result = prepare_text(options)

    assert "BOOK TITLE" in result.text
    assert result.header_footer_cleanup_enabled is False
