# Credits

WinDevKit and its kits are written for this repository and MIT
licensed (see the root `LICENSE` and each kit's own `LICENSE`).
A few kits build on third-party components:

## Vendored engine sources (OCRKit)

`kits/OCRKit` vendors the sources of its OCR engine stack —
zlib, libpng, Leptonica and Tesseract. The pinned sources are
downloaded and SHA-256-verified at build time by the kit's fetch
scripts (`fetch.ps1` / `fetch.sh`, pins in `pins.txt`) and built
into the DLL by its `build.rs`. Each component remains under its
own license; the license texts ship inside the vendored source
trees.

## Runtime-loaded engine (EmbedKit)

`kits/EmbedKit` loads an ONNX Runtime library that the user
supplies at runtime (ONNX Runtime is MIT licensed). Its
end-to-end test uses the all-MiniLM-L6-v2 model and vocabulary,
fetched pinned and hash-verified like the OCRKit sources.

## Forks and provenance

Repositories in this project family that continue or adapt
upstream work are tracked, with upstream credit, in
[`FORK_PROVENANCE.md`](FORK_PROVENANCE.md).
