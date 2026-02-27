# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Binaryen is a C++17 compiler and toolchain infrastructure library for WebAssembly. It provides `wasm-opt` (optimizer), assembler/disassembler, interpreter, and C/JS APIs. Used by Emscripten, wasm-pack, Dart/Flutter, and Kotlin/Wasm.

## Build

```bash
git submodule init && git submodule update
cmake -S . -B out -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build out
```

Binaries go to `out/bin/`. Key CMake options: `BUILD_TESTS=ON` (default), `BUILD_TOOLS=ON` (default), `ENABLE_WERROR=ON` (default), `BYN_ENABLE_ASSERTIONS=ON` (default, even in Release).

## Testing

Requires Python 3.10+ and dev deps: `pip3 install -r requirements-dev.txt`

```bash
# Full test suite
python check.py --binaryen-bin=out/bin

# Individual suites
python check.py --binaryen-bin=out/bin lit
python check.py --binaryen-bin=out/bin gtest
python check.py --binaryen-bin=out/bin spec
python check.py --binaryen-bin=out/bin wasm-opt

# Single lit test
python out/bin/binaryen-lit -vv test/lit/passes/some-pass.wast

# Single gtest
./out/bin/binaryen-unittests --gtest_filter='*TypeBuilder*'

# Update lit test CHECK lines
python scripts/update_lit_checks.py test/lit/passes/some-pass.wast

# List all suites
python check.py --list-suites
```

## Linting

```bash
# C++ format check (requires clang-format-21)
./scripts/clang-format-diff.sh

# Apply format
git clang-format --binary=clang-format-21 origin/main

# Python lint
flake8 && ruff check

# S-parser codegen verification (regenerate if you change S-expression syntax)
./scripts/gen-s-parser.py > src/gen-s-parser.inc
```

Code style: LLVM-based (`.clang-format`), 2-space continuation indent, left pointer alignment, no bin-packing of args/params.

## Architecture

### Core IR (`src/`)

- `wasm.h` — All expression node types (Block, If, Loop, Call, Binary, etc.) and module structure
- `wasm-traversal.h` — Visitor/Walker base classes used by all passes
- `wasm-builder.h` — Helper to construct IR nodes
- `wasm-type.h` — Type system including GC types
- `wasm-binary.h/.cpp` — Binary format encode/decode
- `wasm-stack.h/.cpp` — Stack IR for binary emission
- `wasm-interpreter.h` — Interpreter (constant folding, spec tests)
- `wasm-validator.h/.cpp` — Validation
- `pass.h` — `Pass` base class, `PassRunner`, `PassRegistry`
- `ir/effects.h` — Side-effect analysis
- `parser/` — Text format (.wat/.wast) parser
- `binaryen-c.h/.cpp` — Public C API

### Passes (`src/passes/`)

~80+ optimization and transform passes, each a `.cpp` file. Registered in `src/passes/pass.cpp` via `PassRegistry`, automatically available in `wasm-opt`.

### Tools (`src/tools/`)

Entry points for CLI tools: `wasm-opt.cpp`, `wasm-as.cpp`, `wasm-dis.cpp`, `wasm2js.cpp`, `wasm-shell.cpp`, etc.

### Tests

- `test/lit/` — LLVM lit tests (FileCheck directives, `.wast`/`.wat`/`.test`). Most pass tests are in `test/lit/passes/`.
- `test/gtest/` — C++ unit tests (built as `binaryen-unittests`)
- `test/spec/` — WebAssembly spec tests (run via `wasm-shell`)

## Adding a New Pass

1. Create `src/passes/MyPass.cpp` implementing `Pass` (typically `WalkerPass<PostWalker<MyPass>>`)
2. Register in `src/passes/pass.cpp`
3. Add tests in `test/lit/passes/my-pass.wast`

## Adding a New Instruction

Checklist from Contributing.md — all these files need updates:
- `src/wasm.h` (class/opcode), `src/wasm-builder.h`, `src/wasm-traversal.h`
- `src/wasm/wasm-validator.cpp`, `src/wasm-interpreter.h`, `src/ir/effects.h`
- `src/passes/Precompute.cpp`, `src/passes/Print.cpp`
- `scripts/gen-s-parser.py`, `src/parser/parsers.h`, `src/parser/contexts.h`, `src/wasm-ir-builder.h`, `src/wasm/wasm-ir-builder.cpp`
- `src/wasm-binary.h`, `src/wasm/wasm-binary.cpp`, `src/wasm-stack.h`, `src/wasm/wasm-stack.cpp`
- All `OverriddenVisitor` subclasses
- `src/tools/fuzzing.h`
- C API (`src/binaryen-c.h/.cpp`), JS API (`src/js/binaryen.js-post.js`)
- Tests: `test/example/c-api-kitchen-sink.c`, `test/binaryen.js/kitchen-sink.js`, `test/spec/`, `test/lit/`
