"use client"

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { LiveActivityFeed } from '@/components/LiveActivityFeed';
import { 
  Users, 
  Truck, 
  TrendingUp, 
  IndianRupee,
  Package,
  MapPin,
  Activity,
  Clock,
  Building2
} from 'lucide-react';
import { Farmer, Driver, MarketItem, Wholesaler } from '@/data/mockData';

interface CommandCenterProps {
  farmers: Farmer[];
  drivers: Driver[];
  marketItems: MarketItem[];
  wholesalers?: Wholesaler[];
  onNavigate?: (tab: string, context?: any) => void;
}

export default function CommandCenter({ farmers, drivers, marketItems, wholesalers = [], onNavigate }: CommandCenterProps) {
  const [animatedRevenue, setAnimatedRevenue] = useState(0);
  const [animatedFarmers, setAnimatedFarmers] = useState(0);
  const [animatedDrivers, setAnimatedDrivers] = useState(0);
  const [animatedItems, setAnimatedItems] = useState(0);
  const [animatedWholesalers, setAnimatedWholesalers] = useState(0);
  const [isLive, setIsLive] = useState(true);
  const { toast } = useToast();

  const totalRevenue = farmers.reduce((sum, farmer) => sum + farmer.totalEarnings, 0);
  const connectedFarmers = farmers.filter(f => f.status === 'Connected').length;
  const availableDrivers = drivers.filter(d => d.status === 'Available').length;
  const criticalItems = marketItems.filter(m => m.spoilageRisk === 'Critical').length;
  const activeWholesalers = wholesalers.filter(w => w.status === 'Active').length;

  // Handler for activity clicks
  const handleActivityClick = (activity: any) => {
    if (!onNavigate) return;
    
    let destination = '';
    switch(activity.type) {
      case 'harvest':
        destination = 'Farmer Network';
        onNavigate('farmers');
        break;
      case 'logistics':
        destination = 'Live Fleet';
        onNavigate('fleet');
        break;
      case 'market':
        destination = 'Market Terminal';
        onNavigate('market');
        break;
      case 'delivery':
        destination = 'Transport Analytics';
        onNavigate('transport');
        break;
      case 'alert':
        destination = 'Market Terminal';
        onNavigate('market');
        break;
    }
    
    toast({
      title: "Navigating...",
      description: `Opening ${destination}`,
    });
  };

  // Handler for farmer clicks
  const handleFarmerClick = (farmer: Farmer) => {
    if (onNavigate) {
      onNavigate('farmers', { farmerId: farmer.id });
      toast({
        title: "Viewing Farmer",
        description: `Loading ${farmer.name}'s profile`,
      });
    }
  };

  // Handler for metric card clicks
  const handleMetricClick = (metric: string) => {
    if (!onNavigate) return;
    
    let destination = '';
    switch(metric) {
      case 'revenue':
        destination = 'Analytics Dashboard';
        onNavigate('analytics');
        break;
      case 'farmers':
        destination = 'Farmer Network';
        onNavigate('farmers');
        break;
      case 'wholesalers':
        destination = 'Wholesaler Network';
        onNavigate('wholesalers');
        break;
      case 'drivers':
        destination = 'Live Fleet';
        onNavigate('fleet');
        break;
      case 'items':
        destination = 'Market Terminal';
        onNavigate('market');
        break;
    }
    
    toast({
      title: "Navigating...",
      description: `Opening ${destination}`,
    });
  };

  // Animate numbers on mount
  useEffect(() => {
    const duration = 1000;
    const steps = 30;
    const stepDuration = duration / steps;

    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      
      setAnimatedRevenue(Math.floor(totalRevenue * progress));
      setAnimatedFarmers(Math.floor(connectedFarmers * progress));
      setAnimatedDrivers(Math.floor(availableDrivers * progress));
      setAnimatedItems(Math.floor(criticalItems * progress));
      setAnimatedWholesalers(Math.floor(activeWholesalers * progress));

      if (currentStep >= steps) {
        clearInterval(interval);
        setAnimatedRevenue(totalRevenue);
        setAnimatedFarmers(connectedFarmers);
        setAnimatedDrivers(availableDrivers);
        setAnimatedItems(criticalItems);
        setAnimatedWholesalers(activeWholesalers);
      }
    }, stepDuration);

    return () => clearInterval(interval);
  }, [totalRevenue, connectedFarmers, availableDrivers, criticalItems, activeWholesalers]);

  // Simulate live updates
  useEffect(() => {
    const liveInterval = setInterval(() => {
      setIsLive(prev => !prev);
    }, 2000);
    return () => clearInterval(liveInterval);
  }, []);

  const recentActivity = [
    { time: '2 mins ago', message: 'New harvest: 50kg Bananas listed in Jalgaon', type: 'harvest' },
    { time: '5 mins ago', message: 'Driver Amit Deshmukh assigned to Ramesh Patil', type: 'logistics' },
    { time: '8 mins ago', message: 'Price updated: Tomatoes ₹150/kg in Pune APMC', type: 'market' },
    { time: '12 mins ago', message: 'Delivery completed by Sunil Jadhav - 300kg Tomatoes', type: 'delivery' },
    { time: '15 mins ago', message: 'Alert: Spinach spoilage risk critical at Mumbai Wholesale', type: 'alert' },
    { time: '18 mins ago', message: 'Payment processed: ₹45,000 to Vikram Deshmukh', type: 'delivery' },
    { time: '22 mins ago', message: 'New order: 200kg Onions from Wholesaler B5', type: 'market' },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card 
          className="bg-gradient-to-br from-emerald-500/20 to-emerald-500/5 border-emerald-500/30 relative overflow-hidden cursor-pointer hover:scale-[1.02] transition-transform"
          onClick={() => handleMetricClick('revenue')}
        >
          <div className={`absolute top-2 right-2 w-2 h-2 rounded-full ${isLive ? 'bg-emerald-500' : 'bg-emerald-500/30'} transition-all duration-300`}></div>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <IndianRupee className="h-4 w-4" />
              Total Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-emerald-500 transition-all duration-300">
              ₹{(animatedRevenue / 100000).toFixed(1)}L
            </p>
            <p className="text-xs text-zinc-500 mt-1">Across all farmers</p>
          </CardContent>
        </Card>

        <Card 
          className="bg-gradient-to-br from-blue-500/20 to-blue-500/5 border-blue-500/30 relative overflow-hidden cursor-pointer hover:scale-[1.02] transition-transform"
          onClick={() => handleMetricClick('farmers')}
        >
          <div className={`absolute top-2 right-2 w-2 h-2 rounded-full ${isLive ? 'bg-blue-500' : 'bg-blue-500/30'} transition-all duration-300`}></div>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <Users className="h-4 w-4" />
              Active Farmers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-500 transition-all duration-300">
              {animatedFarmers}/{farmers.length}
            </p>
            <p className="text-xs text-zinc-500 mt-1">Connected to network</p>
          </CardContent>
        </Card>

        <Card 
          className="bg-gradient-to-br from-orange-500/20 to-orange-500/5 border-orange-500/30 relative overflow-hidden cursor-pointer hover:scale-[1.02] transition-transform"
          onClick={() => handleMetricClick('wholesalers')}
        >
          <div className={`absolute top-2 right-2 w-2 h-2 rounded-full ${isLive ? 'bg-orange-500' : 'bg-orange-500/30'} transition-all duration-300`}></div>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              Active Wholesalers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-orange-500 transition-all duration-300">
              {animatedWholesalers}/{wholesalers.length}
            </p>
            <p className="text-xs text-zinc-500 mt-1">Connected to network</p>
          </CardContent>
        </Card>

        <Card 
          className="bg-gradient-to-br from-purple-500/20 to-purple-500/5 border-purple-500/30 relative overflow-hidden cursor-pointer hover:scale-[1.02] transition-transform"
          onClick={() => handleMetricClick('drivers')}
        >
          <div className={`absolute top-2 right-2 w-2 h-2 rounded-full ${isLive ? 'bg-purple-500' : 'bg-purple-500/30'} transition-all duration-300`}></div>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <Truck className="h-4 w-4" />
              Available Drivers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-500 transition-all duration-300">
              {animatedDrivers}/{drivers.length}
            </p>
            <p className="text-xs text-zinc-500 mt-1">Ready for dispatch</p>
          </CardContent>
        </Card>

        <Card 
          className="bg-gradient-to-br from-red-500/20 to-red-500/5 border-red-500/30 relative overflow-hidden cursor-pointer hover:scale-[1.02] transition-transform"
          onClick={() => handleMetricClick('items')}
        >
          <div className={`absolute top-2 right-2 w-2 h-2 rounded-full ${isLive ? 'bg-red-500' : 'bg-red-500/30'} transition-all duration-300`}></div>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Critical Items
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-red-500 transition-all duration-300">
              {animatedItems}
            </p>
            <p className="text-xs text-zinc-500 mt-1">High spoilage risk</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live WhatsApp Activity Feed - Real-time from backend */}
        <LiveActivityFeed />

        {/* Top Performing Farmers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Top Performers
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {farmers
              .sort((a, b) => b.totalEarnings - a.totalEarnings)
              .slice(0, 5)
              .map((farmer, index) => (
                <div
                  key={farmer.id}
                  className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/50 hover:bg-zinc-700 transition-all cursor-pointer border border-transparent hover:border-blue-500/30"
                  onClick={() => handleFarmerClick(farmer)}
                >
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center text-white font-bold text-lg">
                      #{index + 1}
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500/30 to-emerald-500/30 border-2 border-emerald-500/50 flex items-center justify-center text-2xl">
                      👨‍🌾
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-white truncate">{farmer.name}</p>
                    <p className="text-xs text-zinc-500">{farmer.village}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-emerald-500">
                      ₹{(farmer.totalEarnings / 1000).toFixed(0)}K
                    </p>
                    <Badge className="bg-yellow-500/20 text-yellow-500 text-xs">
                      ⭐ {farmer.rating}
                    </Badge>
                  </div>
                </div>
              ))}
          </CardContent>
        </Card>
      </div>

      {/* Market Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Market Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {marketItems.slice(0, 6).map((item) => (
              <div
                key={item.id}
                className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-800"
              >
                <p className="text-xs text-zinc-400 mb-1">{item.cropName}</p>
                <p className="text-lg font-bold text-emerald-500">₹{item.price}</p>
                <Badge
                  variant="outline"
                  className={`text-xs mt-1 ${
                    item.trend === 'up' ? 'text-emerald-500' : 'text-red-500'
                  }`}
                >
                  {item.trend === 'up' ? '↑' : '↓'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
