# backend/app/agents/market_agent.py
"""
Market Agent - Fetches wholesale prices and determines optimal pricing strategy
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import statistics

class MarketAgent:
    """
    Analyzes market data from MongoDB wholesalers collection
    and determines best pricing strategy for crops.
    """
    
    def __init__(self):
        self.market_conditions = {}
    
    async def fetch_market_data(
        self,
        db,
        crop_name: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch market data from MongoDB wholesalers collection
        
        Args:
            db: MongoDB database instance
            crop_name: Name of the crop
            location: Optional location for localized pricing
        
        Returns:
            Dict with market analysis
        """
        try:
            # Query wholesaler collection for crop prices
            query = {"crop_name": {"$regex": crop_name, "$options": "i"}}
            if location:
                query["location"] = location
            
            wholesaler_data = await db.wholesalers.find(query).to_list(100)
            
            if not wholesaler_data:
                return {
                    "status": "no_data",
                    "message": f"No wholesaler data found for {crop_name}",
                    "prices": [],
                    "average_price": 0
                }
            
            return await self._analyze_market_data(wholesaler_data, crop_name)
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "prices": [],
                "average_price": 0
            }
    
    async def _analyze_market_data(
        self,
        wholesaler_data: List[Dict],
        crop_name: str
    ) -> Dict[str, Any]:
        """Analyze wholesaler data to extract market insights"""
        
        prices = []
        demand_levels = []
        supply_levels = []
        
        for entry in wholesaler_data:
            if "price" in entry:
                prices.append(float(entry["price"]))
            if "demand" in entry:
                demand_levels.append(entry["demand"])
            if "supply" in entry:
                supply_levels.append(entry["supply"])
        
        if not prices:
            return {
                "status": "no_prices",
                "crop_name": crop_name,
                "prices": [],
                "average_price": 0
            }
        
        # Calculate market statistics
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        min_price = min(prices)
        max_price = max(prices)
        stdev_price = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # Analyze demand/supply for market trend
        market_trend = self._analyze_trend(demand_levels, supply_levels)
        
        return {
            "status": "success",
            "crop_name": crop_name,
            "market_data": {
                "average_price": round(avg_price, 2),
                "median_price": round(median_price, 2),
                "min_price": round(min_price, 2),
                "max_price": round(max_price, 2),
                "price_volatility": round(stdev_price, 2),
                "sample_size": len(prices)
            },
            "market_trend": market_trend,
            "demand_distribution": self._get_demand_summary(demand_levels),
            "supply_distribution": self._get_supply_summary(supply_levels)
        }
    
    async def determine_best_price(
        self,
        crop_name: str,
        freshness_score: float,
        quantity: float,
        market_data: Dict[str, Any],
        urgency: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determine optimal pricing based on freshness, freshness_score, market conditions
        
        Args:
            crop_name: Name of the crop
            freshness_score: Freshness score from FreshnessAgent (0-100)
            quantity: Quantity available (in kg or units)
            market_data: Market analysis from fetch_market_data
            urgency: Optional urgency level ('LOW', 'MEDIUM', 'HIGH')
        
        Returns:
            Dict with recommended pricing strategy
        """
        
        if market_data.get("status") != "success":
            return {
                "status": "insufficient_data",
                "recommended_price": 0,
                "price_multiplier": 1.0,
                "notes": "Unable to determine optimal price"
            }
        
        market_metrics = market_data.get("market_data", {})
        base_price = market_metrics.get("average_price", 0)
        
        # Freshness-based multiplier
        freshness_multiplier = self._get_freshness_multiplier(freshness_score)
        
        # Demand-based multiplier
        market_trend = market_data.get("market_trend", "stable")
        demand_multiplier = {
            "high_demand": 1.15,
            "normal_demand": 1.0,
            "low_demand": 0.85,
            "stable": 1.0
        }.get(market_trend, 1.0)
        
        # Urgency-based multiplier
        urgency_multiplier = {
            "LOW": 1.0,
            "MEDIUM": 0.95,
            "HIGH": 0.85
        }.get(urgency, 1.0)
        
        # Quantity-based discount (larger quantities = slight discount)
        quantity_multiplier = 1.0 if quantity < 50 else (0.98 if quantity < 100 else 0.95)
        
        # Calculate final recommended price
        total_multiplier = freshness_multiplier * demand_multiplier * urgency_multiplier * quantity_multiplier
        recommended_price = base_price * total_multiplier
        
        return {
            "status": "success",
            "crop_name": crop_name,
            "recommended_price": round(recommended_price, 2),
            "base_price": round(base_price, 2),
            "price_multiplier": round(total_multiplier, 3),
            "freshness_multiplier": round(freshness_multiplier, 3),
            "demand_multiplier": round(demand_multiplier, 3),
            "urgency_multiplier": round(urgency_multiplier, 3),
            "quantity_multiplier": round(quantity_multiplier, 3),
            "price_range": {
                "min": round(base_price * 0.85, 2),
                "max": round(base_price * 1.15, 2)
            },
            "pricing_strategy": self._get_pricing_strategy(freshness_score, market_trend)
        }
    
    def _get_freshness_multiplier(self, freshness_score: float) -> float:
        """Calculate price multiplier based on freshness"""
        if freshness_score >= 80:
            return 1.20  # 20% premium for excellent freshness
        elif freshness_score >= 60:
            return 1.10  # 10% premium for good freshness
        elif freshness_score >= 40:
            return 0.95  # 5% discount for fair freshness
        elif freshness_score >= 20:
            return 0.75  # 25% discount for poor freshness
        else:
            return 0.50  # 50% discount for critical freshness
    
    def _analyze_trend(self, demand_levels: list, supply_levels: list) -> str:
        """Analyze market trend from demand/supply"""
        if not demand_levels or not supply_levels:
            return "stable"
        
        avg_demand = sum(d for d in demand_levels if isinstance(d, (int, float))) / len(demand_levels) if demand_levels else 0
        avg_supply = sum(s for s in supply_levels if isinstance(s, (int, float))) / len(supply_levels) if supply_levels else 0
        
        if avg_demand > avg_supply:
            return "high_demand"
        elif avg_demand < avg_supply * 0.7:
            return "low_demand"
        else:
            return "normal_demand"
    
    def _get_demand_summary(self, demand_levels: list) -> dict:
        """Get demand distribution summary"""
        if not demand_levels:
            return {"distribution": "unknown", "primary": None}
        
        high = len([d for d in demand_levels if d == "HIGH" or d == "high"])
        medium = len([d for d in demand_levels if d == "MEDIUM" or d == "medium"])
        low = len([d for d in demand_levels if d == "LOW" or d == "low"])
        
        return {
            "high": high,
            "medium": medium,
            "low": low,
            "total_wholesalers": len(demand_levels)
        }
    
    def _get_supply_summary(self, supply_levels: list) -> dict:
        """Get supply distribution summary"""
        if not supply_levels:
            return {"distribution": "unknown", "primary": None}
        
        high = len([s for s in supply_levels if s == "HIGH" or s == "high"])
        medium = len([s for s in supply_levels if s == "MEDIUM" or s == "medium"])
        low = len([s for s in supply_levels if s == "LOW" or s == "low"])
        
        return {
            "high": high,
            "medium": medium,
            "low": low,
            "total_wholesalers": len(supply_levels)
        }
    
    def _get_pricing_strategy(self, freshness_score: float, market_trend: str) -> str:
        """Get recommended pricing strategy"""
        if freshness_score >= 80 and market_trend == "high_demand":
            return "PREMIUM_PRICING - High demand + Excellent freshness"
        elif freshness_score >= 80:
            return "ABOVE_MARKET - Excellent freshness compensates"
        elif market_trend == "high_demand":
            return "MARKET_RATE_PLUS - Capitalize on high demand"
        elif market_trend == "low_demand":
            return "COMPETITIVE_DISCOUNT - Lower demand requires price competitiveness"
        elif freshness_score < 40:
            return "CLEARANCE_PRICING - Poor freshness requires aggressive pricing"
        else:
            return "MARKET_RATE - Standard market pricing"
