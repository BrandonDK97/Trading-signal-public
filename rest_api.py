"""
REST API for Trading Signal Processing

Receives trade signals via POST request, parses them, calculates position sizing and TPs.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from llm_gateway import parse_trade_signal
from calculate_size import calculate_all_position_sizing_modes, calculate_take_profits


app = FastAPI(title="Trading Signal API", version="1.0.0")


class SignalRequest(BaseModel):
    """Request model for incoming trade signals"""
    message: str
    balance: Optional[float] = 10000  # Default balance
    risk_tolerance: Optional[float] = 3  # Default risk %


class SignalResponse(BaseModel):
    """Response model for processed trade signals"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Trading Signal API is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/signal", response_model=SignalResponse)
async def process_signal(request: SignalRequest):
    """
    Process a trading signal message.

    Args:
        request: SignalRequest containing the message and optional balance/risk settings

    Returns:
        SignalResponse with parsed trade data, position sizing, and take profits

    Example request:
        POST /signal
        {
            "message": "longed MON at 0.029529 sl: 0.02835 (0.5% risk)",
            "balance": 10000,
            "risk_tolerance": 3
        }
    """
    try:
        # Step 1: Parse the message using LLM gateway
        trade_data = parse_trade_signal(request.message)

        if not trade_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse trade signal from message"
            )

        # Step 2: Calculate take profits
        tps = calculate_take_profits(
            entry=trade_data['entry'],
            stop_loss=trade_data['stop_loss']
        )

        # Step 3: Calculate position sizing for all modes
        position_sizing = calculate_all_position_sizing_modes(
            entry=trade_data['entry'],
            stop_loss=trade_data['stop_loss'],
            balance=request.balance,
            user_risk_tolerance=request.risk_tolerance
        )

        # Step 4: Combine all data
        response_data = {
            "trade": trade_data,
            "take_profits": tps,
            "position_sizing": position_sizing,
            "settings": {
                "balance": request.balance,
                "risk_tolerance": request.risk_tolerance
            }
        }

        return SignalResponse(success=True, data=response_data)

    except HTTPException:
        raise
    except Exception as e:
        return SignalResponse(
            success=False,
            error=f"Error processing signal: {str(e)}"
        )


if __name__ == "__main__":
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)
