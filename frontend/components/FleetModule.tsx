"use client"

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Driver } from '@/data/mockData';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Phone } from 'lucide-react';

// Dynamically import map components to avoid SSR issues
const LeafletMap = dynamic<{ drivers: Driver[]; selectedDriver: Driver | null }>(
  () => import('./LeafletMap'),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full bg-zinc-900 rounded-lg">
        <p className="text-zinc-400">Loading map...</p>
      </div>
    ),
  }
);

interface FleetModuleProps {
  drivers: Driver[];
  onUpdateDrivers: (drivers: Driver[]) => void;
}

export default function FleetModule({ drivers, onUpdateDrivers }: FleetModuleProps) {
  const [selectedDriver, setSelectedDriver] = useState<Driver | null>(null);

  // Simulation: Update driver positions every 2 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      onUpdateDrivers(
        drivers.map((driver) => ({
          ...driver,
          lat: driver.lat + (Math.random() - 0.5) * 0.001,
          lng: driver.lng + (Math.random() - 0.5) * 0.001,
        }))
      );
    }, 2000);

    return () => clearInterval(interval);
  }, [drivers, onUpdateDrivers]);

  const handleDriverClick = (driver: Driver) => {
    setSelectedDriver(driver);
  };

  return (
    <div className="flex h-[calc(100vh-120px)]">
      {/* Left Side - Driver List (30%) */}
      <div className="w-[30%] border-r border-zinc-800 overflow-y-auto p-4 space-y-3">
        <h3 className="text-lg font-semibold text-white mb-4">Active Drivers ({drivers.length})</h3>
        
        {drivers.map((driver) => (
          <Card
            key={driver.id}
            className={`p-4 cursor-pointer transition-all hover:border-emerald-500 ${
              selectedDriver?.id === driver.id ? 'border-emerald-500 bg-emerald-500/10' : ''
            }`}
            onClick={() => handleDriverClick(driver)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-semibold text-white">{driver.name}</h4>
                <p className="text-sm text-zinc-400">{driver.vehicleType}</p>
              </div>
              <Badge
                variant={driver.status === 'Available' ? 'default' : 'secondary'}
                className={driver.status === 'Available' ? 'bg-emerald-500' : 'bg-red-500'}
              >
                {driver.status}
              </Badge>
            </div>
            
            <div className="mt-3 space-y-1">
              <p className="text-sm text-zinc-300">
                <span className="text-zinc-500">Load:</span> {driver.currentLoad}
              </p>
              <p className="text-xs text-zinc-400 flex items-center gap-1">
                <Phone className="h-3 w-3" />
                {driver.phone}
              </p>
            </div>
          </Card>
        ))}
      </div>

      {/* Right Side - Map (70%) */}
      <div className="w-[70%] relative" key="map-container">
        <LeafletMap drivers={drivers} selectedDriver={selectedDriver} />
      </div>
    </div>
  );
}
