# MCP Wellness Agent

[![License: MIT](https://img.shields.io/badge/License-AGPL_v3%20%2F%20NonCommercial-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-2.0-green.svg)](https://modelcontextprotocol.io)

A **Model Context Protocol (MCP)** server that exposes wellness data (sleep, activity, heart rate) as tools for AI agents. Built for the Amazon Build Ship Shape 2026 hackathon as part of the **Open Source Mini-Challenge**.

## 🌟 Features

- **MCP Protocol**: Implements the Model Context Protocol for agent-tool communication
- **Multi-Provider**: Supports Fitbit, Apple Health, and realistic simulation
- **A2A Compatible**: Includes agent card for agent-to-agent discovery
- **Voice-Ready**: Optimized for Alexa+ and voice-first interfaces
- **Type-Safe**: Full Pydantic models for all data
- **Extensible**: Easy to add new wellness providers

## 🚀 Quick Start

```bash
# Install
pip install mcp-wellness-agent

# Run MCP server
mcp-wellness-server --transport streamable-http --port 8001

# Or use as library
from mcp_wellness_agent import WellnessServer
server = WellnessServer(provider="fitbit")
```

## 📡 MCP Tools

### `get_vitals(user_id: str)`
Get current wellness vitals for a user.

Returns:
- `sleep_hours`: Hours of sleep
- `sleep_quality`: Quality score (1-10)
- `activity_level`: low/normal/high
- `heart_rate_avg`: Resting heart rate
- `steps`: Daily step count
- `stress_level`: Stress score (1-10)

### `get_history(user_id: str, days: int)`
Get historical wellness data.

### `analyze_trends(user_id: str)`
Get trend analysis and insights.

## 🔌 Providers

| Provider | Status | Notes |
|----------|--------|-------|
| Simulated | ✅ Ready | Realistic physiological simulation |
| Fitbit | ✅ Ready | Requires OAuth2 credentials |
| Apple Health | 🚧 Planned | macOS/iOS only |
| Garmin | 🚧 Planned | Coming soon |

## 🏗️ Architecture

```
┌─────────────────┐     MCP      ┌──────────────────┐
│   AI Agent      │◄────────────►│  Wellness Agent  │
│  (Claude, etc)  │  Streamable  │   MCP Server     │
└─────────────────┘   HTTP       └──────────────────┘
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                         ┌────────┐   ┌─────────┐   ┌──────────┐
                         │ Fitbit │   │ Apple   │   │ Simulated│
                         │  API   │   │ Health  │   │ Engine   │
                         └────────┘   └─────────┘   └──────────┘
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

Dual-Licensed under **GNU AGPLv3 (`AGPL-3.0-only`)** and **PolyForm Noncommercial 1.0.0** — **No closed-source or commercial use is permitted without prior written permission** (see [LICENSE](LICENSE), [LICENSE.NONCOMMERCIAL.md](LICENSE.NONCOMMERCIAL.md), and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)).

## 🏆 Hackathon

Built for **Amazon Build Ship Shape 2026** - Open Source Mini-Challenge.
