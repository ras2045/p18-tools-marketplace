# Prime & Number Theory Utils — Claude Code Plugin

Real number-theory tools: deterministic primality testing, factorization,
sieving, and the one number-theory finding from the P18 research project
that held up under repeated, independent testing. No competing
"prime"/"number theory"/"sieve" plugin existed in the community
marketplace at build time (checked against all 2,282 listed plugins).

## What's real here

- **`is-prime <n>`** — deterministic Miller-Rabin (not probabilistic),
  exact for all n < 3.3 × 10²⁴.
- **`factor <n>`** — trial division + Pollard's rho, with a real
  multiply-back verification printed alongside the result.
- **`sieve <n>`** — real sieve of Eratosthenes (capped at 50M to avoid
  excessive memory use).
- **`gap-residues <n>`** — computes real gaps between consecutive primes
  up to n and reports which of the 18 possible `gap mod 18` residues
  actually occur. Real, reproducible result: only 10 of 18 ever occur
  (`[0,1,2,4,6,8,10,12,14,16]`) — a structural consequence of primes >2,3
  being coprime to 18, reconfirmed at multiple scales in this project's
  research. Presented as exactly that: a real, computed-now fact, not a
  new theorem or a claim about *where* primes occur.

Verified live: `factor(3215031751)` correctly returns `151 × 751 × 28351`
(a known Fermat pseudoprime factorization, real Pollard's rho stress
test), and `gap-residues(200000)` reproduces the documented 10/18-residue
result exactly on 17,983 real computed gaps.

## Requirements

- Python 3 on PATH (standard library only, no network dependency)

## Install

```
/plugin marketplace add ras2045/p18-tools-marketplace
/plugin install prime-utils@p18-marketplace
```

## Structure

```
prime-utils-plugin/
├── .claude-plugin/plugin.json
├── skills/prime-utils/SKILL.md
└── scripts/prime_utils.py
```
