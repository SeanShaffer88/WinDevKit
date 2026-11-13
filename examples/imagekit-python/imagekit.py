#!/usr/bin/env python3
"""ImageKit from Python (ctypes) — the smallest runnable example.

Image decode, transform, and encode behind one clean C ABI — PNG/BMP in pure Rust

Put imagekit.dll (from the ImageKit release zip in this repository's
Releases) next to this script and run:

    python imagekit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with ik_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/ImageKit/include/imagekit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "imagekit.dll"))

dll.ik_version.restype = ctypes.c_char_p        # borrowed
dll.ik_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.ik_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("ImageKit version:", dll.ik_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: ik_free_buffer — its exact
    # signature from imagekit.h is quoted at the bottom of this
    # file, and the kit README in kits/ImageKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check ik_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from imagekit.h:
#   IK_API void ik_free_buffer(uint8_t *p, size_t len);
