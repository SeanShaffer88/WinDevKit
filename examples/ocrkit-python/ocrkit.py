#!/usr/bin/env python3
"""OCRKit from Python (ctypes) — the smallest runnable example.

Offline OCR behind one clean C ABI: Tesseract + Leptonica (pinned, vendored, hash-verified) returning JSON text + confidence

Put ocrkit.dll (from the OCRKit release zip in this repository's
Releases) next to this script and run:

    python ocrkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with ok_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/OCRKit/include/ocrkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "ocrkit.dll"))

dll.ok_version.restype = ctypes.c_char_p        # borrowed
dll.ok_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.ok_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("OCRKit version:", dll.ok_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from ocrkit.h is quoted at the bottom of this
    # file, and the kit README in kits/OCRKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check ok_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from ocrkit.h:
#   OK_API __declspec(dllexport) #elif defined(_WIN32) #define OK_API __declspec(dllimport) #else #define OK_API #endif enum { OK_OK = 0, OK_ERR_INVALID_ARG = 1, OK_ERR_NOT_SUPPORTED = 2, OK_ERR_NOT_FOUND = 3, OK_ERR_ACCESS_DENIED = 4, OK_ERR_PLATFORM = 5, OK_ERR_INTERNAL = 6 };
