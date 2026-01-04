"""
Examples of using Telegram Gateway for logging and notifications

These examples show how to integrate Telegram notifications into your trading system.
"""

import asyncio
from telegram_gateway import send_telegram_message, TelegramGateway


async def example_1_simple_notification():
    """Example 1: Simple notification after calculation"""

    # Simulated trade calculation result
    trade_data = {
        "symbol": "BTC",
        "entry": 50000,
        "stop_loss": 49000,
        "quantity": 0.3
    }

    # Send notification
    message = f"""🔔 Position Size Calculated

Symbol: {trade_data['symbol']}
Entry: ${trade_data['entry']:,.2f}
Stop Loss: ${trade_data['stop_loss']:,.2f}
Quantity: {trade_data['quantity']} BTC"""

    await send_telegram_message(
        chat_id="@your_channel",  # or use chat ID like "123456789"
        message=message
    )


async def example_2_trade_execution_log():
    """Example 2: Log trade execution"""

    gateway = TelegramGateway()

    # After calculating position size
    message = """✅ Trade Signal Processed

📊 **BTC LONG**
💰 Entry: $50,000
🎯 TP1: $50,500 (35%)
🎯 TP2: $51,250 (50%)
🛑 SL: $49,000

💼 Position: $15,000 USDT
📈 Quantity: 0.3 BTC
⚠️ Max Loss: $300"""

    success = await gateway.send_message(
        chat_id="@trading_logs",
        message=message
    )

    if success:
        print("Log sent to Telegram")


async def example_3_integration_with_rest_api():
    """Example 3: How to integrate with REST API endpoint"""

    # This would be inside your rest_api.py /signal endpoint
    # After processing the signal...

    trade_summary = {
        "symbol": "MON",
        "direction": "long",
        "entry": 0.029529,
        "tp1": 0.029882,
        "tp2": 0.029970,
        "sl": 0.02835,
        "quantity": 423.57
    }

    # Format message
    message = f"""🚀 NEW SIGNAL

**{trade_summary['symbol']} {trade_summary['direction'].upper()}**
Entry: {trade_summary['entry']}
TP1: {trade_summary['tp1']} (35%)
TP2: {trade_summary['tp2']} (50%)
SL: {trade_summary['sl']}

Position: {trade_summary['quantity']} {trade_summary['symbol']}"""

    # Send to Telegram (non-blocking)
    await send_telegram_message("@your_channel", message)


async def example_4_error_logging():
    """Example 4: Log errors to Telegram"""

    try:
        # Simulated error scenario
        raise ValueError("Failed to parse trade signal")
    except Exception as e:
        error_message = f"""⚠️ **ERROR ALERT**

Error: {str(e)}
Endpoint: /signal
Time: 2025-01-04 10:30:00

Please investigate!"""

        await send_telegram_message(
            chat_id="@error_logs",
            message=error_message
        )


# How to use in your code:

# Option 1: In async context (like FastAPI endpoint)
async def in_fastapi_endpoint():
    """Example usage in FastAPI"""
    # After processing trade...
    await send_telegram_message("@channel", "Trade processed!")


# Option 2: In sync context (if needed)
def in_sync_context():
    """Example usage in synchronous code"""
    from telegram_gateway import TelegramGateway

    gateway = TelegramGateway()
    gateway.send_message_sync("@channel", "Trade processed!")


# Run examples
if __name__ == "__main__":
    print("Telegram Gateway Usage Examples")
    print("================================\n")

    print("Example 1: Simple Notification")
    asyncio.run(example_1_simple_notification())

    print("\nExample 2: Trade Execution Log")
    asyncio.run(example_2_trade_execution_log())

    print("\nExample 3: REST API Integration")
    asyncio.run(example_3_integration_with_rest_api())

    print("\nExample 4: Error Logging")
    asyncio.run(example_4_error_logging())

    print("\n✅ All examples completed!")
