"""
Track A: paired-lemniscate-loop codebook (fixed, non-adaptive master structure).

User's framing: "keep the master loop a baseline unchanging and the inner can
be a pair of lemniscate loop ops that can intersect in three different ways
giving the complication for context."

Loop A = the SAME size-matched cascade codebook from the original prototype
(num_bands=1, steps_per_band=7 -> 8 positive magnitudes) -- unchanged, this is
the fixed "master loop" baseline.

Loop B = a second, phase-rotated instance of the identical cascade structure:
same anchors, same geometric interpolation, but the r18 step index is offset
by half a section (phase shift of one half-step, i.e. 10 degrees of the
18-section sweep) -- a genuine second lemniscate loop, same shape, rotated
relative to the first, not a different formula.

Both loops are combined into ONE single fixed global codebook per mode --
there is no per-block adaptivity anywhere in this file, unlike the nested
scheme tested previously (which was found to be a null result specifically
because it made the outer scale data-dependent). That is the explicit point
of this test: does combining two FIXED loops geometrically beat one, without
reintroducing adaptivity.

Three intersection modes, grounded in actual two-lemniscate-curve topology
(two figure-eight curves sharing a center, related by a rotation offset):

  MODE 1 -- UNION ("share only the central crossing node"):
    The two loops' lobes are disjoint except at the shared center/origin.
    Combined codebook = A's magnitudes UNION B's magnitudes. Each weight is
    assigned to whichever single anchor (from either loop) is nearest. This
    is the cheapest combination -- roughly doubles the level count.

  MODE 2 -- PRODUCT ("arcs cross at multiple points, interference-style"):
    Rotated so the curves intersect repeatedly, not just at the center.
    Combined codeword = a_i * b_j for every pairing of an A-anchor and a
    B-anchor (a genuine two-loop PRODUCT, i.e. product quantization: each
    representable value carries information from BOTH loops jointly, not
    either alone). Up to |A|*|B| distinct values.

  MODE 3 -- VERNIER / NESTED-BUT-FIXED ("one loop's envelope tangent inside
  the other's, without crossing"):
    Loop B acts as a small, FIXED (not per-block, not data-dependent) residual
    refinement inside each of Loop A's own steps -- like a vernier scale.
    Combined codeword = a_i + eps * b_j, where eps is a single fixed global
    constant (independent of the data) chosen so B's contribution never
    exceeds A's own smallest step size, preserving strict coarse-then-fine
    ordering. This differs from the earlier (null-result) nested test because
    the "which ring" decision is NOT based on the block's data at all -- A and
    B's roles are fixed for every weight, everywhere.

This set was chosen because it maps directly onto the three topologically
distinct ways two centered curves can relate (disjoint-but-touching,
repeatedly-crossing, tangent-nested) rather than being an arbitrary list.
"""
import math
import numpy as np
from codebook import cascade_anchor, DGI, PHI, NSEC


def _positive_anchors(num_bands: int, steps_per_band: int, phase_offset_steps: float = 0.0):
    """Same construction as codebook.build_codebook, generalized with a phase offset
    (fraction of one r18 step) so a second, rotated loop can be generated from the
    identical formula."""
    anchors = [cascade_anchor(k) for k in range(num_bands + 1)]
    values = []
    for k in range(num_bands):
        hi, lo = anchors[k], anchors[k + 1]
        log_hi, log_lo = math.log(hi), math.log(lo)
        for r18 in range(steps_per_band):
            frac = (r18 + phase_offset_steps) / steps_per_band
            frac = min(max(frac, 0.0), 1.0)
            values.append(math.exp(log_hi + frac * (log_lo - log_hi)))
    values.append(anchors[num_bands])
    return np.array(sorted(set(values)), dtype=np.float64)


NUM_BANDS = 1
STEPS_PER_BAND = 7

LOOP_A = _positive_anchors(NUM_BANDS, STEPS_PER_BAND, phase_offset_steps=0.0)     # master, unchanged
LOOP_B = _positive_anchors(NUM_BANDS, STEPS_PER_BAND, phase_offset_steps=0.5)     # phase-rotated twin


def _to_signed_codebook(pos_values: np.ndarray) -> np.ndarray:
    pos_values = np.array(sorted(set(pos_values.tolist())), dtype=np.float64)
    return np.concatenate([-pos_values[::-1], [0.0], pos_values])


def mode1_union() -> np.ndarray:
    pos = np.concatenate([LOOP_A, LOOP_B])
    return _to_signed_codebook(pos)


def mode2_product() -> np.ndarray:
    pos = np.outer(LOOP_A, LOOP_B).reshape(-1)
    return _to_signed_codebook(pos)


def mode3_vernier() -> np.ndarray:
    # eps: keep B's contribution strictly under A's own smallest positive step size
    a_sorted = np.sort(LOOP_A)
    min_gap = np.min(np.diff(a_sorted))
    eps = min_gap / (np.max(LOOP_B) * 2.0)  # /2 safety margin, single fixed constant, data-independent
    pos = np.array([a + eps * b for a in LOOP_A for b in LOOP_B])
    pos = pos[pos > 0]
    return _to_signed_codebook(pos)


def nearest_quantize(data: np.ndarray, levels: np.ndarray) -> np.ndarray:
    order = np.argsort(levels)
    sorted_levels = levels[order]
    idx = np.searchsorted(sorted_levels, data)
    idx = np.clip(idx, 1, len(sorted_levels) - 1)
    left = sorted_levels[idx - 1]
    right = sorted_levels[idx]
    choose_left = (data - left) < (right - data)
    return np.where(choose_left, left, right)
