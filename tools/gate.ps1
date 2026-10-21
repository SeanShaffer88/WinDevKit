# Same gate as gate.sh; native Windows link/runtime verification remains in CI.
param([switch]$Quick)
$ErrorActionPreference = 'Stop'
function Step($name) { Write-Host "`n== $name ==" -ForegroundColor Cyan }
function Run([scriptblock]$Command) {
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "FAILED: $Command (exit $LASTEXITCODE)" }
}
if (-not $Quick) {
    $installed = & rustup target list --installed
    if ($LASTEXITCODE -ne 0) { throw 'FAILED: rustup target list --installed' }
    if ($installed -notcontains 'x86_64-pc-windows-msvc') {
        throw 'Missing required target: rustup target add x86_64-pc-windows-msvc; use -Quick for partial host checks'
    }
}
Step 'cargo fmt --all -- --check'
Run { cargo fmt --all -- --check }
Step 'cargo clippy --workspace --all-targets --locked (host)'
Run { cargo clippy --workspace --all-targets --locked -- -D warnings }
if (-not $Quick) {
    Step 'cargo clippy --workspace --target x86_64-pc-windows-msvc --all-targets --locked'
    Run { cargo clippy --workspace --target x86_64-pc-windows-msvc --all-targets --locked -- -D warnings }
    Step 'cargo check --workspace --target x86_64-pc-windows-msvc --all-targets --locked'
    Run { cargo check --workspace --target x86_64-pc-windows-msvc --all-targets --locked }
}
Step 'cargo test --workspace --locked (full suite)'
Run { cargo test --workspace --locked }
if ($Quick) {
    Write-Host "`nPARTIAL: host checks passed; Windows target checks not run" -ForegroundColor Yellow
} else {
    Write-Host "`nGATE GREEN: host + Windows cross-checks passed; native Windows link/runtime still requires CI" -ForegroundColor Green
}
