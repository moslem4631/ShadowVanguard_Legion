# F:\ShadowVanguard_Legion_Godspeed\analyst_ai\fibonacci_helper.py
# Version 5.0 - Prometheus, The Confluence Sniper

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

# [SURGICAL UPGRADE]: The Sniper now imports the universal blueprints for perfect protocol alignment.
from core.data_models import MarketDataFrame, OrderBlockReport, LiquidityReport, FibonacciReport, FibonacciZone, FibonacciSignal

logger = logging.getLogger("FibonacciHelper")

class FibonacciHelper:
    """
    THE CONFLUENCE SNIPER: This version completes the final protocol synchronization for
    the intelligence wing and elevates its science to the highest modern standards.
    It now speaks the universal Legion language, correctly interpreting modern `OrderBlock`
    and `Liquidity` reports. Furthermore, its core logic is enhanced to prioritize
    "Confluence" - the powerful alignment of Fibonacci levels with strategic OBs and FVGs,
    turning it from a simple level-watcher into a true hunter of high-probability setups.
    """
    def __init__(self, config: Dict[str, Any]):
        # [PACT KEPT]: Core configuration logic is preserved.
        self.config = config.get('fibonacci_helper', {})
        self.analysis_timeframes = self.config.get('analysis_timeframes', ['15m', '1h'])
        self.tactical_timeframe = self.config.get('tactical_timeframe', '5m')
        self.fib_levels = self.config.get('levels', [0.382, 0.5, 0.618, 0.705, 0.786, 0.886])
        self.swing_order = self.config.get('swing_order', 15)
        self.confluence_tolerance_pct = self.config.get('confluence_tolerance_pct', 0.05) / 100.0
        self.confirmation_atr_multiplier = self.config.get('confirmation_atr_multiplier', 0.8)
        self.signal_memory_lifespan_candles = self.config.get('signal_memory_lifespan_candles', 500)
        self.golden_pocket_levels = self.config.get('golden_pocket_levels', [0.618, 0.705, 0.786])
        self.golden_pocket_strength_bonus = self.config.get('golden_pocket_strength_bonus', 0.2)
        self.fvg_confluence_strength_bonus = self.config.get('fvg_confluence_strength_bonus', 0.3)
        self.ob_confluence_strength_bonus = self.config.get('ob_confluence_strength_bonus', 0.4)
        
        self.active_zones: Dict[str, List[FibonacciZone]] = {tf: [] for tf in self.analysis_timeframes}
        self.last_swing_analyzed_idx: Dict[str, int] = {tf: 0 for tf in self.analysis_timeframes}
        self.triggered_signals: Dict[str, int] = {}
        logger.info(f"[FibonacciHelper] The Confluence Sniper v5.0 is online. Awaiting high-probability targets.")

    def analyze(self, mdf: MarketDataFrame) -> FibonacciReport:
        # [PACT KEPT]: The analysis loop structure is preserved.
        report = FibonacciReport()
        tactical_ohlcv = mdf.ohlcv_multidim.get(self.tactical_timeframe)
        if tactical_ohlcv is None or tactical_ohlcv.empty: return report

        current_candle_index = len(tactical_ohlcv) - 1
        self._manage_signal_memory(current_candle_index)

        for tf in self.analysis_timeframes:
            ohlcv = mdf.ohlcv_multidim.get(tf)
            if ohlcv is not None and len(ohlcv) >= self.swing_order * 2 + 1:
                # Pass the full MDF for contextual analysis
                self._update_active_zones(ohlcv, mdf, tf)

        # Populate the report with the latest active zones
        report.active_zones = self.active_zones
        
        # Hunt for signals
        if 'atr' not in tactical_ohlcv.columns:
            tr = abs(tactical_ohlcv['high'] - tactical_ohlcv['low']); tactical_ohlcv['atr'] = tr.ewm(span=14, adjust=False).mean()
        last_candle = tactical_ohlcv.iloc[-1]
        
        all_zones_flat_list: List[FibonacciZone] = [zone for tf_zones in self.active_zones.values() for zone in tf_zones]
        signals_flat_list = self._hunt_for_confirmation_signals(all_zones_flat_list, last_candle, current_candle_index)
        
        # Populate the report with signals, correctly organized by timeframe
        if signals_flat_list:
            for signal in signals_flat_list:
                # Infer timeframe from the zone's reason list
                tf = next((reason.split('_')[-1] for reason in signal.triggering_zone.reasons if 'FIB_' in reason), self.tactical_timeframe)
                if tf not in report.confirmation_signals: report.confirmation_signals[tf] = []
                report.confirmation_signals[tf].append(signal)

        if any(report.confirmation_signals.values()):
            total_signals = sum(len(s) for s in report.confirmation_signals.values())
            logger.info(f"!!! GHOST SNIPER SIGNAL !!! {total_signals} clean signal(s) detected.")

        return report

    def _update_active_zones(self, ohlcv: pd.DataFrame, mdf: MarketDataFrame, timeframe: str):
        # [SURGICAL INTERVENTION & SCIENTIFIC UPGRADE]: This method is now fully synchronized and context-aware.
        if timeframe not in self.active_zones: self.active_zones[timeframe] = []
        if timeframe not in self.last_swing_analyzed_idx: self.last_swing_analyzed_idx[timeframe] = 0
            
        swings = self._find_significant_swings(ohlcv)
        if not swings: return
        
        last_swing = swings[-1]
        if last_swing['end_idx'] == self.last_swing_analyzed_idx.get(timeframe): return
            
        self.last_swing_analyzed_idx[timeframe] = last_swing['end_idx']
        self.active_zones[timeframe].clear()
        
        logger.debug(f"New primary swing on {timeframe}. Recalculating Fibonacci confluence zones.")

        start_price, end_price, range_size = last_swing['start_price'], last_swing['end_price'], abs(last_swing['end_price'] - last_swing['start_price'])
        is_bullish_swing = last_swing['type'] == 'impulse_up'
        if range_size < 1e-9: return

        for level in self.fib_levels:
            fib_price = end_price - (range_size * level) if is_bullish_swing else end_price + (range_size * level)
            base_strength = 0.3
            reasons = [f"FIB_{level:.3f}_{timeframe}"]
            
            if level in self.golden_pocket_levels:
                base_strength += self.golden_pocket_strength_bonus
                reasons.append("OTE_ZONE")
            
            fib_window = (fib_price * (1 - self.confluence_tolerance_pct), fib_price * (1 + self.confluence_tolerance_pct))
            
            # --- CONFLUENCE CHECK: ORDER BLOCKS ---
            # Correctly accesses the modern `all_blocks` structure.
            if mdf.ob_report and timeframe in mdf.ob_report.all_blocks:
                ob_side = 'bullish' if is_bullish_swing else 'bearish'
                for ob in mdf.ob_report.all_blocks[timeframe].get(ob_side, []):
                    if fib_window[0] < ob.price_high and fib_window[1] > ob.price_low:
                        base_strength += self.ob_confluence_strength_bonus
                        reasons.append(f"OB_{ob.timeframe}")
                        break
            
            # --- CONFLUENCE CHECK: FAIR VALUE GAPS ---
            # Correctly accesses the modern `unfilled_fvgs` structure.
            if mdf.liq_report and timeframe in mdf.liq_report.unfilled_fvgs:
                fvg_side = 'bullish' if is_bullish_swing else 'bearish'
                for fvg in mdf.liq_report.unfilled_fvgs[timeframe].get(fvg_side, []):
                    if fib_window[0] < fvg.price_high and fib_window[1] > fvg.price_low:
                         base_strength += self.fvg_confluence_strength_bonus
                         reasons.append(f"FVG_{fvg.timeframe}")
                         break

            zone_tolerance = (ohlcv.iloc[-1]['close'] * self.confluence_tolerance_pct) / 2
            zone_id = f"FIB_{level:.3f}_{'BULL' if is_bullish_swing else 'BEAR'}_{timeframe}_{last_swing['end_idx']}"
            
            self.active_zones[timeframe].append(FibonacciZone(
                zone_id=zone_id, price_range=(fib_price - zone_tolerance, fib_price + zone_tolerance),
                strength=round(min(1.0, base_strength), 2), is_bullish=is_bullish_swing,
                source_level=level, reasons=reasons ))
            
    # [PACT KEPT]: The following methods are battle-hardened and preserved with minimal changes for protocol alignment.
    def _hunt_for_confirmation_signals(self, all_active_zones: List[FibonacciZone], current_candle: pd.Series, current_candle_index: int) -> List[FibonacciSignal]:
        signals: List[FibonacciSignal] = []; confirmation_body_size = current_candle['atr'] * self.confirmation_atr_multiplier
        if not all_active_zones or pd.isna(current_candle.get('atr')): return signals
        for zone in all_active_zones:
            signal_id = f"{zone.zone_id}_{current_candle_index}"
            if signal_id in self.triggered_signals: continue
            zone_low, zone_high = zone.price_range; signal_fired = False
            if zone.is_bullish and current_candle['low'] <= zone_high:
                if current_candle['close'] > current_candle['open'] and (current_candle['close'] - current_candle['open']) >= confirmation_body_size:
                    signals.append(FibonacciSignal(signal_type='BULLISH_FIB_CONFIRMATION', triggering_zone=zone, confidence_score=zone.strength)); signal_fired = True
            elif not zone.is_bullish and current_candle['high'] >= zone_low:
                if current_candle['close'] < current_candle['open'] and (current_candle['open'] - current_candle['close']) >= confirmation_body_size:
                    signals.append(FibonacciSignal(signal_type='BEARISH_FIB_CONFIRMATION', triggering_zone=zone, confidence_score=zone.strength)); signal_fired = True
            if signal_fired: self.triggered_signals[signal_id] = current_candle_index
        return signals

    def _manage_signal_memory(self, current_index: int):
        if not self.triggered_signals: return
        old_signals = [sig_id for sig_id, index in self.triggered_signals.items() if current_index - index > self.signal_memory_lifespan_candles]
        if old_signals:
            for sig_id in old_signals: del self.triggered_signals[sig_id]
            logger.debug(f"Sniper cleared {len(old_signals)} old signals from memory.")

    def _find_significant_swings(self, ohlcv: pd.DataFrame) -> List[Dict[str, Any]]:
        try:
            highs_idx=argrelextrema(ohlcv['high'].values,np.greater_equal,order=self.swing_order)[0]; lows_idx=argrelextrema(ohlcv['low'].values,np.less_equal,order=self.swing_order)[0]
            all_points = sorted([{'idx': i, 'price': ohlcv['high'].iloc[i], 'type': 'high'} for i in highs_idx] + [{'idx': i, 'price': ohlcv['low'].iloc[i], 'type': 'low'} for i in lows_idx], key=lambda x: x['idx'])
            if len(all_points) < 2: return []
            impulses = []
            for i in range(len(all_points)-1):
                p1,p2=all_points[i],all_points[i+1]
                if p1['type'] != p2['type']:
                    if p1['type']=='low' and p2['type']=='high': impulses.append({'start_price': p1['price'], 'end_price': p2['price'], 'type': 'impulse_up', 'end_idx': p2['idx']})
                    else: impulses.append({'start_price': p1['price'], 'end_price': p2['price'], 'type': 'impulse_down', 'end_idx': p2['idx']})
            return impulses
        except Exception as e:
            logger.error(f"Error finding swing points: {e}"); return []