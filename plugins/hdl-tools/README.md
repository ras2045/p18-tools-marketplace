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
  With `--timing`, also prints an approximate real-ns delay estimate using
  real average per-cell delays measured from the actual SkyWater
  `sky130_fd_sc_hd` Liberty timing tables — clearly labeled as an
  approximation (dominant-cell-type × path-length), not a real per-node
  static timing analysis.

- **`/hdl-tools:hdl-wave`** — runs a testbench and produces a real VCD
  waveform dump, optionally opening it in GTKWave. Works even on
  testbenches with no `$dumpfile`/`$dumpvars` — wraps the testbench in a
  generated top module rather than editing the user's file.

All three commands were verified live against a real design (`classify.v`,
an 8-bit byte classifier) before packaging: 256/256 simulation pass, a
real 507-cell / 9-level synthesis result matching prior documented results
exactly, a `--timing` estimate of 4.33 ns / ~231 MHz built from a mux2
delay (481.1 ps) independently recomputed from the raw Liberty LUT data,
and a real 19,860-byte VCD with a real GTKWave process launched against it
(confirmed via `pgrep`, then closed).

## Requirements

- Python 3 on PATH (standard library only)
- `iverilog` and `vvp` for `hdl-sim` and `hdl-wave` (`sudo apt install iverilog`)
- `yosys` for `hdl-synth` (`sudo apt install yosys`)
- `gtkwave` for `hdl-wave --open` (`sudo apt install gtkwave`), plus a
  working X display

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

`hdl-synth --timing` is a real but approximate estimate, not a static
timing analysis: it assumes every level on the critical path is the same
cell type (the design's most common logic cell), using one real average
delay figure per cell type rather than tracing actual per-node delays
along the path. A genuine per-node STA would need the full sky130 Liberty
file run through OpenSTA or `abc -liberty`, which this tool does not do.
Without `--timing`, `hdl-synth` reports only gate count and critical-path
*length* (logic levels) — don't treat that number as nanoseconds.

## Structure

```
hdl-tools-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── hdl-sim/SKILL.md
│   ├── hdl-synth/SKILL.md
│   └── hdl-wave/SKILL.md
└── scripts/
    ├── hdl_sim.py
    ├── hdl_synth.py
    ├── hdl_wave.py
    └── sky130_avg_delays.json   # real sky130_fd_sc_hd average cell delays
```

Both skills are `disable-model-invocation: true` — user-triggered slash
commands only.
