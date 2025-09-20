# F:\ShadowVanguard_Legion_Godspeed\core\live_data_provider.py
# Version 2.9 - The MEXC Ambassador

import logging
import time
from typing import Dict, Any, Optional
import ccxt
import pandas as pd
from datetime import datetime, timezone
from collections import deque

# [PACT KEPT]: Core model imports are preserved.
from .data_models import MarketDataFrame
from .interface_book import IDataProvider

logger = logging.getLogger("LiveDataProvider")

class LiveDataProvider(IDataProvider):
    """
    THE MEXC AMBASSADOR: This version officially adds the diplomatic protocols for the
    MEXC forward base. The ambassador's universal logic is expanded to recognize and
    correctly apply the standard sandbox protocol for MEXC, making it fully operational
    for Operation: New Hope.
    """
    def __init__(self, main_config: Dict[str, Any], live_config: Dict[str, Any], api_key: str, secret_key: str, passphrase: Optional[str], is_paper: bool):
        # [PACT KEPT]: Core configuration reading is preserved.
        self.live_config = live_config
        self.main_config = main_config
        
        self.exchange_id = self.live_config.get('exchange', 'mexc')
        self.symbol = self.main_config.get('target_symbol', 'BTC/USDT:USDT')
        self.market_type = self.live_config.get('market_type', 'swap')
        
        self.base_timeframe_str = f"{self.main_config.get('data_provider', {}).get('timeframe_minutes', 5)}m"
        self.fetch_interval_seconds = self.live_config.get('data_fetch_interval_seconds', 5)
        self.data_window_size = self.main_config.get('data_provider', {}).get('data_window_size', 600)
        
        self.request_timeout_ms = self.live_config.get('request_timeout_ms', 30000)
        self.max_retries = self.live_config.get('max_retries', 5)

        self.last_candle_timestamp = None
        self.is_warmed_up = False
        self.data_buffer = deque(maxlen=self.data_window_size)

        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            
            exchange_config = {
                'apiKey': api_key,
                'secret': secret_key,
                'password': passphrase, # ccxt will ignore this if not needed by the exchange
                'options': { 'defaultType': self.market_type },
                'timeout': self.request_timeout_ms,
            }

            self.exchange = exchange_class(exchange_config)
            
            # [SURGICAL UPGRADE - MEXC DIPLOMACY PROTOCOL]:
            if is_paper:
                logger.warning(f"!!! OPERATING IN PAPER TRADING ({self.exchange_id.upper()} DEMO) MODE !!!")
                
                if self.exchange_id == 'okx':
                    self.exchange.headers = { 'x-simulated-trading': '1' }
                    logger.info("OKX-specific demo trading protocol enabled via headers.")
                
                elif self.exchange_id == 'kucoinfutures':
                    kucoin_sandbox_url = 'https://api-sandbox-futures.kucoin.com'
                    self.exchange.urls['api'] = {
                        'public': kucoin_sandbox_url, 'private': kucoin_sandbox_url,
                        'futuresPublic': kucoin_sandbox_url, 'futuresPrivate': kucoin_sandbox_url,
                    }
                    logger.info(f"Manual and COMPLETE sandbox route map set for KuCoin Futures.")
                
                # New protocol for our new forward base.
                elif self.exchange_id == 'mexc':
                    if self.exchange.has['sandbox']:
                        self.exchange.set_sandbox_mode(True)
                        logger.info(f"Standard sandbox mode enabled for MEXC.")
                    else:
                        logger.error(f"MEXC is selected, but ccxt reports no sandbox support for it.")
                        raise NotImplementedError(f"MEXC sandbox not supported by this ccxt version.")

                elif self.exchange.has['sandbox']:
                    self.exchange.set_sandbox_mode(True)
                    logger.info(f"Standard sandbox mode enabled for {self.exchange_id}.")
                
                else:
                    logger.error(f"Paper trading selected, but no specific demo protocol is defined for {self.exchange_id}.")
                    raise NotImplementedError(f"Demo mode protocol not implemented for {self.exchange_id}")
            else:
                logger.warning("!!! WARNING: OPERATING IN LIVE TRADING MODE WITH REAL CAPITAL !!!")

        except Exception as e:
            logger.critical(f"Failed to initialize exchange '{self.exchange_id}': {e}", exc_info=True)
            raise
            
        logger.info(f"[LiveDataProvider] The MEXC Ambassador v2.9 online, connected to {self.exchange_id.upper()}.")

    # [PACT KEPT]: All other methods are 100% PRESERVED.

    def _fetch_with_retry(self, limit: int) -> Optional[list]:
        for attempt in range(self.max_retries):
            try:
                return self.exchange.fetch_ohlcv(self.symbol, self.base_timeframe_str, limit=limit)
            except (ccxt.RequestTimeout, ccxt.NetworkError) as e:
                logger.warning(f"Network error on attempt {attempt + 1}/{self.max_retries}: {e}. Retrying...")
                time.sleep(self.fetch_interval_seconds * (attempt + 1))
            except Exception as e:
                 logger.error(f"An unexpected error occurred during fetch: {e}", exc_info=True)
                 return None
        logger.error(f"Failed to fetch data after {self.max_retries} attempts. Giving up on this cycle.")
        return None
    
    def _warmup_memory_buffer(self) -> bool:
        logger.info(f"Warming up memory buffer... fetching last {self.data_window_size} candles.")
        ohlcv = self._fetch_with_retry(limit=self.data_window_size)
        
        if not ohlcv or len(ohlcv) < 2:
            logger.error("Failed to fetch sufficient historical data for warmup.")
            return False
        
        complete_candles = ohlcv[:-1]
        self.data_buffer.extend(complete_candles)
        last_complete_candle = complete_candles[-1]
        self.last_candle_timestamp = pd.to_datetime(last_complete_candle[0], unit='ms', utc=True)
        self.is_warmed_up = True
        logger.info(f"Memory buffer warmup complete. Last known candle: {self.last_candle_timestamp}")
        return True
        
    def fetch_next_market_data(self) -> Optional[MarketDataFrame]:
        if not self.is_warmed_up:
            if not self._warmup_memory_buffer():
                return None
            return self._create_mdf_from_buffer()

        while True:
            ohlcv = self._fetch_with_retry(limit=2)
            if not ohlcv or len(ohlcv) < 2:
                logger.warning("Received empty/incomplete data despite retries. Waiting...")
                time.sleep(self.fetch_interval_seconds)
                continue
            
            latest_complete_candle = ohlcv[-2]
            candle_timestamp = pd.to_datetime(latest_complete_candle[0], unit='ms', utc=True)
            
            if candle_timestamp > self.last_candle_timestamp:
                logger.info(f"New {self.base_timeframe_str} candle detected for {candle_timestamp}")
                self.last_candle_timestamp = candle_timestamp
                self.data_buffer.append(latest_complete_candle)
                return self._create_mdf_from_buffer()
            else:
                logger.debug(f"No new candle since {self.last_candle_timestamp}. Waiting...")
                time.sleep(self.fetch_interval_seconds)

    def _create_mdf_from_buffer(self) -> MarketDataFrame:
        ohlcv_list = list(self.data_buffer)
        if not ohlcv_list:
            return MarketDataFrame(timestamp=datetime.now(timezone.utc), symbol=self.symbol)
            
        df = pd.DataFrame(ohlcv_list, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df.set_index('timestamp', inplace=True)
        latest_timestamp = df.index[-1].to_pydatetime()
        
        return MarketDataFrame(
            timestamp=latest_timestamp,
            symbol=self.symbol,
            ohlcv_multidim={self.base_timeframe_str: df}
        )
        
    def has_more_data(self) -> bool:
        return True