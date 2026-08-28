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
  finding from this project's own research, reconfirmed at multiple scales:
  only 10 of 18 residues ever occur (the other 8 are structurally
  impossible, a consequence of primes >2,3 being coprime to 18). Report
  this as exactly what it is — a real, computed-now, verifiable number
  fact — not as a hypothesis or as evidence for anything beyond itself. It
  does not predict where primes occur.

Report the tool's real output verbatim. Do not round `factor`'s
verification claim if it says `False` — that would mean a real bug, not a
minor discrepancy.
