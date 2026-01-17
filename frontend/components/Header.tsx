"use client"

import { Badge } from '@/components/ui/badge';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface HeaderProps {
  pageTitle: string;
}

export default function Header({ pageTitle }: HeaderProps) {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const result = await api.health();
        setBackendStatus(result.success ? 'connected' : 'disconnected');
      } catch {
        setBackendStatus('disconnected');
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="glass-header sticky top-0 z-10 px-8 py-4 flex items-center justify-between">
      <div>
        <h2 className="text-2xl font-bold text-white">{pageTitle}</h2>
        <p className="text-sm text-zinc-400 mt-1">Professional middleman supply chain platform</p>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Backend Connection Status */}
        <Badge className={`px-3 py-1 text-xs ${
          backendStatus === 'connected' 
            ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
            : backendStatus === 'checking'
            ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
            : 'bg-red-500/20 text-red-400 border-red-500/30'
        }`}>
          <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
            backendStatus === 'connected' ? 'bg-blue-400' : 
            backendStatus === 'checking' ? 'bg-yellow-400 animate-pulse' : 'bg-red-400'
          }`}></span>
          {backendStatus === 'connected' ? 'Backend Connected' : 
           backendStatus === 'checking' ? 'Connecting...' : 'Mock Data Mode'}
        </Badge>

        <Badge className="bg-emerald-500/20 text-emerald-500 border-emerald-500/30 px-4 py-2 text-sm">
          <span className="inline-block w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></span>
          System Online
        </Badge>
      </div>
    </header>
  );
}
