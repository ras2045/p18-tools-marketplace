# HDL Sim & Synth Tools — Claude Code Plugin

Two real commands wrapping open-source EDA tools: simulate a Verilog
design against a testbench, or synthesize it and get real gate counts and
critical-path length. No competing plugin for Verilog/Yosys synthesis
workflows existed in the community marketplace at the time this was built
(checked against all 2,282 listed plugins — zero matches for "verilog",
"vhdl", "yosys", "gate-level", or "hardware description").

## What's real here

- **`/hdl-tools:hdl-sim`** — compiles and runs a real testbench with
  Icarus Verilog (`iverilog` + `vvp`), reports the simulation's real
  output verbatim.
- **`/hdl-tools:hdl-synth`** — synthesizes a module with Yosys
  (`synth -top <module>; stat; ltp`), reports the real total cell count,
  real cell-type breakdown, and real critical-path length in logic levels.

Both commands were verified live against a real design (`classify.v`, an
8-bit byte classifier) before packaging: 256/256 simulation pass, and a
real 507-cell / 9-level synthesis result matching prior documented results
exactly.

## Requirements

- Python 3 on PATH (standard library only)
- `iverilog` and `vvp` for `hdl-sim` (`sudo apt install iverilog`)
- `yosys` for `hdl-synth` (`sudo apt install yosys`)

## Install

Test without installing:
```
claude --plugin-dir /path/to/hdl-tools-plugin
```

Install for yourself, in every project:
```
claude plugin install /path/to/hdl-tools-plugin --scope user
```

Or via a marketplace:
```
/plugin marketplace add ras2045/p18-tools-marketplace
/plugin install hdl-tools@p18-marketplace
```

## Honest limits

`hdl-synth` reports gate count and critical-path *length* (logic levels),
not real propagation delay in seconds — Yosys's generic synthesis targets
an abstract standard-cell library, not a real fabricated process. Getting
a real timing number requires real per-cell delay data for a specific PDK
(e.g. SkyWater sky130) multiplied against the critical path, which this
tool doesn't do automatically — don't treat "critical path: 9" as
nanoseconds.

## Structure

```
hdl-tools-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── hdl-sim/SKILL.md
│   └── hdl-synth/SKILL.md
└── scripts/
    ├── hdl_sim.py
    └── hdl_synth.py
```

Both skills are `disable-model-invocation: true` — user-triggered slash
commands only.
