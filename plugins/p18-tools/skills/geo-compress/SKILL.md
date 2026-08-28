---
name: geo-compress
description: Compress or decompress a file using the real byte-pair geo codec (canonical Huffman + geo-sorted table + escape symbol). Use when the user asks to compress, shrink, or pack a file, or to decompress a .geoc file. No network dependency.
argument-hint: "[compress|decompress|test] <file> [outfile]"
disable-model-invocation: true
---

Run the bundled geo compressor on the user's file:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/geo_compress_cli.py" $ARGUMENTS`
```

Report the real output exactly as printed — it already includes the real
size before/after and the real ratio. Do not estimate or round the ratio
yourself; use the number the tool reports.

If the command is `test`, the tool compresses, decompresses, and verifies
the round-trip in one step without writing any output file — use this when
the user just wants to know how well a file would compress, not to
actually produce a compressed copy.

Honest expectation to set for the user if they ask: this codec was built
and tested this session on a real 809,568-byte compiled binary (1.277:1)
and a real cache file of JSON-text embeddings (2.246:1, beating gzip on
that specific data). Small files (well under ~1KB) often come out *larger*
after compression — the table overhead dominates — this is real, expected
behavior, not a bug, and the tool will report it honestly either way.
