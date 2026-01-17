"use client"

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import CommandCenter from '@/components/CommandCenter';
import FarmersModule from '@/components/FarmersModule';
import MarketTerminal from '@/components/MarketTerminal';
import TransportAnalytics from '@/components/TransportAnalytics';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import WholesalersModule from '@/components/WholesalersModule';
import SimulationOverlay from '@/components/SimulationOverlay';
import { useLocalStorage } from '@/hooks/useLocalStorage';
import { farmersData, driversData, marketItemsData, wholesalersData, Farmer, Driver, MarketItem, Wholesaler } from '@/data/mockData';

// Dynamic import for FleetModule to avoid SSR issues with Leaflet
const FleetModule = dynamic(() => import('@/components/FleetModule'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-[calc(100vh-120px)]">
      <p className="text-zinc-400">Loading map...</p>
    </div>
  ),
});

export default function Home() {
  const [activeTab, setActiveTab] = useState('command');
  const [farmers, setFarmers, farmersLoaded] = useLocalStorage<Farmer[]>('farmers', farmersData);
  const [drivers, setDrivers, driversLoaded] = useLocalStorage<Driver[]>('drivers', driversData);
  const [marketItems, setMarketItems, marketLoaded] = useLocalStorage<MarketItem[]>('marketItems', marketItemsData);
  const [wholesalers, setWholesalers, wholesalersLoaded] = useLocalStorage<Wholesaler[]>('wholesalers', wholesalersData);

  const isDataLoaded = farmersLoaded && driversLoaded && marketLoaded && wholesalersLoaded;

  const pageTitles: Record<string, string> = {
    command: 'Command Center',
    fleet: 'Live Fleet Tracking',
    transport: 'Transport Analytics',
    farmers: 'Farmer Network',
    wholesalers: 'Wholesaler Network',
    market: 'Market Terminal',
    analytics: 'Analytics Dashboard',
  };

  const handleNavigate = (tab: string) => {
    setActiveTab(tab);
  };

  // Show loading state while data is being loaded from localStorage
  if (!isDataLoaded) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-950">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-emerald-500 border-r-transparent mb-4"></div>
          <p className="text-zinc-400">Initializing Neural Roots🌱 Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-zinc-950 text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 ml-[250px] flex flex-col overflow-hidden">
        {/* Header */}
        <Header pageTitle={pageTitles[activeTab]} />

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto">
          {activeTab === 'command' && (
            <CommandCenter 
              farmers={farmers} 
              drivers={drivers} 
              marketItems={marketItems} 
              wholesalers={wholesalers}
              onNavigate={handleNavigate}
            />
          )}
          {activeTab === 'fleet' && (
            <FleetModule drivers={drivers} onUpdateDrivers={setDrivers} />
          )}
          {activeTab === 'transport' && (
            <TransportAnalytics drivers={drivers} />
          )}
          {activeTab === 'farmers' && <FarmersModule farmers={farmers} />}
          {activeTab === 'wholesalers' && <WholesalersModule wholesalers={wholesalers} />}
          {activeTab === 'market' && (
            <MarketTerminal marketItems={marketItems} onUpdateMarketItems={setMarketItems} />
          )}
          {activeTab === 'analytics' && (
            <AnalyticsDashboard farmers={farmers} drivers={drivers} marketItems={marketItems} />
          )}
        </main>
      </div>

      {/* Background Simulation */}
      <SimulationOverlay onNavigate={handleNavigate} />
    </div>
  );
}
