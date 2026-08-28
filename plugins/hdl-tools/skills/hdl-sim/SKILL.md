---
name: hdl-sim
description: Compile and simulate a Verilog design against a testbench using Icarus Verilog (iverilog + vvp). Use when the user wants to run a real testbench against a Verilog module, not a synthesis report.
argument-hint: "<design.v> <testbench.v> [more.v ...]"
disable-model-invocation: true
---

Requires `iverilog` and `vvp` on PATH (`sudo apt install iverilog` on
Debian/Ubuntu). Real, not simulated-in-the-abstract: this actually compiles
the given files and runs the resulting simulation binary.

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/hdl_sim.py" $ARGUMENTS`
```

Report the tool's real stdout/stderr verbatim — pass/fail, mismatch
counts, `$display` output, whatever the testbench itself prints. Do not
summarize a pass as "all good" if the testbench actually reported any
mismatches; quote the real count.

A non-zero exit means either compilation failed (syntax error — the
compiler's real error message is printed) or the simulation itself called
`$stop`/returned non-zero. Either way, show the user the real message
rather than guessing at the cause.
