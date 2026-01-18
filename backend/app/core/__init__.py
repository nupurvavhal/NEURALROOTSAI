"""
Core utilities for Neural Roots AI backend.
Provides configuration and database helpers.
"""

from .config import settings  # noqa: F401
from .database import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
)  # noqa: F401

__all__ = [
    "settings",
    "connect_to_mongo",
    "close_mongo_connection",
    "get_database",
]
