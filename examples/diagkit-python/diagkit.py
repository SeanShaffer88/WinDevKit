#!/usr/bin/env python3
"""DiagKit from Python (ctypes) — the smallest runnable example.

One-call diagnostics bundles (logs, dumps, versions, hashes) as a single zip with a JSON manifest

Put diag_kit.dll (from the DiagKit release zip in this repository's
Releases) next to this script and run:

    python diagkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with di_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/DiagKit/include/diagkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "diag_kit.dll"))

dll.di_version.restype = ctypes.c_char_p        # borrowed
dll.di_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.di_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("DiagKit version:", dll.di_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from diagkit.h is quoted at the bottom of this
    # file, and the kit README in kits/DiagKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check di_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from diagkit.h:
#   DI_API __declspec(dllexport) #elif defined(_WIN32) #define DI_API __declspec(dllimport) #else #define DI_API #endif enum { DI_OK = 0, DI_ERR_INVALID_ARG = 1, DI_ERR_NOT_SUPPORTED = 2, DI_ERR_NOT_FOUND = 3, DI_ERR_ACCESS_DENIED = 4, DI_ERR_PLATFORM = 5, DI_ERR_INTERNAL = 6, DI_ERR_PARSE = 7, DI_ERR_TOO_LARGE = 8 };
