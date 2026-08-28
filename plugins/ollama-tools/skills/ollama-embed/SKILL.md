---
name: ollama-embed
description: Get a real embedding vector for text from the local nomic-embed-text model. Use when the user wants embedding stats (dimensions, norm) or the raw vector for text, not a text answer.
argument-hint: "<text>"
disable-model-invocation: true
---

Requires a local Ollama instance at `http://127.0.0.1:11434` with
`nomic-embed-text` pulled.

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ollama_embed.py" $ARGUMENTS`
```

This prints the real dimension count (768 for `nomic-embed-text`), the
real L2 norm, and the first 8 real values — not the full vector, since
that's rarely useful to read directly. Report these numbers exactly as
printed; do not estimate or fabricate vector values.
