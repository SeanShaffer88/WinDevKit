#!/usr/bin/env python3
"""BridgeKit from the command line — generate bindings, don't type them.

BridgeKit is the one kit that is a program rather than a DLL, so
its example is a script: put bridgekit.exe (from the BridgeKit
release zip in this repository's Releases) next to this script
and run:

    python bridgekit.py

It generates C# and Rust bindings from the bundled sample.h and
prints them. Point the same two commands at any real kit header
(kits/<Kit>/include/<kit>.h) and you get that kit's bindings —
or download the prebuilt bindings pack from Releases instead.
"""

import os
import subprocess
import sys
import tempfile

if sys.platform != "win32":
    sys.exit("This example drives the Windows bridgekit.exe and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
exe = os.path.join(here, "bridgekit.exe")
header = os.path.join(here, "sample.h")

with tempfile.TemporaryDirectory() as td:
    cs = os.path.join(td, "Sample.cs")
    rs = os.path.join(td, "sample.rs")
    subprocess.run([exe, "gen-cs", "--header", header,
                    "--dll-name", "sample.dll", "--out", cs], check=True)
    subprocess.run([exe, "gen-rs", "--header", header,
                    "--out", rs], check=True)
    print("===== Sample.cs (generated) =====")
    print(open(cs).read())
    print("===== sample.rs (generated) =====")
    print(open(rs).read())
