<#
.SYNOPSIS
    Read a PE file's imported DLL names and exported function
    names, in pure PowerShell — no dumpbin, no SDK, no downloads.

.DESCRIPTION
    Part of the WinDevKit VM verification pack (tools/vm-verify).
    Verify-Release.ps1 uses this to answer the two questions a
    clean-machine check cares about:

      * Imports: does this DLL/EXE depend on anything that will
        not already be on a clean Windows install?
      * Exports: is the family's <prefix>_version handshake
        present, so the load test knows what to call?

    Only the headers are parsed; the file is never loaded or
    executed, so this script is safe to run anywhere (including
    off Windows) against untrusted binaries.

.PARAMETER Path
    The PE file (.dll or .exe) to inspect.

.OUTPUTS
    A PSCustomObject: Path, Machine ('x64'/'x86'/'arm64'/'unknown'),
    Imports (string[] of DLL names, as written in the file),
    Exports (string[] of exported names, ordinal-only exports
    excluded).

.EXAMPLE
    ./Get-PeInfo.ps1 media_kit.dll | Format-List
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)]
    [string] $Path
)

$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $Path).Path)

function Read-U16([int] $off) { [BitConverter]::ToUInt16($bytes, $off) }
function Read-U32([int] $off) { [BitConverter]::ToUInt32($bytes, $off) }
function Read-CString([int] $off) {
    $end = $off
    while ($end -lt $bytes.Length -and $bytes[$end] -ne 0) { $end++ }
    [System.Text.Encoding]::ASCII.GetString($bytes, $off, $end - $off)
}

# --- Headers ---
if ($bytes.Length -lt 0x40 -or $bytes[0] -ne 0x4D -or $bytes[1] -ne 0x5A) {
    throw "$Path is not a PE file (no MZ signature)."
}
$peOff = [BitConverter]::ToInt32($bytes, 0x3C)
if ((Read-U32 $peOff) -ne 0x4550) { throw "$Path is not a PE file (no PE signature)." }

$coff = $peOff + 4
$machineCode = Read-U16 $coff
$machine = switch ($machineCode) {
    0x8664 { 'x64' } 0x14C { 'x86' } 0xAA64 { 'arm64' } default { 'unknown' }
}
$numSections = Read-U16 ($coff + 2)
$optSize = Read-U16 ($coff + 16)
$opt = $coff + 20
$is64 = (Read-U16 $opt) -eq 0x20B
$dirStart = $opt + $(if ($is64) { 112 } else { 96 })
$exportDirRva = Read-U32 $dirStart          # directory[0]: exports
$importDirRva = Read-U32 ($dirStart + 8)    # directory[1]: imports

# --- Sections (for RVA -> file offset) ---
$sections = @()
$secOff = $opt + $optSize
for ($i = 0; $i -lt $numSections; $i++) {
    $s = $secOff + 40 * $i
    $sections += [pscustomobject]@{
        VirtualSize    = Read-U32 ($s + 8)
        VirtualAddress = Read-U32 ($s + 12)
        RawSize        = Read-U32 ($s + 16)
        RawPointer     = Read-U32 ($s + 20)
    }
}
function Rva-ToOffset([uint32] $rva) {
    foreach ($s in $sections) {
        $span = [Math]::Max($s.VirtualSize, $s.RawSize)
        if ($rva -ge $s.VirtualAddress -and $rva -lt $s.VirtualAddress + $span) {
            return [int] ($s.RawPointer + ($rva - $s.VirtualAddress))
        }
    }
    return -1
}

# --- Imports: walk the descriptor table, one entry per DLL ---
$imports = @()
if ($importDirRva -ne 0) {
    $desc = Rva-ToOffset $importDirRva
    while ($desc -ge 0) {
        $nameRva = Read-U32 ($desc + 12)
        $firstThunk = Read-U32 ($desc + 16)
        if ($nameRva -eq 0 -and $firstThunk -eq 0) { break }
        $imports += Read-CString (Rva-ToOffset $nameRva)
        $desc += 20
    }
}

# --- Exports: the name-pointer table ---
$exports = @()
if ($exportDirRva -ne 0) {
    $exp = Rva-ToOffset $exportDirRva
    $numNames = Read-U32 ($exp + 24)
    $namesRva = Read-U32 ($exp + 32)
    $namesOff = Rva-ToOffset $namesRva
    for ($i = 0; $i -lt $numNames; $i++) {
        $nameOff = Rva-ToOffset (Read-U32 ($namesOff + 4 * $i))
        if ($nameOff -ge 0) { $exports += Read-CString $nameOff }
    }
}

[pscustomobject]@{
    Path    = $Path
    Machine = $machine
    Imports = $imports
    Exports = $exports
}
