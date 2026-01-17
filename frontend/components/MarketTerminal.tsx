"use client"

import { useState } from 'react';
import { MarketItem } from '@/data/mockData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface MarketTerminalProps {
  marketItems: MarketItem[];
  onUpdateMarketItems: (items: MarketItem[]) => void;
}

export default function MarketTerminal({ marketItems, onUpdateMarketItems }: MarketTerminalProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const { toast } = useToast();

  const handlePriceClick = (item: MarketItem) => {
    setEditingId(item.id);
    setEditValue(item.price.toString());
  };

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditValue(e.target.value);
  };

  const handlePriceSubmit = (item: MarketItem) => {
    const newPrice = parseFloat(editValue);
    
    if (isNaN(newPrice) || newPrice <= 0) {
      toast({
        title: "❌ Invalid Price",
        description: "Please enter a valid price",
      });
      setEditingId(null);
      return;
    }

    const oldPrice = item.price;
    const newTrend: 'up' | 'down' = newPrice > oldPrice ? 'up' : 'down';

    const updatedItems = marketItems.map((i) =>
      i.id === item.id ? { ...i, price: newPrice, trend: newTrend } : i
    );

    onUpdateMarketItems(updatedItems);
    
    toast({
      title: "📢 Price Broadcasted!",
      description: `${item.cropName}: ₹${newPrice}/kg broadcasted to 150 farmers`,
    });

    setEditingId(null);
  };

  const handleKeyPress = (e: React.KeyboardEvent, item: MarketItem) => {
    if (e.key === 'Enter') {
      handlePriceSubmit(item);
    } else if (e.key === 'Escape') {
      setEditingId(null);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-white">Market Terminal</h3>
        <p className="text-sm text-zinc-400 mt-1">
          Live market prices · Click any price to edit
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {marketItems.map((item) => (
          <Card
            key={item.id}
            className={`relative overflow-hidden transition-all hover:scale-105 ${
              item.spoilageRisk === 'Critical' ? 'pulse-border border-2' : ''
            }`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">{item.cropName}</CardTitle>
                {item.trend === 'up' ? (
                  <TrendingUp className="h-5 w-5 text-emerald-500" />
                ) : (
                  <TrendingDown className="h-5 w-5 text-red-500" />
                )}
              </div>
              <p className="text-sm text-zinc-400">{item.mandiName}</p>
            </CardHeader>

            <CardContent className="space-y-3">
              {/* Price Display/Edit */}
              <div>
                <p className="text-xs text-zinc-500 mb-1">Price per kg</p>
                {editingId === item.id ? (
                  <Input
                    type="number"
                    value={editValue}
                    onChange={handlePriceChange}
                    onKeyDown={(e) => handleKeyPress(e, item)}
                    onBlur={() => handlePriceSubmit(item)}
                    autoFocus
                    className="text-3xl font-bold h-12 bg-zinc-800 border-emerald-500"
                  />
                ) : (
                  <p
                    className="text-3xl font-bold text-emerald-500 cursor-pointer hover:text-emerald-400 transition-colors"
                    onClick={() => handlePriceClick(item)}
                    title="Click to edit price"
                  >
                    ₹{item.price}
                  </p>
                )}
              </div>

              {/* Spoilage Risk Badge */}
              <div>
                <Badge
                  variant={item.spoilageRisk === 'Critical' ? 'destructive' : 'secondary'}
                  className={`w-full justify-center ${
                    item.spoilageRisk === 'Low'
                      ? 'bg-emerald-500/20 text-emerald-500'
                      : item.spoilageRisk === 'Medium'
                      ? 'bg-yellow-600/20 text-yellow-600'
                      : 'bg-red-500/20 text-red-500'
                  }`}
                >
                  {item.spoilageRisk === 'Critical' && (
                    <AlertTriangle className="h-3 w-3 mr-1" />
                  )}
                  {item.spoilageRisk} Risk
                </Badge>
              </div>
            </CardContent>

            {/* Animated gradient overlay for critical items */}
            {item.spoilageRisk === 'Critical' && (
              <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent pointer-events-none" />
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
