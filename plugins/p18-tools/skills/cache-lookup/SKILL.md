---
name: cache-lookup
description: Check or update an offline tiered-confidence response cache — instant answers for previously-seen prompts instead of a real model call. Use when the user wants to check if a query is cached, or wants to record a real answer into the cache for future reuse.
argument-hint: "[check|learn|table|export|import] <store_file> [\"prompt\"|output.json] [\"response\"]"
disable-model-invocation: true
---

Requires a local Ollama instance at `http://127.0.0.1:11434` with the
`nomic-embed-text` model pulled — this tool matches prompts by real
embedding similarity, it does not do plain string matching. If Ollama
isn't reachable, the command will fail with a connection error; tell the
user to start Ollama and pull `nomic-embed-text` first.

Run the bundled cache tool:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/cache_lookup_cli.py" $ARGUMENTS`
```

Three real subcommands:
- `check <store_file> "<prompt>"` — returns a cache hit (with the stored
  response) if a sufficiently similar prompt has already been learned and
  activated (3 consistent real responses), otherwise reports a miss or
  learning status.
- `learn <store_file> "<prompt>" "<response>"` — records a real response
  you already obtained some other way, advancing that pattern's learning
  lifecycle. This does NOT call any model itself; the response must be
  real content the user or another process already generated.
- `table <store_file>` — lists every learned pattern and its real status
  (learning / activated / abandoned) and measured consistency.
- `export <store_file> <output.json>` — writes every pattern (full
  plain-float embeddings, not the quantized on-disk form) to a portable,
  uncompressed JSON file, for sharing a learned cache to another
  machine/session.
- `import <store_file> <input.json>` — merges patterns from a file
  produced by `export` into `store_file`. No Ollama call needed — dedup
  compares the real embeddings already stored in each pattern (including
  abandoned ones, so repeated imports of the same file are idempotent —
  a real bug where they weren't was found and fixed before shipping).
  Real use case: warm-start a new machine's cache from another session's
  already-activated patterns instead of relearning from scratch.

Report the tool's real JSON output plainly. Do not claim a prompt is
cached, or invent a consistency score, if the tool didn't actually report
one — a `"hit": false` result means it's not cached, full stop, even if
you'd expect it to be.
