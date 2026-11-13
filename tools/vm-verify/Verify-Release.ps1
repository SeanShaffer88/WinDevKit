<#
.SYNOPSIS
    Verify release zips the way a clean Windows machine would
    meet them: hash, contents, DLL imports, and a real load test.

.DESCRIPTION
    Part of the WinDevKit VM verification pack (tools/vm-verify).
    Run it on the cleanest Windows machine (or VM snapshot) you
    have, against the zips exactly as downloaded from a Releases
    page. For each zip it:

      1. Checks the zip's SHA-256 against the SHA256SUMS.txt
         sitting next to it.
      2. Extracts it into a fresh work folder.
      3. Parses every .dll/.exe with Get-PeInfo.ps1 and flags any
         imported DLL that is not a Windows system library (the
         failure mode where a binary needs a DLL nobody shipped).
      4. On Windows: loads each DLL and calls the kit family's
         <prefix>_version export, recording the version string —
         the "it actually starts" check a hash can never give.

    Everything lands in a JSON report (verify-report.json), and
    the exit code says the verdict plainly:

      0  every check passed (off Windows, the load test is
         reported as Skipped rather than Passed)
      1  at least one check failed
      2  usage error (no zips found, a SHA256SUMS.txt missing...)

    The script never modifies the input zips and writes only to
    its work folder and the report path.

.PARAMETER Path
    A release .zip, or a folder containing release zips. Each zip
    needs its SHA256SUMS.txt in the same folder.

.PARAMETER WorkDir
    Extraction scratch folder. Default: a fresh folder under the
    system temp directory.

.PARAMETER ReportPath
    Where to write verify-report.json. Default: .\verify-report.json

.EXAMPLE
    ./Verify-Release.ps1 C:\Downloads\MediaKit-release
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)]
    [string] $Path,
    [string] $WorkDir,
    [string] $ReportPath = (Join-Path (Get-Location) 'verify-report.json')
)

$ErrorActionPreference = 'Stop'
$isWindowsHost = [Environment]::OSVersion.Platform -eq 'Win32NT'

# Windows system libraries a release binary may import without
# shipping anything: the same list the collection's download
# verifier uses (plus the api-ms-/ext-ms- API-set prefixes, which
# resolve inside Windows itself). Anything else must be IN the zip.
$SystemDlls = @(
    'kernel32.dll','user32.dll','advapi32.dll','bcrypt.dll','crypt32.dll','ws2_32.dll',
    'shell32.dll','ole32.dll','oleaut32.dll','gdi32.dll','ntdll.dll','msvcrt.dll','comdlg32.dll',
    'comctl32.dll','setupapi.dll','cfgmgr32.dll','powrprof.dll','dwmapi.dll','uxtheme.dll',
    'version.dll','winmm.dll','secur32.dll','iphlpapi.dll','psapi.dll','wininet.dll','winhttp.dll',
    'ncrypt.dll','credui.dll','bcryptprimitives.dll','dbghelp.dll','wintrust.dll','netapi32.dll',
    'wtsapi32.dll','shlwapi.dll','imm32.dll','opengl32.dll',
    'd3d11.dll','dxgi.dll','windows.storage.dll','runtimeobject.dll'
)

function Test-SystemDll([string] $name) {
    $n = $name.ToLowerInvariant()
    ($SystemDlls -contains $n) -or $n.StartsWith('api-ms-') -or $n.StartsWith('ext-ms-')
}

