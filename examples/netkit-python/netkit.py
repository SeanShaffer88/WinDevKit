#!/usr/bin/env python3
"""NetKit from Python (ctypes) — the smallest runnable example.

Hardened HTTP(S) client behind one C call

Put net_kit.dll (from the NetKit release zip in this repository's
Releases) next to this script and run:

    python netkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with nk_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/NetKit/include/netkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "net_kit.dll"))

dll.nk_version.restype = ctypes.c_char_p        # borrowed
dll.nk_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.nk_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("NetKit version:", dll.nk_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from netkit.h is quoted at the bottom of this
    # file, and the kit README in kits/NetKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check nk_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from netkit.h:
#   NK_API __declspec(dllexport) #elif defined(_WIN32) #define NK_API __declspec(dllimport) #else #define NK_API #endif enum { NK_OK = 0, NK_ERR_INVALID_ARG = 1, NK_ERR_NOT_SUPPORTED = 2, NK_ERR_NOT_FOUND = 3, NK_ERR_ACCESS_DENIED = 4, NK_ERR_PLATFORM = 5, NK_ERR_INTERNAL = 6, NK_ERR_PARSE = 7, NK_ERR_DIGEST = 8, NK_ERR_REDIRECT_DOWNGRADE = 9, NK_ERR_TOO_MANY_REDIRECTS = 10, NK_ERR_TOO_LARGE = 11, NK_ERR_BUFFER_TOO_SMALL = 12, NK_ERR_TIMEOUT = 13, NK_ERR_URL = 14 };
