#!/usr/bin/env python3
"""TimeKit from Python (ctypes) — the smallest runnable example.

Timezones and civil time done once, correctly: IANA zones, DST transitions, gap/overlap-safe conversions behind a small C ABI

Put timekit.dll (from the TimeKit release zip in this repository's
Releases) next to this script and run:

    python timekit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with tk_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/TimeKit/include/timekit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "timekit.dll"))

dll.tk_version.restype = ctypes.c_char_p        # borrowed
dll.tk_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.tk_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("TimeKit version:", dll.tk_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from timekit.h is quoted at the bottom of this
    # file, and the kit README in kits/TimeKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check tk_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from timekit.h:
#   TK_API __declspec(dllexport) #elif defined(_WIN32) #define TK_API __declspec(dllimport) #else #define TK_API #endif enum { TK_OK = 0, TK_ERR_INVALID_ARG = 1, TK_ERR_UNKNOWN_ZONE = 2, TK_ERR_GAP = 3, TK_ERR_AMBIGUOUS = 4, TK_ERR_INTERNAL = 6 };
