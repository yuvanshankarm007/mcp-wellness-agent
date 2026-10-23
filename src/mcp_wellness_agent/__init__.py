"""
MCP Wellness Agent
A Model Context Protocol server for wellness data integration
"""
from .server import WellnessServer, create_server
from .providers import WellnessProvider, SimulatedProvider, FitbitProvider

__version__ = "1.0.0"
__all__ = [
    "WellnessServer",
    "create_server",
    "WellnessProvider",
    "SimulatedProvider",
    "FitbitProvider",
]
