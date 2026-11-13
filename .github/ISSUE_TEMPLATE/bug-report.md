---
name: Bug report
about: Something in a kit, a tool or a template does not work as documented
title: "[KitOrTool] Short summary"
labels: bug
---

**Which kit, tool or template?**
Name it exactly as it appears in the catalog or the `kits/` /
`tools/` / `templates/` folders.

**Version**
The release tag you downloaded (for example `WatchKit-v0.2.0`), or
the commit you built from.

**What happened?**
What you called, what you passed in, and what came back — including
the exact error text. For a DLL call, the value of the kit's
`<prefix>_last_error()` is the single most useful line you can add.

**What did you expect?**
What the kit's README or header led you to expect instead.

**Your setup**
Windows version, and the language/runtime you called from
(C / C++ / C# / Rust / Python / PowerShell, with its version).

**Anything else?**
A minimal repro — the smallest program or script that shows the
problem — is worth more than a long description.
