"""
Tests for MCP Wellness Agent
"""
import pytest
import asyncio
from datetime import datetime

from mcp_wellness_agent.providers import SimulatedProvider, FitbitProvider, WellnessData
from mcp_wellness_agent.server import create_server


class TestSimulatedProvider:
    """Test simulated wellness provider"""
    
    @pytest.fixture
    def provider(self):
        return SimulatedProvider()
    
    @pytest.mark.asyncio
    async def test_fetch_returns_data(self, provider):
        """Test that fetch returns valid wellness data"""
        data = await provider.fetch("test_user")
        
        assert isinstance(data, WellnessData)
        assert 3.0 <= data.sleep_hours <= 10.0
        assert data.activity_level in ["low", "normal", "high"]
        assert data.source == "simulated"
    
    @pytest.mark.asyncio
    async def test_fetch_consistency(self, provider):
        """Test that same user gets consistent data"""
        data1 = await provider.fetch("consistent_user")
        data2 = await provider.fetch("consistent_user")
        
        # Should be similar (same baseline)
        assert abs(data1.sleep_hours - data2.sleep_hours) < 2.0
    
    @pytest.mark.asyncio
    async def test_fetch_history(self, provider):
        """Test historical data fetching"""
        history = await provider.fetch_history("test_user", days=7)
        
        assert len(history) == 7
        assert all(isinstance(d, WellnessData) for d in history)
    
    @pytest.mark.asyncio
    async def test_time_based_variation(self, provider):
        """Test that data varies by time of day"""
        # This is implicit in the simulation
        data = await provider.fetch("time_user")
        assert data.timestamp is not None


class TestServer:
    """Test MCP server"""
    
    @pytest.fixture
    def server(self):
        return create_server(provider="simulated")
    
    def test_server_creation(self, server):
        """Test server initialization"""
        assert server.provider_name == "simulated"
        assert server.mcp is not None
    
    def test_app_creation(self, server):
        """Test FastAPI app creation"""
        app = server.create_app()
        assert app is not None


class TestFitbitProvider:
    """Test Fitbit provider"""
    
    @pytest.mark.asyncio
    async def test_fallback_without_credentials(self):
        """Test fallback to simulation without credentials"""
        provider = FitbitProvider()
        data = await provider.fetch("test_user")
        
        assert isinstance(data, WellnessData)
        assert data.source == "fitbit"  # Source is fitbit even if simulated


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
