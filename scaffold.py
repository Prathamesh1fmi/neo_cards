import os
import json
from pathlib import Path

base = Path('.')

dirs = [
    'src/assets',
    'src/features/decks',
    'src/features/study',
    'src/features/browser',
    'src/components/ui',
    'src/components/layout',
    'src/components/theme',
    'src/hooks',
    'src/store',
    'src/lib',
    'src/types',
    'src/router',
    'src/db',
    'src/tests',
    'src-tauri/src/db',
    'src-tauri/src/commands',
    'src-tauri/src/domain',
    'src-tauri/src/infrastructure',
    'docs',
    'plugins',
    '.husky'
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

# 1. package.json
package_json = {
  "name": "neocards",
  "private": True,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \\"src/**/*.{ts,tsx,css}\\"",
    "preview": "vite preview",
    "tauri": "tauri",
    "test": "vitest run",
    "test:e2e": "playwright test",
    "prepare": "husky install"
  },
  "dependencies": {
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-toast": "^1.1.5",
    "@tauri-apps/api": "^1.5.3",
    "@tanstack/react-query": "^5.28.4",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "framer-motion": "^11.0.24",
    "lucide-react": "^0.364.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.51.2",
    "react-router-dom": "^6.22.3",
    "recharts": "^2.12.3",
    "tailwind-merge": "^2.2.2",
    "tailwindcss-animate": "^1.0.7",
    "zod": "^3.22.4",
    "zustand": "^4.5.2"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^1.5.11",
    "@types/node": "^20.12.2",
    "@types/react": "^18.2.73",
    "@types/react-dom": "^18.2.23",
    "@typescript-eslint/eslint-plugin": "^7.5.0",
    "@typescript-eslint/parser": "^7.5.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.19",
    "eslint": "^8.57.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.6",
    "husky": "^9.0.11",
    "lint-staged": "^15.2.2",
    "postcss": "^8.4.38",
    "prettier": "^3.2.5",
    "prettier-plugin-tailwindcss": "^0.5.13",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.3",
    "vite": "^5.2.7",
    "vitest": "^1.4.0",
    "@playwright/test": "^1.42.1"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
(base / 'package.json').write_text(json.dumps(package_json, indent=2))

# 2. tsconfig.json
(base / 'tsconfig.json').write_text('''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}''')

(base / 'tsconfig.node.json').write_text('''{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}''')

# 3. vite.config.ts
(base / 'vite.config.ts').write_text('''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
  },
  envPrefix: ['VITE_', 'TAURI_'],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});''')

# 4. tailwind.config.js
(base / 'tailwind.config.js').write_text('''/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}''')

# 5. postcss.config.js
(base / 'postcss.config.js').write_text('''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}''')

# 6. Global CSS
(base / 'src/index.css').write_text('''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 240 10% 3.9%;
    --primary: 240 5.9% 10%;
    --primary-foreground: 0 0% 98%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 240 5.9% 10%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 240 10% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground font-sans antialiased selection:bg-primary/20;
  }
}''')

# 7. Utils (shadcn)
(base / 'src/lib/utils.ts').write_text('''import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}''')

# 8. src-tauri scaffolding
(base / 'src-tauri/Cargo.toml').write_text('''[package]
name = "neocards"
version = "0.1.0"
description = "A local-first learning platform"
authors = ["NeoCards Team"]
edition = "2021"

[build-dependencies]
tauri-build = { version = "1.5", features = [] }

[dependencies]
tauri = { version = "1.5", features = ["shell-open"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
rusqlite = { version = "0.31.0", features = ["bundled"] }

[features]
custom-protocol = ["tauri/custom-protocol"]
''')

(base / 'src-tauri/tauri.conf.json').write_text('''{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:1420",
    "distDir": "../dist",
    "withGlobalTauri": false
  },
  "package": {
    "productName": "NeoCards",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "shell": {
        "all": false,
        "open": true
      }
    },
    "bundle": {
      "active": true,
      "targets": "all",
      "identifier": "com.neocards.dev",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ]
    },
    "security": {
      "csp": null
    },
    "windows": [
      {
        "fullscreen": false,
        "resizable": true,
        "title": "NeoCards",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600,
        "hiddenTitle": true,
        "titleBarStyle": "Overlay"
      }
    ]
  }
}''')

(base / 'src-tauri/src/main.rs').write_text('''// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod db;
mod commands;
mod domain;
mod infrastructure;

fn main() {
    tauri::Builder::default()
        .setup(|_app| {
            // DB Migration Placeholder
            db::migrations::run_migrations();
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}''')

(base / 'src-tauri/src/db/mod.rs').write_text('''pub mod migrations;''')
(base / 'src-tauri/src/db/migrations.rs').write_text('''pub fn run_migrations() {
    println!("Running SQLite migrations...");
    // TODO: Initialize Rusqlite pool and run PRAGMA user_version checks
}''')

# 9. React Router
(base / 'src/router/index.tsx').write_text('''import { createBrowserRouter } from "react-router-dom";
import { NavigationShell } from "@/components/layout/NavigationShell";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <NavigationShell />,
    children: [
      { path: "/", element: <div>Dashboard Placeholder</div> },
      { path: "/decks", element: <div>Decks Placeholder</div> },
      { path: "/review", element: <div>Review Engine Placeholder</div> },
      { path: "/browse", element: <div>Browser Placeholder</div> },
      { path: "/stats", element: <div>Statistics Placeholder</div> },
      { path: "/settings", element: <div>Settings Placeholder</div> },
      { path: "/plugins", element: <div>Plugins Placeholder</div> },
    ]
  }
]);''')

# 10. Navigation Shell
(base / 'src/components/layout/NavigationShell.tsx').write_text('''import { Outlet } from "react-router-dom";

export function NavigationShell() {
  return (
    <div className="flex h-screen bg-background text-foreground">
      <aside className="w-64 border-r border-border bg-card p-4 hidden md:flex flex-col">
        <h1 className="text-xl font-bold mb-8">NeoCards</h1>
        <nav className="space-y-2 flex-1">
          <div className="p-2 hover:bg-accent rounded-md cursor-pointer">Dashboard</div>
          <div className="p-2 hover:bg-accent rounded-md cursor-pointer">Decks</div>
          <div className="p-2 hover:bg-accent rounded-md cursor-pointer">Browse</div>
          <div className="p-2 hover:bg-accent rounded-md cursor-pointer">Stats</div>
        </nav>
        <div className="p-2 hover:bg-accent rounded-md cursor-pointer mt-auto">Settings</div>
      </aside>
      <main className="flex-1 overflow-auto p-8">
        <Outlet />
      </main>
    </div>
  );
}''')

# 11. Theme Provider
(base / 'src/components/theme/ThemeProvider.tsx').write_text('''import { createContext, useContext, useEffect, useState } from "react"

type Theme = "dark" | "light" | "system"
type ThemeProviderProps = { children: React.ReactNode; defaultTheme?: Theme; storageKey?: string }
type ThemeProviderState = { theme: Theme; setTheme: (theme: Theme) => void }

const initialState: ThemeProviderState = { theme: "system", setTheme: () => null }
const ThemeProviderContext = createContext<ThemeProviderState>(initialState)

export function ThemeProvider({ children, defaultTheme = "system", storageKey = "neocards-ui-theme", ...props }: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(() => (localStorage.getItem(storageKey) as Theme) || defaultTheme)

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove("light", "dark")
    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
      root.classList.add(systemTheme)
      return
    }
    root.classList.add(theme)
  }, [theme])

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
  }
  return <ThemeProviderContext.Provider {...props} value={value}>{children}</ThemeProviderContext.Provider>
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)
  if (context === undefined) throw new Error("useTheme must be used within a ThemeProvider")
  return context
}''')

# 12. App & Main
(base / 'src/App.tsx').write_text('''import { RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "@/components/theme/ThemeProvider";
import { router } from "@/router";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="neocards-theme">
        <RouterProvider router={router} />
      </ThemeProvider>
    </QueryClientProvider>
  );
}''')

(base / 'src/main.tsx').write_text('''import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);''')

(base / 'index.html').write_text('''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NeoCards</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>''')

# 13. UI Components placeholders
def make_ui_placeholder(name):
    return f'''import React from "react";\n\nexport function {name}() {{\n  return <div>{name} Component Placeholder</div>;\n}}'''

for c in ['Button', 'Input', 'Textarea', 'Card', 'Dialog', 'Dropdown', 'Modal', 'Toast', 'Skeleton']:
    (base / f'src/components/ui/{c}.tsx').write_text(make_ui_placeholder(c))

print("Scaffolding complete.")
