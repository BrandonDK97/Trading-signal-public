# Trading Signal Processing System

A REST API system that processes natural language trading signals, calculates position sizing, and determines take profit levels.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐      ┌──────────────────┐
│   Client    │─────▶│  REST API    │─────▶│  LLM Gateway    │─────▶│   Claude API     │
│             │      │  (FastAPI)   │      │  (Parser)       │      │   (Anthropic)    │
└─────────────┘      └──────────────┘      └─────────────────┘      └──────────────────┘
                             │
                             ▼
                     ┌──────────────┐
                     │ Calculate    │
                     │ Size Module  │
                     └──────────────┘
```

## Components

1. **`main.py`** - Entry point, starts the FastAPI server
2. **`rest_api.py`** - REST API endpoints
3. **`llm_gateway.py`** - Claude API integration for parsing messages
4. **`calculate_size.py`** - Position sizing and take profit calculations

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### Start the Server

```bash
python main.py
```

Server will run on `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Process Trading Signal
```bash
POST /signal
Content-Type: application/json

{
  "message": "longed MON at 0.029529 sl: 0.02835 (0.5% risk)",
  "balance": 10000,
  "risk_tolerance": 3
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "trade": {
      "symbol": "MON",
      "direction": "long",
      "entry": 0.029529,
      "stop_loss": 0.02835,
      "risk_percent": 0.5
    },
    "take_profits": {
      "tp1_price": 0.029882,
      "tp2_price": 0.029970,
      "tp1_percent": 35,
      "tp2_percent": 50,
      "manual_percent": 15,
      "risk_distance": 0.000706,
      "rr_ratio_tp1": 0.5,
      "rr_ratio_tp2": 1.25,
      "direction": "long"
    },
    "position_sizing": {
      "conservative": {
        "notional_value": 4169.97,
        "quantity": 141.19,
        "max_loss": 100.00,
        "risk_percent": 1.0,
        "mode": "conservative"
      },
      "normal": {
        "notional_value": 12509.92,
        "quantity": 423.57,
        "max_loss": 300.00,
        "risk_percent": 3.0,
        "mode": "normal"
      },
      "aggressive": {
        "notional_value": 20849.87,
        "quantity": 705.96,
        "max_loss": 500.00,
        "risk_percent": 5.0,
        "mode": "aggressive"
      }
    },
    "settings": {
      "balance": 10000,
      "risk_tolerance": 3
    }
  }
}
```

## Example Usage

```bash
# Using curl
curl -X POST http://localhost:8000/signal \
  -H "Content-Type: application/json" \
  -d '{
    "message": "longed MON at 0.029529 sl: 0.02835 (0.5% risk)",
    "balance": 10000,
    "risk_tolerance": 3
  }'
```

## Features

- ✅ Natural language parsing using Claude API
- ✅ Automatic direction detection (LONG/SHORT)
- ✅ Position sizing with 3 risk modes (Conservative, Normal, Aggressive)
- ✅ Take profit calculations (0.5R and 1.25R)
- ✅ Exit strategy (35% at TP1, 50% at TP2, 15% manual)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Claude API key from Anthropic | Yes |

## License

MIT