function Invoke-VersionCall([string] $dllPath, [string] $exportName, [int] $index) {
    # One generated P/Invoke type per DLL: the export name differs
    # per kit (me_version, sk_version, ...), so the shim is built
    # from the export the parser actually found.
    $typeName = "VmVerifyNative$index"
    $escapedPath = $dllPath.Replace('\', '\\').Replace('"', '\"')
    $code = @"
using System;
using System.Runtime.InteropServices;
public static class $typeName {
    [DllImport("$escapedPath", CallingConvention = CallingConvention.Cdecl, ExactSpelling = true)]
    public static extern IntPtr $exportName();
    public static string CallVersion() {
        IntPtr p = $exportName();
        return p == IntPtr.Zero ? null : Marshal.PtrToStringAnsi(p);
    }
}
"@
    Add-Type -TypeDefinition $code -Language CSharp
    & ([type]$typeName)::CallVersion
}

# --- Collect inputs ---
$zips = @()
if (Test-Path $Path -PathType Container) {
    $zips = Get-ChildItem (Join-Path $Path '*.zip') | ForEach-Object { $_.FullName }
} elseif (Test-Path $Path -PathType Leaf) {
    $zips = @((Resolve-Path $Path).Path)
}
if ($zips.Count -eq 0) {
    Write-Host "No .zip found at $Path"
    exit 2
}

if (-not $WorkDir) {
    $WorkDir = Join-Path ([System.IO.Path]::GetTempPath()) ("vm-verify-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
}
New-Item -ItemType Directory -Force $WorkDir | Out-Null
Write-Host "Work folder: $WorkDir"

$report = [ordered]@{
    tool    = 'WinDevKit vm-verify'
    started = (Get-Date).ToString('o')
    machine = [ordered]@{
        name      = $env:COMPUTERNAME
        os        = [Environment]::OSVersion.VersionString
        isWindows = $isWindowsHost
    }
    inputs  = @()
    verdict = 'Passed'
}
$anyFailure = $false
$dllIndex = 0

foreach ($zip in $zips) {
    $zipName = Split-Path $zip -Leaf
    $entry = [ordered]@{ zip = $zipName; sha256 = $null; files = @() }
    Write-Host "`n== $zipName =="

    # 1. Hash against the sibling SHA256SUMS.txt
    $sumsPath = Join-Path (Split-Path $zip -Parent) 'SHA256SUMS.txt'
    if (-not (Test-Path $sumsPath)) {
        Write-Host "  FAIL  no SHA256SUMS.txt next to the zip"
        $entry.sha256 = [ordered]@{ status = 'Failed'; error = 'SHA256SUMS.txt not found' }
        $anyFailure = $true
        $report.inputs += $entry
        continue
    }
    $expected = $null
    foreach ($line in Get-Content $sumsPath) {
        if ($line -match '^([0-9a-fA-F]{64})\s+\*?(.+)$' -and $Matches[2].Trim() -eq $zipName) {
            $expected = $Matches[1].ToLowerInvariant()
        }
    }
    $actual = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
    $hashOk = $null -ne $expected -and $expected -eq $actual
    $entry.sha256 = [ordered]@{ status = $(if ($hashOk) { 'Passed' } else { 'Failed' }); expected = $expected; actual = $actual }
    Write-Host "  $(if ($hashOk) { 'PASS' } else { 'FAIL' })  SHA-256 matches SHA256SUMS.txt"
    if (-not $hashOk) { $anyFailure = $true }

    # 2. Extract fresh
    $dest = Join-Path $WorkDir ([System.IO.Path]::GetFileNameWithoutExtension($zipName))
    Expand-Archive -Path $zip -DestinationPath $dest -Force

    # 3 + 4. Inspect and (on Windows) load every binary
    $binaries = Get-ChildItem $dest -Recurse -Include *.dll, *.exe
    foreach ($bin in $binaries) {
        $fileEntry = [ordered]@{ file = $bin.Name; machine = $null; imports = @(); nonSystemImports = @(); versionExport = $null; loadTest = [ordered]@{ status = 'Skipped'; detail = 'not a DLL' } }
        try {
            $pe = & (Join-Path $PSScriptRoot 'Get-PeInfo.ps1') $bin.FullName
            $fileEntry.machine = $pe.Machine
            $fileEntry.imports = @($pe.Imports)
            $fileEntry.nonSystemImports = @($pe.Imports | Where-Object { -not (Test-SystemDll $_) })
            if ($fileEntry.nonSystemImports.Count -gt 0) {
                Write-Host "  FAIL  $($bin.Name) imports non-system DLLs: $($fileEntry.nonSystemImports -join ', ')"
                $anyFailure = $true
            } else {
                Write-Host "  PASS  $($bin.Name) imports are system-only ($($pe.Machine))"
            }
            $fileEntry.versionExport = @($pe.Exports | Where-Object { $_ -like '*_version' }) | Select-Object -First 1
            if ($bin.Extension -eq '.dll') {
                if (-not $isWindowsHost) {
                    $fileEntry.loadTest = [ordered]@{ status = 'Skipped'; detail = 'load test needs a Windows host' }
                    Write-Host "  SKIP  $($bin.Name) load test (not on Windows)"
                } elseif (-not $fileEntry.versionExport) {
                    $fileEntry.loadTest = [ordered]@{ status = 'Failed'; detail = 'no *_version export found' }
                    Write-Host "  FAIL  $($bin.Name) has no *_version export to call"
                    $anyFailure = $true
                } else {
                    $dllIndex++
                    try {
                        $version = Invoke-VersionCall $bin.FullName $fileEntry.versionExport $dllIndex
                        $fileEntry.loadTest = [ordered]@{ status = 'Passed'; detail = "$($fileEntry.versionExport)() returned '$version'" }
                        Write-Host "  PASS  $($bin.Name) loaded; $($fileEntry.versionExport)() -> $version"
                    } catch {
                        $fileEntry.loadTest = [ordered]@{ status = 'Failed'; detail = $_.Exception.Message }
                        Write-Host "  FAIL  $($bin.Name) load test: $($_.Exception.Message)"
                        $anyFailure = $true
                    }
                }
            }
        } catch {
            $fileEntry.loadTest = [ordered]@{ status = 'Failed'; detail = "PE parse failed: $($_.Exception.Message)" }
            Write-Host "  FAIL  $($bin.Name): $($_.Exception.Message)"
            $anyFailure = $true
        }
        $entry.files += $fileEntry
    }
    $report.inputs += $entry
}

if ($anyFailure) { $report.verdict = 'Failed' }
$report | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $ReportPath
Write-Host "`nVerdict: $($report.verdict)  (report: $ReportPath)"
if ($anyFailure) { exit 1 } else { exit 0 }
