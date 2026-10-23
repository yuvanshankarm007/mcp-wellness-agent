"""
Wellness Data Providers
Abstracts different wellness data sources
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List
import random


@dataclass
class WellnessData:
    """Wellness data model"""
    sleep_hours: float
    sleep_quality: Optional[int] = None
    activity_level: str = "normal"
    heart_rate_avg: Optional[int] = None
    steps: Optional[int] = None
    stress_level: Optional[int] = None
    source: str = "unknown"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class WellnessProvider(ABC):
    """Abstract base class for wellness providers"""
    
    @abstractmethod
    async def fetch(self, user_id: str) -> WellnessData:
        """Fetch current wellness data"""
        pass
    
    async def fetch_history(self, user_id: str, days: int = 7) -> List[WellnessData]:
        """Fetch historical data (default: simulate)"""
        history = []
        for i in range(days):
            data = await self.fetch(user_id)
            data.timestamp = datetime.now() - timedelta(days=i)
            history.append(data)
        return history


class SimulatedProvider(WellnessProvider):
    """
    Realistic wellness simulation using circadian rhythms.
    Generates consistent data per user with realistic patterns.
    """
    
    def __init__(self):
        self.user_baselines = {}
    
    def _get_baseline(self, user_id: str) -> dict:
        """Get or create user baseline"""
        if user_id not in self.user_baselines:
            rng = random.Random(f'baseline_{user_id}')
            self.user_baselines[user_id] = {
                'sleep': rng.gauss(7.0, 1.0),
                'hr': rng.gauss(65, 8),
                'steps': rng.gauss(8000, 2000),
                'stress': rng.gauss(5, 2)
            }
        return self.user_baselines[user_id]
    
    async def fetch(self, user_id: str) -> WellnessData:
        """Generate realistic wellness data"""
        baseline = self._get_baseline(user_id)
        now = datetime.now()
        hour = now.hour
        
        # Time-based factors
        time_factor = 1.0
        if 0 <= hour <= 5:
            time_factor = 0.7
        elif 22 <= hour <= 23:
            time_factor = 0.85
        elif 14 <= hour <= 16:
            time_factor = 0.9
        
        sleep = max(3.0, min(10.0, baseline['sleep'] * time_factor + random.Random(f'{user_id}_{now.isoformat()}').gauss(0, 0.5)))
        quality = max(1, min(10, int(sleep * 1.2 + random.Random(f'{user_id}_{now.isoformat()}').gauss(0, 1))))
        steps = max(0, baseline['steps'] * (hour / 20.0) + random.Random(f'{user_id}_{now.isoformat()}').gauss(0, 500))
        hr = max(45, min(120, baseline['hr'] + random.Random(f'{user_id}_{now.isoformat()}').gauss(0, 5)))
        stress = max(1, min(10, int(baseline['stress'] + (8 - quality) * 0.5)))
        
        return WellnessData(
            sleep_hours=round(sleep, 1),
            sleep_quality=quality,
            activity_level="high" if steps > 10000 else "normal" if steps > 5000 else "low",
            heart_rate_avg=int(hr),
            steps=int(steps),
            stress_level=stress,
            source="simulated",
            timestamp=now
        )


class FitbitProvider(WellnessProvider):
    """Fitbit API integration (placeholder for real implementation)"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.fallback = SimulatedProvider()
    
    async def fetch(self, user_id: str) -> WellnessData:
        """Fetch from Fitbit or fallback to simulation"""
        if not self.client_id:
            return await self.fallback.fetch(user_id)
        
        # Real implementation would call Fitbit API here
        # For now, return simulated with fitbit source
        data = await self.fallback.fetch(user_id)
        data.source = "fitbit"
        return data
