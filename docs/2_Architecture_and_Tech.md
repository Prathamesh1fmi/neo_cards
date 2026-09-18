# Architecture & Technology

## 2. Architecture Overview
NeoCards follows **Clean Architecture** combined with a **Feature-First** modular organization. 
- **Tauri Core**: Handles window management, native OS integrations, and spawns the Rust backend.
- **Rust Backend**: Interacts securely with the local SQLite database. Exposes Tauri Commands to the frontend.
- **React Frontend**: A pure presentation and state-management layer. No direct database access.

## 3. Technology Justification
- **Desktop (Tauri)**: Dramatically smaller memory footprint than Electron. Near-instant startup times. Native OS feeling.
- **Frontend (React + Vite + TypeScript)**: The industry standard for robust, type-safe, and highly interactive UIs. Vite provides HMR for unmatched developer velocity.
- **Styling (TailwindCSS + shadcn/ui)**: Utility-first CSS allows rapid prototyping. shadcn/ui provides accessible (Radix UI), unstyled, and highly customizable components that fit the Linear/Raycast aesthetic perfectly.
- **Animations (Framer Motion)**: Physics-based animations are critical for the "premium" feel. CSS transitions are too rigid.
- **State (Zustand)**: Lightweight, boilerplate-free global state management. Redux is too heavy for this architecture.
- **Backend (Rust + SQLite)**: SQLite is the perfect local-first database. Rust ensures memory safety, incredible performance, and powers the Tauri bridge.
- **Search (SQLite FTS5)**: Full-Text Search directly inside SQLite eliminates the need for a heavy secondary search index.

## 5. Folder Structure
```text
neocards/
├── src-tauri/                 # Rust Backend
│   ├── src/
│   │   ├── commands/          # Tauri IPC endpoints
│   │   ├── db/                # SQLite connection pool & migrations
│   │   ├── domain/            # Core Rust logic (Algorithms, Models)
│   │   └── main.rs            # Entry point
│   ├── Cargo.toml
│   └── tauri.conf.json
├── src/                       # React Frontend
│   ├── assets/                # Fonts, static icons
│   ├── components/            # Reusable UI (shadcn, core buttons)
│   ├── features/              # Feature-sliced modules
│   │   ├── decks/             # Deck list, deck API, deck state
│   │   ├── study/             # Study interface, grader, shortcuts
│   │   └── browser/           # Note browser, search
│   ├── hooks/                 # Global React hooks
│   ├── store/                 # Zustand stores
│   ├── types/                 # Global TS definitions
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

## 11. Application Architecture
1. **Presentation Layer (React Components)**: Dispatches actions to Zustand or calls Tauri commands directly via `@tauri-apps/api`.
2. **State Layer (Zustand)**: Caches UI state and handles optimistic updates.
3. **Application Layer (Tauri Commands in Rust)**: Receives IPC calls, validates input, and orchestrates domain logic.
4. **Domain Layer (Rust)**: Contains the Spaced Repetition logic (e.g., FSRS or SM-2).
5. **Infrastructure Layer (Rust + SQLite)**: Executes SQL queries and handles disk I/O.

