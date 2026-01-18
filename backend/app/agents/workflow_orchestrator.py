# backend/app/agents/workflow_orchestrator.py
"""
Workflow Orchestrator - Coordinates all agents to calculate final freshness assessment
This is the central hub that manages the agentic AI workflow.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.agents.freshness_agent import FreshnessAgent
from app.agents.market_agent import MarketAgent
from app.agents.logistics_agent import LogisticsAgent
from app.agents.weather_agent import WeatherAgent

class WorkflowOrchestrator:
    """
    Orchestrates the complete agentic AI workflow for freshness prediction and optimization.
    
    Workflow:
    1. Freshness Agent - Analyzes current freshness based on temp/humidity/age
    2. Market Agent - Fetches market data and determines optimal pricing
    3. Logistics Agent - Recommends delivery mode and driver selection
    4. Weather Agent - Assesses weather impact on freshness during transport
    5. Final Synthesis - Combines all factors to produce final freshness assessment
    """
    
    def __init__(self):
        self.freshness_agent = FreshnessAgent()
        self.market_agent = MarketAgent()
        self.logistics_agent = LogisticsAgent()
        self.weather_agent = WeatherAgent()
        self.workflow_history = []
    
    async def execute_workflow(
        self,
        db,
        crop_data: Dict[str, Any],
        logistics_params: Optional[Dict[str, Any]] = None,
        market_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete workflow to assess crop freshness and determine optimal strategy
        
        Args:
            db: MongoDB database instance
            crop_data: Dict with crop information including:
                - crop_name: Name of the crop
                - temperature: Current temperature
                - humidity: Current humidity
                - age_hours: Hours since harvest
                - quantity: Quantity available
            logistics_params: Optional logistics parameters:
                - location: Current location
                - destination: Delivery destination
                - distance_km: Distance to destination
            market_params: Optional market parameters:
                - target_location: Market location
                - urgency: Urgency level (LOW, MEDIUM, HIGH)
        
        Returns:
            Comprehensive freshness assessment and recommendations
        """
        
        workflow_id = datetime.now().isoformat()
        results = {
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "stages": {}
        }
        
        try:
            # ==================== STAGE 1: FRESHNESS ANALYSIS ====================
            freshness_result = await self._execute_freshness_stage(crop_data)
            results["stages"]["freshness"] = freshness_result
            
            # ==================== STAGE 2: MARKET ANALYSIS ====================
            market_result = await self._execute_market_stage(
                db, 
                crop_data, 
                freshness_result,
                market_params
            )
            results["stages"]["market"] = market_result
            
            # ==================== STAGE 3: LOGISTICS ANALYSIS ====================
            logistics_result = await self._execute_logistics_stage(
                db,
                crop_data,
                freshness_result,
                logistics_params
            )
            results["stages"]["logistics"] = logistics_result
            
            # ==================== STAGE 4: WEATHER ANALYSIS ====================
            weather_result = await self._execute_weather_stage(
                db,
                crop_data,
                logistics_params
            )
            results["stages"]["weather"] = weather_result
            
            # ==================== FINAL SYNTHESIS ====================
            synthesis = await self._synthesize_results(
                freshness_result,
                market_result,
                logistics_result,
                weather_result,
                crop_data
            )
            results["synthesis"] = synthesis
            
            results["status"] = "completed"
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
        
        # Store workflow history
        self.workflow_history.append(results)
        
        return results
    
    async def _execute_freshness_stage(self, crop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute freshness analysis stage"""
        try:
            result = await self.freshness_agent.predict_freshness(
                crop_name=crop_data.get("crop_name", "unknown"),
                temperature=crop_data.get("temperature", 25),
                humidity=crop_data.get("humidity", 70),
                age_hours=crop_data.get("age_hours", 0),
                iot_data=crop_data.get("iot_data")
            )
            
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_market_stage(
        self,
        db,
        crop_data: Dict[str, Any],
        freshness_result: Dict[str, Any],
        market_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute market analysis stage"""
        try:
            # Fetch market data
            market_data = await self.market_agent.fetch_market_data(
                db,
                crop_name=crop_data.get("crop_name", "unknown"),
                location=market_params.get("target_location") if market_params else None
            )
            
            # Determine best price if market data available
            if freshness_result.get("status") == "success":
                freshness_info = freshness_result.get("data", {})
                price_recommendation = await self.market_agent.determine_best_price(
                    crop_name=crop_data.get("crop_name", "unknown"),
                    freshness_score=freshness_info.get("freshness_score", 50),
                    quantity=crop_data.get("quantity", 0),
                    market_data=market_data,
                    urgency=market_params.get("urgency") if market_params else None
                )
            else:
                price_recommendation = {"status": "no_freshness_data"}
            
            return {
                "status": "success",
                "market_data": market_data,
                "price_recommendation": price_recommendation
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_logistics_stage(
        self,
        db,
        crop_data: Dict[str, Any],
        freshness_result: Dict[str, Any],
        logistics_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute logistics analysis stage"""
        try:
            freshness_info = freshness_result.get("data", {})
            
            # Recommend delivery mode
            delivery_recommendation = await self.logistics_agent.recommend_delivery_mode(
                freshness_score=freshness_info.get("freshness_score", 50),
                freshness_level=freshness_info.get("freshness_level", "FAIR"),
                distance_km=logistics_params.get("distance_km", 100) if logistics_params else 100,
                quantity=crop_data.get("quantity", 0),
                availability_window_hours=24
            )
            
            # Get available drivers
            drivers = await self.logistics_agent.get_available_drivers(
                db,
                location=logistics_params.get("location") if logistics_params else None,
                vehicle_type=delivery_recommendation.get("recommended_delivery_mode"),
                freshness_requirement=freshness_info.get("freshness_level")
            )
            
            # Optimize route if drivers available
            route_optimization = None
            if drivers.get("status") == "success":
                route_optimization = await self.logistics_agent.optimize_delivery_route(
                    drivers=drivers.get("drivers", []),
                    shipment_info={
                        "freshness": freshness_info.get("freshness_level"),
                        "freshness_score": freshness_info.get("freshness_score"),
                        "quantity": crop_data.get("quantity", 0)
                    },
                    delivery_location=logistics_params.get("destination", "market") if logistics_params else "market"
                )
            
            return {
                "status": "success",
                "delivery_recommendation": delivery_recommendation,
                "available_drivers": drivers,
                "route_optimization": route_optimization
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_weather_stage(
        self,
        db,
        crop_data: Dict[str, Any],
        logistics_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute weather analysis stage"""
        try:
            # Calculate transportation duration (assume 100km takes 2 hours)
            distance = logistics_params.get("distance_km", 100) if logistics_params else 100
            transport_duration = distance / 50  # Assume 50 km/h average
            
            weather_impact = await self.weather_agent.assess_weather_impact(
                location=logistics_params.get("location", "default") if logistics_params else "default",
                crop_type=crop_data.get("crop_name", "vegetable"),
                transportation_duration_hours=transport_duration,
                db=db
            )
            
            return {
                "status": "success",
                "data": weather_impact
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _synthesize_results(
        self,
        freshness_result: Dict[str, Any],
        market_result: Dict[str, Any],
        logistics_result: Dict[str, Any],
        weather_result: Dict[str, Any],
        crop_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize all agent outputs into final freshness assessment and recommendations
        """
        
        # Extract data from each stage
        freshness_data = freshness_result.get("data", {}) if freshness_result.get("status") == "success" else {}
        market_data = market_result.get("price_recommendation", {}) if market_result.get("status") == "success" else {}
        logistics_data = logistics_result.get("delivery_recommendation", {}) if logistics_result.get("status") == "success" else {}
        weather_data = weather_result.get("data", {}) if weather_result.get("status") == "success" else {}
        
        # Calculate adjusted freshness considering all factors
        base_freshness = freshness_data.get("freshness_score", 50)
        
        # Weather impact on transport (will degrade freshness)
        weather_degradation_rate = weather_data.get("freshness_degradation_rate", 1.0)
        transport_hours = weather_data.get("transportation_duration_hours", 2)
        weather_impact_loss = weather_degradation_rate * transport_hours
        
        # Logistics impact (better delivery mode can preserve freshness)
        delivery_mode = logistics_data.get("recommended_delivery_mode", "standard")
        mode_preservation_bonus = {
            "cold_chain": 5,
            "refrigerated": 3,
            "standard": 0
        }.get(delivery_mode, 0)
        
        # Calculate final freshness score
        final_freshness_score = max(0, min(100, 
            base_freshness - weather_impact_loss + mode_preservation_bonus
        ))
        
        # Determine final freshness level
        if final_freshness_score >= 80:
            final_freshness_level = "EXCELLENT"
        elif final_freshness_score >= 60:
            final_freshness_level = "GOOD"
        elif final_freshness_score >= 40:
            final_freshness_level = "FAIR"
        elif final_freshness_score >= 20:
            final_freshness_level = "POOR"
        else:
            final_freshness_level = "CRITICAL"
        
        # Generate comprehensive recommendations
        recommendations = self._generate_comprehensive_recommendations(
            base_freshness,
            final_freshness_score,
            final_freshness_level,
            market_data,
            logistics_data,
            weather_data
        )
        
        return {
            "final_freshness_score": round(final_freshness_score, 2),
            "final_freshness_level": final_freshness_level,
            "base_freshness_score": round(base_freshness, 2),
            "weather_impact": {
                "degradation_rate": round(weather_degradation_rate, 2),
                "estimated_loss": round(weather_impact_loss, 2),
                "risk_level": weather_data.get("risk_level", "UNKNOWN")
            },
            "logistics_impact": {
                "delivery_mode": delivery_mode,
                "preservation_bonus": mode_preservation_bonus,
                "feasible": logistics_data.get("feasible", False)
            },
            "market_recommendation": {
                "recommended_price": market_data.get("recommended_price", 0),
                "pricing_strategy": market_data.get("pricing_strategy", "MARKET_RATE"),
                "market_trend": market_result.get("market_data", {}).get("market_trend", "stable")
            },
            "comprehensive_recommendations": recommendations,
            "action_items": self._generate_action_items(
                final_freshness_level,
                market_data,
                logistics_data
            )
        }
    
    def _generate_comprehensive_recommendations(
        self,
        base_freshness: float,
        final_freshness: float,
        final_level: str,
        market_data: Dict,
        logistics_data: Dict,
        weather_data: Dict
    ) -> list:
        """Generate comprehensive recommendations from all data"""
        recommendations = []
        
        # Freshness recommendations
        if final_freshness < base_freshness:
            loss = base_freshness - final_freshness
            recommendations.append(
                f"⚠️ Weather will degrade freshness by ~{loss:.1f}% during transport"
            )
        
        recommendations.append(
            f"Current Status: {final_level} (Score: {final_freshness:.0f}/100)"
        )
        
        # Market recommendations
        if market_data.get("recommended_price"):
            recommendations.append(
                f"💰 Recommended Price: Rs. {market_data['recommended_price']:.2f} "
                f"({market_data.get('pricing_strategy', 'MARKET_RATE')})"
            )
        
        # Logistics recommendations
        if logistics_data.get("recommended_delivery_mode"):
            recommendations.append(
                f"🚚 Use {logistics_data['recommended_delivery_mode'].upper()} delivery"
            )
        
        if not logistics_data.get("feasible", True):
            recommendations.extend(logistics_data.get("feasibility_notes", []))
        
        # Weather recommendations
        if weather_data.get("recommendations"):
            recommendations.extend(weather_data["recommendations"])
        
        # General action recommendations
        if final_level in ["POOR", "CRITICAL"]:
            recommendations.append(
                "🚨 URGENT: Initiate immediate distribution to prevent total loss"
            )
        elif final_level == "FAIR":
            recommendations.append(
                "⏱️ HIGH PRIORITY: Schedule delivery within 24 hours"
            )
        
        return recommendations
    
    def _generate_action_items(
        self,
        final_level: str,
        market_data: Dict,
        logistics_data: Dict
    ) -> list:
        """Generate prioritized action items"""
        actions = []
        
        if final_level in ["CRITICAL", "POOR"]:
            priority = "🔴 CRITICAL"
        elif final_level == "FAIR":
            priority = "🟡 HIGH"
        else:
            priority = "🟢 NORMAL"
        
        actions.append({
            "priority": priority,
            "action": "Confirm delivery arrangements",
            "details": f"Recommended mode: {logistics_data.get('recommended_delivery_mode', 'standard')}"
        })
        
        if market_data.get("recommended_price"):
            actions.append({
                "priority": "📊 IMPORTANT",
                "action": "Set market price",
                "details": f"Rs. {market_data['recommended_price']:.2f} based on {market_data.get('pricing_strategy', 'market analysis')}"
            })
        
        if logistics_data.get("feasibility_notes"):
            actions.append({
                "priority": "⚠️ WARNING",
                "action": "Address logistics constraints",
                "details": "; ".join(logistics_data["feasibility_notes"][:2])
            })
        
        return actions
    
    def get_workflow_history(self, limit: int = 10) -> list:
        """Retrieve recent workflow executions"""
        return self.workflow_history[-limit:]
