/**
 * useLiveActivity Hook
 * Real-time polling for WhatsApp messages, bookings, and driver updates
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { API_CONFIG } from '@/lib/config';

export interface WhatsAppMessage {
  _id: string;
  direction: 'incoming' | 'outgoing';
  from_number?: string;
  to_number?: string;
  profile_name?: string;
  message: string;
  timestamp: string;
  type?: string;
}

export interface Booking {
  _id: string;
  booking_id: string;
  farmer_id: string;
  farmer_name: string;
  farmer_phone: string;
  driver_id: string;
  driver_name: string;
  driver_phone: string;
  vehicle_type: string;
  pickup_location: string;
  destination_mandi: string;
  crop_type: string;
  quantity_kg: number;
  estimated_distance_km: number;
  estimated_cost: number;
  status: string;
  assigned_at: string;
  type?: string;
}

export interface ConversationState {
  _id: string;
  farmer_id: string;
  farmer_phone: string;
  current_step: string;
  selected_crop?: string;
  quantity_kg?: number;
  selected_mandi?: string;
  started_at: string;
  last_interaction: string;
  type?: string;
}

export interface DriverStatus {
  _id: string;
  id: string;
  name: string;
  phone: string;
  vehicleType: string;
  status: string;
  currentLoad?: string;
  location?: { lat: number; lng: number };
  type?: string;
}

export interface LiveActivityState {
  whatsappLogs: WhatsAppMessage[];
  bookings: Booking[];
  activeConversations: ConversationState[];
  drivers: DriverStatus[];
  isConnected: boolean;
  lastUpdated: string | null;
  error: string | null;
}

interface UseLiveActivityOptions {
  pollingInterval?: number;
  enabled?: boolean;
}

export function useLiveActivity(options: UseLiveActivityOptions = {}) {
  const { pollingInterval = 3000, enabled = true } = options;
  
  const [state, setState] = useState<LiveActivityState>({
    whatsappLogs: [],
    bookings: [],
    activeConversations: [],
    drivers: [],
    isConnected: false,
    lastUpdated: null,
    error: null,
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  const fetchLiveActivity = useCallback(async () => {
    if (!isMountedRef.current) return;

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/activity/live`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && isMountedRef.current) {
        setState({
          whatsappLogs: data.data.whatsapp_logs || [],
          bookings: data.data.bookings || [],
          activeConversations: data.data.active_conversations || [],
          drivers: data.data.drivers || [],
          isConnected: true,
          lastUpdated: data.data.timestamp || new Date().toISOString(),
          error: null,
        });
      }
    } catch (error) {
      if (isMountedRef.current) {
        setState(prev => ({
          ...prev,
          isConnected: false,
          error: error instanceof Error ? error.message : 'Connection failed',
        }));
      }
    }
  }, []);

  // Start polling
  useEffect(() => {
    isMountedRef.current = true;

    if (enabled) {
      // Initial fetch
      fetchLiveActivity();

      // Set up polling
      intervalRef.current = setInterval(fetchLiveActivity, pollingInterval);
    }

    return () => {
      isMountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, pollingInterval, fetchLiveActivity]);

  // Manual refresh
  const refresh = useCallback(() => {
    fetchLiveActivity();
  }, [fetchLiveActivity]);

  return {
    ...state,
    refresh,
  };
}
