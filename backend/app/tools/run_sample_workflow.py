# backend/app/tools/run_sample_workflow.py
import asyncio
from pprint import pprint

from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.agents.workflow_orchestrator import WorkflowOrchestrator


async def main():
    # Connect to MongoDB (requires MONGODB_URL and DB_NAME configured)
    await connect_to_mongo()
    db = get_database()

    orchestrator = WorkflowOrchestrator()

    crop_data = {
        "crop_name": "tomato",
        "temperature": 24.5,
        "humidity": 72.0,
        "age_hours": 12.5,
        "quantity": 150,
    }

    logistics_params = {
        "location": "Nashik",
        "destination": "Mumbai",
        "distance_km": 180,
    }

    market_params = {
        "target_location": "Mumbai Mandi",
        "urgency": "MEDIUM",
    }

    print("\nRunning sample workflow...\n")
    result = await orchestrator.execute_workflow(
        db=db,
        crop_data=crop_data,
        logistics_params=logistics_params,
        market_params=market_params,
    )

    print("Status:", result.get("status"))
    synthesis = result.get("synthesis", {})
    print("Final Freshness:", synthesis.get("final_freshness_level"), synthesis.get("final_freshness_score"))
    print("Recommended Price:", synthesis.get("market_recommendation", {}).get("recommended_price"))
    print("Delivery Mode:", synthesis.get("logistics_impact", {}).get("delivery_mode"))
    print("Weather Risk:", synthesis.get("weather_impact", {}).get("risk_level"))

    print("\nFull synthesis:")
    pprint(synthesis)

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
