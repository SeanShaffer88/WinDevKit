# The Windows DLL Collection — Catalog

## TL;DR

33 small Windows DLLs that each do one common job — watching folders, making
thumbnails, showing notifications, handling settings — so programs do not have
to reinvent them. Every kit is free (MIT), has no dependencies, and ships as a
ready-to-use download: the DLL, a C header, and an import library. Any
programming language that can call C functions can use them.

## How every kit works

All 33 kits share one pattern:

- Plain C interface (a header file is included), so C, C++, C#, Rust, Python,
  PowerShell and anything else with a C-calling feature can use them.
- Settings and results travel as JSON text — no structs to line up.
- Errors come back as readable text, never as a crash.
- Zero dependencies: each DLL is a single file you can drop next to your
  program.
- Built from Rust with the full test suite in the repo; every kit is covered
  by an on-machine smoke test against the shipped DLL.

Downloads are x64 and unsigned (there is no code-signing certificate);
Windows may show a SmartScreen prompt on first use.

## Files and folders

| Kit | What it does | Version | Download |
|---|---|---|---|
| FileOpsKit | Copy, move and delete batches of files, with dry-run plans and undo | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/FileOpsKit/releases/download/v0.1.0/FileOpsKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/FileOpsKit) |
| PathKit | Joins, splits, normalizes and converts Windows paths (including extended-length) | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/PathKit/releases/download/v0.1.0/PathKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/PathKit) |
| RenameKit | Batch file renaming with a preview before anything changes | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/RenameKit/releases/download/v0.1.0/RenameKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/RenameKit) |
| WatchKit | Watches folders and reports created, changed and deleted files (native Windows events since v0.2) | v0.2.0 | [DLL zip](https://github.com/SeanShaffer88/WatchKit/releases/download/v0.2.0/WatchKit-v0.2.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/WatchKit) |
| ProviderKit | Browses and reads files the same way from disk, network folders, ZIP and TAR | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/ProviderKit/releases/download/v0.1.0/ProviderKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/ProviderKit) |
| FileMetaKit | Reads what is known about a file: image size, audio tags, video and document facts | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/FileMetaKit/releases/download/v0.1.0/FileMetaKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/FileMetaKit) |
| FastSearch | Indexes a folder tree once, then searches it in memory | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/FastSearch/releases/download/v0.1.0/FastSearch-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/FastSearch) |
| ThumbKit | One thumbnail pipeline for every file type, with built-in PNG and JPEG decoding since v0.2 | v0.2.0 | [DLL zip](https://github.com/SeanShaffer88/ThumbKit/releases/download/v0.2.0/ThumbKit-v0.2.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/ThumbKit) |

## Archives, data and documents

| Kit | What it does | Version | Download |
|---|---|---|---|
| ArchiveKit | Creates, lists, tests and extracts ZIP and TAR archives | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/ArchiveKit/releases/download/v0.1.0/ArchiveKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/ArchiveKit) |
| SQLiteSuperBuild | A drop-in sqlite3.dll with everything switched on (FTS5, math, JSON) plus the sqlite-vec extension | v0.1.0 | [Release page](https://github.com/SeanShaffer88/SQLiteSuperBuild/releases/tag/v0.1.0) · [Repo](https://github.com/SeanShaffer88/SQLiteSuperBuild) |
| DocConvert | Converts between Markdown, HTML, CSV, JSON and plain text | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/DocConvert/releases/download/v0.1.0/DocConvert-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/DocConvert) |
| PDFKit | Reads, extracts text from, and generates PDF files | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/PDFKit/releases/download/v0.1.0/PDFKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/PDFKit) |

## Media, speech and AI

