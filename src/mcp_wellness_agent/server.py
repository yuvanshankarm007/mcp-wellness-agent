"""
MCP Wellness Agent Server (Open Source Mini-Challenge Package)
Implements Model Context Protocol (Spec 2025-11-25) over Streamable HTTP for physiological wellness data.
"""
from fastapi import FastAPI, Request, Response
import uvicorn
import uuid
import json
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    class FastMCP:
        def __init__(self, name: str):
            self.name = name
            self.tools = {}
        def tool(self):
            def dec(fn):
                self.tools[fn.__name__] = fn
                return fn
            return dec

from .providers import WellnessProvider, SimulatedProvider, FitbitProvider

MCP_PROTOCOL_VERSION = "2025-11-25"


class WellnessServer:
    """MCP Server (Spec 2025-11-25 Streamable HTTP) for wearable & physiological wellness data"""

    def __init__(self, provider: str = "simulated", **provider_kwargs):
        self.provider_name = provider
        self.provider = self._create_provider(provider, **provider_kwargs)
        self.mcp = FastMCP("WellnessAgent")
        self._register_tools()

    def _create_provider(self, name: str, **kwargs) -> WellnessProvider:
        if name == "fitbit":
            return FitbitProvider(**kwargs)
        return SimulatedProvider()

    def _register_tools(self):
        @self.mcp.tool()
        async def get_vitals(user_id: str = "user_123") -> dict:
            """Get current wellness vitals for user"""
            data = await self.provider.fetch(user_id)
            return {
                "sleep_hours": data.sleep_hours,
                "sleep_quality": data.sleep_quality,
                "activity_level": data.activity_level,
                "heart_rate_avg": data.heart_rate_avg,
                "steps": data.steps,
                "stress_level": data.stress_level,
                "source": data.source,
                "timestamp": data.timestamp.isoformat()
            }

        @self.mcp.tool()
        async def get_history(user_id: str = "user_123", days: int = 7) -> list:
            """Get historical wellness data"""
            history = await self.provider.fetch_history(user_id, days)
            return [
                {
                    "sleep_hours": h.sleep_hours,
                    "activity_level": h.activity_level,
                    "stress_level": h.stress_level,
                    "timestamp": h.timestamp.isoformat()
                }
                for h in history
            ]

        @self.mcp.tool()
        async def analyze_trends(user_id: str = "user_123") -> dict:
            """Analyze wellness trends"""
            history = await self.provider.fetch_history(user_id, 30)
            if not history:
                return {"status": "no_data", "message": "No historical data available"}
            avg_sleep = sum(h.sleep_hours for h in history) / len(history)
            avg_stress = sum(h.stress_level or 5 for h in history) / len(history)
            trend = "improving" if history[-1].sleep_hours >= history[0].sleep_hours else "declining"
            return {
                "status": "success",
                "average_sleep": round(avg_sleep, 1),
                "average_stress": round(avg_stress, 1),
                "trend": trend,
                "data_points": len(history),
                "recommendation": self._get_recommendation(avg_sleep, avg_stress)
            }

        self._tools_map = {
            "get_vitals": get_vitals,
            "get_history": get_history,
            "analyze_trends": analyze_trends,
        }

    def _get_recommendation(self, avg_sleep: float, avg_stress: float) -> str:
        if avg_sleep < 6:
            return "Your sleep average is below recommended. Consider an earlier bedtime."
        if avg_stress > 7:
            return "High stress detected. Try meditation or shorter study sessions."
        if avg_sleep >= 7 and avg_stress < 5:
            return "Great wellness metrics! Maintain your healthy habits."
        return "Moderate wellness levels. Focus on a consistent sleep schedule."

    def create_app(self) -> FastAPI:
        app = FastAPI(title="MCP Wellness Agent", version="1.1.0")

        @app.get("/")
        async def root():
            return {
                "name": "MCP Wellness Agent",
                "version": "1.1.0",
                "provider": self.provider_name,
                "protocol": f"MCP ({MCP_PROTOCOL_VERSION})",
                "transport": "Streamable HTTP",
                "tools": ["get_vitals", "get_history", "analyze_trends"]
            }

        @app.get("/mcp")
        async def mcp_info():
            return {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "transport": "streamable-http",
                "serverInfo": {"name": "mcp-wellness-agent", "version": "1.1.0"},
                "tools": list(self._tools_map.keys())
            }

        @app.post("/mcp")
        async def mcp_rpc(request: Request, response: Response):
            body = await request.json()
            response.headers["Mcp-Session-Id"] = request.headers.get("Mcp-Session-Id") or str(uuid.uuid4())
            method = body.get("method")
            rpc_id = body.get("id", 1)
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {
                        "protocolVersion": MCP_PROTOCOL_VERSION,
                        "serverInfo": {"name": "mcp-wellness-agent", "version": "1.1.0"},
                        "capabilities": {"tools": {"listChanged": False}}
                    }
                }
            if method == "tools/call":
                params = body.get("params") or {}
                fn = self._tools_map.get(params.get("name"))
                if not fn:
                    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": "Tool not found"}}
                res = await fn(**(params.get("arguments") or {}))
                return {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res)}], "structuredContent": res}
                }
            return {"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": list(self._tools_map.keys())}}

        @app.get("/health")
        async def health():
            return {"status": "healthy", "provider": self.provider_name, "protocolVersion": MCP_PROTOCOL_VERSION}

        return app

    def run(self, host: str = "0.0.0.0", port: int = 8001):
        app = self.create_app()
        uvicorn.run(app, host=host, port=port)


def create_server(provider: str = "simulated", **kwargs) -> WellnessServer:
    return WellnessServer(provider=provider, **kwargs)
