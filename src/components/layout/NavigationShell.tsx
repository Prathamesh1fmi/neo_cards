import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { StatusBar } from "./StatusBar";
import { CommandPalette } from "./CommandPalette";
import { TitleBar } from "./TitleBar";

export function NavigationShell() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <>
      <TitleBar />
      <div className="flex h-screen w-full bg-background text-foreground overflow-hidden pt-10">
        <Sidebar isOpen={sidebarOpen} toggle={() => setSidebarOpen(!sidebarOpen)} />
        <div className="flex flex-1 flex-col overflow-hidden relative">
        <TopBar toggleSidebar={() => setSidebarOpen(!sidebarOpen)} sidebarOpen={sidebarOpen} />
        <main className="flex-1 overflow-auto bg-muted/20 relative">
          <Outlet />
        </main>
        <StatusBar />
      </div>
      <CommandPalette />
    </div>
    </>
  );
}