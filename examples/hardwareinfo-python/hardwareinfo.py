#!/usr/bin/env python3
"""HardwareInfo from Python (ctypes) — the smallest runnable example.

Hardware inventory behind one clean C ABI — CPU, GPU, memory, disks, monitors, network, battery

Put hardwareinfo.dll (from the HardwareInfo release zip in this repository's
Releases) next to this script and run:

    python hardwareinfo.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with hw_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/HardwareInfo/include/hardwareinfo.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "hardwareinfo.dll"))

dll.hw_version.restype = ctypes.c_char_p        # borrowed
dll.hw_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.hw_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("HardwareInfo version:", dll.hw_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: hw_cpu_json — its exact
    # signature from hardwareinfo.h is quoted at the bottom of this
    # file, and the kit README in kits/HardwareInfo/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check hw_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from hardwareinfo.h:
#   HW_API char *hw_cpu_json(void);
