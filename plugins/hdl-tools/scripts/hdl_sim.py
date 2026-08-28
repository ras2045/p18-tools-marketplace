#!/usr/bin/env python3
"""Simulate a Verilog design against a testbench with Icarus Verilog.
Usage: hdl_sim.py <design.v> <testbench.v> [more.v ...]
"""
import shutil
import subprocess
import sys
import tempfile
import os


def main():
    if len(sys.argv) < 3:
        print("Usage: hdl_sim.py <design.v> <testbench.v> [more.v ...]", file=sys.stderr)
        sys.exit(1)

    files = sys.argv[1:]
    for f in files:
        if not os.path.isfile(f):
            print(f"File not found: {f}", file=sys.stderr)
            sys.exit(1)

    if shutil.which("iverilog") is None or shutil.which("vvp") is None:
        print("iverilog/vvp not found on PATH. Install with: sudo apt install iverilog",
              file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp:
        sim_out = os.path.join(tmp, "sim.out")
        compile_cmd = ["iverilog", "-o", sim_out] + files
        r = subprocess.run(compile_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("Compilation failed:", file=sys.stderr)
            print(r.stderr, file=sys.stderr)
            sys.exit(1)

        r = subprocess.run(["vvp", sim_out], capture_output=True, text=True, timeout=60)
        print(r.stdout.strip())
        if r.stderr.strip():
            print(r.stderr.strip(), file=sys.stderr)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
