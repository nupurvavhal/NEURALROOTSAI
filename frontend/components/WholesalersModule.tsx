"use client"

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Wholesaler } from '@/data/mockData';
import { Building2, Phone, Star, TrendingUp, Package, CreditCard, FileText, ArrowUpRight, ArrowDownRight, Clock } from 'lucide-react';

interface WholesalersModuleProps {
  wholesalers: Wholesaler[];
}

export default function WholesalersModule({ wholesalers }: WholesalersModuleProps) {
  const [selectedWholesaler, setSelectedWholesaler] = useState<Wholesaler | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'Active' | 'Pending Verification' | 'Inactive'>('all');

  const filteredWholesalers = wholesalers.filter(w => {
    const matchesSearch = w.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         w.businessName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         w.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || w.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getTotalRevenue = (w: Wholesaler) => {
    return w.purchases.reduce((acc, p) => acc + (p.revenue || 0), 0);
  };

  const getTotalCost = (w: Wholesaler) => {
    return w.purchases.reduce((acc, p) => acc + p.cost, 0);
  };

  const getProfit = (w: Wholesaler) => {
    return getTotalRevenue(w) - getTotalCost(w);
  };

  const getProfitMargin = (w: Wholesaler) => {
    const cost = getTotalCost(w);
    const profit = getProfit(w);
    return cost > 0 ? ((profit / cost) * 100).toFixed(1) : '0';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-2">
            <Building2 className="h-8 w-8 text-emerald-500" />
            Wholesaler & Trader Network
          </h2>
          <p className="text-zinc-400 mt-1">
            Managing {wholesalers.length} wholesalers across Maharashtra
          </p>
        </div>

        {/* Stats Cards */}
        <div className="flex gap-4">
          <Card className="bg-zinc-900 border-zinc-800 p-4">
            <div className="text-xs text-zinc-500">Active Wholesalers</div>
            <div className="text-2xl font-bold text-emerald-500">
              {wholesalers.filter(w => w.status === 'Active').length}
            </div>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800 p-4">
            <div className="text-xs text-zinc-500">Total Orders</div>
            <div className="text-2xl font-bold text-blue-500">
              {wholesalers.reduce((acc, w) => acc + w.activeOrders, 0)}
            </div>
          </Card>
          <Card className="bg-zinc-900 border-zinc-800 p-4">
            <div className="text-xs text-zinc-500">Total Volume</div>
            <div className="text-2xl font-bold text-purple-500">
              ₹{(wholesalers.reduce((acc, w) => acc + w.totalVolume, 0) / 1000000).toFixed(1)}M
            </div>
          </Card>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <input
          type="text"
          placeholder="Search by name, business, or location..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
        />
        <div className="flex gap-2">
          {['all', 'Active', 'Pending Verification', 'Inactive'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filterStatus === status
                  ? 'bg-emerald-500 text-white'
                  : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
              }`}
            >
              {status === 'all' ? 'All' : status}
            </button>
          ))}
        </div>
      </div>

      {/* Wholesalers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredWholesalers.map((wholesaler) => (
          <Card
            key={wholesaler.id}
            className="bg-zinc-900 border-zinc-800 hover:border-emerald-500 transition-all cursor-pointer group"
            onClick={() => setSelectedWholesaler(wholesaler)}
          >
            <div className="p-6 space-y-4">
              {/* Header */}
              <div className="flex items-start gap-4">
                <img
                  src={wholesaler.photoUrl}
                  alt={wholesaler.name}
                  className="w-16 h-16 rounded-full border-2 border-emerald-500"
                />
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-white truncate group-hover:text-emerald-500 transition-colors">
                    {wholesaler.name}
                  </h3>
                  <p className="text-sm text-emerald-400 truncate font-medium">
                    {wholesaler.businessName}
                  </p>
                  <p className="text-xs text-zinc-500 flex items-center gap-1 mt-1">
                    <Building2 className="h-3 w-3" />
                    {wholesaler.location}
                  </p>
                </div>
              </div>

              {/* Status & Rating */}
              <div className="flex items-center justify-between">
                <Badge
                  variant={wholesaler.status === 'Active' ? 'default' : 'secondary'}
                  className={
                    wholesaler.status === 'Active'
                      ? 'bg-emerald-500/20 text-emerald-500'
                      : wholesaler.status === 'Pending Verification'
                      ? 'bg-yellow-500/20 text-yellow-500'
                      : 'bg-zinc-700 text-zinc-400'
                  }
                >
                  {wholesaler.status}
                </Badge>
                <div className="flex items-center gap-1 text-yellow-500">
                  <Star className="h-4 w-4 fill-yellow-500" />
                  <span className="font-bold">{wholesaler.rating}</span>
                </div>
              </div>

              {/* Specialization */}
              <div className="flex flex-wrap gap-1">
                {wholesaler.specialization.slice(0, 3).map((spec, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs border-zinc-700 text-zinc-400">
                    {spec}
                  </Badge>
                ))}
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-zinc-800">
                <div>
                  <div className="text-xs text-zinc-500 flex items-center gap-1">
                    <Package className="h-3 w-3" />
                    Active Orders
                  </div>
                  <div className="text-xl font-bold text-blue-500">{wholesaler.activeOrders}</div>
                </div>
                <div>
                  <div className="text-xs text-zinc-500 flex items-center gap-1">
                    <TrendingUp className="h-3 w-3" />
                    Total Volume
                  </div>
                  <div className="text-xl font-bold text-emerald-500">
                    ₹{(wholesaler.totalVolume / 1000).toFixed(0)}K
                  </div>
                </div>
                <div>
                  <div className="text-xs text-zinc-500 flex items-center gap-1">
                    <CreditCard className="h-3 w-3" />
                    Credit Limit
                  </div>
                  <div className="text-sm font-bold text-purple-500">
                    ₹{(wholesaler.creditLimit / 1000).toFixed(0)}K
                  </div>
                </div>
                <div>
                  <div className="text-xs text-zinc-500 flex items-center gap-1">
                    <TrendingUp className="h-3 w-3" />
                    Profit Margin
                  </div>
                  <div className="text-sm font-bold text-green-500">
                    {getProfitMargin(wholesaler)}%
                  </div>
                </div>
              </div>

              {/* Contact Info */}
              <div className="pt-4 border-t border-zinc-800">
                <div className="flex items-center gap-2 text-xs text-zinc-400">
                  <Phone className="h-3 w-3" />
                  {wholesaler.phone}
                </div>
                <div className="flex items-center gap-2 text-xs text-zinc-400 mt-1">
                  <FileText className="h-3 w-3" />
                  GST: {wholesaler.gstNumber}
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Detail Sheet */}
      <Sheet open={!!selectedWholesaler} onOpenChange={() => setSelectedWholesaler(null)}>
        <SheetContent className="w-full sm:max-w-2xl bg-zinc-950 border-zinc-800 overflow-y-auto">
          {selectedWholesaler && (
            <>
              <SheetHeader>
                <SheetTitle className="text-2xl font-bold text-white flex items-center gap-3">
                  <img
                    src={selectedWholesaler.photoUrl}
                    alt={selectedWholesaler.name}
                    className="w-12 h-12 rounded-full border-2 border-emerald-500"
                  />
                  <div>
                    <div>{selectedWholesaler.name}</div>
                    <div className="text-sm text-emerald-400 font-normal">
                      {selectedWholesaler.businessName}
                    </div>
                  </div>
                </SheetTitle>
              </SheetHeader>

              <div className="mt-6 space-y-6">
                {/* Business Info */}
                <Card className="bg-zinc-900 border-zinc-800 p-4">
                  <h3 className="text-lg font-semibold text-white mb-4">Business Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs text-zinc-500">Location</div>
                      <div className="text-sm text-white font-medium">{selectedWholesaler.location}</div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Status</div>
                      <Badge
                        variant={selectedWholesaler.status === 'Active' ? 'default' : 'secondary'}
                        className={
                          selectedWholesaler.status === 'Active'
                            ? 'bg-emerald-500/20 text-emerald-500'
                            : 'bg-yellow-500/20 text-yellow-500'
                        }
                      >
                        {selectedWholesaler.status}
                      </Badge>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Phone</div>
                      <div className="text-sm text-white font-medium">{selectedWholesaler.phone}</div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">GST Number</div>
                      <div className="text-sm text-white font-medium">{selectedWholesaler.gstNumber}</div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Rating</div>
                      <div className="flex items-center gap-1 text-yellow-500">
                        <Star className="h-4 w-4 fill-yellow-500" />
                        <span className="font-bold">{selectedWholesaler.rating}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Credit Limit</div>
                      <div className="text-sm text-purple-500 font-bold">
                        ₹{(selectedWholesaler.creditLimit / 1000).toFixed(0)}K
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Specialization */}
                <Card className="bg-zinc-900 border-zinc-800 p-4">
                  <h3 className="text-lg font-semibold text-white mb-3">Specialization</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedWholesaler.specialization.map((spec, idx) => (
                      <Badge key={idx} className="bg-emerald-500/20 text-emerald-500">
                        {spec}
                      </Badge>
                    ))}
                  </div>
                </Card>

                {/* Financial Summary */}
                <Card className="bg-zinc-900 border-zinc-800 p-4">
                  <h3 className="text-lg font-semibold text-white mb-4">Financial Summary</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs text-zinc-500">Total Cost</div>
                      <div className="text-xl font-bold text-red-500">
                        ₹{(getTotalCost(selectedWholesaler) / 1000).toFixed(0)}K
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Total Revenue</div>
                      <div className="text-xl font-bold text-green-500">
                        ₹{(getTotalRevenue(selectedWholesaler) / 1000).toFixed(0)}K
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Total Profit</div>
                      <div className="text-xl font-bold text-emerald-500">
                        ₹{(getProfit(selectedWholesaler) / 1000).toFixed(0)}K
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-zinc-500">Profit Margin</div>
                      <div className="text-xl font-bold text-blue-500">
                        {getProfitMargin(selectedWholesaler)}%
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Purchase History */}
                <Card className="bg-zinc-900 border-zinc-800 p-4">
                  <h3 className="text-lg font-semibold text-white mb-4">Purchase History</h3>
                  <div className="space-y-3">
                    {selectedWholesaler.purchases.map((purchase, idx) => (
                      <div
                        key={idx}
                        className="p-4 bg-zinc-800 rounded-lg border border-zinc-700 hover:border-emerald-500 transition-colors"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <h4 className="text-white font-semibold">{purchase.crop}</h4>
                            <p className="text-sm text-zinc-400">from {purchase.boughtFrom}</p>
                          </div>
                          <Badge
                            className={
                              purchase.status === 'Sold'
                                ? 'bg-green-500/20 text-green-500'
                                : purchase.status === 'In Transit'
                                ? 'bg-blue-500/20 text-blue-500'
                                : 'bg-yellow-500/20 text-yellow-500'
                            }
                          >
                            {purchase.status}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-zinc-500">Quantity: </span>
                            <span className="text-white font-medium">{purchase.quantity}</span>
                          </div>
                          <div>
                            <span className="text-zinc-500">Date: </span>
                            <span className="text-white font-medium">{purchase.date}</span>
                          </div>
                          <div>
                            <span className="text-zinc-500">Cost: </span>
                            <span className="text-red-500 font-bold">₹{purchase.cost.toLocaleString()}</span>
                          </div>
                          {purchase.revenue && (
                            <div>
                              <span className="text-zinc-500">Revenue: </span>
                              <span className="text-green-500 font-bold">₹{purchase.revenue.toLocaleString()}</span>
                            </div>
                          )}
                        </div>

                        {purchase.soldTo && (
                          <div className="mt-2 pt-2 border-t border-zinc-700">
                            <span className="text-xs text-zinc-500">Sold to: </span>
                            <span className="text-xs text-emerald-400 font-medium">{purchase.soldTo}</span>
                          </div>
                        )}

                        {purchase.revenue && (
                          <div className="mt-2 flex items-center gap-2">
                            {purchase.revenue > purchase.cost ? (
                              <ArrowUpRight className="h-4 w-4 text-green-500" />
                            ) : (
                              <ArrowDownRight className="h-4 w-4 text-red-500" />
                            )}
                            <span className={`text-sm font-bold ${
                              purchase.revenue > purchase.cost ? 'text-green-500' : 'text-red-500'
                            }`}>
                              Profit: ₹{(purchase.revenue - purchase.cost).toLocaleString()}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