| Kit | What it does | Version | Download |
|---|---|---|---|
| MediaKit | Answers "what is this media file?": duration, codecs, dimensions, channels | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/MediaKit/releases/download/v0.1.0/MediaKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/MediaKit) |
| ImageKit | Loads, resizes, transforms and saves images in pure Rust | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/ImageKit/releases/download/v0.1.0/ImageKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/ImageKit) |
| OCRKit | Offline text recognition (OCR) with the engine built into the DLL | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/OCRKit/releases/download/v0.1.0/OCRKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/OCRKit) |
| Whisper | Offline speech-to-text with the engine built into the DLL | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/Whisper/releases/download/v0.1.0/Whisper-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/Whisper) |
| EmbedKit | Local semantic search (text embeddings) that runs fully offline | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/EmbedKit/releases/download/v0.1.0/EmbedKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/EmbedKit) |

## Windows system and shell

| Kit | What it does | Version | Download |
|---|---|---|---|
| ShellKit | Explorer integration the safe way: context-menu verbs, file associations, protocol handlers, and jump lists (v0.2) | v0.2.0 | [DLL zip](https://github.com/SeanShaffer88/ShellKit/releases/download/v0.2.0/ShellKit-v0.2.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/ShellKit) |
| ShellInteropKit | Shell file information, type names, associations and icon details | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/ShellInteropKit/releases/download/v0.1.0/ShellInteropKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/ShellInteropKit) |
| WinRecovery | Windows recovery primitives: restore points and recycle bin information | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/WinRecovery/releases/download/v0.1.0/WinRecovery-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/WinRecovery) |
| HardwareInfo | A hardware inventory: CPU, OS, memory, disks and GPUs | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/HardwareInfo/releases/download/v0.1.0/HardwareInfo-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/HardwareInfo) |
| WinUIHelpers | Window polish: dark title bars, DPI scaling and Windows information | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/WinUIHelpers/releases/download/v0.1.0/WinUIHelpers-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/WinUIHelpers) |
| SignKit | Inspects program files: PE details, the Authenticode hash, and the Windows trust verdict | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/SignKit/releases/download/v0.1.0/SignKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/SignKit) |

## App plumbing

| Kit | What it does | Version | Download |
|---|---|---|---|
| SettingsKit | Loads and saves JSON settings files atomically, with schema checks | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/SettingsKit/releases/download/v0.1.0/SettingsKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/SettingsKit) |
| LogKit | One structured log format for every app: one-line timestamped records | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/LogKit/releases/download/v0.1.0/LogKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/LogKit) |
| ProcessKit | Launches and supervises child processes, capturing output and exit codes | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/ProcessKit/releases/download/v0.1.0/ProcessKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/ProcessKit) |
| JobKit | A background-work engine: weighted steps on a worker thread, with progress | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/JobKit/releases/download/v0.1.0/JobKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/JobKit) |
| NetKit | HTTP and HTTPS requests over WinHTTP with hardened defaults | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/NetKit/releases/download/v0.1.0/NetKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/NetKit) |
| UpdateKit | Self-update pieces: version comparison and SHA-256 file verification | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/UpdateKit/releases/download/v0.1.0/UpdateKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/UpdateKit) |
| VaultKit | Stores secrets in Windows Credential Manager instead of plaintext files | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/VaultKit/releases/download/v0.1.0/VaultKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/VaultKit) |
| CrashKit | Captures a minidump and a JSON sidecar when a program crashes | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/CrashKit/releases/download/v0.1.0/CrashKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/CrashKit) |
| TimeKit | Time zones and date handling done once, correctly (497 canonical zones) | v0.1.0 | [DLL zip](https://github.com/SeanShaffer88/TimeKit/releases/download/v0.1.0/TimeKit-v0.1.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/TimeKit) |
| NotifyKit | Tells the user something: a notification queue plus tray balloons and real WinRT toasts (v0.2) | v0.2.0 | [DLL zip](https://github.com/SeanShaffer88/NotifyKit/releases/download/v0.2.0/NotifyKit-v0.2.0-x64.zip) · [Repo](https://github.com/SeanShaffer88/NotifyKit) |

## License

Every kit is MIT-licensed and free, including for commercial use.
