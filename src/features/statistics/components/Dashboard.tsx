import React from 'react';
import { HeatmapChart } from './charts/HeatmapChart';
import { Activity, Brain, Target, Clock, Zap } from 'lucide-react';

export function Dashboard() {
  return (
    <div className="flex flex-col h-full w-full bg-background overflow-y-auto pt-8 pb-12 px-6 sm:px-12 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Intelligence</h1>
          <p className="text-sm text-muted-foreground mt-1">Your learning analytics and memory health.</p>
        </div>
        <div className="flex gap-2">
          <select className="bg-card border border-border text-sm rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary">
            <option>All Decks</option>
            <option>Biology</option>
            <option>Spanish</option>
          </select>
          <select className="bg-card border border-border text-sm rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary">
            <option>Last 30 Days</option>
            <option>This Year</option>
            <option>All Time</option>
          </select>
        </div>
      </div>

      {/* KPI Cards (Stripe Style) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard title="Total Reviews" value="14,205" trend="+12% this week" icon={<Activity size={16} />} />
        <MetricCard title="Retention Rate" value="87.5%" trend="Optimal range" icon={<Target size={16} />} />
        <MetricCard title="Current Streak" value="12 Days" trend="Longest: 45 days" icon={<Zap size={16} />} />
        <MetricCard title="Avg. Review Time" value="4.5s" trend="-0.2s this week" icon={<Clock size={16} />} />
      </div>

      {/* Main Charts Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-semibold mb-4">Review Heatmap</h3>
          <HeatmapChart />
        </div>
        
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm flex flex-col">
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Brain size={16} className="text-primary" /> FSRS Memory State
          </h3>
          <div className="flex-1 space-y-6 mt-2">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Estimated Retrievability</span>
                <span className="font-medium text-green-500">89.2%</span>
              </div>
              <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden"><div className="h-full bg-green-500 w-[89.2%]"></div></div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground mb-1">Avg. Stability</div>
                <div className="font-medium text-xl">21.5d</div>
              </div>
              <div>
                <div className="text-muted-foreground mb-1">Avg. Difficulty</div>
                <div className="font-medium text-xl">5.2</div>
              </div>
              <div>
                <div className="text-muted-foreground mb-1">Mature Cards</div>
                <div className="font-medium text-xl">450</div>
              </div>
              <div>
                <div className="text-muted-foreground mb-1">Young Cards</div>
                <div className="font-medium text-xl">120</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, trend, icon }: any) {
  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between text-muted-foreground mb-3">
        <span className="text-sm font-medium">{title}</span>
        {icon}
      </div>
      <div className="text-3xl font-semibold tracking-tight mb-1">{value}</div>
      <div className="text-xs text-muted-foreground">{trend}</div>
    </div>
  );
}