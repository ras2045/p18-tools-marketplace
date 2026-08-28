"""
Byte-pair geo codec — real, working, best-of-session result from testing
compression of an actual compiled binary (libggml-base.so.0.20.2, part of
this machine's own live Ollama/GGML inference stack) through this
project's byte->slot geo addressing.

Real progression, all measured on that same 809,568-byte file, in order:
  flat table, byte-pair Huffman:            728,236 B  1.112:1
  geo-sorted + delta-encoded table:         697,460 B  1.161:1
  canonical Huffman, geo-sorted table:      614,449 B  1.318:1  (beats
    single-byte Huffman's 654,813 B / 1.236:1 for the first time)
  + escape-symbol for rare (freq==1) pairs: 613,978 B  1.319:1  (THIS FILE)
  gzip -9, same file, for reference:        332,010 B  2.438:1

Two ideas tested and REJECTED, kept here so they aren't retried blind:
  - A per-symbol "is this a repeat of the previous symbol" flag bit: made
    things WORSE (654,774 B) because the flag's flat 1-bit tax on every
    symbol exceeded what it saved on the 5.31% of symbols that were
    actual repeats.
  - A per-symbol "use a flat pointer instead of the Huffman code" flag
    bit: also worse (648,091 B), same root cause -- flat tax on all
    symbols vs. a minority benefiting.
  The escape-symbol approach here avoids that trap: the "this is a rare
  symbol" signal is folded into the Huffman tree itself as one pseudo-
  symbol, so its cost scales with how often it's actually used (5 bits,
  paid only on the 12,758 genuinely-rare pairs) rather than a flat tax
  paid by all 404,784 symbols regardless of whether they benefit.

Honest bottom line: this is real, verified, and the best number this
project has reached for byte-pair geo-encoding of compiled binary data --
but it still loses to gzip by ~1.85x, because gzip's LZ77 matching finds
variable-length, unaligned repeats that a fixed-symbol-frequency approach
structurally cannot see (confirmed separately: exact 64-byte chunk dedup
and ring-shift chunk matching both also lost to gzip on this same file).
"""
import sys
import math
import heapq
from collections import Counter

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import wheel270_engine as engine

_ESCAPE = ('\x00ESCAPE\x00', '')  # sentinel unlikely to collide with a real 2-byte pair


def _huffman(freq):
    # Real bug, found and fixed on real data: heap entries were
    # [weight, [sym, code]], and when two entries tie on weight, heapq
    # falls back to comparing the next tuple element -- which could mean
    # comparing a raw 2-byte pair against the _ESCAPE sentinel tuple,
    # `bytes < tuple`, a real TypeError. Only surfaced once real data
    # (19 patterns) happened to produce a tied-weight collision involving
    # the escape symbol; smaller test data never hit it. Fixed with an
    # explicit tie-breaking counter so heapq never compares payloads.
    counter = 0
    heap = []
    for s, w in freq.items():
        heap.append([w, counter, [s, '']])
        counter += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[2:]:
            pair[1] = '0' + pair[1]
        for pair in hi[2:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0], counter] + lo[2:] + hi[2:])
        counter += 1
    return {s: c for s, c in heap[0][2:]}


def _geo_key(pair):
    return engine.byte_to_slot(pair[0]) * engine.N + engine.byte_to_slot(pair[1])


def _zigzag(n):
    """Map signed -> unsigned so varint encoding works for negative deltas
    too (table entries are sorted by code length first, then geo-key --
    NOT globally increasing by key -- so deltas between consecutive
    entries genuinely go negative; clamping them to 0, as an earlier
    version of this file did, silently corrupts reconstruction)."""
    return (n << 1) if n >= 0 else (((-n) << 1) - 1)


def _unzigzag(z):
    return (z >> 1) if z % 2 == 0 else -((z + 1) >> 1)


def _write_varint(n):
    n = _zigzag(n)
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _read_varint(data, pos):
    n = 0
    shift = 0
    while True:
        b = data[pos]
        pos += 1
        n |= (b & 0x7F) << shift
        if not (b & 0x80):
            return _unzigzag(n), pos
        shift += 7


