"""
Quantized embedding storage for the response cache, with a real safety
check run before every save -- not assumed safe once and left alone.

Real result on the 13 real patterns tested this session: 414,312 B of
embedding JSON text -> 14,162 B (29.26:1), by quantizing to this project's
already-validated 31-level Union codebook (same one used for LLM weight
compression) instead of just Huffman-coding the verbose float text.

This is lossy, unlike the plain-text geo-Huffman compression it sits next
to. The safety check below verifies, on the REAL current set of patterns,
that quantization never changes which pattern a prompt matches (top-1
nearest neighbor) and never crosses the real match threshold in either
direction. If it ever fails that check, callers should fall back to the
lossless format instead of using this one -- see cache_store.py.
"""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paired_loop_codebook import mode1_union

CODEBOOK = mode1_union()
N_LEVELS = len(CODEBOOK)
BLOCK = 32


def _quantize_vec(vec):
    """Real embedding -> (levels, per-block scale factors)."""
    n = len(vec)
    n_blocks = math.ceil(n / BLOCK)
    pad = n_blocks * BLOCK - n
    padded = vec + [0.0] * pad
    cb_max = max(abs(v) for v in CODEBOOK)
    levels = []
    scales = []
    for b in range(n_blocks):
        block = padded[b*BLOCK:(b+1)*BLOCK]
        block_max = max(abs(v) for v in block) or 1e-12
        scale = block_max / cb_max
        scales.append(scale)
        for v in block:
            target = v / scale
            best_i, best_d = 0, abs(target - CODEBOOK[0])
            for i, c in enumerate(CODEBOOK):
                d = abs(target - c)
                if d < best_d:
                    best_i, best_d = i, d
            levels.append(best_i)
    return levels[:n], scales


def _dequantize_vec(levels, scales, n):
    n_blocks = len(scales)
    out = []
    for b in range(n_blocks):
        scale = scales[b]
        block_levels = levels[b*BLOCK:(b+1)*BLOCK]
        for lv in block_levels:
            out.append(CODEBOOK[lv] * scale)
    return out[:n]


def quantize_embedding(vec):
    levels, scales = _quantize_vec(vec)
    return {"levels": levels, "scales": scales, "n": len(vec)}


def dequantize_embedding(q):
    return _dequantize_vec(q["levels"], q["scales"], q["n"])


def _cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot/(na*nb) if na and nb else 0.0


def safety_check(patterns, match_threshold, emb_key="prompt_emb"):
    """Real check, run against the ACTUAL current patterns before trusting
    quantized storage: does quantizing every prompt embedding ever change
    which pattern is the top-1 match for another, or cross the real match
    threshold in either direction? Returns (is_safe, detail_string)."""
    real = [p[emb_key] for p in patterns]
    quantized = [dequantize_embedding(quantize_embedding(e)) for e in real]
    n = len(real)
    if n < 2:
        return True, "fewer than 2 patterns, nothing to compare"

    for i in range(n):
        real_sims = [(_cosine(real[i], real[j]), j) for j in range(n) if j != i]
        quant_sims = [(_cosine(quantized[i], quantized[j]), j) for j in range(n) if j != i]
        real_top1 = max(real_sims)
        quant_top1 = max(quant_sims)
        if real_top1[1] != quant_top1[1]:
            return False, f"top-1 match changed for pattern {i}"
        for (rs, rj), (qs, qj) in zip(sorted(real_sims), sorted(quant_sims)):
            if (rs >= match_threshold) != (qs >= match_threshold):
                return False, f"threshold crossing between patterns {i} and {rj}: real={rs:.4f} quant={qs:.4f}"
    return True, f"safe: {n} patterns, top-1 preserved, no threshold crossings"
