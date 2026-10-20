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
[ "${1:-}" = "--quick" ] && QUICK=1

step() { printf '\n== %s ==\n' "$1"; }

step "cargo fmt --all -- --check"
cargo fmt --all -- --check

step "cargo clippy --all-targets (host)"
cargo clippy --all-targets -- -D warnings

if [ "$QUICK" -eq 0 ]; then
  if rustup target list --installed | grep -q '^x86_64-pc-windows-msvc'; then
    step "cargo clippy --target x86_64-pc-windows-msvc --all-targets"
    cargo clippy --target x86_64-pc-windows-msvc --all-targets -- -D warnings
    step "cargo check --target x86_64-pc-windows-msvc --all-targets"
    cargo check --target x86_64-pc-windows-msvc --all-targets
  else
    echo "SKIP: x86_64-pc-windows-msvc target not installed (rustup target add x86_64-pc-windows-msvc)"
  fi
fi

step "cargo test (full suite)"
cargo test

printf '\nGATE GREEN\n'
