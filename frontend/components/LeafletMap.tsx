"use client"

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Driver } from '@/data/mockData';

interface LeafletMapProps {
  drivers: Driver[];
  selectedDriver: Driver | null;
}

export default function LeafletMap({ drivers, selectedDriver }: LeafletMapProps) {
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<L.Marker[]>([]);

  // Initialize map once
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Create map
    mapRef.current = L.map(mapContainerRef.current, {
      center: [19.0760, 72.8777],
      zoom: 10,
      zoomControl: true,
    });

    // Add dark tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 19,
    }).addTo(mapRef.current);

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Update markers when drivers change
  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add new markers
    drivers.forEach((driver) => {
      const color = driver.status === 'Available' ? '#10b981' : '#ef4444';
      const icon = L.divIcon({
        html: `<div style="background-color: ${color}; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);">
          <span style="font-size: 18px;">🚚</span>
        </div>`,
        className: '',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      const marker = L.marker([driver.lat, driver.lng], { icon })
        .bindPopup(`
          <div style="color: #000; padding: 8px;">
            <h3 style="font-weight: bold; margin-bottom: 4px;">${driver.name}</h3>
            <p style="font-size: 12px; color: #666;">${driver.vehicleType}</p>
            <p style="font-size: 12px; margin-top: 4px;">
              <span style="padding: 2px 8px; background: ${color}; color: white; border-radius: 4px; font-size: 10px;">
                ${driver.status}
              </span>
            </p>
            <p style="font-size: 11px; margin-top: 4px;">📞 ${driver.phone}</p>
          </div>
        `)
        .addTo(mapRef.current);

      markersRef.current.push(marker);
    });
  }, [drivers]);

  // Fly to selected driver
  useEffect(() => {
    if (!mapRef.current || !selectedDriver) return;

    mapRef.current.flyTo([selectedDriver.lat, selectedDriver.lng], 14, {
      duration: 1.5,
    });
  }, [selectedDriver]);

  return (
    <div 
      ref={mapContainerRef} 
      style={{ 
        height: '100%', 
        width: '100%', 
        borderRadius: '8px',
        zIndex: 0 
      }}
      className="leaflet-container"
    />
  );
}
