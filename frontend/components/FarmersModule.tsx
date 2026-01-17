"use client"

import { useState } from 'react';
import { Farmer } from '@/data/mockData';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Star, IndianRupee, Package, TrendingUp } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface FarmersModuleProps {
  farmers: Farmer[];
}

export default function FarmersModule({ farmers }: FarmersModuleProps) {
  const [selectedFarmer, setSelectedFarmer] = useState<Farmer | null>(null);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const { toast } = useToast();

  const handleRowClick = (farmer: Farmer) => {
    setSelectedFarmer(farmer);
    setIsSheetOpen(true);
  };

  const handleAssignLogistics = () => {
    toast({
      title: "🔍 Searching for drivers...",
      description: `Finding nearby drivers for ${selectedFarmer?.name}`,
    });
    
    setTimeout(() => {
      toast({
        title: "✅ Driver Assigned!",
        description: "Driver will reach in 15 minutes",
      });
    }, 2000);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-white">Farmer Network</h3>
        <p className="text-sm text-zinc-400 mt-1">
          {farmers.length} farmers connected · Click any row for details
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Village</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead className="text-right">Total Earnings</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {farmers.map((farmer) => (
                <TableRow
                  key={farmer.id}
                  className="cursor-pointer hover:bg-zinc-800/50"
                  onClick={() => handleRowClick(farmer)}
                >
                  <TableCell className="font-medium">{farmer.name}</TableCell>
                  <TableCell className="text-zinc-400">{farmer.village}</TableCell>
                  <TableCell>
                    <Badge
                      variant={farmer.status === 'Connected' ? 'default' : 'secondary'}
                      className={
                        farmer.status === 'Connected'
                          ? 'bg-emerald-500'
                          : 'bg-yellow-600'
                      }
                    >
                      {farmer.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                      <span className="text-sm font-medium">{farmer.rating}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-semibold text-emerald-500">
                    ₹{farmer.totalEarnings.toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Drill-Down Sheet */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent className="w-[500px] overflow-y-auto">
          {selectedFarmer && (
            <>
              <SheetHeader>
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-16 h-16 rounded-full border-2 border-emerald-500 bg-gradient-to-br from-emerald-500/20 to-blue-500/20 flex items-center justify-center text-3xl">
                    👨‍🌾
                  </div>
                  <div>
                    <SheetTitle className="text-2xl">{selectedFarmer.name}</SheetTitle>
                    <SheetDescription>{selectedFarmer.village}</SheetDescription>
                  </div>
                </div>
              </SheetHeader>

              {/* Performance Stats */}
              <div className="mt-6 space-y-4">
                <h4 className="text-lg font-semibold text-white">Performance Stats</h4>
                
                <div className="grid grid-cols-2 gap-3">
                  <Card className="bg-zinc-800/50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
                        <IndianRupee className="h-4 w-4" />
                        Total Revenue
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-emerald-500">
                        ₹{selectedFarmer.totalEarnings.toLocaleString()}
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="bg-zinc-800/50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        Crops Sold
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-white">
                        {selectedFarmer.history.length}
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="bg-zinc-800/50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
                        <Star className="h-4 w-4" />
                        Rating
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-2xl font-bold text-yellow-500">
                        {selectedFarmer.rating}/5.0
                      </p>
                    </CardContent>
                  </Card>

                  <Card className="bg-zinc-800/50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm text-zinc-400 flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Status
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge
                        className={
                          selectedFarmer.status === 'Connected'
                            ? 'bg-emerald-500'
                            : 'bg-yellow-600'
                        }
                      >
                        {selectedFarmer.status}
                      </Badge>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Transaction History */}
              <div className="mt-6 space-y-4">
                <h4 className="text-lg font-semibold text-white">Transaction History</h4>
                
                <div className="space-y-3">
                  {selectedFarmer.history.slice(0, 3).map((transaction, index) => (
                    <Card key={index} className="bg-zinc-800/50">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-semibold text-white">{transaction.crop}</p>
                            <p className="text-sm text-zinc-400">
                              {transaction.amount} → {transaction.soldTo}
                            </p>
                            <p className="text-xs text-zinc-500 mt-1">{transaction.date}</p>
                          </div>
                          <p className="font-bold text-emerald-500">
                            ₹{transaction.revenue.toLocaleString()}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-6">
                <Button
                  className="w-full bg-emerald-500 hover:bg-emerald-600 text-white h-12 text-lg"
                  onClick={handleAssignLogistics}
                >
                  🚚 Assign Logistics
                </Button>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
