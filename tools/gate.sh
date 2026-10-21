#!/usr/bin/env bash
# WinDevKit gate — the full local quality gate for Rust Windows projects.
#
# Why each step exists (every one has caught a real failure):
#   1. fmt --check                      — CI enforces it; catch it locally.
#   2. clippy (host target)             — pure-logic lints.
#   3. clippy (x86_64-pc-windows-msvc)  — host clippy NEVER sees cfg(windows)
#      code. WinRecovery CI run #1 failed on exactly this blind spot.
#   4. cargo test (full suite, never a filtered subset — a filtered gate
#      once missed a golden-fixture failure in InstallScope PR #11).
#   5. cargo check --target windows, --all-targets — test targets live in
#      bin/lib test harnesses that a plain check skips.
# NOTE: check/clippy do NOT link. Unresolved Win32 symbols (LNK2019) are
# only caught by a real build — CI's `cargo build --release` step, or a
# windows-gnu/MSVC build on a Windows machine. This gate reduces, not
# eliminates, CI surprises.
#
# Usage: gate.sh [--quick]   (--quick skips the windows-target steps)
set -euo pipefail
QUICK=0
case "${1:-}" in
  --quick) QUICK=1 ;;
  "") ;;
  *) echo "Usage: gate.sh [--quick]" >&2; exit 2 ;;
esac
if [ "$#" -gt 1 ]; then echo "Usage: gate.sh [--quick]" >&2; exit 2; fi
if [ "$QUICK" -eq 0 ]; then
  installed=$(rustup target list --installed)
  if ! printf '%s\n' "$installed" | grep -qx 'x86_64-pc-windows-msvc'; then
    echo "FAILED: install required target: rustup target add x86_64-pc-windows-msvc; use --quick for a partial host check" >&2
    exit 1
  fi
fi

step() { printf '\n== %s ==\n' "$1"; }

step "cargo fmt --all -- --check"
cargo fmt --all -- --check

step "cargo clippy --workspace --all-targets --locked (host)"
cargo clippy --workspace --all-targets --locked -- -D warnings

if [ "$QUICK" -eq 0 ]; then
  step "cargo clippy --workspace --target x86_64-pc-windows-msvc --all-targets --locked"
  cargo clippy --workspace --target x86_64-pc-windows-msvc --all-targets --locked -- -D warnings
  step "cargo check --workspace --target x86_64-pc-windows-msvc --all-targets --locked"
  cargo check --workspace --target x86_64-pc-windows-msvc --all-targets --locked
fi

step "cargo test --workspace --locked (full suite)"
cargo test --workspace --locked

if [ "$QUICK" -eq 1 ]; then
  printf '\nPARTIAL: host checks passed; Windows target checks not run\n'
else
  printf '\nGATE GREEN: host + Windows cross-checks passed; native Windows link/runtime still requires CI\n'
fi
