#!/usr/bin/env python3
"""NotifyKit from Python (ctypes) — the smallest runnable example.

Tray notifications: classic balloon alerts plus a WinRT toast backend, behind a small C ABI

Put notify_kit.dll (from the NotifyKit release zip in this repository's
Releases) next to this script and run:

    python notifykit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with no_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/NotifyKit/include/notifykit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "notify_kit.dll"))

dll.no_version.restype = ctypes.c_char_p        # borrowed
dll.no_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.no_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("NotifyKit version:", dll.no_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from notifykit.h is quoted at the bottom of this
    # file, and the kit README in kits/NotifyKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check no_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from notifykit.h:
#   NO_API __declspec(dllexport) #elif defined(_WIN32) #define NO_API __declspec(dllimport) #else #define NO_API #endif #define NO_OK 0 #define NO_ERR_INVALID_ARG 1 #define NO_ERR_NOT_SUPPORTED 2 #define NO_ERR_NOT_FOUND 3 #define NO_ERR_ACCESS_DENIED 4 #define NO_ERR_PLATFORM 5 #define NO_ERR_INTERNAL 6 typedef struct NoCenter NoCenter;
