#!/usr/bin/env python3
"""ShellInteropKit from Python (ctypes) — the smallest runnable example.

Windows Shell interop wrapper behind a small C ABI: typed icons, file info, verbs and properties without raw COM/Shell boilerplate

Put shell_interop_kit.dll (from the ShellInteropKit release zip in this repository's
Releases) next to this script and run:

    python shellinteropkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with si_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/ShellInteropKit/include/shellinteropkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "shell_interop_kit.dll"))

dll.si_version.restype = ctypes.c_char_p        # borrowed
dll.si_free_string.argtypes = [ctypes.c_void_p]
dll.si_type_name_for_extension.restype = ctypes.c_void_p  # caller-owned


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.si_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("ShellInteropKit version:", dll.si_version().decode("utf-8"))


def main():
    print_version()
    # A real call: the shell's display name for a .txt file.
    print(take(dll.si_type_name_for_extension(b".txt")))


if __name__ == "__main__":
    main()
