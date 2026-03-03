"""
Exchange client module for fetching prices and liquidity data from multiple DEXs.
Implements robust error handling, rate limiting, and connection pooling.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime
import json
from decimal import Decimal
import time
from enum import Enum

from config.arbitrage_config import ExchangeConfig, ExchangeType

logger = logging.getLogger(__name__)

class ExchangeError(Exception):
    """Custom exception for exchange-related errors"""
    pass

class ConnectionState(Enum):
    """Connection state enumeration"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

@dataclass
class TokenPrice:
    """Token price data structure"""
    token_address: str
    token_symbol: str
    price_usd: Decimal
    liquidity_usd: Decimal
    volume_24h_usd: Decimal
    price_change_24h: float
    exchange: str
    timestamp: datetime
    confidence_score: float  # 0-1 confidence in price accuracy

@dataclass
class ExchangeHealth:
    """Exchange health metrics"""
    exchange_name: str
    state: ConnectionState
    last_success: Optional[datetime]
    error_count: int
    avg_response_time_ms: float
    requests_per_minute