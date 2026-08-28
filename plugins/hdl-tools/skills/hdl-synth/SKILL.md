---
name: hdl-synth
description: Synthesize a Verilog module with Yosys (generic standard-cell library) and report the real gate count, cell-type breakdown, critical-path length in logic levels, and (with --timing) an approximate real-ns delay estimate using real sky130 cell data. Use when the user wants real synthesis numbers for a design, not a simulation pass/fail.
argument-hint: "<design.v> <top_module_name> [--timing]"
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
critical-path length (in logic levels) exactly as printed.

Add `--timing` to get a real-ns delay estimate: the script bundles real
average per-cell delays measured from the actual SkyWater
`sky130_fd_sc_hd` Liberty timing tables (tt_025C_1v80 corner), maps
Yosys's generic cell types to the nearest sky130 cell, picks the most
common logic-cell type in the design as the critical path's assumed
dominant type, and multiplies by the path length. **This is a real,
disclosed approximation, not a per-node static timing analysis** — the
script prints its own caveat explaining exactly this; always pass that
caveat through to the user rather than presenting the ns/MHz number as
precise. A genuine per-node STA would need the full sky130 Liberty file
run through OpenSTA or `abc -liberty`, which this tool does not do.

If synthesis fails (bad top-module name, syntax error), the real Yosys
error is printed — pass it through rather than guessing at the fix.
