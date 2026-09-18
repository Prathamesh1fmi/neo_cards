# NeoCards v1.0 Release Candidate Checklist

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