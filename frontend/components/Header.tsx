"use client"

import { Badge } from '@/components/ui/badge';

interface HeaderProps {
  pageTitle: string;
}

export default function Header({ pageTitle }: HeaderProps) {
  return (
    <header className="glass-header sticky top-0 z-10 px-8 py-4 flex items-center justify-between">
      <div>
        <h2 className="text-2xl font-bold text-white">{pageTitle}</h2>
        <p className="text-sm text-zinc-400 mt-1">Professional middleman supply chain platform</p>
      </div>
      
      <div className="flex items-center gap-4">
        <Badge className="bg-emerald-500/20 text-emerald-500 border-emerald-500/30 px-4 py-2 text-sm">
          <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></span>
          System Online
        </Badge>
      </div>
    </header>
  );
}
