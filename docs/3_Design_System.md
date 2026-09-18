# Design System & Component Library

## 8. Design System

### Philosophy
Zero visual clutter. Content is king. The UI should fade away when studying.

### Typography
- **Primary Font**: `Inter` or system-native (`San Francisco` on macOS, `Segoe UI` on Windows) for UI elements.
- **Card Font**: User-configurable, defaulting to `Lora` or `Merriweather` for serif readability, or `Inter` for sans-serif.
- **Monospace**: `JetBrains Mono` or `Fira Code` for code snippets.

### Color Palette
- **Light Mode**: Off-white backgrounds (`#FAFAFA`), subtle gray borders (`#E5E5E5`), stark black text (`#111111`) for maximum contrast.
- **Dark Mode**: Deep OLED blacks (`#000000`) or very dark grays (`#121212`), muted text (`#A1A1AA`).
- **Accents**: A single primary accent color (e.g., a vibrant Blue or Violet) used exceedingly sparingly—only for primary calls to action or focus states.
- **Spaced Repetition Colors**: 
  - Again: `Red-500`
  - Hard: `Orange-500`
  - Good: `Green-500`
  - Easy: `Blue-500`

### Spacing & Layout
- 4px grid system (`0.25rem` in Tailwind).
- Generous padding around cards to draw the eye to the center.

### Animation Philosophy
Animations should be physics-based (springs), never linear.
- **Modals**: Scale up slightly (0.95 -> 1) with an opacity fade.
- **Cards**: Swiping/flipping should follow the user's velocity.

## 9. Component Library

### Primitive Components (shadcn/ui)
- `Button`: Primary, Secondary, Ghost, Destructive, Icon.
- `Input` / `Textarea`: Borderless variants for clean note-taking.
- `Dialog`: For settings and deck creation.
- `Command`: The global Command Palette (combobox).
- `DropdownMenu`: Context menus for decks and notes.
- `Tooltip`: Essential for keyboard shortcut hints.

### Domain Components
- `DeckListItem`: Displays deck name, due counts (red/green badges), and a subtle sparkline chart.
- `StudyCard`: The main flashcard view. Handles 3D flip animations or smooth scrolling.
- `RichTextEditor`: A tiptap or Lexical-based editor for creating cards with Markdown shortcuts.
- `Heatmap`: GitHub-style contribution graph for daily study activity.

