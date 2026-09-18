$NODE_DIR = "$PSScriptRoot\tools\node"
if (Test-Path "$NODE_DIR\node.exe") {
    $env:PATH = "$NODE_DIR;" + $env:PATH
}
npm run tauri build