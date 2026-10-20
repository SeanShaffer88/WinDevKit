# WinDevKit gate — Windows/PowerShell version of gate.sh. Same steps, same
# reasons; see gate.sh for the failure each step has caught in practice.
# Usage: .\gate.ps1 [-Quick]
param([switch]$Quick)
$ErrorActionPreference = 'Stop'
function Step($name) { Write-Host "`n== $name ==" -ForegroundColor Cyan }
function Run($cmd) { Invoke-Expression $cmd; if ($LASTEXITCODE -ne 0) { throw "FAILED: $cmd" } }

Step 'cargo fmt --all -- --check'
Run 'cargo fmt --all -- --check'

Step 'cargo clippy --all-targets (host)'
Run 'cargo clippy --all-targets -- -D warnings'

if (-not $Quick) {
    $installed = rustup target list --installed
    if ($installed -match 'x86_64-pc-windows-msvc') {
        Step 'cargo clippy --target x86_64-pc-windows-msvc --all-targets'
        Run 'cargo clippy --target x86_64-pc-windows-msvc --all-targets -- -D warnings'
        Step 'cargo check --target x86_64-pc-windows-msvc --all-targets'
        Run 'cargo check --target x86_64-pc-windows-msvc --all-targets'
    } else {
        Write-Host 'SKIP: x86_64-pc-windows-msvc target not installed'
    }
}

Step 'cargo test (full suite)'
Run 'cargo test'

Write-Host "`nGATE GREEN" -ForegroundColor Green
