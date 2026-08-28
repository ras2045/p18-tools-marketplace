"""
Lemniscate/prime integer codebook for LLM weight quantization.

Grounded in the P18/LGO18 framework's documented cascade formula
(from the project's own system-prompt context, 01_STATE.md-derived facts):

  DGI = 13/800 exact = 0.01625          (master constant)
  phi = (1+sqrt(5))/2                    (golden ratio)
  A_0 = 1
  A_1 = DGI
  A_k = phi^(k-1) * DGI^k    for k >= 2  (documented as exact only for k=0,1;
                                          k>=2 uses this explicit non-geometric form,
                                          NOT a naive continuation of A_1 * rho^(k-1))
  Nsec = 18 sections; sweep t = r18 * pi/9 (full 2*pi over 18 sections)

Codebook construction:
  - Cascade anchors A_0..A_K define K "octave bands" (each band = [A_k, A_{k-1}]).
  - Within each band, r18 in [0, STEPS_PER_BAND) subdivides it via *geometric*
    interpolation (log-uniform steps), using the section index as the fine-grained
    integer coordinate -- this is the literal "18-fold sweep" from the framework
    applied as the intra-octave resolution, not decoration.
  - Each codeword is addressed by an integer coordinate (sign, k, r18) -- whole
    numbers only, no floats needed to *store* a codeword, only to *generate* the
    table once (matches the "whole integer math" requirement: runtime lookup/index
    arithmetic is integer, the float values live in a precomputed table exactly
    like GGUF's own block-scale dequant tables do).
"""
import math
import numpy as np

DGI = 13 / 800  # exact per framework
PHI = (1 + math.sqrt(5)) / 2
NSEC = 18


def cascade_anchor(k: int) -> float:
    """A_k per framework's documented (non-naive) formula."""
    if k == 0:
        return 1.0
    if k == 1:
        return DGI
    return (PHI ** (k - 1)) * (DGI ** k)


def build_codebook(num_bands: int, steps_per_band: int = NSEC):
    """
    Build a signed lemniscate/cascade codebook.

    Returns:
        values: sorted 1D float array of representable magnitudes (positive only;
                 sign handled separately -> full codebook is values + (-values) + {0})
        coords: list of (k, r18) integer coordinates matching `values` order
    """
    anchors = [cascade_anchor(k) for k in range(num_bands + 1)]  # A_0 .. A_num_bands
    values = []
    coords = []
    for k in range(num_bands):
        hi, lo = anchors[k], anchors[k + 1]  # hi = A_k (band top), lo = A_{k+1} (band bottom)
        # geometric (log-uniform) interpolation across the band using r18 as the
        # integer step index -- this is the "18-fold sweep" providing intra-octave
        # resolution, i.e. t = r18 * pi/9 is used only to *index* the step, the
        # actual value is a pure geometric mean between the two documented anchors.
        log_hi, log_lo = math.log(hi), math.log(lo)
        for r18 in range(steps_per_band):
            frac = r18 / steps_per_band
            val = math.exp(log_hi + frac * (log_lo - log_hi))
            values.append(val)
            coords.append((k, r18))
    # append the final anchor itself (bottom of last band) so the smallest anchor
    # is representable, plus 0.0 for the true-zero case
    values.append(anchors[num_bands])
    coords.append((num_bands, 0))
    values = np.array(values, dtype=np.float64)
    order = np.argsort(values)
    return values[order], [coords[i] for i in order]


def signed_codebook(num_bands: int, steps_per_band: int = NSEC):
    pos_values, pos_coords = build_codebook(num_bands, steps_per_band)
    zero = np.array([0.0])
    full_values = np.concatenate([-pos_values[::-1], zero, pos_values])
    n_levels = full_values.shape[0]
    return full_values, n_levels
