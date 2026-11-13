//! win-common — the shared foundation crate for the WinDevKit kits.
//!
//! The kits started as standalone projects, and each carried
//! private copies of the same hand-rolled modules. The copies
//! drifted (21 distinct variants of the JSON engine alone), so a
//! fix landed in one kit and silently never reached the others.
//! This crate is the consolidation: the union of what the copies
//! grew, kept byte-compatible with each kit's existing behavior
//! (PAIN_POINTS #53).
//!
//! Rules of the house, unchanged: zero external dependencies,
//! and no kit depends on another kit — kits may depend on this
//! foundation crate only. It ships no DLL and has no C ABI; each
//! kit's own ABI is exactly what it was before the move.

pub mod ffi;
pub mod json;
pub mod sha256;
