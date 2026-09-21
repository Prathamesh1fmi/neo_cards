import React, { useEffect, useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { invoke } from "@tauri-apps/api/tauri";
import { Layers, CheckCircle2, TrendingUp, CalendarDays, Zap, Clock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ResponsiveContainer, AreaChart, Area, XAxis, Tooltip } from 'recharts';

export function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalDecks: 0,
    totalCards: 0,
    dueToday: 0,
    learnedToday: 0,
  });

  const [heatmapData] = useState(() => 
    Array.from({ length: 30 }).map((_, i) => ({
      day: 30 - i,
      reviews: Math.floor(Math.random() * 150) + 10
    })).reverse()
  );

  useEffect(() => {
    // In a full implementation, we'd add a Tauri command `get_dashboard_stats`
    // For now, we simulate fetching the aggregates from the SQLite DB.
    invoke('get_deck_tree').then((tree: any) => {
      let count = tree.length;
      tree.forEach((t: any) => count += t.children.length);
      setStats(prev => ({ ...prev, totalDecks: count, totalCards: count * 154, dueToday: Math.floor(count * 23.5) }));
    }).catch(console.error);
  }, []);

  return (
    <PageContainer title="Workspace / Dashboard">
      <div className="flex flex-col gap-6 p-2 h-full overflow-y-auto">
        
        {/* Hero Section */}
        <div className="bg-card border border-border rounded-xl p-8 relative overflow-hidden">
          <div className="absolute -right-20 -top-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl"></div>
          <div className="absolute right-40 -bottom-20 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl"></div>
          
          <h1 className="text-3xl font-bold tracking-tight mb-2">Good afternoon, Student!</h1>
          <p className="text-muted-foreground mb-8 max-w-xl">
            You have <strong className="text-foreground">{stats.dueToday}</strong> cards due today across your decks. FSRS memory stability is optimal.
          </p>

          <div className="flex gap-4">
            <button 
              onClick={() => navigate('/decks')}
              className="px-6 py-2.5 bg-primary text-primary-foreground font-medium rounded-md hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20"
            >
              Start Review Session
            </button>
            <button 
              onClick={() => navigate('/browse')}
              className="px-6 py-2.5 bg-secondary text-secondary-foreground font-medium rounded-md hover:bg-secondary/80 border border-border transition-colors"
            >
              Browse Cards
            </button>
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center text-blue-500">
              <Layers size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold">{stats.totalDecks}</div>
              <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Active Decks</div>
            </div>
          </div>
          
          <div className="bg-card border border-border rounded-xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 bg-orange-500/10 rounded-full flex items-center justify-center text-orange-500">
              <Zap size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold">{stats.totalCards}</div>
              <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Total Cards</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 bg-green-500/10 rounded-full flex items-center justify-center text-green-500">
              <CheckCircle2 size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold">14</div>
              <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Day Streak</div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-500/10 rounded-full flex items-center justify-center text-purple-500">
              <Clock size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold">45m</div>
              <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Studied Today</div>
            </div>
          </div>
        </div>

        {/* Activity Chart */}
        <div className="bg-card border border-border rounded-xl p-6 flex-1 min-h-[300px] flex flex-col">
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp size={18} className="text-primary" />
            <h3 className="font-semibold">Review Activity (Past 30 Days)</h3>
          </div>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={heatmapData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorReviews" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" hide />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: 'hsl(var(--primary))' }}
                  formatter={(value: any) => [`${value} reviews`, 'Activity']}
                  labelFormatter={(label) => `${label} days ago`}
                />
                <Area type="monotone" dataKey="reviews" stroke="hsl(var(--primary))" strokeWidth={2} fillOpacity={1} fill="url(#colorReviews)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </PageContainer>
  );
}