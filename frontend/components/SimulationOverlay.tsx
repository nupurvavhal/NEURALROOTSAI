"use client"

import { useEffect } from 'react';
import { useToast } from '@/hooks/use-toast';

interface SimulationOverlayProps {
  onNavigate: (tab: string) => void;
}

const notifications = [
  { message: '🌾 New Harvest Alert: 50kg Bananas listed in Nashik', tab: 'farmers' },
  { message: '🚛 Driver reached destination: Tomato delivery complete', tab: 'fleet' },
  { message: '📈 Price Alert: Onions up by 15% in Pune Mandi', tab: 'market' },
  { message: '👨‍🌾 New farmer joined: Kiran Singh from Satara', tab: 'farmers' },
  { message: '⚠️ Spoilage Alert: 100kg Grapes need urgent pickup', tab: 'market' },
  { message: '✅ Payment processed: ₹45,000 to Meena Kumari', tab: 'farmers' },
  { message: '🗺️ Fleet update: 3 drivers available in your area', tab: 'fleet' },
  { message: '💰 Market surge: Mango prices increased to ₹420/kg', tab: 'market' },
];

export default function SimulationOverlay({ onNavigate }: SimulationOverlayProps) {
  const { toast } = useToast();

  useEffect(() => {
    const interval = setInterval(() => {
      const randomNotification = notifications[Math.floor(Math.random() * notifications.length)];
      
      toast({
        title: "System Notification",
        description: randomNotification.message,
        action: (
          <button
            onClick={() => onNavigate(randomNotification.tab)}
            className="text-emerald-500 hover:text-emerald-400 text-sm font-semibold"
          >
            View →
          </button>
        ),
      });
    }, 15000); // Every 15 seconds

    return () => clearInterval(interval);
  }, [toast, onNavigate]);

  return null; // This component doesn't render anything visible
}
