/**
 * useBackendData Hook
 * Fetches data from centralized MongoDB backend with fallback to mock data
 */

import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { FEATURE_FLAGS } from '@/lib/config';
import { 
  farmersData, 
  driversData, 
  marketItemsData, 
  wholesalersData,
  Farmer,
  Driver,
  MarketItem,
  Wholesaler
} from '@/data/mockData';

interface BackendDataState {
  farmers: Farmer[];
  drivers: Driver[];
  marketItems: MarketItem[];
  wholesalers: Wholesaler[];
  isLoading: boolean;
  isConnected: boolean;
  error: string | null;
}

export function useBackendData() {
  const [state, setState] = useState<BackendDataState>({
    farmers: [],
    drivers: [],
    marketItems: [],
    wholesalers: [],
    isLoading: true,
    isConnected: false,
    error: null,
  });

  // Fetch all data from backend
  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Check backend health first
      const healthCheck = await api.health();
      
      if (!healthCheck.success) {
        console.warn('⚠️ Backend not available, using mock data');
        setState({
          farmers: farmersData,
          drivers: driversData,
          marketItems: marketItemsData,
          wholesalers: wholesalersData,
          isLoading: false, 
          isConnected: false,
          error: 'Backend not available'
        });
        return;
      }

      // Fetch data in parallel from centralized MongoDB
      const [farmersRes, driversRes, pricesRes, wholesalersRes] = await Promise.all([
        api.farmers.getAll(),
        api.drivers.getAll(),
        api.prices.getAll(),
        api.wholesalers.getAll(),
      ]);

      // Extract data from responses
      const farmersFromDB = farmersRes.data?.data || [];
      const driversFromDB = driversRes.data?.data || [];
      const marketItemsFromDB = pricesRes.data?.data || [];
      const wholesalersFromDB = wholesalersRes.data?.data || [];

      setState({
        // Use database data if available, fallback to mock data
        farmers: farmersFromDB.length > 0 ? farmersFromDB : farmersData,
        drivers: driversFromDB.length > 0 ? driversFromDB : driversData,
        marketItems: marketItemsFromDB.length > 0 ? marketItemsFromDB : marketItemsData,
        wholesalers: wholesalersFromDB.length > 0 ? wholesalersFromDB : wholesalersData,
        isLoading: false,
        isConnected: true,
        error: null,
      });

      console.log('✅ Connected to Neural Roots Centralized Database');
      console.log(`   📊 Loaded: ${farmersFromDB.length} farmers, ${driversFromDB.length} drivers, ${marketItemsFromDB.length} market items, ${wholesalersFromDB.length} wholesalers`);
    } catch (error) {
      console.error('❌ Backend fetch error:', error);
      setState({
        farmers: farmersData,
        drivers: driversData,
        marketItems: marketItemsData,
        wholesalers: wholesalersData,
        isLoading: false,
        isConnected: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Update functions
  const setFarmers = useCallback((farmers: Farmer[] | ((prev: Farmer[]) => Farmer[])) => {
    setState(prev => ({
      ...prev,
      farmers: typeof farmers === 'function' ? farmers(prev.farmers) : farmers
    }));
  }, []);

  const setDrivers = useCallback((drivers: Driver[] | ((prev: Driver[]) => Driver[])) => {
    setState(prev => ({
      ...prev,
      drivers: typeof drivers === 'function' ? drivers(prev.drivers) : drivers
    }));
  }, []);

  const setMarketItems = useCallback((items: MarketItem[] | ((prev: MarketItem[]) => MarketItem[])) => {
    setState(prev => ({
      ...prev,
      marketItems: typeof items === 'function' ? items(prev.marketItems) : items
    }));
  }, []);

  const setWholesalers = useCallback((wholesalers: Wholesaler[] | ((prev: Wholesaler[]) => Wholesaler[])) => {
    setState(prev => ({
      ...prev,
      wholesalers: typeof wholesalers === 'function' ? wholesalers(prev.wholesalers) : wholesalers
    }));
  }, []);

  return {
    ...state,
    setFarmers,
    setDrivers,
    setMarketItems,
    setWholesalers,
    refetch: fetchData,
  };
}

export default useBackendData;
