---
name: disasm
description: List a binary's real defined function symbols (sorted by size), or disassemble one specific function by name, via objdump. Use when the user wants to see what functions exist in a binary or read the actual disassembly of one function.
argument-hint: "<file> [function_name]"
disable-model-invocation: true
---

Requires `objdump` (part of `binutils`, usually preinstalled on Linux).

Run the bundled script:

```
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/disasm.py" $ARGUMENTS`
```

Without a function name: lists real defined function symbols from the
symbol table (`objdump -t`), sorted largest first. **Most release
binaries are stripped and will report 0 symbols** — this is real, honest,
and expected, not a bug; tell the user their binary is stripped rather
than implying the tool failed. Stripped binaries have no name-to-address
mapping to recover without much heavier reverse-engineering tooling
(e.g. Ghidra) this plugin doesn't attempt.

With a function name: disassembles just that function
(`objdump -d --disassemble=<name> -M intel`, Intel syntax). If the name
doesn't match a real symbol, the tool reports that plainly — check the
exact name via the no-argument form first rather than guessing spellings.

Report the real disassembly output verbatim, don't summarize instructions
away — the user asked to see the actual machine code.
