from pathlib import Path

from tts_preprocess.pipeline import PrepareOptions, prepare_text, run_pipeline


def test_prepare_text_runs_pipeline_steps(monkeypatch, tmp_path: Path) -> None:
    def fake_extract_pages(pdf_path: Path, page_indexes: list[int]) -> str:
        assert pdf_path == tmp_path / "book.pdf"
        assert page_indexes == [0, 1]
        return "Remove this. START This is hyphen-\nated.\n\n42\n\nEND Remove this too."

    monkeypatch.setattr(
        "tts_preprocess.pipeline.extract_pages",
        fake_extract_pages,
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


def test_run_pipeline_writes_output(monkeypatch, tmp_path: Path) -> None:
    def fake_extract_pages(pdf_path: Path, page_indexes: list[int]) -> str:
        return "This is extracted text."

    monkeypatch.setattr(
        "tts_preprocess.pipeline.extract_pages",
        fake_extract_pages,
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
