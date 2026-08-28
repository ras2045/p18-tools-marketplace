#!/usr/bin/env python3
"""Real disassembly + symbol table summary via objdump.

Usage: disasm.py <file> [function_name]
  No function_name: lists real defined symbols (objdump -t), sorted by size.
  With function_name: disassembles just that function (objdump -d --disassemble=NAME).
"""
import shutil
import subprocess
import sys
import os


def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return 1, "", str(e)


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: disasm.py <file> [function_name]", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    func = sys.argv[2] if len(sys.argv) == 3 else None

    if not os.path.isfile(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    if shutil.which("objdump") is None:
        print("objdump not found on PATH (part of binutils).", file=sys.stderr)
        sys.exit(1)

    if func is None:
        rc, out, err = run(["objdump", "-t", path])
        if rc != 0:
            print(f"objdump failed: {err.strip()}", file=sys.stderr)
            sys.exit(1)
        rows = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 6 and parts[2] == "F":  # function symbol
                try:
                    size = int(parts[4], 16)
                except ValueError:
                    continue
                name = parts[-1]
                rows.append((size, name))
        rows.sort(reverse=True)
        print(f"real defined function symbols in {path}: {len(rows)} found")
        if not rows:
            print("(none — likely stripped; try objdump -d directly for raw disassembly)")
        for size, name in rows[:25]:
            print(f"  {size:6d} bytes  {name}")
        if len(rows) > 25:
            print(f"  ... and {len(rows) - 25} more (re-run with a function name to disassemble it)")
    else:
        rc, out, err = run(["objdump", "-d", f"--disassemble={func}", "-M", "intel", path])
        if rc != 0:
            print(f"objdump failed: {err.strip()}", file=sys.stderr)
            sys.exit(1)
        if not out.strip() or f"<{func}>:" not in out:
            print(f"Function '{func}' not found in disassembly output "
                  f"(check the exact symbol name with `disasm.py {path}` first).", file=sys.stderr)
            sys.exit(1)
        print(out)


if __name__ == "__main__":
    main()
