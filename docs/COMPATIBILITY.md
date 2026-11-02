# Compatibility

## Kits

- **Platform:** Windows. The primary build target is
  `x86_64-pc-windows-msvc`; each kit's `.cargo/config.toml` also
  carries the static-CRT setting for the `i686` and `aarch64`
  MSVC targets.
- **Interface:** every kit exposes a plain C ABI (JSON in and
  out), so the DLLs can be called from any language with C
  interop — C/C++, Rust, C#, Python (ctypes), PowerShell, and
  others.
- **Runtime:** kits built from this repository link the static C
  runtime, so the DLLs do not need a separate VC++ runtime
  install. Release zips published earlier from the standalone kit
  repositories predate the static-CRT configuration.
- **Dependencies:** kits are zero-dependency Rust where feasible.
  Two kits use native engines: OCRKit vendors its OCR stack
  (built from pinned sources at build time), and EmbedKit loads
  an ONNX Runtime library supplied by the user at runtime.
- **Signing:** all binaries are unsigned (there is no
  code-signing certificate), so Windows SmartScreen may warn on
  first run of a downloaded binary.

## Tools and templates

- The Python tools require Python 3.10 or newer and run on
  Windows, Linux and macOS.
- The gate scripts need a Rust toolchain; a full (non-`--quick`)
  gate run also needs the `x86_64-pc-windows-msvc` target
  installed (`rustup target add x86_64-pc-windows-msvc`).
- Templates target GitHub Actions on `windows-latest` runners.
