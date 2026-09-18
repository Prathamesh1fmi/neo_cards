import React from 'react';

// For Milestone 9, we scaffold the visual representation.
// In production, this uses an Area Chart or GitHub-style calendar SVG
export function HeatmapChart() {
  return (
    <div className="w-full h-[200px] flex items-center justify-center bg-muted/20 border border-dashed border-border rounded-md">
      <span className="text-sm text-muted-foreground">Heatmap / Chart rendering visualization goes here (via Rust pre-aggregated data)</span>
    </div>
  );
}