#!/usr/bin/env python3
"""EmbedKit from Python (ctypes) — the smallest runnable example.

Local semantic search behind one clean C ABI: a pure-Rust embedding index plus BERT-class sentence embeddings via a runtime-loaded ONNX Runtime

Put embedkit.dll (from the EmbedKit release zip in this repository's
Releases) next to this script and run:

    python embedkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with ek_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/EmbedKit/include/embedkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "embedkit.dll"))

dll.ek_version.restype = ctypes.c_char_p        # borrowed
dll.ek_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.ek_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("EmbedKit version:", dll.ek_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: see the header — its exact
    # signature from embedkit.h is quoted at the bottom of this
    # file, and the kit README in kits/EmbedKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check ek_last_error on failure.


if __name__ == "__main__":
    main()
