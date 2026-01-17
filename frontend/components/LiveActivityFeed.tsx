/**
 * LiveActivityFeed Component
 * Real-time display of WhatsApp conversations, bookings, and driver activity
 */

'use client';

import React, { useState } from 'react';
import { useLiveActivity, WhatsAppMessage, Booking, ConversationState } from '@/hooks/useLiveActivity';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

// Icons (using text-based for simplicity)
const Icons = {
  whatsapp: '💬',
  booking: '📦',
  driver: '🚛',
  farmer: '🌾',
  refresh: '🔄',
  connected: '🟢',
  disconnected: '🔴',
  incoming: '📥',
  outgoing: '📤',
};

interface LiveActivityFeedProps {
  className?: string;
  compact?: boolean;
}

export function LiveActivityFeed({ className = '', compact = false }: LiveActivityFeedProps) {
  const {
    whatsappLogs,
    bookings,
    activeConversations,
    drivers,
    isConnected,
    lastUpdated,
    error,
    refresh,
  } = useLiveActivity({ pollingInterval: 3000 });

  const [activeTab, setActiveTab] = useState<'whatsapp' | 'bookings' | 'conversations'>('whatsapp');

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timestamp;
    }
  };

  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    } catch {
      return '';
    }
  };

  return (
    <Card className={`${className} bg-gray-900 border-gray-700`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
            {Icons.whatsapp} Live Activity Feed
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">
              {isConnected ? Icons.connected : Icons.disconnected}
              {isConnected ? ' Connected' : ' Disconnected'}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={refresh}
              className="text-gray-400 hover:text-white"
            >
              {Icons.refresh}
            </Button>
          </div>
        </div>
        {lastUpdated && (
          <p className="text-xs text-gray-500">
            Last updated: {formatTime(lastUpdated)}
          </p>
        )}
        {error && (
          <p className="text-xs text-red-400">{error}</p>
        )}
      </CardHeader>

      <CardContent className="pt-2">
        {/* Tab Navigation */}
        <div className="flex gap-1 mb-4 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('whatsapp')}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === 'whatsapp'
                ? 'text-green-400 border-b-2 border-green-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {Icons.whatsapp} WhatsApp ({whatsappLogs.length})
          </button>
          <button
            onClick={() => setActiveTab('bookings')}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === 'bookings'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {Icons.booking} Bookings ({bookings.length})
          </button>
          <button
            onClick={() => setActiveTab('conversations')}
            className={`px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === 'conversations'
                ? 'text-yellow-400 border-b-2 border-yellow-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {Icons.farmer} Active ({activeConversations.length})
          </button>
        </div>

        {/* Tab Content */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
          {activeTab === 'whatsapp' && (
            <WhatsAppLogsList logs={whatsappLogs} formatTime={formatTime} formatDate={formatDate} />
          )}
          {activeTab === 'bookings' && (
            <BookingsList bookings={bookings} formatTime={formatTime} />
          )}
          {activeTab === 'conversations' && (
            <ConversationsList conversations={activeConversations} />
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// WhatsApp Logs List
function WhatsAppLogsList({ 
  logs, 
  formatTime, 
  formatDate 
}: { 
  logs: WhatsAppMessage[]; 
  formatTime: (t: string) => string;
  formatDate: (t: string) => string;
}) {
  if (logs.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <p className="text-2xl mb-2">💬</p>
        <p>No WhatsApp messages yet</p>
        <p className="text-xs mt-1">Send "sell" to the WhatsApp bot to start</p>
      </div>
    );
  }

  return (
    <>
      {logs.map((log, index) => (
        <div
          key={log._id || index}
          className={`p-3 rounded-lg ${
            log.direction === 'incoming'
              ? 'bg-gray-800 border-l-4 border-green-500'
              : 'bg-gray-800/50 border-l-4 border-blue-500'
          }`}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs">
                  {log.direction === 'incoming' ? Icons.incoming : Icons.outgoing}
                </span>
                <span className="text-xs font-medium text-gray-300">
                  {log.direction === 'incoming' 
                    ? (log.profile_name || log.from_number || 'Farmer')
                    : 'Neural Roots Bot'
                  }
                </span>
                <Badge 
                  variant="outline" 
                  className={`text-xs ${
                    log.direction === 'incoming' 
                      ? 'border-green-500 text-green-400' 
                      : 'border-blue-500 text-blue-400'
                  }`}
                >
                  {log.direction}
                </Badge>
              </div>
              <p className="text-sm text-white whitespace-pre-wrap break-words">
                {log.message.length > 200 ? `${log.message.slice(0, 200)}...` : log.message}
              </p>
            </div>
            <div className="text-right flex-shrink-0">
              <p className="text-xs text-gray-500">{formatTime(log.timestamp)}</p>
              <p className="text-xs text-gray-600">{formatDate(log.timestamp)}</p>
            </div>
          </div>
        </div>
      ))}
    </>
  );
}

// Bookings List
function BookingsList({ 
  bookings, 
  formatTime 
}: { 
  bookings: Booking[]; 
  formatTime: (t: string) => string;
}) {
  if (bookings.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <p className="text-2xl mb-2">📦</p>
        <p>No bookings yet</p>
        <p className="text-xs mt-1">Complete a WhatsApp sale to see bookings</p>
      </div>
    );
  }

  return (
    <>
      {bookings.map((booking, index) => (
        <div
          key={booking._id || index}
          className="p-3 rounded-lg bg-gray-800 border-l-4 border-blue-500"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Badge className="bg-blue-600 text-white text-xs">
                  {booking.booking_id}
                </Badge>
                <Badge 
                  variant="outline" 
                  className={`text-xs ${
                    booking.status === 'assigned' ? 'border-yellow-500 text-yellow-400' :
                    booking.status === 'confirmed' ? 'border-green-500 text-green-400' :
                    booking.status === 'in_transit' ? 'border-blue-500 text-blue-400' :
                    'border-gray-500 text-gray-400'
                  }`}
                >
                  {booking.status}
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                <p className="text-gray-400">
                  {Icons.farmer} {booking.farmer_name}
                </p>
                <p className="text-gray-400">
                  {Icons.driver} {booking.driver_name}
                </p>
                <p className="text-gray-300">
                  🌾 {booking.quantity_kg}kg {booking.crop_type}
                </p>
                <p className="text-gray-300">
                  🏪 {booking.destination_mandi}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">{formatTime(booking.assigned_at)}</p>
              <p className="text-sm font-semibold text-green-400">₹{booking.estimated_cost}</p>
            </div>
          </div>
        </div>
      ))}
    </>
  );
}

// Active Conversations List
function ConversationsList({ conversations }: { conversations: ConversationState[] }) {
  if (conversations.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        <p className="text-2xl mb-2">🌾</p>
        <p>No active conversations</p>
        <p className="text-xs mt-1">Farmers chatting with the bot will appear here</p>
      </div>
    );
  }

  const stepLabels: Record<string, { label: string; color: string }> = {
    'idle': { label: 'Idle', color: 'gray' },
    'awaiting_crop': { label: 'Selecting Crop', color: 'yellow' },
    'awaiting_quantity': { label: 'Entering Quantity', color: 'blue' },
    'awaiting_mandi_choice': { label: 'Choosing Mandi', color: 'purple' },
    'awaiting_confirmation': { label: 'Confirming Order', color: 'green' },
  };

  return (
    <>
      {conversations.map((conv, index) => {
        const step = stepLabels[conv.current_step] || { label: conv.current_step, color: 'gray' };
        
        return (
          <div
            key={conv._id || index}
            className="p-3 rounded-lg bg-gray-800 border-l-4 border-yellow-500"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white">
                {Icons.farmer} {conv.farmer_phone}
              </span>
              <Badge 
                className={`text-xs bg-${step.color}-600`}
                style={{ 
                  backgroundColor: 
                    step.color === 'yellow' ? '#ca8a04' :
                    step.color === 'blue' ? '#2563eb' :
                    step.color === 'purple' ? '#9333ea' :
                    step.color === 'green' ? '#16a34a' : '#6b7280'
                }}
              >
                {step.label}
              </Badge>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs text-gray-400">
              {conv.selected_crop && (
                <span>🌾 {conv.selected_crop}</span>
              )}
              {conv.quantity_kg && (
                <span>📦 {conv.quantity_kg}kg</span>
              )}
              {conv.selected_mandi && (
                <span>🏪 {conv.selected_mandi}</span>
              )}
            </div>
          </div>
        );
      })}
    </>
  );
}

export default LiveActivityFeed;
