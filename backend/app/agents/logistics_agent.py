# backend/app/agents/logistics_agent.py
"""
Logistics Agent - Provides driver information and delivery optimization
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class LogisticsAgent:
    """
    Manages driver information and logistics optimization.
    Considers freshness requirements when planning deliveries.
    """
    
    def __init__(self):
        self.delivery_modes = {
            "cold_chain": {"priority": "HIGH", "temp_control": True, "cost_multiplier": 1.5},
            "refrigerated": {"priority": "MEDIUM", "temp_control": True, "cost_multiplier": 1.3},
            "standard": {"priority": "LOW", "temp_control": False, "cost_multiplier": 1.0}
        }
    
    async def get_available_drivers(
        self,
        db,
        location: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        freshness_requirement: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch available drivers from MongoDB drivers collection
        
        Args:
            db: MongoDB database instance
            location: Optional location filter
            vehicle_type: Optional vehicle type (refrigerated, standard, etc.)
            freshness_requirement: Required temperature control level
        
        Returns:
            Dict with available drivers and their details
        """
        try:
            query = {"status": "available"}
            
            if location:
                query["location"] = location
            
            if vehicle_type:
                query["vehicle_type"] = vehicle_type
            
            # Match freshness requirement with vehicle capability
            if freshness_requirement:
                capability_query = self._get_capability_query(freshness_requirement)
                query.update(capability_query)
            
            drivers = await db.drivers.find(query).to_list(50)
            
            if not drivers:
                return {
                    "status": "no_drivers",
                    "drivers": [],
                    "message": "No available drivers matching criteria"
                }
            
            # Convert ObjectIds to strings
            for driver in drivers:
                driver["_id"] = str(driver["_id"])
            
            return {
                "status": "success",
                "drivers_count": len(drivers),
                "drivers": drivers,
                "total_capacity": sum([d.get("capacity", 0) for d in drivers])
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "drivers": []
            }
    
    async def recommend_delivery_mode(
        self,
        freshness_score: float,
        freshness_level: str,
        distance_km: float,
        quantity: float,
        availability_window_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Recommend delivery mode based on freshness and logistics requirements
        
        Args:
            freshness_score: Score from FreshnessAgent (0-100)
            freshness_level: Level from FreshnessAgent (EXCELLENT, GOOD, FAIR, POOR, CRITICAL)
            distance_km: Distance to delivery location
            quantity: Quantity to be delivered
            availability_window_hours: Hours until delivery must be completed
        
        Returns:
            Dict with delivery mode recommendation
        """
        
        # Determine required delivery mode based on freshness
        if freshness_level in ["POOR", "CRITICAL"]:
            required_mode = "cold_chain"
            urgency = "IMMEDIATE"
        elif freshness_level == "FAIR":
            required_mode = "refrigerated"
            urgency = "HIGH"
        elif freshness_level == "GOOD":
            required_mode = "refrigerated"
            urgency = "NORMAL"
        else:  # EXCELLENT
            required_mode = "standard"
            urgency = "NORMAL"
        
        # Calculate estimated delivery time based on distance
        # Assume average speed: cold_chain 60km/h, refrigerated 70km/h, standard 80km/h
        speed_map = {"cold_chain": 60, "refrigerated": 70, "standard": 80}
        estimated_hours = distance_km / speed_map.get(required_mode, 70)
        
        # Check if delivery is feasible
        feasible = True
        feasibility_notes = []
        
        if availability_window_hours and estimated_hours > availability_window_hours:
            feasible = False
            feasibility_notes.append(f"Estimated delivery time {estimated_hours:.1f}h exceeds window")
        
        if freshness_score < 20 and estimated_hours > 6:
            feasible = False
            feasibility_notes.append("Freshness critical - delivery must be within 6 hours")
        
        # Calculate estimated cost
        base_cost = (distance_km * 0.5) + (quantity * 0.1)
        cost_multiplier = self.delivery_modes[required_mode]["cost_multiplier"]
        total_cost = base_cost * cost_multiplier
        
        return {
            "status": "success",
            "recommended_delivery_mode": required_mode,
            "urgency": urgency,
            "feasible": feasible,
            "feasibility_notes": feasibility_notes,
            "delivery_details": {
                "distance_km": distance_km,
                "estimated_delivery_hours": round(estimated_hours, 2),
                "estimated_cost": round(total_cost, 2),
                "temperature_controlled": self.delivery_modes[required_mode]["temp_control"]
            },
            "alternative_modes": self._get_alternative_modes(required_mode)
        }
    
    async def optimize_delivery_route(
        self,
        drivers: List[Dict],
        shipment_info: Dict[str, Any],
        delivery_location: str,
        num_stops: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Optimize delivery route considering driver availability and shipment requirements
        
        Args:
            drivers: List of available drivers
            shipment_info: Shipment details (freshness, quantity, etc.)
            delivery_location: Target delivery location
            num_stops: Optional number of delivery stops
        
        Returns:
            Dict with optimized route recommendations
        """
        
        if not drivers:
            return {
                "status": "no_drivers",
                "message": "No drivers available for routing",
                "optimal_route": None
            }
        
        # Score drivers based on suitability
        scored_drivers = []
        for driver in drivers:
            score = self._score_driver(driver, shipment_info)
            scored_drivers.append({
                "driver": driver,
                "score": score
            })
        
        # Sort by score
        scored_drivers.sort(key=lambda x: x["score"], reverse=True)
        
        # Get top 3 recommendations
        recommendations = scored_drivers[:3]
        
        return {
            "status": "success",
            "delivery_location": delivery_location,
            "recommended_drivers": [
                {
                    "rank": idx + 1,
                    "driver_id": rec["driver"].get("_id"),
                    "driver_name": rec["driver"].get("name"),
                    "vehicle": rec["driver"].get("vehicle_type"),
                    "rating": rec["driver"].get("rating", 0),
                    "suitability_score": round(rec["score"], 2),
                    "estimated_pickup_time": self._estimate_pickup_time(rec["driver"])
                }
                for idx, rec in enumerate(recommendations)
            ],
            "delivery_windows": self._calculate_delivery_windows(recommendations)
        }
    
    def _get_capability_query(self, freshness_requirement: str) -> dict:
        """Get database query for driver capability matching"""
        requirement_map = {
            "cold_chain": {"capabilities": "cold_chain"},
            "refrigerated": {"capabilities": {"$in": ["cold_chain", "refrigerated"]}},
            "standard": {}  # All drivers can do standard
        }
        return requirement_map.get(freshness_requirement, {})
    
    def _score_driver(self, driver: Dict, shipment_info: Dict) -> float:
        """Calculate suitability score for a driver (0-100)"""
        score = 50.0  # Base score
        
        # Capacity check (max 30 points)
        capacity = driver.get("capacity", 0)
        quantity = shipment_info.get("quantity", 0)
        if capacity >= quantity:
            score += min(30, (capacity / quantity) * 10)
        
        # Rating (max 20 points)
        rating = driver.get("rating", 0)
        score += (rating / 5.0) * 20
        
        # Vehicle type match (max 20 points)
        freshness_level = shipment_info.get("freshness_level", "FAIR")
        vehicle_type = driver.get("vehicle_type", "standard")
        
        if freshness_level in ["POOR", "CRITICAL"] and vehicle_type == "cold_chain":
            score += 20
        elif freshness_level in ["GOOD", "FAIR"] and vehicle_type in ["cold_chain", "refrigerated"]:
            score += 15
        elif vehicle_type == "standard":
            score += 10
        
        # Availability bonus (max 10 points)
        if driver.get("available_hours", 0) >= 12:
            score += 10
        
        return min(100, score)
    
    def _estimate_pickup_time(self, driver: Dict) -> str:
        """Estimate when driver can pick up shipment"""
        current_hour = datetime.now().hour
        availability = driver.get("available_hours", 0)
        
        if availability >= 8:
            return "Immediate (0-1 hour)"
        elif availability >= 4:
            return "Soon (1-3 hours)"
        else:
            return "Delayed (3+ hours)"
    
    def _calculate_delivery_windows(self, recommendations: list) -> dict:
        """Calculate delivery time windows"""
        now = datetime.now()
        
        return {
            "express": f"{now.isoformat()} to {(now + timedelta(hours=6)).isoformat()}",
            "standard": f"{now.isoformat()} to {(now + timedelta(hours=24)).isoformat()}",
            "economy": f"{now.isoformat()} to {(now + timedelta(hours=48)).isoformat()}"
        }
    
    def _get_alternative_modes(self, primary_mode: str) -> list:
        """Get alternative delivery modes"""
        alternatives = {
            "cold_chain": ["refrigerated", "standard"],
            "refrigerated": ["cold_chain", "standard"],
            "standard": ["refrigerated", "cold_chain"]
        }
        return alternatives.get(primary_mode, [])
