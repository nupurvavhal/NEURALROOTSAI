# backend/app/routers/workflow_assessment.py
"""
Workflow Assessment Router - API endpoints for executing the agentic workflow
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.core.database import get_database
from app.agents.workflow_orchestrator import WorkflowOrchestrator

# Initialize router and orchestrator
router = APIRouter()
orchestrator = WorkflowOrchestrator()

# ==================== REQUEST/RESPONSE MODELS ====================

class CropData(BaseModel):
    crop_name: str
    temperature: float
    humidity: float
    age_hours: Optional[float] = 0
class CropData(BaseModel):
    crop_name: str = Field(..., min_length=2, max_length=50, regex=r"^[A-Za-z_\- ]+$")
    temperature: float = Field(..., ge=-10, le=60, description="Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Percentage")
    age_hours: Optional[float] = Field(0, ge=0)
    quantity: Optional[float] = Field(10, gt=0)
    iot_data: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"

class MarketParams(BaseModel):
    location: Optional[str] = Field(None, max_length=100)
    destination: Optional[str] = Field(None, max_length=100)
    distance_km: Optional[float] = Field(100, gt=0, le=5000)

    class Config:
        extra = "forbid"
class WorkflowRequest(BaseModel):
    crop_data: CropData
    target_location: Optional[str] = Field(None, max_length=100)
    urgency: Optional[str] = Field("MEDIUM", regex=r"^(LOW|MEDIUM|HIGH)$")

    class Config:
        extra = "forbid"

# ==================== API ENDPOINTS ====================

@router.post("/assess-freshness")
async def assess_freshness(request: WorkflowRequest):

    class Config:
        extra = "forbid"
    """
    Execute the complete workflow to assess crop freshness and determine strategy
    
    This endpoint orchestrates all agents:
    1. Freshness Agent - Analyzes current freshness
    2. Market Agent - Determines optimal pricing
    3. Logistics Agent - Recommends delivery mode
    4. Weather Agent - Assesses weather impact
    
    Returns comprehensive freshness assessment with recommendations
    """
    try:
        db = get_database()
        
        # Convert request models to dicts
        crop_data = request.crop_data.dict()
        logistics_params = request.logistics_params.dict() if request.logistics_params else None
        market_params = request.market_params.dict() if request.market_params else None
        
        # Execute workflow
        result = await orchestrator.execute_workflow(
            db=db,
            crop_data=crop_data,
            logistics_params=logistics_params,
            market_params=market_params
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow-history")
async def get_workflow_history(limit: int = 10):
    """Retrieve recent workflow assessments"""
    try:
        history = orchestrator.get_workflow_history(limit=limit)
        return {
            "status": "success",
            "total_workflows": len(history),
            "workflows": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-assessment")
async def quick_assessment(
    crop_name: str,
    temperature: float,
    humidity: float,
    age_hours: Optional[float] = 0,
    quantity: Optional[float] = 10,
    distance_km: Optional[float] = 100
):
    """
    Quick freshness assessment without detailed market/logistics analysis
    
    Useful for rapid freshness checks without full workflow
    """
    try:
        db = get_database()
        
        crop_data = {
            "crop_name": crop_name,
            "temperature": temperature,
            "humidity": humidity,
            "age_hours": age_hours,
            "quantity": quantity
        }
        
        logistics_params = {
            "distance_km": distance_km
        }
        
        result = await orchestrator.execute_workflow(
            db=db,
            crop_data=crop_data,
            logistics_params=logistics_params
        )
        
        # Return simplified result for quick assessment
        synthesis = result.get("synthesis", {})
        return {
            "crop_name": crop_name,
            "freshness_score": synthesis.get("final_freshness_score"),
            "freshness_level": synthesis.get("final_freshness_level"),
            "recommended_price": synthesis.get("market_recommendation", {}).get("recommended_price"),
            "delivery_mode": synthesis.get("logistics_impact", {}).get("delivery_mode"),
            "weather_risk": synthesis.get("weather_impact", {}).get("risk_level"),
            "recommendations": synthesis.get("comprehensive_recommendations", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detailed-analysis")
async def detailed_analysis(request: WorkflowRequest):
    """
    Execute full detailed workflow with all data points
    
    Returns complete analysis from all agents with detailed breakdowns
    """
    try:
        db = get_database()
        
        crop_data = request.crop_data.dict()
        logistics_params = request.logistics_params.dict() if request.logistics_params else None
        market_params = request.market_params.dict() if request.market_params else None
        
        result = await orchestrator.execute_workflow(
            db=db,
            crop_data=crop_data,
            logistics_params=logistics_params,
            market_params=market_params
        )
        
        # Return detailed result with all stages
        return {
            "workflow_id": result.get("workflow_id"),
            "timestamp": result.get("timestamp"),
            "crop_data": crop_data,
            "stages": result.get("stages", {}),
            "synthesis": result.get("synthesis", {}),
            "status": result.get("status")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def workflow_health():
    """Health check for workflow service"""
    return {
        "status": "healthy",
        "service": "Agentic AI Workflow",
        "agents": [
            "Freshness Agent",
            "Market Agent",
            "Logistics Agent",
            "Weather Agent"
        ],
        "workflows_executed": len(orchestrator.get_workflow_history(limit=1000))
    }


@router.post("/validate-input")
async def validate_input(request: WorkflowRequest):
    """
    Validate input payloads for correctness without running the workflow.
    Checks ranges, allowed values, and basic DB presence.
    """
    try:
        db = get_database()

        crop_data = request.crop_data.dict()
        logistics_params = request.logistics_params.dict() if request.logistics_params else {}
        market_params = request.market_params.dict() if request.market_params else {}

        crop_validation = await validate_crop_data(db, crop_data)
        logistics_validation = await validate_logistics_params(db, logistics_params)
        market_validation = await validate_market_params(db, market_params)

        overall_valid = all([
            crop_validation.get("valid"),
            logistics_validation.get("valid"),
            market_validation.get("valid"),
        ])

        return {
            "status": "success" if overall_valid else "invalid",
            "valid": overall_valid,
            "crop": crop_validation,
            "logistics": logistics_validation,
            "market": market_validation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
