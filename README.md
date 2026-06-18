# reading-tools

`reading-tools` is a collection of command-line tools for building personal reading workflows.

The project is not limited to text-to-speech. Its broader purpose is to make reading, reviewing, extracting, transforming, listening, and working with texts easier from the command line.

The first usable version of the repo focuses on one workflow:

```text
PDF excerpt → clean text → MP3 audio
```

This is useful for reading setups where a book or article is available as a PDF, but the actual reading session concerns only a small section of it, such as a few pages or a chapter subsection.

The current implementation has two main parts:

```text
tts_preprocess    PDF → audio-ready .txt
tts_generation    audio-ready .txt → .mp3
```

---

## Current commands

### `prepare-for-audiobook`

Prepares selected PDF text for later audio generation.

This command does **not** generate audio. It extracts and cleans text from a PDF and writes a plain `.txt` file that can be passed to a TTS or audiobook generation tool.

Basic usage:

```bash
prepare-for-audiobook book.pdf --pages 34-41 -o audio-ready-book.txt
```

With section trimming:

```bash
prepare-for-audiobook book.pdf \
  --pages 34-41 \
  --start "The first words of the section" \
  --end "The first words of the next section" \
  -o audio-ready-book.txt \
  --preview
```

What it does:

1. Opens the input PDF.
2. Extracts text from the selected page range.
3. Optionally trims the text to begin at `--start`.
4. Optionally trims the text to stop at `--end`.
5. Removes repeated headers and footers.
6. Removes repeated odd/even page headers and footers.
7. Cleans common PDF extraction artifacts.
8. Writes an audio-ready `.txt` file.
9. Optionally prints a preview of the result.

The goal is to avoid manually splitting PDFs, copying text, removing headers, fixing line breaks, and preparing text by hand before generating audio.

#### Page ranges

Pages are written using human page numbers:

```bash
prepare-for-audiobook book.pdf --pages 12-18 -o section.txt
```

You can also select individual pages and mixed ranges:

```bash
prepare-for-audiobook book.pdf --pages 1,3-5,9 -o section.txt
```

Internally, the tool converts these into zero-based PDF page indexes.

#### Start and end markers

Many reading sections do not begin or end exactly at a page boundary.

Use `--start` and `--end` to keep only the relevant part:

```bash
prepare-for-audiobook book.pdf \
  --pages 20-26 \
  --start "Chapter 2. The Problem" \
  --end "Chapter 3. The Consequences" \
  -o chapter-2.txt
```

By default:

* the `--start` marker is kept in the output;
* the `--end` marker is not kept in the output.

This is useful when the end marker is actually the title of the next section.

To keep the end marker:

```bash
prepare-for-audiobook book.pdf \
  --pages 20-26 \
  --start "Chapter 2. The Problem" \
  --end "Chapter 3. The Consequences" \
  --include-end \
  -o chapter-2.txt
```

To ignore capitalization when matching markers:

```bash
prepare-for-audiobook book.pdf \
  --pages 20-26 \
  --start "chapter 2. the problem" \
  --end "chapter 3. the consequences" \
  --ignore-case \
  -o chapter-2.txt
```

#### Text cleanup

By default, `prepare-for-audiobook` performs conservative cleanup intended to make PDF text better for listening.

It can:

* fix words split by hyphenated line breaks;
* remove standalone page numbers;
* normalize spacing;
* unwrap hard PDF line breaks into paragraphs;
* collapse excessive blank lines;
* remove repeated headers and footers;
* remove odd/even page-specific running headers and footers.

Example:

```text
The theory of social ac-
tion depends on several assumptions.

42
```

becomes:

```text
The theory of social action depends on several assumptions.
```

To disable all text cleanup:

```bash
prepare-for-audiobook book.pdf \
  --pages 12-18 \
  --no-clean \
  -o raw-section.txt
```

To keep page numbers:

```bash
prepare-for-audiobook book.pdf \
  --pages 12-18 \
  --keep-page-numbers \
  -o section.txt
```

To preserve original line breaks:

```bash
prepare-for-audiobook book.pdf \
  --pages 12-18 \
  --keep-line-breaks \
  -o section.txt
```

#### Header and footer cleanup

By default, the tool tries to remove repeated marginal text.

This includes repeated headers and footers across all selected pages:

```text
BOOK TITLE
Actual page text...
```

It also checks odd and even pages separately, because books often use different running headers on left and right pages:

```text
Odd pages:   CHAPTER TITLE
Even pages:  AUTHOR NAME
```

The odd/even cleanup can also handle cases where the page number appears together with the repeated text:

```text
BOOK TITLE 13
BOOK TITLE 15
BOOK TITLE 17
```

or:

