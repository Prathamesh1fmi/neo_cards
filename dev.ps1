$NODE_DIR = "$PSScriptRoot\tools\node"
if (Test-Path "$NODE_DIR\node.exe") {
    $env:PATH = "$NODE_DIR;" + $env:PATH
}
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Error: npm not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}
if (!(Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "Error: cargo not found. Please install Rust (https://rustup.rs)." -ForegroundColor Red
    exit 1
}
npm run tauri dev