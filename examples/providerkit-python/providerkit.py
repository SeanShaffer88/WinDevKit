#!/usr/bin/env python3
"""ProviderKit from Python (ctypes) — the smallest runnable example.

File provider adapter SDK behind a small C ABI: browse local disks, archives and custom providers through one interface

Put provider_kit.dll (from the ProviderKit release zip in this repository's
Releases) next to this script and run:

    python providerkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with pv_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/ProviderKit/include/providerkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "provider_kit.dll"))

dll.pv_version.restype = ctypes.c_char_p        # borrowed
dll.pv_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.pv_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("ProviderKit version:", dll.pv_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from providerkit.h is quoted at the bottom of this
    # file, and the kit README in kits/ProviderKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check pv_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from providerkit.h:
#   PV_API __declspec(dllexport) #elif defined(_WIN32) #define PV_API __declspec(dllimport) #else #define PV_API #endif enum { PV_OK = 0, PV_ERR_INVALID_ARG = 1, PV_ERR_NOT_SUPPORTED = 2, PV_ERR_NOT_FOUND = 3, PV_ERR_ACCESS_DENIED = 4, PV_ERR_PLATFORM = 5, PV_ERR_INTERNAL = 6, PV_ERR_PARSE = 7, PV_ERR_UNKNOWN_PROVIDER = 8, PV_ERR_DUPLICATE = 9, PV_ERR_TOO_LARGE = 10, PV_ERR_INTEGRITY = 11 };
