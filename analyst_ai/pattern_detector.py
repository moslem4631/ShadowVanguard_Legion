# F:\ShadowVanguard_Legion\analyst_ai\pattern_detector.py
# Version 2.1 - Cleanup

import logging
import pandas as pd
from typing import Dict, List, Any
import numpy as np

from core.data_models import MarketDataFrame

logger = logging.getLogger("PatternDetector")

class PatternDetector:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "swing_point_lookback": 5,
            "fvg_sensitivity": 1
        }
        logger.info("[PatternDetector] Pattern Detection unit is ready with default settings.")

    def analyze(self, mdf: MarketDataFrame) -> Dict[str, List[Dict]]:
        ohlcv_df = mdf.ohlcv.copy()
        if not ohlcv_df.index.is_unique:
             ohlcv_df = ohlcv_df.loc[~ohlcv_df.index.duplicated(keep='first')]

        swing_points = self._detect_swing_points(ohlcv_df)
        
        report = {
            "bos_choch": self._detect_bos_choch(ohlcv_df, swing_points),
            "fair_value_gaps": self._detect_fvg(ohlcv_df),
            "order_blocks": self._detect_order_blocks(ohlcv_df, swing_points)
        }
        
        summary_log = ", ".join([f"{key}: {len(value)}" for key, value in report.items() if value])
        if summary_log:
            logger.info(f"Patterns Detected: {summary_log}")
            
        return report

    def _detect_swing_points(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        n = self.config['swing_point_lookback']
        df['is_swing_high'] = df['high'].rolling(window=2*n+1, center=True).max() == df['high']
        df['swing_high'] = df.apply(lambda row: row['high'] if row['is_swing_high'] else np.nan, axis=1)
        df['is_swing_low'] = df['low'].rolling(window=2*n+1, center=True).min() == df['low']
        df['swing_low'] = df.apply(lambda row: row['low'] if row['is_swing_low'] else np.nan, axis=1)
        return {
            "highs": df['swing_high'].dropna(),
            "lows": df['swing_low'].dropna()
        }

    def _detect_bos_choch(self, df: pd.DataFrame, swing_points: Dict[str, pd.Series]) -> List[Dict]:
        events = []
        if len(swing_points['highs']) < 2 or len(swing_points['lows']) < 2:
            return []
            
        last_swing_high_price = swing_points['highs'].iloc[-1]
        last_swing_high_time = swing_points['highs'].index[-1]
        prev_swing_high_price = swing_points['highs'].iloc[-2]
        last_swing_low_price = swing_points['lows'].iloc[-1]
        recent_candles = df[df.index > last_swing_high_time]

        if last_swing_high_price > prev_swing_high_price:
             if not recent_candles.empty and recent_candles['high'].max() > last_swing_high_price:
                events.append({
                    "type": "BOS", "direction": "UP",
                    "price": last_swing_high_price,
                    "timestamp": recent_candles['high'].idxmax()
                })
        
        if last_swing_high_price > prev_swing_high_price:
             if not recent_candles.empty and recent_candles['low'].min() < last_swing_low_price:
                events.append({
                    "type": "CHoCH", "direction": "DOWN",
                    "price": last_swing_low_price,
                    "timestamp": recent_candles['low'].idxmin()
                })
        return events

    def _detect_fvg(self, df: pd.DataFrame) -> List[Dict]:
        fvgs = []
        n = self.config['fvg_sensitivity'] + 1
        bullish_fvg_mask = df['low'] > df['high'].shift(n)
        for index in df[bullish_fvg_mask].index:
            fvgs.append({
                "type": "BULLISH",
                "price_range": [df['high'].shift(n).loc[index], df['low'].loc[index]],
                "timestamp": index
            })
            
        bearish_fvg_mask = df['high'] < df['low'].shift(n)
        for index in df[bearish_fvg_mask].index:
            fvgs.append({
                "type": "BEARISH",
                "price_range": [df['high'].loc[index], df['low'].shift(n).loc[index]],
                "timestamp": index
            })
        return fvgs

    def _detect_order_blocks(self, df: pd.DataFrame, swing_points: Dict[str, pd.Series]) -> List[Dict]:
        obs = []
        for high_time, high_price in swing_points['highs'].items():
            df_slice = df[df.index < high_time].tail(10)
            last_bullish_candle = df_slice[df_slice['close'] > df_slice['open']].tail(1)
            
            if not last_bullish_candle.empty:
                 obs.append({
                     "type": "BEARISH",
                     "price_range": [last_bullish_candle['low'].iloc[0], last_bullish_candle['high'].iloc[0]],
                     "timestamp": last_bullish_candle.index[0]
                 })

        for low_time, low_price in swing_points['lows'].items():
            df_slice = df[df.index < low_time].tail(10)
            last_bearish_candle = df_slice[df_slice['close'] < df_slice['open']].tail(1)

            if not last_bearish_candle.empty:
                obs.append({
                    "type": "BULLISH",
                    "price_range": [last_bearish_candle['low'].iloc[0], last_bearish_candle['high'].iloc[0]],
                    "timestamp": last_bearish_candle.index[0]
                })
        return obs