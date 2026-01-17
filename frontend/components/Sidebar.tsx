"use client"

import { LayoutDashboard, Map, Users, TrendingUp, Truck, BarChart3, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const navItems = [
    { id: 'command', label: 'Command Center', icon: LayoutDashboard },
    { id: 'fleet', label: 'Live Fleet', icon: Map },
    { id: 'transport', label: 'Transport Analytics', icon: Truck },
    { id: 'farmers', label: 'Farmer Network', icon: Users },
    { id: 'wholesalers', label: 'Wholesaler Network', icon: Building2 },
    { id: 'market', label: 'Market Terminal', icon: TrendingUp },
    { id: 'analytics', label: 'Analytics Dashboard', icon: BarChart3 },
  ];

  return (
    <div className="w-[250px] h-screen bg-zinc-900 border-r border-zinc-800 fixed left-0 top-0 flex flex-col">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-zinc-800">
        <h1 className="text-2xl font-bold text-emerald-500">NEURAL ROOTS 🌱</h1>
        <p className="text-xs text-zinc-500 mt-1">Middleman Supply Chain Platform</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? 'default' : 'ghost'}
              className={`w-full justify-start gap-3 ${
                isActive 
                  ? 'bg-emerald-500 text-white hover:bg-emerald-600' 
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800'
              }`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-800">
        <div className="text-xs text-zinc-500 space-y-1">
          <p className="font-semibold text-emerald-500">Professional Edition</p>
          <p>Version 2.0.0</p>
          <p>© 2026 Neural Roots</p>
        </div>
      </div>
    </div>
  );
}
