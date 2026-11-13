#!/usr/bin/env python3
"""VaultKit from Python (ctypes) — the smallest runnable example.

Store secrets safely on Windows: DPAPI + Credential Manager behind a five-function C ABI, so apps stop keeping tokens in plaintext files

Put vaultkit.dll (from the VaultKit release zip in this repository's
Releases) next to this script and run:

    python vaultkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with vk_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/VaultKit/include/vaultkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "vaultkit.dll"))

dll.vk_version.restype = ctypes.c_char_p        # borrowed
dll.vk_free_string.argtypes = [ctypes.c_void_p]
dll.vk_list_json.restype = ctypes.c_void_p       # caller-owned


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.vk_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("VaultKit version:", dll.vk_version().decode("utf-8"))


def main():
    print_version()
    # A real call: list the credential names in a namespace
    # (read-only; an unused namespace lists as empty).
    print(take(dll.vk_list_json(b"windevkit-example")))


if __name__ == "__main__":
    main()
