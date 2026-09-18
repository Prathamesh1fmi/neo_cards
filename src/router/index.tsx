import React from "react";
import { createBrowserRouter } from "react-router-dom";
import { NavigationShell } from "@/components/layout/NavigationShell";
import { Dashboard } from "@/pages/Dashboard";
import { Decks } from "@/pages/Decks";
import { Review } from "@/pages/Review";
import { Browse } from "@/pages/Browse";
import { Stats } from "@/pages/Stats";
import { Settings } from "@/pages/Settings";
import { Plugins } from "@/pages/Plugins";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <NavigationShell />,
    children: [
      { path: "/", element: <Dashboard /> },
      { path: "/decks", element: <Decks /> },
      { path: "/review", element: <Review /> },
      { path: "/browse", element: <Browse /> },
      { path: "/stats", element: <Stats /> },
      { path: "/settings", element: <Settings /> },
      { path: "/plugins", element: <Plugins /> },
    ]
  }
]);