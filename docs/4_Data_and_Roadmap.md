# Database, Roadmap, and Risks

## 10. Database Design

NeoCards uses SQLite. The schema separates the *Content* (Notes) from the *Review State* (Cards), identical to Anki's underlying philosophy but modernized.

### Tables
1. **Decks**
   - `id` (UUID, PK)
   - `name` (String)
   - `created_at` (Timestamp)

2. **NoteTypes** (Templates)
   - `id` (UUID, PK)
   - `name` (String)
   - `fields` (JSON - e.g., ["Front", "Back"])

3. **Notes** (The actual content)
   - `id` (UUID, PK)
   - `note_type_id` (FK)
   - `deck_id` (FK)
   - `content` (JSON - maps to fields)
   - `tags` (JSON Array)

4. **Cards** (The specific testable face of a Note)
   - `id` (UUID, PK)
   - `note_id` (FK)
   - `due_date` (Timestamp)
   - `interval` (Integer)
   - `ease_factor` (Real)
   - `reps` (Integer)
   - `lapses` (Integer)
   - `state` (Enum: New, Learning, Review, Suspended)

5. **RevLog** (Review History for Statistics)
   - `id` (UUID, PK)
   - `card_id` (FK)
   - `graded` (Integer: 1,2,3,4)
   - `time_taken_ms` (Integer)
   - `created_at` (Timestamp)

## 12. Development Roadmap

- **Milestone 1: Scaffold & Architecture (Week 1)**
  - Setup Tauri + React + Vite.
  - Implement SQLite connection pool in Rust.
  - Scaffold shadcn/ui and Zustand.
- **Milestone 2: Data Layer & CRUD (Week 2)**
  - Implement Decks and Notes tables.
  - Create the Browser view (Notion-style data table).
  - Create the Note Editor (Markdown support).
- **Milestone 3: The Study Engine (Week 3)**
  - Implement the Spaced Repetition algorithm in Rust.
  - Build the Study UI (Framer Motion animations, Keyboard listeners).
- **Milestone 4: Polish & V1.0 (Week 4)**
  - Command Palette.
  - Statistics Dashboard (Recharts).
  - Anki `.apkg` importer.

## 13. Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Anki Compatibility** | High | Users won't switch without importing their decks. We must build a robust `.apkg` (SQLite + Media zip) unzipper and schema mapper in Rust for Milestone 4. |
| **Rich Text Performance** | Medium | Large notes with images might lag. We will store images on disk locally and use Tauri's `asset://` protocol to stream them to the DOM. |
| **Algorithm Tuning** | High | If the SRS algorithm feels "wrong", users will fail tests. We should default to FSRS (Free Spaced Repetition Scheduler), the modern industry standard, rather than SM-2. |

## 14. Questions for Approval

1. **Algorithm**: Do you prefer we implement the classic SM-2 algorithm (Anki default) or the newer, more accurate FSRS algorithm?
2. **Note Editor**: Should the editor be pure Markdown (like Obsidian) or a WYSIWYG block editor (like Notion)?
3. **Data Sync**: For MVP, is it acceptable to be 100% local, with users manually syncing the `.sqlite` file via Dropbox/Google Drive, before we build a dedicated sync server?

*Awaiting your review and approval before beginning Milestone 1.*

