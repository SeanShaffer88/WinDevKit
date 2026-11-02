#!/usr/bin/env bash
# WinDevKit collection gate — runs tools/gate.sh inside kits under
# kits/, so the whole merged collection can be gated locally with
# one command. Mirrors .github/workflows/kits-ci.yml (the CI twin
# adds the release build plus the per-kit e2e/interop steps, which
# need a real Windows link/run — see gate.sh's header for why local
# checks reduce, not eliminate, CI surprises).
#
# Kits whose engines are fetched (EmbedKit, OCRKit) run their POSIX
# fetch first (sh ./fetch.sh, SHA-256-verified against pins.txt),
# matching CI's fetch.ps1 step.
#
# Usage: gate-kits.sh [--quick] [KIT ...]
#   --quick   passed through to gate.sh (host checks only)
#   KIT ...   only gate the named kits (default: all under kits/)
# Exit code is non-zero if any kit fails; every kit still runs, and
# the failures are listed at the end — a red kit is never hidden.
# Pain point: docs/PAIN_POINTS.md #49.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUICK=""
KITS=()
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK="--quick" ;;
    -*) echo "Usage: gate-kits.sh [--quick] [KIT ...]" >&2; exit 2 ;;
    *) KITS+=("$arg") ;;
  esac
done
if [ "${#KITS[@]}" -eq 0 ]; then
  for d in "$ROOT"/kits/*/; do
    [ -f "$d/Cargo.toml" ] && KITS+=("$(basename "$d")")
  done
fi
FAILED=()
for kit in "${KITS[@]}"; do
  dir="$ROOT/kits/$kit"
  if [ ! -f "$dir/Cargo.toml" ]; then
    echo "== $kit: NOT FOUND under kits/ ==" >&2
    FAILED+=("$kit (not found)")
    continue
  fi
  printf '\n######## %s ########\n' "$kit"
  if [ -f "$dir/fetch.sh" ]; then
    echo "== $kit: sh ./fetch.sh =="
    (cd "$dir" && sh ./fetch.sh) || { FAILED+=("$kit (fetch)"); continue; }
  fi
  (cd "$dir" && bash "$ROOT/tools/gate.sh" $QUICK) || FAILED+=("$kit")
done
printf '\n========================================\n'
if [ "${#FAILED[@]}" -eq 0 ]; then
  echo "COLLECTION GATE GREEN: all ${#KITS[@]} kit(s) passed"
else
  echo "COLLECTION GATE FAILED: ${#FAILED[@]} of ${#KITS[@]} kit(s):" >&2
  printf '  - %s\n' "${FAILED[@]}" >&2
  exit 1
fi
