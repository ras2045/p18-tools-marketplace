#!/usr/bin/env python3
"""Embed text with a local Ollama embedding model. Usage: ollama_embed.py TEXT..."""
import json
import sys
import urllib.request

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "nomic-embed-text"


def embed(model, text, timeout=60):
    body = json.dumps({"model": model, "input": text}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return data["embeddings"][0]


def main():
    if not sys.argv[1:]:
        print("Usage: ollama_embed.py TEXT...", file=sys.stderr)
        sys.exit(1)
    text = " ".join(sys.argv[1:])

    try:
        vec = embed(DEFAULT_MODEL, text)
    except Exception as e:
        print(f"Embedding request failed (is Ollama running with {DEFAULT_MODEL} pulled?): {e}",
              file=sys.stderr)
        sys.exit(1)

    norm = sum(x * x for x in vec) ** 0.5
    print(f"model: {DEFAULT_MODEL}")
    print(f"dimensions: {len(vec)}")
    print(f"L2 norm: {norm:.4f}")
    print(f"first 8 values: {[round(x, 4) for x in vec[:8]]}")


if __name__ == "__main__":
    main()
