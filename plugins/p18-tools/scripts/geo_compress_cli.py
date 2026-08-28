#!/usr/bin/env python3
"""
geo-compress -- real byte-pair geo codec (canonical Huffman + geo-sorted
table + escape symbol), the same one built and tested this session on a
real 809,568-byte compiled binary and a real 425KB->44KB cache file.

Self-contained: no network dependency, no Ollama. Just this file plus
geo_pair_codec.py and wheel270_engine.py alongside it.

Usage:
    geo_compress_cli.py compress <infile> [outfile]
    geo_compress_cli.py decompress <infile> [outfile]
    geo_compress_cli.py test <infile>     # compress+decompress+verify, report real ratio
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_pair_codec as gpc

MAGIC = b"GEOC"


def cmd_compress(infile, outfile=None):
    with open(infile, "rb") as f:
        data = f.read()
    packed = MAGIC + gpc.compress(data)
    outfile = outfile or (infile + ".geoc")
    with open(outfile, "wb") as f:
        f.write(packed)
    ratio = len(data) / len(packed) if packed else 0
    print(f"{infile}: {len(data):,} B -> {outfile}: {len(packed):,} B  ({ratio:.3f}:1)")


def cmd_decompress(infile, outfile=None):
    with open(infile, "rb") as f:
        raw = f.read()
    if raw[:4] != MAGIC:
        print(f"error: {infile} is not a geo-compress file (bad magic)", file=sys.stderr)
        sys.exit(1)
    data = gpc.decompress(raw[4:])
    outfile = outfile or (infile[:-5] if infile.endswith(".geoc") else infile + ".out")
    with open(outfile, "wb") as f:
        f.write(data)
    print(f"{infile}: {len(raw):,} B -> {outfile}: {len(data):,} B")


def cmd_test(infile):
    with open(infile, "rb") as f:
        data = f.read()
    packed = gpc.compress(data)
    restored = gpc.decompress(packed)
    ratio = len(data) / len(packed) if packed else 0
    print(f"{infile}: {len(data):,} B -> {len(packed):,} B  ratio={ratio:.3f}:1  "
          f"round-trip exact={restored == data}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, infile = sys.argv[1], sys.argv[2]
    outfile = sys.argv[3] if len(sys.argv) > 3 else None
    if cmd == "compress":
        cmd_compress(infile, outfile)
    elif cmd == "decompress":
        cmd_decompress(infile, outfile)
    elif cmd == "test":
        cmd_test(infile)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
