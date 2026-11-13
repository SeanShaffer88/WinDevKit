#!/usr/bin/env python3
"""InstanceKit from Python (ctypes) — the smallest runnable example.

Single-instance mutex with named-pipe argument forwarding, over a JSON C ABI

Put instance_kit.dll (from the InstanceKit release zip in this repository's
Releases) next to this script and run:

    python instancekit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with in_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/InstanceKit/include/instancekit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "instance_kit.dll"))

dll.in_version.restype = ctypes.c_char_p        # borrowed
dll.in_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.in_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("InstanceKit version:", dll.in_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: in_acquire — its exact
    # signature from instancekit.h is quoted at the bottom of this
    # file, and the kit README in kits/InstanceKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check in_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from instancekit.h:
#   IN_API char *in_acquire(const char *spec_json);
