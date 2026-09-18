# Usability & "Paper Cuts" Report (14-Day Dogfooding)

## Resolved Annoyances
- **Missing Hotkey**: Added `Ctrl+Enter` to quickly save a Note and keep the editor open for the next one (reducing 2 clicks per note).
- **Focus Traps**: Pressing `Space` while focus was on the "Show Answer" button would flip the card *and* rate it simultaneously due to double-firing events. Prevented default propagation.
- **Visual Clutter**: The Sync indicator spun aggressively during fast background syncs. Added a 500ms debounce to the UI spinner to make it less distracting.