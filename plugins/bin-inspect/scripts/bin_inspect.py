#!/usr/bin/env python3
"""Real binary file inspector: type, size, hash, Shannon entropy, hex preview,
and honest gzip vs. geo-codec compression comparison.

Usage: bin_inspect.py <file>
"""
import gzip
import hashlib
import math
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import geo_pair_codec as gpc  # noqa: E402


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    ent = 0.0
    for c in counts:
        if c:
            p = c / n
            ent -= p * math.log2(p)
    return ent


def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"(failed to run {cmd[0]}: {e})"


def main():
    if len(sys.argv) != 2:
        print("Usage: bin_inspect.py <file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    data = open(path, "rb").read()
    size = len(data)

    print(f"file: {path}")
    print(f"size: {size} bytes")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")

    if shutil.which("file"):
        print(f"type: {run(['file', '-b', path])}")

    ent = shannon_entropy(data)
    print(f"shannon entropy: {ent:.4f} bits/byte (max 8.0000 — near 8 means "
          f"already compressed/encrypted/random-looking)")

    if shutil.which("xxd"):
        print("\nhex preview (first 128 bytes):")
        preview = run(["xxd", "-l", "128", path])
        print(preview)

    print("\ncompression comparison (real, both computed on the actual file bytes):")
    if size == 0:
        print("  (empty file — skipped)")
    else:
        gz = gzip.compress(data, compresslevel=9)
        gz_ratio = size / len(gz) if gz else 0
        print(f"  gzip -9: {len(gz)} bytes ({gz_ratio:.3f}:1)")

        try:
            geo = gpc.compress(data)
            geo_ratio = size / len(geo) if geo else 0
            print(f"  geo-pair codec: {len(geo)} bytes ({geo_ratio:.3f}:1)")
            if geo_ratio > gz_ratio:
                print("  -> geo codec wins on this file (uncommon — it usually loses to or "
                      "ties gzip; even on embedding-shaped data a real independent test "
                      "found gzip winning more often than not, so this is not a reliable "
                      "pattern to expect)")
            else:
                print("  -> gzip wins on this file (typical/expected for general binary data, "
                      "including embedding data — an earlier near-tie result on one specific "
                      "file did not hold up on independent data)")
        except Exception as e:
            print(f"  geo-pair codec: failed ({e})")

    if shutil.which("readelf"):
        header = run(["readelf", "-h", path])
        if "ELF Header" in header:
            print("\nELF header (readelf -h):")
            print(header)


if __name__ == "__main__":
    main()
