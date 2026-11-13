#!/usr/bin/env python3
"""FileOpsKit from Python (ctypes) — the smallest runnable example.

File operation engine behind a small C ABI: copy, move, rename and delete jobs with progress, cancellation, conflict policies, retries and undo

Put file_ops_kit.dll (from the FileOpsKit release zip in this repository's
Releases) next to this script and run:

    python fileopskit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with fo_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/FileOpsKit/include/fileopskit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "file_ops_kit.dll"))

dll.fo_version.restype = ctypes.c_char_p        # borrowed
dll.fo_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.fo_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("FileOpsKit version:", dll.fo_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: fo_plan — its exact
    # signature from fileopskit.h is quoted at the bottom of this
    # file, and the kit README in kits/FileOpsKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check fo_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from fileopskit.h:
#   FO_API char *fo_plan(const char *spec_json);
