#!/usr/bin/env python3
"""FastSearch from Python (ctypes) — the smallest runnable example.

Instant file search for Windows — build an index once, search it in milliseconds, from any language that can call C

Put fast_search.dll (from the FastSearch release zip in this repository's
Releases) next to this script and run:

    python fastsearch.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with fs_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/FastSearch/include/fastsearch.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "fast_search.dll"))

dll.fs_version.restype = ctypes.c_char_p        # borrowed
dll.fs_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.fs_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("FastSearch version:", dll.fs_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: fs_index_create — its exact
    # signature from fastsearch.h is quoted at the bottom of this
    # file, and the kit README in kits/FastSearch/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check fs_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from fastsearch.h:
#   FS_API uint64_t fs_index_create(void);
