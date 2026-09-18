$ErrorActionPreference = "Stop"

$TOOLS_DIR = "$PSScriptRoot\tools"
$NODE_DIR = "$TOOLS_DIR\node"
$NODE_VERSION = "v20.12.0"
$NODE_ZIP = "node-$NODE_VERSION-win-x64.zip"
$NODE_URL = "https://nodejs.org/dist/$NODE_VERSION/$NODE_ZIP"

if (!(Test-Path $TOOLS_DIR)) { New-Item -ItemType Directory -Force -Path $TOOLS_DIR | Out-Null }

Write-Host "Verifying Node.js..."
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "Global Node.js detected." -ForegroundColor Green
} elseif (Test-Path "$NODE_DIR\node.exe") {
    Write-Host "Portable Node.js detected." -ForegroundColor Green
} else {
    Write-Host "Node.js not found. Downloading portable version ($NODE_VERSION)..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $NODE_URL -OutFile "$TOOLS_DIR\$NODE_ZIP"
    Expand-Archive -Path "$TOOLS_DIR\$NODE_ZIP" -DestinationPath $TOOLS_DIR -Force
    Rename-Item -Path "$TOOLS_DIR\node-$NODE_VERSION-win-x64" -NewName "node"
    Remove-Item -Path "$TOOLS_DIR\$NODE_ZIP"
    Write-Host "Portable Node.js installed." -ForegroundColor Green
}

Write-Host "Verifying Rust..."
if (Get-Command cargo -ErrorAction SilentlyContinue) {
    Write-Host "Global Rust/Cargo detected." -ForegroundColor Green
} else {
    Write-Host "WARNING: Cargo not found in PATH." -ForegroundColor Red
    Write-Host "A fully portable Rust toolchain is not feasible on Windows due to heavy dependencies on the MSVC C++ Build Tools." -ForegroundColor Yellow
    Write-Host "Please install Rust globally via https://rustup.rs and ensure MSVC C++ build tools are installed." -ForegroundColor Yellow
}

Write-Host "Setup complete!"