import os
import json
from pathlib import Path

base = Path('.')

dirs = [
    '.github/workflows',
    'scripts/release',
    'installer/windows',
    'docs/release',
    'tests/e2e',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. CI/CD Release Workflow
scripts['.github/workflows/release.yml'] = r'''name: "Release v1.0"
on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-release:
    strategy:
      fail-fast: false
      matrix:
        platform: [macos-latest, ubuntu-20.04, windows-latest]
    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        
      - name: Install Linux Dependencies
        if: matrix.platform == 'ubuntu-20.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.0-dev libappindicator3-dev librsvg2-dev patchelf
          
      - name: Install Frontend Dependencies
        run: npm ci

      - name: Run E2E Tests (Playwright)
        run: npx playwright test
        
      - name: Build and Package (Tauri)
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAURI_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_KEY_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: "NeoCards ${{ github.ref_name }}"
          releaseBody: "See RELEASE_NOTES.md for full details."
          releaseDraft: true
          prerelease: false
'''

# 2. Update tauri.conf.json for Packaging & Updater
tauri_conf_path = base / 'src-tauri/tauri.conf.json'
if tauri_conf_path.exists():
    try:
        conf = json.loads(tauri_conf_path.read_text())
        
        # Inject Bundler targets
        if 'tauri' not in conf: conf['tauri'] = {}
        if 'bundle' not in conf['tauri']: conf['tauri']['bundle'] = {}
        
        conf['tauri']['bundle']['targets'] = ["msi", "nsis", "appimage", "deb", "dmg", "updater"]
        conf['tauri']['bundle']['identifier'] = "com.neocards.app"
        conf['tauri']['bundle']['icon'] = [
            "icons/32x32.png", "icons/128x128.png", "icons/128x128@2x.png", "icons/icon.icns", "icons/icon.ico"
        ]
        
        # Inject Updater
        if 'updater' not in conf['tauri']: conf['tauri']['updater'] = {}
        conf['tauri']['updater'] = {
            "active": True,
            "endpoints": [
                "https://releases.neocards.io/update/{{target}}/{{current_version}}"
            ],
            "dialog": True,
            "pubkey": "UPDATE_PUB_KEY"
        }
        
        tauri_conf_path.write_text(json.dumps(conf, indent=2))
    except Exception as e:
        print(f"Failed to update tauri.conf.json: {e}")

# 3. Release Checklist
scripts['docs/release/RELEASE_CHECKLIST.md'] = r'''# NeoCards v1.0 Release Candidate Checklist

## 1. Security & Credentials
- [ ] Verify `rusqlite` is NOT storing API keys or user passwords.
- [ ] Migrate all secret storage to `tauri-plugin-store` utilizing the OS native Keychain (Credential Manager / Keyring).
- [ ] Audit IPC commands. Ensure no `String` errors leak database paths or SQL query structures to React.

## 2. Packaging & Installers
- [ ] **Windows**: Build `.msi` and `.nsis`. Verify desktop shortcut creation and uninstall cleanup.
- [ ] **macOS**: Build universal `.dmg`. Verify Apple Notarization and Developer ID signing.
- [ ] **Linux**: Build `.AppImage` and `.deb`. Verify `patchelf` hooks.

## 3. Auto-Updater
- [ ] Verify ECDSA public/private key pairs for update manifests.
- [ ] Test upgrade path from v0.9.9 -> v1.0.0.
- [ ] Test downgrade rollback on failed installation.

## 4. Performance & Memory
- [ ] Run `cargo bench` against the 1,000,000 Note dataset. Validate < 100ms startup.
- [ ] Profile memory using `valgrind` / Instruments. Ensure idle memory remains < 150MB.

## 5. Testing
- [ ] Unit Tests: `cargo test` passing.
- [ ] E2E Tests: `playwright` passing across all Critical User Journeys (Create Deck -> Add Note -> Sync -> Review).
- [ ] Accessibility: Pass Lighthouse / aXe audits for ARIA labels and Contrast.
'''

# 4. Release Notes
scripts['docs/release/RELEASE_NOTES.md'] = r'''# NeoCards v1.0.0 "Genesis"

NeoCards v1.0 is officially here. 

After months of architectural planning, we have delivered a native desktop platform that fundamentally modernizes learning. 

## Key Features
- **Local-First Architecture**: Your knowledge is yours. SQLite is the source of truth. No internet required.
- **FSRS Intelligence**: The official Rust FSRS scheduler is built directly into the core, optimizing your memory retention automatically.
- **Document Engine**: Built on Tiptap ProseMirror JSON AST, notes are structural, extensible, and immune to HTML lock-in.
- **Plugin Platform**: Extend NeoCards safely via our sandboxed API capabilities.
- **Native Sync**: Decentralized, E2EE sync engine using CRDT-ready delta replication.

## System Requirements
- Windows 10/11
- macOS 12+ (Intel & Apple Silicon)
- Ubuntu 20.04+ (or equivalent AppImage-compatible distro)

Thank you for being part of the NeoCards journey.
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Version 1.0 Release Scaffolding complete.")

