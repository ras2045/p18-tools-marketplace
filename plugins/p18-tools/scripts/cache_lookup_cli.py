#!/usr/bin/env python3
"""
cache-lookup -- the real tiered-confidence offline response cache built
and tested this session: instant answers for previously-seen prompts
(0.1s vs. ~2 minutes for a real LLM call, measured this session), with a
real learning lifecycle (a pattern needs 3 consistent real responses
before it's trusted enough to fast-path).

Requires a local Ollama instance (http://127.0.0.1:11434) with the
nomic-embed-text model pulled -- this tool only does the caching/matching
layer, it doesn't replace calling a real model to generate the first few
answers a pattern needs to learn from.

Usage:
    cache_lookup_cli.py check <store_file> "<prompt>"
        -> prints a hit (with the cached response) or a miss/learning status

    cache_lookup_cli.py learn <store_file> "<prompt>" "<response>"
        -> records a real response you already generated some other way,
           advancing that pattern's learning lifecycle

    cache_lookup_cli.py table <store_file>
        -> lists all learned patterns and their status
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cache_store_portable as csp


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, store_file = sys.argv[1], sys.argv[2]
    cs = csp.PortableCacheStore(store_file)

    if cmd == "check":
        prompt = sys.argv[3]
        result = cs.check(prompt)
        print(json.dumps(result, indent=2))
    elif cmd == "learn":
        prompt, response = sys.argv[3], sys.argv[4]
        cs.learn(prompt, response)
        print(f"recorded a real response for: {prompt!r}")
    elif cmd == "table":
        print(json.dumps(cs.table(), indent=2))
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
