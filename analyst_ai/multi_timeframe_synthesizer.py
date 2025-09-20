# F:\ShadowVanguard_Legion_Godspeed\analyst_ai\multi_timeframe_synthesizer.py
# Version 15.0 - Prometheus, The Timeless Oracle

import logging
import pandas as pd
from typing import Dict, Any, List

from core.data_models import MarketDataFrame

logger = logging.getLogger("MultiTimeframeSynthesizer")

class MultiTimeframeSynthesizer:
    """
    THE TIMELESS ORACLE: This is a master clockmaker for the Legion. It does not
    analyze the market itself, but enables true strategic insight by synthesizing
    higher timeframe data from a single, high-frequency stream of truth.
    It takes the base tactical data (e.g., 5m) and, on the fly, forges the
    1h and 4h strategic charts, making them available to all other analysts.
    This unit is the heart of the Watchtower.
    """
    def __init__(self, config: Dict[str, Any]):
        # The configuration is read from the new, dedicated section in settings.yaml
        self.config = config.get('multi_timeframe_synthesizer', {})
        self.target_timeframes = self.config.get('target_timeframes', ['1h', '4h'])
        self.base_timeframe = self.config.get('base_timeframe', '5m')
        
        # This mapping is crucial for pandas' resample function.
        self.aggregation_rules = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        
        logger.info(f"[MultiTimeframeSynthesizer] The Timeless Oracle v15.0 is online. Synthesizing {self.target_timeframes} from base '{self.base_timeframe}'.")

    def synthesize(self, mdf: MarketDataFrame) -> MarketDataFrame:
        """
        Takes the central intelligence packet (MDF), enriches its ohlcv_multidim
        attribute with higher timeframe data, and returns the enriched packet.
        This method is the core ritual of the Oracle.
        """
        # --- Defensive Protocol: Ensure the Stream of Truth is Valid ---
        base_df = mdf.ohlcv_multidim.get(self.base_timeframe)
        if base_df is None or base_df.empty or len(base_df) < 2:
            logger.warning(f"Base timeframe '{self.base_timeframe}' data is missing or insufficient for synthesis. Skipping multi-timeframe analysis.")
            return mdf

        try:
            # --- The Sacred Ritual of Time Synthesis ---
            for tf in self.target_timeframes:
                # pandas' resample is the scientifically correct and industry-standard
                # method for this conversion. It is fast, accurate, and battle-hardened.
                # 'T' is used for minute-based frequencies ('15T', '60T'), 'H' for hourly.
                # We need to map '5m' to '5T', '1h' to '1H' or '60T' etc.
                pandas_freq = tf.replace('m', 'T').replace('h', 'H')
                
                # Perform the resampling based on the sacred rules.
                resampled_df = base_df.resample(pandas_freq).agg(self.aggregation_rules)
                
                # Remove any rows that might be empty due to resampling gaps.
                resampled_df.dropna(inplace=True)
                
                # Add the newly forged strategic chart to the central intelligence packet.
                if not resampled_df.empty:
                    mdf.ohlcv_multidim[tf] = resampled_df
                    logger.debug(f"Successfully synthesized '{tf}' timeframe with {len(resampled_df)} candles.")

        except Exception as e:
            logger.error(f"A critical error occurred during time synthesis for timeframe '{tf}': {e}", exc_info=True)
        
        # Return the enriched MDF, now carrying multi-timeframe wisdom.
        return mdf