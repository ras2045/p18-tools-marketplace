---
name: bindiff
description: Real byte-level diff between two files — differing offsets grouped into contiguous runs, with hex context for each. Use when the user wants to compare two binaries (or any two files) at the byte level, not a text/line diff.
argument-hint: "<file1> <file2> [--max-runs N]"
disable-model-invocation: true
---

Requires Python 3 (standard library only, no dependencies).

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bindiff.py" $ARGUMENTS`
```

Compares the two files byte-for-byte over their overlapping length (if
sizes differ, this is reported separately, and only the common prefix
region is diffed — bytes past the shorter file's end are not "diffs",
they're absence). Differing bytes are grouped into contiguous runs (not
listed byte-by-byte), each shown with real hex context from both files.
`--max-runs N` caps how many runs are printed in detail (default 20) —
the real total run count is always reported even if truncated.

Report the real output verbatim: byte counts, percentage identical, real
offsets in hex, real hex bytes from each file. Do not estimate similarity
or guess at what changed semantically (e.g. "looks like a version bump")
unless the user asks you to interpret the diff — the tool's job is to
report exactly what differs, not what it means.
