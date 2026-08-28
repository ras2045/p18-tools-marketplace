---
name: hdl-synth
description: Synthesize a Verilog module with Yosys (generic standard-cell library) and report the real gate count, cell-type breakdown, and critical-path length in logic levels. Use when the user wants real synthesis numbers for a design, not a simulation pass/fail.
argument-hint: "<design.v> <top_module_name>"
disable-model-invocation: true
---

Requires `yosys` on PATH (`sudo apt install yosys` on Debian/Ubuntu). Runs
real logic synthesis (`synth -top <module>`) followed by Yosys's real
`stat` and `ltp` (longest topological path) passes — not an estimate.

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/hdl_synth.py" $ARGUMENTS`
```

Report the real total cell count, real cell-type breakdown, and real
critical-path length (in logic levels, not nanoseconds — Yosys's generic
synth doesn't know real gate delays) exactly as printed. If the user wants
a real timing estimate in seconds, you'd need real cell-delay data for a
specific PDK (e.g. SkyWater sky130) multiplied by the critical-path
length — don't invent delay numbers for cells that weren't actually
characterized.

If synthesis fails (bad top-module name, syntax error), the real Yosys
error is printed — pass it through rather than guessing at the fix.
