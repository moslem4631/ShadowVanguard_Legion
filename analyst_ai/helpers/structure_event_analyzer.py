# F:\ShadowVanguard_Legion\analyst_ai\helpers\structure_event_analyzer.py
# Version 5.2 - Prometheus: The Fortified Chrono-Engine Watchtower

import logging
from typing import List, Tuple, Dict
import pandas as pd
import numpy as np

from core.data_models import MarketDataFrame, StructureEvent, PowerReport
from core.market_enums import PositionSide

logger = logging.getLogger("StructureEventAnalyzer")

def _resample_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    AI-UPGRADE: This new, hardened resampling engine is fully robust.
    It can handle data whether the timestamp is a column or the index,
    thus fixing the "Resampling failed" error permanently.
    """
    df_to_resample = df.copy()

    # Step 1: Ensure we have a DatetimeIndex to work with.
    # If 'timestamp' is a column, convert it and set it as the index.
    if 'timestamp' in df_to_resample.columns:
        df_to_resample['timestamp'] = pd.to_datetime(df_to_resample['timestamp'])
        df_to_resample.set_index('timestamp', inplace=True)

    # Step 2: Check if the index is a valid DatetimeIndex.
    if not isinstance(df_to_resample.index, pd.DatetimeIndex):
        logger.error("Resampling failed: DataFrame index is not a DatetimeIndex and 'timestamp' column was not found.")
        return pd.DataFrame()
    
    # Step 3: Now we can safely resample on the index without the 'on=' argument.
    df_resampled = df_to_resample.resample(timeframe).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    # The resampled df has a timestamp index. We reset it to match the input format for our analysis functions.
    return df_resampled.reset_index()

def _find_swing_points_for_timeframe(df: pd.DataFrame, order: int) -> Tuple[List[int], List[int]]:
    """(This logic is PRESERVED EXACTLY from your v5.1 blueprint)"""
    if len(df) < order * 2 + 1: return [], []
    
    highs, lows = df['high'], df['low']
    swing_highs_indices, swing_lows_indices = [], []
    
    highs_arr = highs.to_numpy(); lows_arr = lows.to_numpy()
    
    for i in range(order, len(df) - order):
        window = highs_arr[i-order : i+order+1]
        if highs_arr[i] >= window.max():
             if np.sum(window == highs_arr[i]) == 1:
                swing_highs_indices.append(i)

        window = lows_arr[i-order : i+order+1]
        if lows_arr[i] <= window.min():
             if np.sum(window == lows_arr[i]) == 1:
                swing_lows_indices.append(i)

    return swing_highs_indices, swing_lows_indices

def _analyze_timeframe(df: pd.DataFrame, power_report: 'PowerReport', timeframe_suffix: str, config: Dict) -> List[StructureEvent]:
    """(This logic is PRESERVED EXACTLY from your v5.1 blueprint)"""
    quality_threshold = config.get('quality_threshold', 0.2)
    swing_order = config.get('swing_order', 5)

    if power_report is None: return []

    swing_highs_idx, swing_lows_idx = _find_swing_points_for_timeframe(df, swing_order)
    if not swing_highs_idx or not swing_lows_idx: return []

    events = []
    
    last_swing_high_price = df['high'].iloc[swing_highs_idx[-1]]
    last_swing_low_price = df['low'].iloc[swing_lows_idx[-1]]
    
    current_high = df['high'].iloc[-1]
    current_low = df['low'].iloc[-1]
    current_idx = len(df) - 1

    if current_high > last_swing_high_price:
        if (quality := power_report.confidence * (power_report.net_force / 50.0 if power_report.net_force > 0 else 0)) > quality_threshold:
            events.append(StructureEvent(f"BOS_BULLISH{timeframe_suffix}", current_high, current_idx, round(quality, 2)))

    if current_low < last_swing_low_price:
        if (quality := power_report.confidence * (-power_report.net_force / 50.0 if power_report.net_force < 0 else 0)) > quality_threshold:
            events.append(StructureEvent(f"BOS_BEARISH{timeframe_suffix}", current_low, current_idx, round(quality, 2)))
    
    if len(swing_highs_idx) > 1 and len(swing_lows_idx) > 1:
        prev_swing_low_idx = swing_lows_idx[-2]
        was_bearish = df['low'].iloc[swing_lows_idx[-1]] < df['low'].iloc[prev_swing_low_idx]
        if was_bearish and current_high > last_swing_high_price:
             if (quality := power_report.confidence * (power_report.net_force / 50.0)) > quality_threshold:
                 events.append(StructureEvent(f"CHOCH_BULLISH{timeframe_suffix}", current_high, current_idx, round(quality, 2)))

        prev_swing_high_idx = swing_highs_idx[-2]
        was_bullish = df['high'].iloc[swing_highs_idx[-1]] > df['high'].iloc[prev_swing_high_idx]
        if was_bullish and current_low < last_swing_low_price:
             if (quality := power_report.confidence * (-power_report.net_force / 50.0)) > quality_threshold:
                 events.append(StructureEvent(f"CHOCH_BEARISH{timeframe_suffix}", current_low, current_idx, round(quality, 2)))
                 
    return events


def find_structure_events(mdf: MarketDataFrame, config: dict) -> List[StructureEvent]:
    """(This orchestrator logic is PRESERVED EXACTLY from your v5.1 blueprint)"""
    all_events = []
    
    tactical_df = mdf.ohlcv
    power_report = mdf.power_report 
    
    tactical_events = _analyze_timeframe(tactical_df, power_report, timeframe_suffix="", config=config)
    all_events.extend(tactical_events)
    
    strategic_timeframe = config.get('strategic_timeframe', '60min')
    strategic_df = _resample_ohlcv(tactical_df, strategic_timeframe)
    
    if not strategic_df.empty:
        strategic_events = _analyze_timeframe(strategic_df, power_report, timeframe_suffix=f"_{strategic_timeframe}", config=config)
        all_events.extend(strategic_events)
    
    if all_events:
        event_names = [e.event_type for e in all_events]
        logger.info(f"Detected {len(all_events)} structure events across timeframes: {', '.join(event_names)}")
        
    return all_events