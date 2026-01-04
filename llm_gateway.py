"""
LLM Gateway for parsing trading signals using Claude API

Sends natural language trading messages to Claude API and receives structured JSON response.
"""

import os
import json
from anthropic import Anthropic
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def parse_trade_signal(message: str) -> Optional[Dict]:
    """
    Parse a natural language trade signal using Claude API.
    Extracts both the telegram handle and trade information from the message.
    Supports both single entry and range/scaled entries.

    Args:
        message: Raw message string containing telegram handle and trade information

    Returns:
        Dictionary containing:
            - telegram_handle: User's telegram handle (without @)
            - symbol: Trading symbol (e.g., "MON", "BTC")
            - direction: Trade direction ("long" or "short")
            - entry_type: "single" or "range"
            - entry: Entry price (for single) or average of range
            - entry_high: High end of range (for range entries)
            - entry_low: Low end of range (for range entries)
            - stop_loss: Stop loss price
            - risk_percent: Optional risk percentage if mentioned

    Example 1 (Single Entry):
        >>> message = "@SpaghettiRavioli longed MON at 0.029529 sl: 0.02835"
        >>> result = parse_trade_signal(message)
        {
            'telegram_handle': 'SpaghettiRavioli',
            'symbol': 'MON',
            'direction': 'long',
            'entry_type': 'single',
            'entry': 0.029529,
            'stop_loss': 0.02835
        }

    Example 2 (Range Entry):
        >>> message = "Tradoor long 1.66 - 1.61 Sl: 1.57"
        >>> result = parse_trade_signal(message)
        {
            'telegram_handle': 'Tradoor',
            'symbol': 'Tradoor',
            'direction': 'long',
            'entry_type': 'range',
            'entry': 1.635,  # average
            'entry_high': 1.66,
            'entry_low': 1.61,
            'stop_loss': 1.57
        }
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    client = Anthropic(api_key=api_key)

    # Construct prompt for Claude
    prompt = f"""Parse the following trading signal message and extract the information.

Message:
{message}

Please extract and return ONLY a JSON object with these fields:
- symbol: the trading pair/token symbol (uppercase)
- direction: "long" or "short"
- entry_type: "single" if one price, or "range" if a price range (e.g., "1.66 - 1.61")
- entry: the entry price (if single) or average of range (if range)
- entry_high: (only for range) the higher price of the range
- entry_low: (only for range) the lower price of the range
- stop_loss: stop loss price (as a number)
- risk_percent: risk percentage if mentioned (as a number, or null if not mentioned)

Return ONLY the JSON object, no other text or explanation.

Example 1 (Single Entry):
{{"symbol": "BTC", "direction": "long", "entry_type": "single", "entry": 50000, "stop_loss": 49000, "risk_percent": 1.0}}

Example 2 (Range Entry):
{{"symbol": "TRADOOR", "direction": "long", "entry_type": "range", "entry": 1.635, "entry_high": 1.66, "entry_low": 1.61, "stop_loss": 1.57, "risk_percent": null}}"""

    try:
        # Call Claude API
        response = client.messages.create(
             model="claude-sonnet-4-5-20250929",
            max_tokens=10,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract text from response
        response_text = response.content[0].text.strip()

         # Remove markdown code fences if present
        if response_text.startswith('```'):
            # Remove opening code fence (```json or ```)
            lines = response_text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]  # Remove first line
            # Remove closing code fence
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove last line
            response_text = '\n'.join(lines).strip()

        print("Claude response:" + response_text)

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

        # Validate entry_type and range fields
        entry_type = trade_data.get('entry_type', 'single')
        trade_data['entry_type'] = entry_type

        if entry_type == 'range':
            # For range entries, ensure we have entry_high and entry_low
            if 'entry_high' not in trade_data or 'entry_low' not in trade_data:
                raise ValueError("Range entry requires entry_high and entry_low")

            # Validate the range makes sense
            if trade_data['entry_high'] <= trade_data['entry_low']:
                raise ValueError("entry_high must be greater than entry_low")

        return trade_data

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Claude response: {e}")
        print(f"Response was: {response_text}")
        return None
    except Exception as e:
        print(f"Error parsing trade signal: {e}")
        return None