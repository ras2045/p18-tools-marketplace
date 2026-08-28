#!/usr/bin/env python3
"""Real multi-algorithm checksums for a file: crc32, adler32, md5, sha1, sha256, sha512.

Usage: checksum.py <file>
"""
import hashlib
import os
import sys
import zlib


def main():
    if len(sys.argv) != 2:
        print("Usage: checksum.py <file>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    data = open(path, "rb").read()

    print(f"file: {path}")
    print(f"size: {len(data)} bytes")
    print(f"crc32:   {zlib.crc32(data) & 0xFFFFFFFF:08x}")
    print(f"adler32: {zlib.adler32(data) & 0xFFFFFFFF:08x}")
    print(f"md5:     {hashlib.md5(data).hexdigest()}  (fast, NOT collision-safe — identity only)")
    print(f"sha1:    {hashlib.sha1(data).hexdigest()}  (NOT collision-safe — identity only)")
    print(f"sha256:  {hashlib.sha256(data).hexdigest()}")
    print(f"sha512:  {hashlib.sha512(data).hexdigest()}")


if __name__ == "__main__":
    main()
