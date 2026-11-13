#!/usr/bin/env python3
"""MediaKit from Python (ctypes) — the smallest runnable example.

Pure-Rust media probing (duration, codecs, streams) for common containers, behind a small C ABI

Put media_kit.dll (from the MediaKit release zip in this repository's
Releases) next to this script and run:

    python mediakit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with me_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/MediaKit/include/mediakit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "media_kit.dll"))

dll.me_version.restype = ctypes.c_char_p        # borrowed
dll.me_free_string.argtypes = [ctypes.c_void_p]
dll.me_probe.restype = ctypes.c_void_p           # caller-owned


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.me_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("MediaKit version:", dll.me_version().decode("utf-8"))


def main():
    print_version()
    # A real call: write a tiny WAV, then let MediaKit probe it.
    import tempfile, wave
    with tempfile.TemporaryDirectory() as td:
        wp = os.path.join(td, "tone.wav")
        with wave.open(wp, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
            w.writeframes(b"\x00\x00" * 800)
        print(take(dll.me_probe(wp.encode("utf-8"))))


if __name__ == "__main__":
    main()
