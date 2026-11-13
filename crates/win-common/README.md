# win-common

The shared foundation crate for the WinDevKit kits: the family
JSON engine, SHA-256, and FFI wide-string helpers — maintained
once, here, instead of as a private copy inside every kit.

## Why this exists

The kits began as standalone projects, and each carried its own
copy of the same hand-rolled modules. The copies drifted: by
2026-11-13 the JSON engine existed as **21 distinct variants**
across the collection, so a fix landed in one kit and silently
never reached the others (PAIN_POINTS #53). This crate is the
consolidation — the *union* of what the copies grew, so every
migrated kit keeps exactly the behavior it had:

- **`json`** — insertion-ordered `Value`, a strict parser
  (duplicate keys in one object are a parse error by design),
  mutation helpers, the settings serializers (`to_string_pretty`
  / `to_string_compact`, which force `.0` on integral floats so
  they re-parse as floats), the result-JSON writer (`to_json`)
  with the `obj` / `s` / `n` / `b` builders, and `json_escape`.
- **`sha256`** — FIPS 180-4 SHA-256, streaming
  (`new` / `update` / `finalize` / `finalize_hex`) plus the
  one-shot `sha256_hex` / `hex` helpers, pinned by the standard
  test vectors.
- **`ffi`** — `to_wide` / `from_wide`, the NUL-terminated UTF-16
  helper pair the kits' platform layers each re-implemented.

## The rules

- **Zero external dependencies.** This crate is first-party,
  in-repo code; depending on it is not a dependency in the sense
  the house rule restricts. Adding an external dependency here
  would need the same written justification as in any kit.
- **Kits never depend on each other.** They may depend on this
  foundation crate. It is not a kit: it ships no DLL and has no
  C ABI of its own, and it is not in the kit catalog.
- **Behavior is contractual.** A kit's parse errors, float
  formatting and digest outputs must not change because the code
  moved. If a change here would alter any consumer's observable
  behavior, it is a breaking change for every consumer at once —
  treat it with that care, and run the consumers' gates.

## Who consumes it

21 kits take `json` from here and 5 take `sha256` (FixtureKit,
NetKit, SignKit, ThumbKit, UpdateKit), each as
`win-common = { path = "../../crates/win-common" }` with a
`pub use win_common::json;` (or `::sha256`) in their `lib.rs`, so
their internal `crate::json::…` paths never changed.

Two kits deliberately keep their own engines, because their
designs genuinely differ rather than merely drifted:

- **UpdateKit** — its JSON value model is `Num(f64)` with
  `BTreeMap` objects (sorted keys, no duplicate-key concept).
- **FileMetaKit** — a reduced parser shaped for metadata
  scalars.

DiagKit's `hash.rs` (SHA-256 + CRC-32 in one module) also stays
in-kit. The kits' private `wide()` helpers retire kit-by-kit as
their platform layers are next touched; new platform code should
use `win_common::ffi` from the start.

## Gate

`tools/gate.sh` from this folder (fmt + clippy on both targets +
the full test suite), like every kit.
