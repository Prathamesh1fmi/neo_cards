# NeoCards: Product Strategy

## 1. Product Vision
NeoCards is a local-first, extremely fast, and keyboard-centric learning platform inspired by the scientifically proven spaced-repetition algorithms of Anki. 
While Anki focuses heavily on pure functionality resulting in a dated and fragmented UX, **NeoCards aims to deliver a premium, fluid, and delightful experience**—reminiscent of tools like Linear, Notion, and Raycast. 
It is not an Anki clone; it is a fundamental reimagining of what a modern knowledge retention tool should be.

## 4. Feature Breakdown

### Minimum Viable Product (MVP)
- Local SQLite database setup.
- Basic Deck creation and management.
- Note/Card separation (Basic front/back cards).
- Study session interface with basic Spaced Repetition (e.g., SM-2 algorithm).
- Keyboard shortcuts for grading (1, 2, 3, 4) and navigation.
- Markdown rendering for cards.

### Version 1.0 (Public Release)
- Advanced Note Types (Cloze deletion, Image occlusion).
- Global Command Palette (Cmd+K / Ctrl+K).
- Statistics Dashboard (Heatmaps, retention rates) using Recharts.
- Dark/Light mode full support with shadcn/ui.
- Anki deck import/export (.apkg compatibility).

### Future (V2.0+)
- Local AI integration (LLM-generated flashcards from PDFs/videos).
- WASM-based Plugin Architecture.
- Peer-to-peer or E2E encrypted cloud sync.
- Mobile application (Tauri mobile or React Native).

## 6. Navigation Flow
The interface is minimal. A single-window application with a dynamic sidebar (toggleable).
- **Home/Library**: Grid/List of Decks, daily review counts, heatmaps.
- **Study Mode**: Distraction-free, fullscreen capable. Hides sidebar. Focuses entirely on the card.
- **Browser/Vault**: Notion-style table view of all Notes and Cards. Powerful filtering.
- **Settings/Preferences**: Application config, algorithm tuning.
- **Command Palette**: Available everywhere via `Ctrl+K`.

## 7. User Flow (New User)
1. **Onboarding**: User opens NeoCards. They see a clean empty state with a "Create Deck" or "Import from Anki" call-to-action.
2. **Creation**: User hits `C` (shortcut) to open a floating "New Note" modal. They type the front/back in Markdown and hit `Cmd+Enter` to save.
3. **Reviewing**: User presses `Space` on a deck to enter Study Mode. They use `Space` to reveal answers and `1-4` to grade.
4. **Completion**: A delightful, subtle animation celebrates the end of the review queue, returning them to the dashboard.

