"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  TrendingUp,
  IndianRupee,
  Calendar,
  ArrowUp,
  ArrowDown,
  Package,
  Users,
  Truck,
  ShoppingCart
} from 'lucide-react';
import { Farmer, Driver, MarketItem } from '@/data/mockData';

interface AnalyticsDashboardProps {
  farmers: Farmer[];
  drivers: Driver[];
  marketItems: MarketItem[];
}

export default function AnalyticsDashboard({ farmers, drivers, marketItems }: AnalyticsDashboardProps) {
  const totalRevenue = farmers.reduce((sum, farmer) => sum + farmer.totalEarnings, 0);
  const weeklyRevenue = 485000;
  const monthlyRevenue = 2150000;
  const revenueGrowth = 23.5;

  const totalTransactions = farmers.reduce((sum, farmer) => sum + farmer.history.length, 0);
  const avgTransactionValue = totalRevenue / totalTransactions;

  const topCrops = [
    { name: 'Alphonso Mangoes', revenue: 320000, volume: '800kg', growth: 45 },
    { name: 'Grapes', revenue: 287500, volume: '1,150kg', growth: 32 },
    { name: 'Onions', revenue: 252000, volume: '2,800kg', growth: -8 },
    { name: 'Tomatoes', revenue: 225000, volume: '1,500kg', growth: 18 },
    { name: 'Pomegranate', revenue: 200000, volume: '500kg', growth: 28 }
  ];

  const monthlyData = [
    { month: 'Aug', revenue: 1850000 },
    { month: 'Sep', revenue: 1920000 },
    { month: 'Oct', revenue: 1995000 },
    { month: 'Nov', revenue: 2080000 },
    { month: 'Dec', revenue: 2145000 },
    { month: 'Jan', revenue: 2150000 }
  ];

  const regionalPerformance = [
    { region: 'Pune', farmers: 3, revenue: 645000, avgRating: 4.7, share: 24 },
    { region: 'Nashik', farmers: 2, revenue: 607500, avgRating: 4.9, share: 23 },
    { region: 'Solapur', farmers: 1, revenue: 385000, avgRating: 5.0, share: 15 },
    { region: 'Kolhapur', farmers: 1, revenue: 290000, avgRating: 4.7, share: 11 },
    { region: 'Satara', farmers: 1, revenue: 180000, avgRating: 4.5, share: 7 },
    { region: 'Others', farmers: 2, revenue: 542500, avgRating: 4.7, share: 20 }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Revenue Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-emerald-500/20 to-emerald-500/5 border-emerald-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <IndianRupee className="h-4 w-4" />
              Total Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-emerald-500">₹{(totalRevenue / 100000).toFixed(2)}L</p>
            <div className="flex items-center gap-1 mt-1">
              <ArrowUp className="h-3 w-3 text-emerald-500" />
              <p className="text-xs text-emerald-500 font-semibold">{revenueGrowth}% growth</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/20 to-blue-500/5 border-blue-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-500">₹{(monthlyRevenue / 100000).toFixed(1)}L</p>
            <p className="text-xs text-zinc-500 mt-1">January 2026</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/20 to-purple-500/5 border-purple-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <ShoppingCart className="h-4 w-4" />
              Transactions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-500">{totalTransactions}</p>
            <p className="text-xs text-zinc-500 mt-1">All-time total</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500/20 to-orange-500/5 border-orange-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Avg Transaction
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-orange-500">₹{Math.round(avgTransactionValue).toLocaleString()}</p>
            <p className="text-xs text-zinc-500 mt-1">Per transaction</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Performing Crops */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Top Performing Crops
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {topCrops.map((crop, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-zinc-800/50 rounded-lg">
                <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <span className="text-lg font-bold text-emerald-500">#{index + 1}</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-white">{crop.name}</p>
                  <p className="text-xs text-zinc-400">{crop.volume} traded</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-emerald-500">₹{(crop.revenue / 1000).toFixed(0)}K</p>
                  <div className="flex items-center gap-1">
                    {crop.growth > 0 ? (
                      <>
                        <ArrowUp className="h-3 w-3 text-emerald-500" />
                        <span className="text-xs text-emerald-500">{crop.growth}%</span>
                      </>
                    ) : (
                      <>
                        <ArrowDown className="h-3 w-3 text-red-500" />
                        <span className="text-xs text-red-500">{Math.abs(crop.growth)}%</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Regional Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Regional Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {regionalPerformance.map((region, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-white">{region.region}</p>
                    <Badge variant="outline" className="text-xs">
                      {region.farmers} farmers
                    </Badge>
                  </div>
                  <p className="text-sm font-bold text-emerald-500">₹{(region.revenue / 1000).toFixed(0)}K</p>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-zinc-400">
                    <span>Market Share: {region.share}%</span>
                    <span>⭐ {region.avgRating}</span>
                  </div>
                  <div className="w-full bg-zinc-700 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full"
                      style={{ width: `${region.share * 4}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Monthly Trend */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Revenue Trend (Last 6 Months)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end justify-between h-64 gap-4">
            {monthlyData.map((data, index) => {
              const maxRevenue = Math.max(...monthlyData.map(d => d.revenue));
              const heightPercent = (data.revenue / maxRevenue) * 100;
              
              return (
                <div key={index} className="flex-1 flex flex-col items-center gap-2">
                  <div className="w-full flex flex-col items-center">
                    <p className="text-xs text-zinc-400 mb-1">
                      ₹{(data.revenue / 100000).toFixed(1)}L
                    </p>
                    <div
                      className="w-full bg-gradient-to-t from-emerald-500 to-emerald-300 rounded-t-lg transition-all hover:opacity-80 cursor-pointer"
                      style={{ height: `${heightPercent * 2}px` }}
                    />
                  </div>
                  <p className="text-sm font-semibold text-zinc-300">{data.month}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
