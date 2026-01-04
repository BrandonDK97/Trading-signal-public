"""
Telegram Gateway for sending notifications and logs

Provides simple interface to send messages to Telegram bot.
"""

import os
import asyncio
from typing import Optional
import aiohttp


class TelegramGateway:
    """Gateway for sending messages to Telegram"""

    def __init__(self, bot_token: Optional[str] = None):
        """
        Initialize Telegram Gateway

        Args:
            bot_token: Telegram bot token (if None, reads from TELEGRAM_BOT_TOKEN env var)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(
        self,
        chat_id: str,
        message: str,
        parse_mode: str = "Markdown"
    ) -> bool:
        """
        Send a message to a Telegram chat

        Args:
            chat_id: Telegram chat ID or username (e.g., "@username" or "123456789")
            message: Message text to send
            parse_mode: Message formatting mode ("Markdown" or "HTML")

        Returns:
            True if message sent successfully, False otherwise

        Example:
            >>> gateway = TelegramGateway()
            >>> await gateway.send_message(
            ...     chat_id="@trading_channel",
            ...     message="Trade alert: BTC Long at $50,000"
            ... )
            True
        """
        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": parse_mode
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_data = await response.json()
                        print(f"Failed to send Telegram message: {error_data}")
                        return False
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def send_message_sync(
        self,
        chat_id: str,
        message: str,
        parse_mode: str = "Markdown"
    ) -> bool:
        """
        Synchronous wrapper for send_message

        Args:
            chat_id: Telegram chat ID or username
            message: Message text to send
            parse_mode: Message formatting mode

        Returns:
            True if message sent successfully, False otherwise
        """
        return asyncio.run(self.send_message(chat_id, message, parse_mode))


# Singleton instance for easy import
_gateway_instance = None


def get_telegram_gateway() -> TelegramGateway:
    """
    Get or create singleton TelegramGateway instance

    Returns:
        TelegramGateway instance

    Example:
        >>> from telegram_gateway import get_telegram_gateway
        >>> gateway = get_telegram_gateway()
        >>> await gateway.send_message("@channel", "Hello!")
    """
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = TelegramGateway()
    return _gateway_instance


# Convenience function for quick sending
async def send_telegram_message(
    chat_id: str,
    message: str,
    parse_mode: str = "Markdown"
) -> bool:
    """
    Convenience function to send a Telegram message

    Args:
        chat_id: Telegram chat ID or username
        message: Message text to send
        parse_mode: Message formatting mode

    Returns:
        True if sent successfully

    Example:
        >>> await send_telegram_message("@channel", "Trade executed!")
    """
    gateway = get_telegram_gateway()
    return await gateway.send_message(chat_id, message, parse_mode)


# Example usage and testing
if __name__ == "__main__":
    import sys

    async def test_send():
        """Test sending a message"""
        if len(sys.argv) < 3:
            print("Usage: python telegram_gateway.py <chat_id> <message>")
            print("Example: python telegram_gateway.py @my_channel 'Test message'")
            return

        chat_id = sys.argv[1]
        message = sys.argv[2]

        print(f"Sending message to {chat_id}...")

        gateway = TelegramGateway()
        success = await gateway.send_message(chat_id, message)

        if success:
            print("✅ Message sent successfully!")
        else:
            print("❌ Failed to send message")

    # Run test
    asyncio.run(test_send())
