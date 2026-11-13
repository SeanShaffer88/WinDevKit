#!/usr/bin/env python3
"""ShellKit from Python (ctypes) — the smallest runnable example.

Safe Windows shell integration (context-menu verbs, file associations, protocol handlers, jump lists) as plan + apply with backup, behind a small C ABI

Put shell_kit.dll (from the ShellKit release zip in this repository's
Releases) next to this script and run:

    python shellkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with sh_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/ShellKit/include/shellkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "shell_kit.dll"))

dll.sh_version.restype = ctypes.c_char_p        # borrowed
dll.sh_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.sh_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("ShellKit version:", dll.sh_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: sh_plan_verb — its exact
    # signature from shellkit.h is quoted at the bottom of this
    # file, and the kit README in kits/ShellKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check sh_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from shellkit.h:
#   SH_API char *sh_plan_verb(const char *spec_json);
