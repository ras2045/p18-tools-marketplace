#!/usr/bin/env python3
"""Real byte-level binary diff: differing offsets, run-length grouped, with hex context.

Usage: bindiff.py <file1> <file2> [--max-runs N]
"""
import os
import sys


def find_diff_runs(a: bytes, b: bytes):
    n = min(len(a), len(b))
    runs = []
    i = 0
    while i < n:
        if a[i] != b[i]:
            start = i
            while i < n and a[i] != b[i]:
                i += 1
            runs.append((start, i))  # [start, end)
        else:
            i += 1
    return runs, n


def hexline(data: bytes) -> str:
    return " ".join(f"{byte:02x}" for byte in data)


def main():
    args = sys.argv[1:]
    max_runs = 20
    if "--max-runs" in args:
        idx = args.index("--max-runs")
        max_runs = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if len(args) != 2:
        print("Usage: bindiff.py <file1> <file2> [--max-runs N]", file=sys.stderr)
        sys.exit(1)

    f1, f2 = args
    for f in (f1, f2):
        if not os.path.isfile(f):
            print(f"File not found: {f}", file=sys.stderr)
            sys.exit(1)

    a = open(f1, "rb").read()
    b = open(f2, "rb").read()

    print(f"{f1}: {len(a)} bytes")
    print(f"{f2}: {len(b)} bytes")

    if a == b:
        print("RESULT: identical (byte-for-byte)")
        return

    if len(a) != len(b):
        print(f"size differs by {abs(len(a) - len(b))} bytes "
              f"(comparing the first {min(len(a), len(b))} bytes common to both)")

    runs, compared_len = find_diff_runs(a, b)
    diff_bytes = sum(end - start for start, end in runs)
    pct_same = 100.0 * (compared_len - diff_bytes) / compared_len if compared_len else 0.0

    print(f"compared {compared_len} bytes (the overlapping region): "
          f"{diff_bytes} differ ({pct_same:.2f}% identical)")
    print(f"{len(runs)} contiguous differing run(s){' (showing first ' + str(max_runs) + ')' if len(runs) > max_runs else ''}:")

    for start, end in runs[:max_runs]:
        length = end - start
        print(f"\n  offset 0x{start:x}-0x{end - 1:x} ({length} byte{'s' if length != 1 else ''}):")
        print(f"    {f1}: {hexline(a[start:min(end, start + 16)])}"
              f"{' ...' if length > 16 else ''}")
        print(f"    {f2}: {hexline(b[start:min(end, start + 16)])}"
              f"{' ...' if length > 16 else ''}")

    if len(runs) > max_runs:
        print(f"\n  ... and {len(runs) - max_runs} more run(s) not shown")


if __name__ == "__main__":
    main()
