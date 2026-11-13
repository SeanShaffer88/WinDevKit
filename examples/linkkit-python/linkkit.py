#!/usr/bin/env python3
"""LinkKit from Python (ctypes) — the smallest runnable example.

Windows shortcut (.lnk) create/read/update including AppUserModelID, over a JSON C ABI

Put link_kit.dll (from the LinkKit release zip in this repository's
Releases) next to this script and run:

    python linkkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with lk_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/LinkKit/include/linkkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "link_kit.dll"))

dll.lk_version.restype = ctypes.c_char_p        # borrowed
dll.lk_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.lk_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("LinkKit version:", dll.lk_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: lk_create — its exact
    # signature from linkkit.h is quoted at the bottom of this
    # file, and the kit README in kits/LinkKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check lk_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from linkkit.h:
#   LK_API int lk_create(const char *spec_json);
