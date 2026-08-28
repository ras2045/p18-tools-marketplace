#!/usr/bin/env python3
"""Dump a real VCD waveform from a Verilog testbench run, optionally opening it in GTKWave.

Works even when the testbench itself has no $dumpfile/$dumpvars: wraps it
in a small generated top module that dumps the whole instantiated
hierarchy, so the user's testbench file is never modified.

Usage: hdl_wave.py <design.v> <testbench.v> <tb_module_name> [out.vcd] [--open]
"""
import os
import shutil
import subprocess
import sys
import tempfile

WRAPPER_TEMPLATE = """\
module __hdlwave_top;
    initial begin
        $dumpfile("{vcd_path}");
        $dumpvars(0, __hdlwave_top);
    end
    {tb_module} __hdlwave_tb ();
endmodule
"""


def main():
    args = sys.argv[1:]
    do_open = "--open" in args
    args = [a for a in args if a != "--open"]

    if len(args) < 3:
        print("Usage: hdl_wave.py <design.v> <testbench.v> <tb_module_name> [out.vcd] [--open]",
              file=sys.stderr)
        sys.exit(1)

    design, testbench, tb_module = args[0], args[1], args[2]
    out_vcd = args[3] if len(args) > 3 else "wave.vcd"

    for f in (design, testbench):
        if not os.path.isfile(f):
            print(f"File not found: {f}", file=sys.stderr)
            sys.exit(1)

    if shutil.which("iverilog") is None or shutil.which("vvp") is None:
        print("iverilog/vvp not found on PATH. Install with: sudo apt install iverilog",
              file=sys.stderr)
        sys.exit(1)

    out_vcd_abs = os.path.abspath(out_vcd)

    with tempfile.TemporaryDirectory() as tmp:
        wrapper_path = os.path.join(tmp, "__hdlwave_wrapper.v")
        with open(wrapper_path, "w") as f:
            f.write(WRAPPER_TEMPLATE.format(vcd_path=out_vcd_abs, tb_module=tb_module))

        sim_out = os.path.join(tmp, "sim.out")
        compile_cmd = ["iverilog", "-o", sim_out, design, testbench, wrapper_path]
        r = subprocess.run(compile_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("Compilation failed:", file=sys.stderr)
            print(r.stderr, file=sys.stderr)
            sys.exit(1)

        r = subprocess.run(["vvp", sim_out], capture_output=True, text=True, timeout=60)
        print(r.stdout.strip())
        if r.stderr.strip():
            print(r.stderr.strip(), file=sys.stderr)

    if not os.path.isfile(out_vcd_abs):
        print(f"No VCD file produced at {out_vcd_abs} — simulation may have errored above.",
              file=sys.stderr)
        sys.exit(1)

    size = os.path.getsize(out_vcd_abs)
    print(f"\nVCD written: {out_vcd_abs} ({size} bytes)")

    if do_open:
        if shutil.which("gtkwave") is None:
            print("gtkwave not found on PATH. Install with: sudo apt install gtkwave",
                  file=sys.stderr)
            sys.exit(1)
        subprocess.Popen(["gtkwave", out_vcd_abs],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Opened in GTKWave.")


if __name__ == "__main__":
    main()
