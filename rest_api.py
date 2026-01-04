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
from config import get_config_manager


app = FastAPI(title="Trading Signal API", version="1.0.0")


class SignalRequest(BaseModel):
    """Request model for incoming trade signals"""
    message: str  # Contains telegram handle and trade data


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
    Extracts telegram handle from message and looks up user config from Firebase.

    Args:
        request: SignalRequest containing the raw message

    Returns:
        SignalResponse with parsed trade data, position sizing, and take profits

    Example request:
        POST /signal
        {
            "message": "@SpaghettiRavioli longed MON at 0.029529 sl: 0.02835 (0.5% risk)"
        }
    """
    try:
        # Step 1: Parse the message using LLM gateway (extracts telegram_handle + trade data)
        trade_data = parse_trade_signal(request.message)

        if not trade_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse trade signal from message"
            )

        # Step 2: Get user configuration from Firebase
        telegram_handle = trade_data['telegram_handle']
        config_manager = get_config_manager()
        user_config = config_manager.get_user_config(telegram_handle)

        if not user_config:
            raise HTTPException(
                status_code=404,
                detail=f"User @{telegram_handle} not found in database. Please register first."
            )

        # Extract user settings
        balance = user_config['account_balance']
        risk_tolerance = user_config['risk_appetite']

        if balance <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"User @{telegram_handle} has no account balance set"
            )

        # Step 3: Calculate take profits
        tps = calculate_take_profits(
            entry=trade_data['entry'],
            stop_loss=trade_data['stop_loss']
        )

        # Step 4: Calculate position sizing for all modes
        position_sizing = calculate_all_position_sizing_modes(
            entry=trade_data['entry'],
            stop_loss=trade_data['stop_loss'],
            balance=balance,
            user_risk_tolerance=risk_tolerance
        )

        # Step 5: Combine all data
        response_data = {
            "trade": trade_data,
            "take_profits": tps,
            "position_sizing": position_sizing,
            "user_settings": {
                "telegram_handle": telegram_handle,
                "balance": balance,
                "risk_tolerance": risk_tolerance
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
