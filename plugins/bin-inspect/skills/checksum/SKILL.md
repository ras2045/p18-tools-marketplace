---
name: checksum
description: Compute real crc32, adler32, md5, sha1, sha256, and sha512 checksums for a file in one pass. Use when the user wants to verify file integrity or compare a file against a known hash.
argument-hint: "<file>"
disable-model-invocation: true
---

Requires Python 3 (standard library only — `zlib` and `hashlib`, both
built in).

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/checksum.py" $ARGUMENTS`
```

Report all six real hashes exactly as printed. If the user gives you a
hash to compare against, do a case-insensitive string match against the
matching algorithm's output — don't guess which algorithm from the hash
length alone without confirming (crc32 and adler32 are both 8 hex chars
but different algorithms; sha1 is 40 hex chars; md5 is 32; sha256 is 64;
sha512 is 128).

md5 and sha1 are included for compatibility/identity checks only — the
tool's own output notes they are not collision-safe; don't present them
as suitable for security-sensitive integrity verification without passing
that caveat along.
