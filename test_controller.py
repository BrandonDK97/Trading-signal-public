"""
Test Controller for Testing Trading Signal System

Provides test endpoints to verify functionality without external dependencies.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import get_config_manager
from llm_gateway import parse_trade_signal
from calculate_size import calculate_all_position_sizing_modes, calculate_take_profits

app = FastAPI(title="Trading Signal Test API", version="1.0.0")


# ============================================================================
# Request/Response Models
# ============================================================================

class UpdateBalanceRequest(BaseModel):
    """Request to update user balance"""
    balance: float


class UpdateLeverageRequest(BaseModel):
    """Request to update coin leverage"""
    leverage: int


class TradeMessageRequest(BaseModel):
    """Request to test trade message processing"""
    message: str


# ============================================================================
# Test Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "message": "Trading Signal Test Controller",
        "endpoints": {
            "get_user": "GET /test/user/{telegram_handle}",
            "update_balance": "PUT /test/user/{telegram_handle}/balance",
            "change_leverage": "PUT /test/leverage/{symbol}",
            "test_trade": "POST /test/trade",
            "get_all_users": "GET /test/users",
            "get_all_leverages": "GET /test/leverages"
        }
    }


@app.get("/test/user/{telegram_handle}")
async def get_user_config(telegram_handle: str):
    """
    Get user configuration by telegram handle

    Args:
        telegram_handle: User's telegram handle (with or without @)

    Returns:
        User configuration from Firebase

    Example:
        GET /test/user/@john_trader
        GET /test/user/john_trader
    """
    try:
        manager = get_config_manager()
        config = manager.get_user_config(telegram_handle)

        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"User {telegram_handle} not found"
            )

        return {
            "success": True,
            "data": config
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching user config: {str(e)}"
        )


@app.get("/test/users")
async def get_all_users():
    """
    Get all user configurations

    Returns:
        List of all users in the system
    """
    try:
        manager = get_config_manager()
        users = manager.get_all_users()

        return {
            "success": True,
            "count": len(users),
            "data": users
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching users: {str(e)}"
        )


@app.put("/test/user/{telegram_handle}/balance")
async def update_user_balance(telegram_handle: str, request: UpdateBalanceRequest):
    """
    Update user's account balance (persistent)

    Args:
        telegram_handle: User's telegram handle
        request: UpdateBalanceRequest with new balance

    Returns:
        Success status and updated config

    Example:
        PUT /test/user/@john_trader/balance
        {
            "balance": 15000.00
        }
    """
    try:
        manager = get_config_manager()

        # Check if user exists
        if not manager.user_exists(telegram_handle):
            raise HTTPException(
                status_code=404,
                detail=f"User {telegram_handle} not found. Create user first."
            )

        # Update balance
        success = manager.update_user_config(
            telegram_handle=telegram_handle,
            account_balance=request.balance
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update balance"
            )

        # Get updated config
        updated_config = manager.get_user_config(telegram_handle)

        return {
            "success": True,
            "message": f"Balance updated to ${request.balance:,.2f}",
            "data": updated_config
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating balance: {str(e)}"
        )


@app.get("/test/leverage/{symbol}")
async def get_leverage(symbol: str):
    """
    Get leverage for a specific symbol

    Args:
        symbol: Trading symbol (e.g., BTC, ETH)

    Returns:
        Leverage value for the symbol
    """
    try:
        manager = get_config_manager()
        leverage = manager.get_leverage_for_symbol(symbol)

        return {
            "success": True,
            "symbol": symbol.upper(),
            "leverage": leverage
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching leverage: {str(e)}"
        )


@app.get("/test/leverages")
async def get_all_leverages():
    """
    Get all symbol leverage mappings

    Returns:
        Dictionary of all symbol->leverage mappings
    """
    try:
        manager = get_config_manager()
        leverages = manager.get_all_leverages()

        return {
            "success": True,
            "count": len(leverages),
            "data": leverages
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching leverages: {str(e)}"
        )


@app.put("/test/leverage/{symbol}")
async def change_leverage(symbol: str, request: UpdateLeverageRequest):
    """
    Change or create leverage for a coin symbol (persistent)

    Args:
        symbol: Trading symbol (e.g., BTC, ETH)
        request: UpdateLeverageRequest with leverage value

    Returns:
        Success status and updated leverage

    Example:
        PUT /test/leverage/BTC
        {
            "leverage": 100
        }

        PUT /test/leverage/NEWCOIN
        {
            "leverage": 25
        }
    """
    try:
        manager = get_config_manager()

        # Validate leverage (reasonable range)
        if request.leverage < 1 or request.leverage > 125:
            raise HTTPException(
                status_code=400,
                detail="Leverage must be between 1 and 125"
            )

        # Set leverage (creates if doesn't exist, updates if exists)
        success = manager.set_leverage_for_symbol(symbol, request.leverage)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update leverage"
            )

        return {
            "success": True,
            "message": f"Leverage for {symbol.upper()} set to {request.leverage}x",
            "data": {
                "symbol": symbol.upper(),
                "leverage": request.leverage
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating leverage: {str(e)}"
        )


@app.post("/test/trade")
async def test_trade_message(request: TradeMessageRequest):
    """
    Test end-to-end trade message processing

    This endpoint simulates the full trading signal flow:
    1. Parse message using LLM gateway
    2. Fetch leverage for symbol
    3. Calculate take profits
    4. Get all users from Firebase
    5. Calculate position sizing for each user
    6. Return complete results

    Args:
        request: TradeMessageRequest with natural language message

    Returns:
        Complete trade processing results including position sizing for all users

    Example:
        POST /test/trade
        {
            "message": "@SpaghettiRavioli longed BTC at 50000 sl: 49000"
        }

        POST /test/trade
        {
            "message": "Tradoor long ETH 3000-2900 sl: 2850"
        }
    """
    try:
        # Step 1: Parse the message using LLM gateway
        print(f"\n{'='*70}")
        print(f"🧪 TEST: Processing Trade Message")
        print(f"{'='*70}")
        print(f"Message: {request.message}\n")

        trade_data = parse_trade_signal(request.message)

        if not trade_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse trade signal from message"
            )

        print(f"✅ Step 1: Parsed trade data")
        print(f"   Symbol: {trade_data['symbol']}")
        print(f"   Direction: {trade_data['direction']}")
        print(f"   Entry: {trade_data['entry']}")
        print(f"   Stop Loss: {trade_data['stop_loss']}")

        # Extract signal sender
        signal_sender = trade_data['telegram_handle']

        # Step 2: Get leverage for this symbol
        config_manager = get_config_manager()
        symbol = trade_data['symbol']
        leverage = config_manager.get_leverage_for_symbol(symbol)

        print(f"\n✅ Step 2: Fetched leverage")
        print(f"   {symbol}: {leverage}x")

        # Step 3: Calculate take profits
        tps = calculate_take_profits(
            entry=trade_data['entry'],
            stop_loss=trade_data['stop_loss']
        )

        print(f"\n✅ Step 3: Calculated take profits")
        print(f"   TP1: {tps['tp1_price']} ({tps['tp1_percent']}%)")
        print(f"   TP2: {tps['tp2_price']} ({tps['tp2_percent']}%)")

        # Step 4: Get ALL users from Firebase
        all_users = config_manager.get_all_users()

        if not all_users:
            raise HTTPException(
                status_code=404,
                detail="No users found in database. Please create users first."
            )

        print(f"\n✅ Step 4: Fetched users")
        print(f"   Found {len(all_users)} user(s)")

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
                print(f"   ⚠️  Skipped {telegram_handle}: No balance")
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

            print(f"   ✅ Calculated {telegram_handle}: {position_sizing['normal']['quantity']} {symbol}")

        # Step 6: Combine all data
        response_data = {
            "signal_sender": signal_sender,
            "trade": {
                "symbol": trade_data['symbol'],
                "direction": trade_data['direction'],
                "entry_type": trade_data.get('entry_type', 'single'),
                "entry": trade_data['entry'],
                "entry_high": trade_data.get('entry_high'),
                "entry_low": trade_data.get('entry_low'),
                "stop_loss": trade_data['stop_loss'],
                "leverage": leverage
            },
            "take_profits": tps,
            "users": user_calculations,
            "summary": {
                "total_users": len(all_users),
                "calculated_users": len([u for u in user_calculations if u['status'] == 'calculated']),
                "skipped_users": len([u for u in user_calculations if u['status'] == 'skipped'])
            }
        }

        print(f"\n✅ Step 5: Complete!")
        print(f"   Calculated: {response_data['summary']['calculated_users']} users")
        print(f"   Skipped: {response_data['summary']['skipped_users']} users")
        print(f"{'='*70}\n")

        return {
            "success": True,
            "data": response_data
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing trade: {str(e)}"
        )


# ============================================================================
# Helper Endpoints for Setup
# ============================================================================

@app.post("/test/setup/user")
async def create_test_user(
    telegram_handle: str,
    balance: float = 10000,
    risk_appetite: float = 3.0
):
    """
    Create a test user for testing

    Query Parameters:
        telegram_handle: User's telegram handle
        balance: Initial balance (default: 10000)
        risk_appetite: Risk percentage (default: 3.0)
    """
    try:
        manager = get_config_manager()

        success = manager.create_user_config(
            telegram_handle=telegram_handle,
            account_balance=balance,
            risk_appetite=risk_appetite
        )

        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"User {telegram_handle} already exists or failed to create"
            )

        config = manager.get_user_config(telegram_handle)

        return {
            "success": True,
            "message": f"Test user created: {telegram_handle}",
            "data": config
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )


@app.post("/test/setup/leverages")
async def initialize_default_leverages():
    """
    Initialize default leverage values for common coins

    Sets default leverages:
    - BTC: 100x
    - ETH: 75x
    - SOL: 50x
    - HYPE: 25x
    - etc.
    """
    try:
        manager = get_config_manager()
        success = manager.initialize_default_leverages()

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize default leverages"
            )

        leverages = manager.get_all_leverages()

        return {
            "success": True,
            "message": "Default leverages initialized",
            "count": len(leverages),
            "data": leverages
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing leverages: {str(e)}"
        )


if __name__ == "__main__":
    # Run the test API server
    print("\n" + "="*70)
    print("🧪 TRADING SIGNAL TEST CONTROLLER")
    print("="*70)
    print("\nStarting test API server on http://localhost:8001")
    print("\nAvailable endpoints:")
    print("  - GET  /test/user/{handle}          - Get user config")
    print("  - PUT  /test/user/{handle}/balance  - Update balance")
    print("  - GET  /test/leverage/{symbol}      - Get leverage")
    print("  - PUT  /test/leverage/{symbol}      - Set leverage")
    print("  - POST /test/trade                  - Test E2E flow")
    print("  - GET  /test/users                  - Get all users")
    print("  - GET  /test/leverages              - Get all leverages")
    print("\nSetup helpers:")
    print("  - POST /test/setup/user             - Create test user")
    print("  - POST /test/setup/leverages        - Init default leverages")
    print("\n" + "="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8001)
