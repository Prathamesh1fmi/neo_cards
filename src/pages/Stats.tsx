import React, { useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { BrainCircuit, BarChart as BarChartIcon, CalendarDays } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';

export function Stats() {
  const [retentionData] = useState([
    { name: 'Learning', value: 20 },
    { name: 'Review', value: 75 },
    { name: 'Relearning', value: 5 },
  ]);

  const [dueData] = useState(() => 
    Array.from({ length: 30 }).map((_, i) => ({
      day: i,
      cards: Math.floor(Math.random() * 200) + 20
    }))
  );

  const COLORS = ['#eab308', '#22c55e', '#ef4444'];

  return (
    <PageContainer title="Workspace / Statistics">
      <div className="flex flex-col gap-6 p-2 h-full overflow-y-auto">
        
        {/* Top Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2 text-muted-foreground">
              <BrainCircuit size={18} />
              <h3 className="font-semibold text-sm uppercase">True Retention</h3>
            </div>
            <div className="text-3xl font-bold mt-4">91.4%</div>
            <div className="text-xs text-muted-foreground mt-2">Optimal FSRS Range (90.0%)</div>
          </div>
          
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2 text-muted-foreground">
              <BarChartIcon size={18} />
              <h3 className="font-semibold text-sm uppercase">Reviews past 30 days</h3>
            </div>
            <div className="text-3xl font-bold mt-4">4,291</div>
            <div className="text-xs text-muted-foreground mt-2">Average 143 reviews/day</div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2 text-muted-foreground">
              <CalendarDays size={18} />
              <h3 className="font-semibold text-sm uppercase">Total Time</h3>
            </div>
            <div className="text-3xl font-bold mt-4">24h 12m</div>
            <div className="text-xs text-muted-foreground mt-2">Average 48m/day</div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <div className="col-span-1 md:col-span-2 bg-card border border-border rounded-xl p-6 flex flex-col min-h-[350px]">
            <h3 className="font-semibold mb-6">Forecast (Next 30 Days)</h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dueData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }} />
                  <Tooltip 
                    cursor={{ fill: 'hsl(var(--accent))' }}
                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }}
                    formatter={(value: any) => [`${value} cards due`, 'Forecast']}
                    labelFormatter={(label) => `In ${label} days`}
                  />
                  <Bar dataKey="cards" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="col-span-1 bg-card border border-border rounded-xl p-6 flex flex-col min-h-[350px]">
            <h3 className="font-semibold mb-6">Card States</h3>
            <div className="flex-1 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={retentionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {retentionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }}
                    formatter={(value: any) => [`${value}%`, 'Share']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-4 text-xs font-medium text-muted-foreground">
              <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-yellow-500"></div> Learning</div>
              <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500"></div> Review</div>
              <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Relearning</div>
            </div>
          </div>

        </div>

      </div>
    </PageContainer>
  );
}