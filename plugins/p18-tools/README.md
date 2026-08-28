# P18 Geo Tools — Claude Code Plugin

Two real, tested tools from a research session building geometric data
addressing and compression, packaged as an installable Claude Code plugin.

## What's real here

- **`/p18-tools:geo-compress`** — a byte-pair Huffman compressor (canonical
  codes, geo-sorted table, escape symbol for rare pairs). Tested on a real
  809,568-byte compiled binary (1.277:1). On a real 13-pattern cache file
  of embedding data it edged out gzip -9 by about 1% (2.246:1 vs 2.222:1),
  but a follow-up test on an independent, freshly generated embedding set
  (20 patterns, unrelated text, same embedding model) reversed that —
  gzip won there (2.741:1 vs 2.493:1). **Conclusion: this codec does not
  reliably beat gzip on embedding data** — the original result was a
  near-tie specific to one file, not a generalizable property. Treat gzip
  as the safer default; this codec's real, general behavior is "usually
  loses to gzip, occasionally close." No network dependency.
- **`/p18-tools:cache-lookup`** — a tiered-confidence offline response
  cache. A pattern needs 3 consistent real responses before it's trusted
  to fast-path; once activated, real measured lookup time was ~0.1s versus
  the ~2 minutes a real local LLM call took to generate the answer being
  cached. Requires a local Ollama instance with `nomic-embed-text` pulled
  (matches by real embedding similarity, not string matching).

## Requirements

- Python 3 on PATH
- `numpy` (`pip install numpy`) — used by the compression codec's
  quantization step
- For `cache-lookup` only: a local Ollama instance
  (`http://127.0.0.1:11434`) with `ollama pull nomic-embed-text`

## Install (local, not published to a marketplace)

Test without installing:
```
claude --plugin-dir /path/to/p18-tools-plugin
```

Install for yourself, in every project:
```
claude plugin install /path/to/p18-tools-plugin --scope user
```

Install for just the current project (commits to `.claude/settings.json`):
```
claude plugin install /path/to/p18-tools-plugin --scope project
```

## Structure

```
p18-tools-plugin/
├── .claude-plugin/plugin.json   # manifest
├── skills/
│   ├── geo-compress/SKILL.md
│   └── cache-lookup/SKILL.md
└── scripts/                     # the real, bundled Python implementation
    ├── geo_compress_cli.py      # entry point for /p18-tools:geo-compress
    ├── cache_lookup_cli.py      # entry point for /p18-tools:cache-lookup
    ├── geo_pair_codec.py        # the real codec
    ├── wheel270_engine.py       # byte/prime/op addressing this codec's geo-sort uses
    ├── cache_store_portable.py  # the cache logic (portable version of cache_store.py)
    ├── embedding_quant.py       # real embedding quantization + safety check
    ├── paired_loop_codebook.py  # the Union codebook embedding_quant uses
    └── codebook.py              # cascade-anchor primitives paired_loop_codebook uses
```

Both `disable-model-invocation: true` skills are user-triggered only
(`/p18-tools:geo-compress`, `/p18-tools:cache-lookup`) — Claude won't
invoke them automatically mid-conversation.
