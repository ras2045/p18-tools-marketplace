---
name: hdl-wave
description: Run a Verilog testbench and produce a real VCD waveform dump, optionally opening it in GTKWave. Works even if the testbench has no $dumpfile/$dumpvars — wraps it in a generated top module instead of editing the user's file. Use when the user wants to see signal waveforms, not just pass/fail output.
argument-hint: "<design.v> <testbench.v> <tb_module_name> [out.vcd] [--open]"
disable-model-invocation: true
---

Requires `iverilog`/`vvp` (`sudo apt install iverilog`); `--open` also
requires `gtkwave` (`sudo apt install gtkwave`) and a working X display.

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/hdl_wave.py" $ARGUMENTS`
```

`tb_module_name` is the testbench's actual Verilog module name (e.g.
`tb_classify` for `module tb_classify; ... endmodule`), not the filename —
ask the user or read the file if it's not obvious. The tool instantiates
that module inside a small generated wrapper that dumps the whole
hierarchy (`$dumpvars(0, ...)`) rather than modifying the testbench file,
so this works on testbenches that were never written with waveform
dumping in mind.

Report the real simulation output and the real VCD file path/size exactly
as printed. Without `--open`, just report where the `.vcd` file was
written — GTKWave viewing is a GUI action the user does themselves, or
opt into explicitly with `--open`, since it opens a window outside this
conversation that you can't observe the contents of.

If no VCD file appears after a run that otherwise looks like it passed,
the real error (compile failure, wrong module name) is printed above —
don't guess, report what the tool actually said.
