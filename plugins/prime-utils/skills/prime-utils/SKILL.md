---
name: prime-utils
description: Real number-theory tools — deterministic primality test, factorization, sieve of Eratosthenes, and a mod-18 prime-gap-residue check. Use for any real primality/factoring/sieving question, or when the user asks about which prime-gap residues mod 18 actually occur.
argument-hint: "<is-prime|factor|sieve|gap-residues> <n>"
disable-model-invocation: true
---

Requires Python 3 (standard library only, no network dependency).

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/prime_utils.py" $ARGUMENTS`
```

Four real subcommands:
- `is-prime <n>` — deterministic Miller-Rabin, exact (not probabilistic)
  for all n < 3,317,044,064,679,887,385,961,981.
- `factor <n>` — trial division for small factors, Pollard's rho for
  larger ones. Prints a real verification that the factors multiply back
  to n.
- `sieve <n>` — real sieve of Eratosthenes, capped at 50,000,000 to avoid
  excessive memory use; reports count and a preview, not the full list for
  large n.
- `gap-residues <n>` — computes real prime gaps up to n and reports which
  of the 18 possible `gap mod 18` residues actually occur. This is a real
  finding, reconfirmed at multiple scales up to a real 300,000,000-scale
  check (16,252,325 primes, run outside this tool's own 20,000,000 cap):
  only 10 of 18 residues ever occur. The exact mechanism (also printed by
  the tool): every gap between two odd primes is even, so its residue must
  be one of the 9 even values; the sole exception is the first gap, 2->3,
  which equals 1. That's fully explained by gap parity alone — not by any
  deeper mod-3/coprimality structure, despite this project's earlier,
  slightly imprecise phrasing. Report this as exactly what it is — a real,
  computed-now, verifiable number fact — not as a hypothesis or as
  evidence for anything beyond itself. It does not predict where primes
  occur.

Report the tool's real output verbatim. Do not round `factor`'s
verification claim if it says `False` — that would mean a real bug, not a
minor discrepancy.
