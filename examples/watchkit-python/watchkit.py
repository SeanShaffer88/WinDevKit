#!/usr/bin/env python3
"""WatchKit from Python (ctypes) — the smallest runnable example.

Folder change and cache coordinator behind a small C ABI: coalesced change events and self-invalidating folder caches

Put watch_kit.dll (from the WatchKit release zip in this repository's
Releases) next to this script and run:

    python watchkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with wa_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/WatchKit/include/watchkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "watch_kit.dll"))

dll.wa_version.restype = ctypes.c_char_p        # borrowed
dll.wa_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.wa_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("WatchKit version:", dll.wa_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from watchkit.h is quoted at the bottom of this
    # file, and the kit README in kits/WatchKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check wa_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from watchkit.h:
#   WA_API __declspec(dllexport) #elif defined(_WIN32) #define WA_API __declspec(dllimport) #else #define WA_API #endif enum { WA_OK = 0, WA_ERR_INVALID_ARG = 1, WA_ERR_NOT_SUPPORTED = 2, WA_ERR_NOT_FOUND = 3, WA_ERR_ACCESS_DENIED = 4, WA_ERR_PLATFORM = 5, WA_ERR_INTERNAL = 6, WA_ERR_PARSE = 7 };
