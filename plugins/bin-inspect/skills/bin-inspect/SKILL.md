---
name: bin-inspect
description: Inspect any file — real size, SHA-256, Shannon entropy, hex preview, ELF header (if applicable), and an honest gzip-vs-geo-codec compression comparison. Use when the user wants to understand what's actually in a binary or unfamiliar file.
argument-hint: "<file>"
disable-model-invocation: true
---

Requires Python 3 (standard library only). Uses `xxd`, `file`, and
`readelf` if present on PATH for the hex preview, type string, and ELF
header respectively — each is skipped cleanly if not installed.

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bin_inspect.py" $ARGUMENTS`
```

Report the real output verbatim: size, SHA-256, Shannon entropy (bits per
byte, real Shannon formula — near 8.0 means the data already looks
compressed, encrypted, or random; well below 8.0 means it has real
exploitable structure), the hex preview, and the compression comparison.

Honest expectation to set for the user: the bundled geo-pair codec loses
to gzip on most general binary/executable data (as shown by the real
comparison the tool prints) — it only wins on specific data shapes like
embedding tables, which this tool will report honestly either way rather
than favoring one result.
