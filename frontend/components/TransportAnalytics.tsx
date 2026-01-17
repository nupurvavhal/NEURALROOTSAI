"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Truck, 
  Package, 
  Clock,
  MapPin,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  IndianRupee,
  Route,
  Fuel,
  Timer
} from 'lucide-react';
import { Driver } from '@/data/mockData';

interface TransportAnalyticsProps {
  drivers: Driver[];
}

export default function TransportAnalytics({ drivers }: TransportAnalyticsProps) {
  const activeDeliveries = 12;
  const completedToday = 28;
  const avgDeliveryTime = "45 mins";
  const totalDistance = "1,240 km";
  const fuelEfficiency = "12.5 km/L";
  const onTimeDelivery = "94%";

  const recentDeliveries = [
    {
      id: 'DEL001',
      driver: 'Amit Deshmukh',
      from: 'Nashik APMC',
      to: 'Reliance Fresh, Pune',
      cargo: '250kg Onions',
      status: 'In Transit',
      eta: '25 mins',
      distance: '42 km',
      progress: 65
    },
    {
      id: 'DEL002',
      driver: 'Sunil Jadhav',
      from: 'Pune Market',
      to: 'BigBasket Warehouse',
      cargo: '300kg Tomatoes',
      status: 'In Transit',
      eta: '15 mins',
      distance: '18 km',
      progress: 85
    },
    {
      id: 'DEL003',
      driver: 'Rahul More',
      from: 'Satara Farm',
      to: 'DMart, Mumbai',
      cargo: '150kg Mangoes',
      status: 'Completed',
      eta: 'Delivered',
      distance: '215 km',
      progress: 100
    },
    {
      id: 'DEL004',
      driver: 'Prakash Bhosale',
      from: 'Kolhapur APMC',
      to: 'Local Mandi, Pune',
      cargo: '400kg Potatoes',
      status: 'Pending Pickup',
      eta: 'Scheduled',
      distance: '98 km',
      progress: 0
    },
    {
      id: 'DEL005',
      driver: 'Santosh Kulkarni',
      from: 'Jalgaon Market',
      to: 'Reliance Fresh, Mumbai',
      cargo: '180kg Bananas',
      status: 'In Transit',
      eta: '35 mins',
      distance: '156 km',
      progress: 45
    }
  ];

  const vehicleStats = [
    { vehicle: 'Tata Ace', count: 3, active: 2, maintenance: 1 },
    { vehicle: 'Mahindra Pickup', count: 2, active: 2, maintenance: 0 },
    { vehicle: 'Tata 407', count: 2, active: 1, maintenance: 1 },
    { vehicle: 'Eicher Pro', count: 1, active: 1, maintenance: 0 }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500/20 to-blue-500/5 border-blue-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <Package className="h-4 w-4" />
              Active Deliveries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-500">{activeDeliveries}</p>
            <p className="text-xs text-zinc-500 mt-1">In transit now</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-500/20 to-emerald-500/5 border-emerald-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Completed Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-emerald-500">{completedToday}</p>
            <p className="text-xs text-zinc-500 mt-1">Deliveries successful</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/20 to-purple-500/5 border-purple-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Avg Delivery Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-500">{avgDeliveryTime}</p>
            <p className="text-xs text-zinc-500 mt-1">20% faster than target</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500/20 to-orange-500/5 border-orange-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              On-Time Delivery
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-orange-500">{onTimeDelivery}</p>
            <p className="text-xs text-zinc-500 mt-1">Excellent performance</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Deliveries */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Truck className="h-5 w-5" />
              Active Shipments
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {recentDeliveries.map((delivery) => (
              <Card key={delivery.id} className="bg-zinc-800/50">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-sm font-semibold text-white">{delivery.id}</p>
                      <p className="text-xs text-zinc-400">{delivery.driver}</p>
                    </div>
                    <Badge
                      className={
                        delivery.status === 'Completed'
                          ? 'bg-emerald-500'
                          : delivery.status === 'In Transit'
                          ? 'bg-blue-500'
                          : 'bg-yellow-600'
                      }
                    >
                      {delivery.status}
                    </Badge>
                  </div>

                  <div className="space-y-2 text-xs text-zinc-300">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-3 w-3 text-emerald-500" />
                      <span>{delivery.from}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="h-3 w-3 text-red-500" />
                      <span>{delivery.to}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Package className="h-3 w-3" />
                      <span>{delivery.cargo}</span>
                    </div>
                  </div>

                  <div className="mt-3 space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-zinc-400">Progress</span>
                      <span className="text-white font-semibold">{delivery.progress}%</span>
                    </div>
                    <div className="w-full bg-zinc-700 rounded-full h-2">
                      <div
                        className="bg-emerald-500 h-2 rounded-full transition-all"
                        style={{ width: `${delivery.progress}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-zinc-400">
                      <span>🕒 ETA: {delivery.eta}</span>
                      <span>📍 {delivery.distance}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>

        {/* Fleet & Performance Stats */}
        <div className="space-y-6">
          {/* Vehicle Fleet */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Truck className="h-5 w-5" />
                Fleet Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {vehicleStats.map((vehicle, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-white">{vehicle.vehicle}</p>
                    <p className="text-xs text-zinc-400">Total: {vehicle.count} units</p>
                  </div>
                  <div className="flex gap-4 text-xs">
                    <div className="text-center">
                      <p className="text-emerald-500 font-bold">{vehicle.active}</p>
                      <p className="text-zinc-500">Active</p>
                    </div>
                    <div className="text-center">
                      <p className="text-yellow-500 font-bold">{vehicle.maintenance}</p>
                      <p className="text-zinc-500">Service</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Route className="h-5 w-5" />
                Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                    <Route className="h-5 w-5 text-blue-500" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Total Distance</p>
                    <p className="text-xs text-zinc-400">Today</p>
                  </div>
                </div>
                <p className="text-xl font-bold text-blue-500">{totalDistance}</p>
              </div>

              <div className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Fuel className="h-5 w-5 text-emerald-500" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Fuel Efficiency</p>
                    <p className="text-xs text-zinc-400">Fleet average</p>
                  </div>
                </div>
                <p className="text-xl font-bold text-emerald-500">{fuelEfficiency}</p>
              </div>

              <div className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                    <Timer className="h-5 w-5 text-purple-500" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Avg Delivery Time</p>
                    <p className="text-xs text-zinc-400">This week</p>
                  </div>
                </div>
                <p className="text-xl font-bold text-purple-500">{avgDeliveryTime}</p>
              </div>

              <div className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center">
                    <IndianRupee className="h-5 w-5 text-orange-500" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Revenue Today</p>
                    <p className="text-xs text-zinc-400">From deliveries</p>
                  </div>
                </div>
                <p className="text-xl font-bold text-orange-500">₹45,600</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
