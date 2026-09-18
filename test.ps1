$NODE_DIR = "$PSScriptRoot\tools\node"
if (Test-Path "$NODE_DIR\node.exe") {
    $env:PATH = "$NODE_DIR;" + $env:PATH
}
Write-Host "Running Frontend Tests..."
npm run test
Write-Host "Running Backend Tests..."
cd src-tauri
cargo test