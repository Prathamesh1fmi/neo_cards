# NeoCards Architecture & Philosophy

## Core Identity
NeoCards is a production-grade native desktop application.
It is NOT a web application wrapped in Tauri.
The React application exists solely as the presentation layer.
Rust is the application core.
Tauri is the native application shell.
SQLite is the local database.

**The desktop application is the product.**

Every architectural decision should prioritize desktop software quality rather than web application patterns. The final deliverable is a native installer (.exe on Windows, with future support for macOS and Linux), not a website.

Users should never feel like they are interacting with a browser. The application should feel comparable to:
- VS Code
- Obsidian
- Linear Desktop
- Raycast
- Arc Browser
- Notion Desktop

Everything should behave like premium desktop software.

## Native Integration Guidelines
NeoCards is desktop software. Always prefer desktop-native solutions over browser-oriented solutions.

Use Tauri APIs whenever desktop functionality is required. 

Ensure the architecture supports and integrates:
- Multiple windows
- Native dialogs
- Native menus
- System tray
- Notifications
- Auto updates
- Global Keyboard shortcuts
- Drag and drop (native file drops)
- File associations
- Clipboard integration
- Window persistence (remembering size and position)
- Native file system access

## Constraints
- Never assume the application will be deployed as a website.
- The browser (WebView) is only used as the rendering engine.
- All heavy lifting, business logic, file I/O, and database operations MUST happen in Rust.
- React is strictly for rendering the state provided by Rust.

