#!/usr/bin/env python3
"""ProcessKit from Python (ctypes) — the smallest runnable example.

Child-process launch and supervision behind a small C ABI: captured output, timeouts, job-object tree kill, elevation rules (WinDevKit DLL #19)

Put process_kit.dll (from the ProcessKit release zip in this repository's
Releases) next to this script and run:

    python processkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with pk_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/ProcessKit/include/processkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "process_kit.dll"))

dll.pk_version.restype = ctypes.c_char_p        # borrowed
dll.pk_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.pk_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("ProcessKit version:", dll.pk_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from processkit.h is quoted at the bottom of this
    # file, and the kit README in kits/ProcessKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check pk_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from processkit.h:
#   PK_API __declspec(dllexport) #elif defined(_WIN32) #define PK_API __declspec(dllimport) #else #define PK_API #endif enum { PK_OK = 0, PK_ERR_INVALID_ARG = 1, PK_ERR_NOT_SUPPORTED = 2, PK_ERR_NOT_FOUND = 3, PK_ERR_ACCESS_DENIED = 4, PK_ERR_PLATFORM = 5, PK_ERR_INTERNAL = 6, PK_ERR_PARSE = 7 };
