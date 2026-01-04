"""
LLM Gateway for parsing trading signals using Claude API

Sends natural language trading messages to Claude API and receives structured JSON response.
"""

import os
import json
from anthropic import Anthropic
from typing import Dict, Optional


def parse_trade_signal(message: str) -> Optional[Dict]:
    """
    Parse a natural language trade signal using Claude API.

    Args:
        message: Raw message string containing trade information

    Returns:
        Dictionary containing:
            - symbol: Trading symbol (e.g., "MON", "BTC")
            - direction: Trade direction ("long" or "short")
            - entry: Entry price
            - stop_loss: Stop loss price
            - risk_percent: Optional risk percentage if mentioned

    Example:
        >>> message = "longed MON at 0.029529 sl: 0.02835 (0.5% risk)"
        >>> result = parse_trade_signal(message)
        >>> print(result)
        {
            'symbol': 'MON',
            'direction': 'long',
            'entry': 0.029529,
            'stop_loss': 0.02835,
            'risk_percent': 0.5
        }
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    client = Anthropic(api_key=api_key)

    # Construct prompt for Claude
    prompt = f"""Parse the following trading signal message and extract the trade information.

Message:
{message}

Please extract and return ONLY a JSON object with these fields:
- symbol: the trading pair/token symbol (uppercase)
- direction: "long" or "short"
- entry: entry price (as a number)
- stop_loss: stop loss price (as a number)
- risk_percent: risk percentage if mentioned (as a number, or null if not mentioned)

Return ONLY the JSON object, no other text or explanation.

Example output format:
{{"symbol": "BTC", "direction": "long", "entry": 50000, "stop_loss": 49000, "risk_percent": 1.0}}"""

    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract text from response
        response_text = response.content[0].text.strip()

        # Parse JSON from response
        trade_data = json.loads(response_text)

        # Validate required fields
        required_fields = ['symbol', 'direction', 'entry', 'stop_loss']
        for field in required_fields:
            if field not in trade_data:
                raise ValueError(f"Missing required field: {field}")

        # Normalize direction to lowercase
        trade_data['direction'] = trade_data['direction'].lower()

        # Validate direction
        if trade_data['direction'] not in ['long', 'short']:
            raise ValueError(f"Invalid direction: {trade_data['direction']}")

        return trade_data

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Claude response: {e}")
        print(f"Response was: {response_text}")
        return None
    except Exception as e:
        print(f"Error parsing trade signal: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Test message
    test_message = """👤 From: WG Bot

💬 Message: @SpaghettiRavioli
longed MON at 0.029529 sl: 0.02835 (0.5% risk)"""

    print("Testing LLM Gateway...\n")
    print(f"Input message:\n{test_message}\n")

    result = parse_trade_signal(test_message)

    if result:
        print("✅ Parsed successfully!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Failed to parse message")
