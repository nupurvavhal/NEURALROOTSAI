# backend/app/routers/__init__.py
"""
Routers package for FastAPI endpoints
Exports individual routers for inclusion in app.main
"""

from .whatsapp_webhook import router as whatsapp_webhook_router  # noqa: F401
from .iot_ingest import router as iot_ingest_router  # noqa: F401
from .workflow_assessment import router as workflow_assessment_router  # noqa: F401

__all__ = [
    "whatsapp_webhook",
    "iot_ingest",
    "workflow_assessment",
]
