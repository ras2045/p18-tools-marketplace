#!/usr/bin/env python3
"""Synthesize a Verilog module with Yosys and report real gate count + critical path.
Usage: hdl_synth.py <design.v> <top_module_name>
"""
import re
import shutil
import subprocess
import sys
import os


def main():
    if len(sys.argv) != 3:
        print("Usage: hdl_synth.py <design.v> <top_module_name>", file=sys.stderr)
        sys.exit(1)

    design, top = sys.argv[1], sys.argv[2]
    if not os.path.isfile(design):
        print(f"File not found: {design}", file=sys.stderr)
        sys.exit(1)

    if shutil.which("yosys") is None:
        print("yosys not found on PATH. Install with: sudo apt install yosys", file=sys.stderr)
        sys.exit(1)

    script = f"read_verilog {design}; synth -top {top}; stat; ltp"
    r = subprocess.run(["yosys", "-p", script], capture_output=True, text=True, timeout=120)
    out = r.stdout

    if r.returncode != 0 or "ERROR" in out:
        print("Synthesis failed:", file=sys.stderr)
        print(out, file=sys.stderr)
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    cells_match = re.search(r"Number of cells:\s+(\d+)", out)
    total_cells = cells_match.group(1) if cells_match else "?"

    path_match = re.search(r"Longest topological path in \S+ \(length=(\d+)\)", out)
    path_len = path_match.group(1) if path_match else "?"

    cell_lines = re.findall(r"^\s+(\$?\w+)\s+(\d+)$", out, re.MULTILINE)
    cell_breakdown = dict(cell_lines)  # yosys prints stat twice (synth + explicit stat call); dedupe

    print(f"module: {top}")
    print(f"total cells: {total_cells}")
    print(f"critical path (logic levels): {path_len}")
    if cell_breakdown:
        print("cell breakdown:")
        for name, count in cell_breakdown.items():
            print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
