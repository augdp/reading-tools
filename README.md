# Reading Tools

I keep the tools I use for reading material here.

It's only got tts_preprocess for now, but more tools will come.

---

## Preprocessing for Audiobook Generation

Module: `tts_preprocess`

Commands: `prepare-for-audiobook book.mp3 [args]`

[args]:
- `--pages n-m` to get the document (not content) pages from `n` to `m` inclusive
- `--start "the actual first words of the section"` - inclusive
- `--end "the actual first words of the next section"` - exclusive
- `--ignore-case` - just if you can't copy-paste it

status: not done.
