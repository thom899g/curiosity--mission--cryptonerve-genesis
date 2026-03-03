"""
Configuration module for the CRYPTONERVE_GENESIS arbitrage scanner.
Handles exchange configurations, token filtering, and scanner parameters.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ExchangeType(Enum):
    """Supported exchange types"""
    DEX = "dex"
    CEX = "cex"

@dataclass
class ExchangeConfig:
    """Configuration for a single exchange"""
    name: str
    type: ExchangeType
    api_key: Optional[str] = None
    secret: Optional[str] = None
    enabled: bool = True
    rate_limit_ms: int = 1000
    max_retries: int = 3
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.enabled and self.type == ExchangeType.CEX:
            if not self.api_key or not self.secret:
                logging.warning(f"Exchange {self.name} enabled but missing API credentials")

@dataclass
class TokenFilter:
    """Filters for micro-token selection"""
    min_liquidity_usd: float = 10000.0
    max_liquidity_usd: float = 1000000.0
    min_price_change_24h: float = 2.0  # Minimum 2% price movement
    exclude_stablecoins: bool = True
    allowed_chains: List[str] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.allowed_chains is None:
            self.allowed_chains = ["ethereum", "bsc", "polygon", "arbitrum"]

@dataclass
class ScannerConfig:
    """Main scanner configuration"""
    # Exchange configurations
    exchanges: Dict[str, ExchangeConfig]
    
    # Token filtering
    token_filter: TokenFilter
    
    # Scanner parameters
    scan_interval_seconds: int = 30
    price_deviation_threshold: float = 1.5  # Minimum % difference for arbitrage
    max_slippage_percent: float = 2.0
    gas_price_buffer_percent: float = 15.0
    
    # Performance limits
    max_concurrent_requests: int = 5
    request_timeout_seconds: int = 10
    
    # Logging & monitoring
    log_level: str = "INFO"
    enable_telegram_alerts: bool = True
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if len(self.exchanges) < 2:
            errors.append("At least 2 exchanges required for arbitrage detection")
        
        if self.price_deviation_threshold < 0.1:
            errors.append("Price deviation threshold too low (<0.1%)")
        
        if self.scan_interval_seconds < 5:
            errors.append("Scan interval too fast (<5 seconds)")
        
        enabled_exchanges = [e for e in self.exchanges.values() if e.enabled]
        if len(enabled_exchanges) < 2:
            errors.append("Less than 2 exchanges enabled")
        
        return errors

# Default configuration
def get_default_config() -> ScannerConfig:
    """Get default scanner configuration"""
    
    exchanges = {
        "uniswap_v3": ExchangeConfig(
            name="uniswap_v3",
            type=ExchangeType.DEX,
            enabled=True,
            rate_limit_ms=500
        ),
        "pancakeswap": ExchangeConfig(
            name="pancakeswap",
            type=ExchangeType.DEX,
            enabled=True,
            rate_limit_ms=500
        ),
        "sushiswap": ExchangeConfig(
            name="sushiswap",
            type=ExchangeType.DEX,
            enabled=True,
            rate_limit_ms=500
        ),
        "quickswap": ExchangeConfig(
            name="quickswap",
            type=ExchangeType.DEX,
            enabled=True,
            rate_limit_ms=500
        )
    }
    
    token_filter = TokenFilter(
        min_liquidity_usd=5000.0,
        max_liquidity_usd=500000.0,
        min_price_change_24h=2.0,
        exclude_stablecoins=True,
        allowed_chains=["ethereum", "bsc", "polygon"]
    )
    
    return ScannerConfig(
        exchanges=exchanges,
        token_filter=token_filter,
        scan_interval_seconds=30,
        price_deviation_threshold=1.5,
        max_slippage_percent=2.0,
        gas_price_buffer_percent=15.0,
        max_concurrent_requests=5,
        request_timeout_seconds=10,
        log_level="INFO",
        enable_telegram_alerts=True
    )