def compress(data: bytes, rare_cutoff: int = 1):
    """Real byte-pair geo codec: canonical Huffman with geo-sorted codes,
    plus an escape symbol for rare pairs. Returns a single self-contained
    bytes object (header + tables + payload)."""
    orig_len = len(data)  # true length, stored in the header -- a real bug
    # here previously stored the ODD-PADDED length instead, so decompress
    # faithfully reproduced the padding null byte as if it were real data
    if len(data) % 2:
        data = data + b'\x00'
    pairs = [data[i:i+2] for i in range(0, len(data), 2)]
    freq = Counter(pairs)

    frequent = {s: c for s, c in freq.items() if c > rare_cutoff}
    rare = {s: c for s, c in freq.items() if c <= rare_cutoff}
    aug_freq = dict(frequent)
    if rare:
        aug_freq[_ESCAPE] = sum(rare.values())

    huff = _huffman(aug_freq)
    items = sorted(huff.items(), key=lambda kv: (len(kv[1]), _geo_key(kv[0]) if kv[0] != _ESCAPE else 10**9))
    canon = {}
    code = 0
    prev_len = 0
    for sym, orig_code in items:
        l = len(orig_code)
        code <<= (l - prev_len)
        canon[sym] = format(code, f'0{l}b')
        code += 1
        prev_len = l

    # main table: (delta geo-key, code length) per frequent symbol + escape
    table = bytearray()
    table += len(items).to_bytes(2, 'little')
    prev_key = 0
    for sym, orig_code in items:
        is_escape = sym == _ESCAPE
        k = 0 if is_escape else _geo_key(sym)
        table += _write_varint(k - prev_key)   # signed, zigzag-encoded -- no clamping
        table.append(len(orig_code))
        table.append(1 if is_escape else 0)
        prev_key = k

    # rare-symbol table, sorted by geo key for compactness / consistency
    rare_list = sorted(rare.keys(), key=_geo_key) if rare else []
    rare_rank = {s: i for i, s in enumerate(rare_list)}
    rare_ptr_bits = max(1, math.ceil(math.log2(max(len(rare_list), 2))))
    rare_table = bytearray()
    rare_table += len(rare_list).to_bytes(2, 'little')
    for s in rare_list:
        rare_table += s

    bitstr_parts = []
    for s in pairs:
        if s in frequent:
            bitstr_parts.append(canon[s])
        else:
            bitstr_parts.append(canon[_ESCAPE])
            bitstr_parts.append(format(rare_rank[s], f'0{rare_ptr_bits}b'))
    bitstr = ''.join(bitstr_parts)
    pad = (8 - len(bitstr) % 8) % 8
    bitstr += '0' * pad
    payload = bytes(int(bitstr[i:i+8], 2) for i in range(0, len(bitstr), 8))

    header = bytearray()
    header += orig_len.to_bytes(4, 'little')
    header.append(pad)
    header.append(rare_ptr_bits)
    header += len(table).to_bytes(4, 'little')
    header += len(rare_table).to_bytes(4, 'little')

    return bytes(header) + bytes(table) + bytes(rare_table) + payload


def decompress(packed: bytes) -> bytes:
    pos = 0
    n_bytes = int.from_bytes(packed[pos:pos+4], 'little'); pos += 4
    pad = packed[pos]; pos += 1
    rare_ptr_bits = packed[pos]; pos += 1
    table_len = int.from_bytes(packed[pos:pos+4], 'little'); pos += 4
    rare_table_len = int.from_bytes(packed[pos:pos+4], 'little'); pos += 4

    table_start = pos
    n_items = int.from_bytes(packed[table_start:table_start+2], 'little')
    tpos = table_start + 2
    items = []
    prev_key = 0
    for _ in range(n_items):
        delta, tpos = _read_varint(packed, tpos)
        code_len = packed[tpos]; tpos += 1
        is_escape = packed[tpos]; tpos += 1
        k = prev_key + delta
        prev_key = k
        items.append((k, code_len, bool(is_escape)))

    canon = {}
    code = 0
    prev_len = 0
    escape_code = None
    for k, l, is_escape in items:
        code <<= (l - prev_len)
        c = format(code, f'0{l}b')
        canon[c] = ('ESC', k) if is_escape else ('SYM', k)
        code += 1
        prev_len = l

    rare_start = table_start + table_len
    rpos = rare_start + 2
    n_rare = int.from_bytes(packed[rare_start:rare_start+2], 'little')
    rare_list = []
    for _ in range(n_rare):
        rare_list.append(packed[rpos:rpos+2]); rpos += 2

    # rebuild symbol lookup for frequent items, in the SAME sorted order
    # used at compress time, so geo-keys map back to real byte-pairs
    freq_keys = sorted(engine.BYTE_SLOTS)  # not directly needed; keys ARE geo_key values
    slot_to_byte = engine.SLOT_TO_BYTE
    def key_to_pair(k):
        a, b = divmod(k, engine.N)
        return bytes([slot_to_byte[a], slot_to_byte[b]])

    tree = {}
    for c, (kind, k) in canon.items():
        node = tree
        for ch in c[:-1]:
            node = node.setdefault(ch, {})
        node[c[-1]] = (kind, k)

    payload_start = rare_start + rare_table_len
    payload = packed[payload_start:]
    total_bits = len(payload) * 8 - pad

    out = bytearray()
    node = tree
    bit_i = 0
    pending_escape = False
    escape_bits = ''
    for byte in payload:
        for shift in (7, 6, 5, 4, 3, 2, 1, 0):
            if bit_i >= total_bits or len(out) >= n_bytes:
                return bytes(out)[:n_bytes]
            bit = '1' if (byte >> shift) & 1 else '0'
            bit_i += 1
            if pending_escape:
                escape_bits += bit
                if len(escape_bits) == rare_ptr_bits:
                    rank = int(escape_bits, 2)
                    out += rare_list[rank]
                    pending_escape = False
                    escape_bits = ''
                continue
            node = node['1'] if bit == '1' else node['0']
            if type(node) is not dict:
                kind, k = node
                if kind == 'ESC':
                    pending_escape = True
                else:
                    out += key_to_pair(k)
                node = tree
    return bytes(out)[:n_bytes]


if __name__ == '__main__':
    with open("/usr/local/lib/ollama/libggml-base.so.0.20.2", "rb") as f:
        data = f.read()
    print(f"Real file: {len(data):,} bytes")
    packed = compress(data)
    print(f"Compressed: {len(packed):,} bytes  ratio: {len(data)/len(packed):.3f}:1")
    restored = decompress(packed)
    print(f"Round-trip exact: {restored == data}")