```text
14 AUTHOR NAME
16 AUTHOR NAME
18 AUTHOR NAME
```

To keep repeated headers and footers:

```bash
prepare-for-audiobook book.pdf \
  --pages 12-18 \
  --keep-headers-footers \
  --keep-parity-headers-footers \
  -o section.txt
```

To disable only the odd/even cleanup:

```bash
prepare-for-audiobook book.pdf \
  --pages 12-18 \
  --keep-parity-headers-footers \
  -o section.txt
```

To make the header/footer scan look farther into the page margins:

```bash
prepare-for-audiobook book.pdf \
  --pages 12-18 \
  --header-lines 5 \
  --footer-lines 5 \
  -o section.txt
```

#### Preview mode

Use `--preview` to inspect the prepared text before generating audio:

```bash
prepare-for-audiobook book.pdf \
  --pages 34-41 \
  --start "Actual first words" \
  --end "Next section title" \
  -o audio-ready-book.txt \
  --preview
```

To control preview length:

```bash
prepare-for-audiobook book.pdf \
  --pages 34-41 \
  -o audio-ready-book.txt \
  --preview \
  --preview-chars 1500
```

This is especially useful before sending the text to audio generation.

---

### `generate-audiobook`

Generates an MP3 file from a prepared `.txt` file.

This command assumes that the text has already been prepared, usually by `prepare-for-audiobook`.

Basic usage:

```bash
generate-audiobook audio-ready-book.txt
```

With explicit output:

```bash
generate-audiobook audio-ready-book.txt -o book.mp3
```

What it does:

1. Takes an input `.txt` file.
2. Validates that the input exists.
3. Builds the audiobook generation command.
4. Calls the configured external audio generation tool.
5. Produces an `.mp3` file.
6. Optionally moves or renames the generated MP3 to the requested output path.

The default generation backend is currently expected to be `make-audiobook`.

#### Dry run

Use `--dry-run` to inspect the command without generating audio:

```bash
generate-audiobook audio-ready-book.txt --dry-run
```

#### Engine, voice, and speed

You can pass TTS options through the wrapper:

```bash
generate-audiobook audio-ready-book.txt \
  --engine kokoro \
  --voice af_bella \
  --speed 1.2 \
  -o book.mp3
```

For Piper-style controls:

```bash
generate-audiobook audio-ready-book.txt \
  --engine piper \
  --length-scale 1.4 \
  -o book.mp3
```

To overwrite an existing MP3:

```bash
generate-audiobook audio-ready-book.txt \
  -o book.mp3 \
  --overwrite
```

To pass additional arguments to the underlying command:

```bash
generate-audiobook audio-ready-book.txt \
  -o book.mp3 \
  -- --some-extra-option value
```

---

## Full current workflow

A typical reading session looks like this:

```bash
prepare-for-audiobook book.pdf \
  --pages 34-41 \
  --start "The beginning of the section" \
  --end "The beginning of the next section" \
  -o audio-ready-book.txt \
  --preview
```

After checking the preview:

```bash
generate-audiobook audio-ready-book.txt -o book.mp3
```

This gives:

```text
book.pdf
  → selected and cleaned text section
  → audio-ready-book.txt
  → book.mp3
```

---

## Project structure

Current structure:

```text
reading-tools/
  pyproject.toml
  README.md
  src/
    tts_preprocess/
      clean.py
      cli.py
      extract.py
      page_clean.py
      pages.py
      pipeline.py
      preview.py
      trim.py
    tts_generation/
      cli.py
      generation.py
  tests/
```

### `tts_preprocess`

Responsible for turning PDF text into a clean text file.

It contains logic for:

* page range parsing;
* PDF text extraction;
* start/end marker trimming;
* text cleanup;
* header/footer cleanup;
* odd/even page marginal cleanup;
* preview rendering;
* preprocessing pipeline orchestration.

### `tts_generation`

Responsible for turning prepared text into audio.

It contains logic for:

* validating `.txt` input;
* building the external generation command;
* calling the audio generation backend;
* handling output paths;
* supporting dry runs and overwrite behavior.

---

## Installation for local development

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

After installation, the commands should be available from the repo environment:

```bash
prepare-for-audiobook --help
generate-audiobook --help
```

---

## Design notes

This repo is intentionally organized around small, composable command-line tools.

The current TTS workflow is split into two commands instead of one:

```text
prepare-for-audiobook
generate-audiobook
```

This is deliberate.

The intermediate `.txt` file is useful because it lets you inspect, edit, archive, diff, or reuse the prepared reading text before generating audio.

The project may later include tools that are not related to text-to-speech, such as tools for annotation, note extraction, bibliography handling, reading queues, summaries, flashcards, or other reading workflows.

The TTS tools are the first working part of the broader `reading-tools` project.
