---
name: ollama-ask
description: Send a prompt to a local Ollama model and return its real response. Use when the user wants a local/offline model's answer specifically, not Claude's own answer.
argument-hint: "[--model NAME] <prompt>"
disable-model-invocation: true
---

Requires a local Ollama instance at `http://127.0.0.1:11434`. Default
model is `llama3.1:8b` — pass `--model NAME` first to use a different one
(e.g. `llama3.3:70b`, `llama3.1:8b-instruct-fp16`).

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ollama_ask.py" $ARGUMENTS`
```

Report the tool's real output (model name, real token count, real elapsed
time, and the response text) exactly as printed. If Ollama isn't reachable
or the model isn't pulled, the script reports that plainly — pass that
message through, don't guess at a fix beyond what it states.

This is the local model's own answer, not Claude's — do not blend it into
your own response as if you generated it, and do not silently "improve"
or fact-check it unless the user asks you to.
