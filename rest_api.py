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
    Process a trading signal message for ALL users.
    Extracts signal sender and trade data, then calculates position sizing for each user in database.

    Args:
        request: SignalRequest containing the raw message

    Returns:
        SignalResponse with trade data and personalized position sizing for each user

    Example request:
        POST /signal
        {
            "message": "@SpaghettiRavioli longed MON at 0.029529 sl: 0.02835 (0.5% risk)"
        }
    """
    try:
        # Step 1: Parse the message using LLM gateway (extracts sender + trade data)
        trade_data = parse_trade_signal(request.message)

        if not trade_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse trade signal from message"
            )

        # Extract signal sender (not used for calculation, just for logging)
        signal_sender = trade_data['telegram_handle']

        # Step 2: Get leverage for this symbol from system config
        config_manager = get_config_manager()
        symbol = trade_data['symbol']
        leverage = config_manager.get_leverage_for_symbol(symbol)

        # Step 3: Calculate take profits (same for all users)
        tps = calculate_take_profits(
            entry=trade_data['entry'],
            stop_loss=trade_data['stop_loss']
        )

        # Step 4: Get ALL user configurations from Firebase
        all_users = config_manager.get_all_users()

        if not all_users:
            raise HTTPException(
                status_code=404,
                detail="No users found in database. Please register users first."
            )

        # Step 5: Calculate position sizing for EACH user
        user_calculations = []

        for user_config in all_users:
            telegram_handle = user_config['telegram_handle']
            balance = user_config['account_balance']
            risk_tolerance = user_config['risk_appetite']

            # Skip users with no balance
            if balance <= 0:
                user_calculations.append({
                    "telegram_handle": telegram_handle,
                    "status": "skipped",
                    "reason": "No account balance set"
                })
                continue

            # Calculate position sizing for this user (with leverage)
            position_sizing = calculate_all_position_sizing_modes(
                entry=trade_data['entry'],
                stop_loss=trade_data['stop_loss'],
                balance=balance,
                user_risk_tolerance=risk_tolerance,
                leverage=leverage
            )

            user_calculations.append({
                "telegram_handle": telegram_handle,
                "status": "calculated",
                "balance": balance,
                "risk_tolerance": risk_tolerance,
                "position_sizing": position_sizing
            })

        # Step 6: Combine all data
        response_data = {
            "signal_sender": signal_sender,
            "trade": {
                "symbol": trade_data['symbol'],
                "direction": trade_data['direction'],
                "entry": trade_data['entry'],
                "stop_loss": trade_data['stop_loss'],
                "leverage": leverage
            },
            "take_profits": tps,
            "users": user_calculations,
            "total_users": len(all_users),
            "calculated_users": len([u for u in user_calculations if u['status'] == 'calculated']),
            "skipped_users": len([u for u in user_calculations if u['status'] == 'skipped'])
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
