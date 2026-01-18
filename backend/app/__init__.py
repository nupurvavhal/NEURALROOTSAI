"""
Neural Roots AI backend app package.
Exports common subpackages for convenient imports.
"""

# Re-export key subpackages
from . import core, agents, models, routers, services  # noqa: F401

__all__ = [
	"core",
	"agents",
	"models",
	"routers",
	"services",
]

__version__ = "1.0.0"
