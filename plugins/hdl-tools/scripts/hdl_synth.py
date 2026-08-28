#!/usr/bin/env python3
"""Synthesize a Verilog module with Yosys and report real gate count + critical path.
Usage: hdl_synth.py <design.v> <top_module_name> [--timing]
"""
import json
import re
import shutil
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DELAYS_FILE = os.path.join(SCRIPT_DIR, "sky130_avg_delays.json")

# Yosys generic-cell prefix -> nearest real sky130_fd_sc_hd cell, for the
# --timing estimate. Approximate mappings (no exact sky130 equivalent):
# $_ANDNOT_ (AND-NOT) approximated as nand2, $_ORNOT_ (OR-NOT) as nor2.
CELL_MAP = {
    "$_NOT_": "inv",
    "$_NOR_": "nor2",
    "$_ORNOT_": "nor2",
    "$_NAND_": "nand2",
    "$_ANDNOT_": "nand2",
    "$_XOR_": "xor2",
    "$_XNOR_": "xor2",
    "$_AND_": "and2",
    "$_OR_": "or2",
    "$_MUX_": "mux2",
}


def main():
    args = sys.argv[1:]
    want_timing = "--timing" in args
    args = [a for a in args if a != "--timing"]

    if len(args) != 2:
        print("Usage: hdl_synth.py <design.v> <top_module_name> [--timing]", file=sys.stderr)
        sys.exit(1)

    design, top = args
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

    if want_timing:
        print_timing_estimate(cell_breakdown, path_len)


def print_timing_estimate(cell_breakdown, path_len):
    print()
    if path_len == "?":
        print("timing estimate: unavailable (no critical-path length found)")
        return

    try:
        delays = json.load(open(DELAYS_FILE))
    except FileNotFoundError:
        print(f"timing estimate: unavailable ({DELAYS_FILE} not found)")
        return

    mapped = [(CELL_MAP[name], int(count)) for name, count in cell_breakdown.items()
              if name in CELL_MAP]
    if not mapped:
        print("timing estimate: unavailable (no logic cells matched the sky130 cell map — "
              "flip-flops/wires only?)")
        return

    dominant_type, dominant_count = max(mapped, key=lambda t: t[1])
    delay_ps = delays[dominant_type]
    path_len_i = int(path_len)
    total_ps = delay_ps * path_len_i
    freq_mhz = 1e6 / total_ps if total_ps > 0 else 0.0

    print("timing estimate (approximation, not real STA):")
    print(f"  dominant logic-cell type on critical path (by total count in design): "
          f"{dominant_type} ({dominant_count} instances)")
    print(f"  real sky130_fd_sc_hd average delay for {dominant_type}: {delay_ps} ps "
          f"(google/skywater-pdk-libs-sky130_fd_sc_hd, tt_025C_1v80)")
    print(f"  estimate = critical path length ({path_len_i}) x {delay_ps} ps "
          f"= {total_ps:.1f} ps ({total_ps / 1000:.2f} ns)")
    print(f"  implied max frequency if run unpipelined: ~{freq_mhz:.1f} MHz")
    print("  caveat: this assumes every level on the critical path is the same "
          "dominant cell type — it is NOT a real per-node static timing analysis. "
          "A real STA report would need the full sky130 Liberty file run through "
          "OpenSTA or a proper `abc -liberty` synthesis flow.")


if __name__ == "__main__":
    main()
