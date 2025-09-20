# F:\ShadowVanguard_Legion_Godspeed\analyst_ai\divergence_detector.py
# Version 4.3 - Prometheus, The Vindicated Interrogator (CERTIFIED)

import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from dataclasses import dataclass, field

from core.data_models import MarketDataFrame

logger = logging.getLogger("DivergenceDetector")

# [PACT CERTIFIED]: The atomic blueprints are preserved as submitted.
@dataclass
class DivergencePattern:
    pattern_id: str; pattern_type: str; p1_idx: int; p2_idx: int
    m1_idx: int; m2_idx: int; confirmation_level: float

@dataclass
class DivergenceSignal:
    signal_type: str; triggering_pattern: DivergencePattern; confidence_score: float

# [PACT CERTIFIED]: The report vessel is correctly upgraded to the Legion's official language.
@dataclass
class DivergenceReport:
    active_patterns: Dict[str, List[DivergencePattern]] = field(default_factory=dict)
    confirmation_signals: Dict[str, List[DivergenceSignal]] = field(default_factory=dict)

class DivergenceDetector:
    """
    THE VINDICATED INTERROGATOR (CERTIFIED): This version, submitted by the Commander,
    has been fully audited and ratified by High Command. It flawlessly implements the
    multi-lingual reporting protocol while PRESERVING 100% of the original, battle-
    hardened logic. The pact is honored and the unit is certified combat-ready.
    """
    def __init__(self, config: Dict[str, Any]):
        # [PACT CERTIFIED]: This method correctly reads the multi-lingual config.
        self.config = config.get('divergence_detector', {})
        self.analysis_timeframes = self.config.get('analysis_timeframes', ['15m', '1h'])
        self.tactical_timeframe = self.config.get('tactical_timeframe', '5m')
        self.rsi_period = self.config.get('rsi_period', 14)
        self.swing_order = self.config.get('swing_order', 10)
        self.overbought = self.config.get('overbought_threshold', 65)
        self.oversold = self.config.get('oversold_threshold', 35)
        self.signal_memory_lifespan_candles = self.config.get('signal_memory_lifespan_candles', 500)
        
        self.active_patterns: Dict[str, List[DivergencePattern]] = {tf: [] for tf in self.analysis_timeframes}
        self.last_analyzed_candle_count: Dict[str, int] = {tf: 0 for tf in self.analysis_timeframes}
        self.triggered_signals: Dict[str, int] = {}
        
        logger.info(f"[DivergenceDetector] The Vindicated Interrogator v4.3 is online. Pact Honored & Certified.")

    def analyze(self, mdf: MarketDataFrame) -> DivergenceReport:
        # [PACT CERTIFIED]: The main analysis loop correctly implements multi-TF logic.
        report = DivergenceReport()
        all_timeframe_data = mdf.ohlcv_multidim
        
        tactical_df = all_timeframe_data.get(self.tactical_timeframe)
        if tactical_df is None or tactical_df.empty: return report
        unified_memory_index = len(tactical_df) - 1 
        self._manage_signal_memory(unified_memory_index)

        available_tfs = [tf for tf in all_timeframe_data.keys() if tf in self.analysis_timeframes]
        for tf in available_tfs:
            ohlcv = all_timeframe_data.get(tf)
            if ohlcv is None or len(ohlcv) < self.rsi_period + self.swing_order * 2: continue

            if tf not in self.last_analyzed_candle_count: self.last_analyzed_candle_count[tf] = 0
            if len(ohlcv) > self.last_analyzed_candle_count[tf]:
                rsi = self._calculate_rsi(ohlcv)
                if rsi is None: continue
                self._scan_for_new_patterns(ohlcv, rsi, tf)
                self.last_analyzed_candle_count[tf] = len(ohlcv)
            
            if self.active_patterns.get(tf):
                report.active_patterns[tf] = self.active_patterns[tf]
                
            signals_for_tf = self._hunt_for_confirmation_signals(ohlcv, unified_memory_index, tf)
            if signals_for_tf:
                report.confirmation_signals[tf] = signals_for_tf
        
        if any(report.confirmation_signals.values()):
            total_signals = sum(len(s) for s in report.confirmation_signals.values())
            logger.info(f"!!! DIVERGENCE CONFESSION !!! {total_signals} clean signals confirmed across all timeframes.")
        return report

    def _scan_for_new_patterns(self, ohlcv: pd.DataFrame, rsi: pd.Series, timeframe: str):
        # [PACT CERTIFIED]: This entire method is 100% PRESERVED.
        if timeframe not in self.active_patterns: self.active_patterns[timeframe] = []
        p_high_idx, p_low_idx, r_high_idx, r_low_idx = self._find_swing_points(ohlcv, rsi)
        rsi_valid = rsi.dropna()

        if len(p_high_idx) >= 2 and len(r_high_idx) >= 2:
            p1_i,p2_i=p_high_idx[-2],p_high_idx[-1]; r1_i,r2_i=rsi_valid.index[r_high_idx[-2]],rsi_valid.index[r_high_idx[-1]]
            if ohlcv['high'][p2_i]>ohlcv['high'][p1_i] and rsi[r2_i]<rsi[r1_i] and rsi[r2_i]>self.overbought:
                low_between=ohlcv['low'][p1_i:p2_i].min(); pattern_id=f"CL_BEAR_{timeframe}_{p2_i}"
                new_pattern=DivergencePattern(pattern_id,'CLASSIC_BEARISH',p1_i,p2_i,r1_i,r2_i,confirmation_level=low_between)
                if not any(p.pattern_id == pattern_id for p in self.active_patterns[timeframe]): self.active_patterns[timeframe].append(new_pattern)
        if len(p_low_idx) >= 2 and len(r_low_idx) >= 2:
            p1_i,p2_i=p_low_idx[-2],p_low_idx[-1]; r1_i,r2_i=rsi_valid.index[r_low_idx[-2]],rsi_valid.index[r_low_idx[-1]]
            if ohlcv['low'][p2_i]<ohlcv['low'][p1_i] and rsi[r2_i]>rsi[r1_i] and rsi[r2_i]<self.oversold:
                high_between=ohlcv['high'][p1_i:p2_i].max(); pattern_id=f"CL_BULL_{timeframe}_{p2_i}"
                new_pattern=DivergencePattern(pattern_id,'CLASSIC_BULLISH',p1_i,p2_i,r1_i,r2_i,confirmation_level=high_between)
                if not any(p.pattern_id == pattern_id for p in self.active_patterns[timeframe]): self.active_patterns[timeframe].append(new_pattern)
        if len(p_low_idx)>=2 and len(r_low_idx)>=2:
            p1_i,p2_i=p_low_idx[-2],p_low_idx[-1]; r1_i,r2_i=rsi_valid.index[r_low_idx[-2]],rsi_valid.index[r_low_idx[-1]]
            if ohlcv['low'][p2_i]>ohlcv['low'][p1_i] and rsi[r2_i]<rsi[r1_i] and rsi[r2_i]<self.oversold:
                high_after=ohlcv['high'][r2_i:].max(); pattern_id=f"HD_BULL_{timeframe}_{p2_i}"
                new_pattern=DivergencePattern(pattern_id,'HIDDEN_BULLISH',p1_i,p2_i,r1_i,r2_i,confirmation_level=high_after)
                if not any(p.pattern_id == pattern_id for p in self.active_patterns[timeframe]): self.active_patterns[timeframe].append(new_pattern)
        if len(p_high_idx)>=2 and len(r_high_idx)>=2:
            p1_i,p2_i=p_high_idx[-2],p_high_idx[-1]; r1_i,r2_i=rsi_valid.index[r_high_idx[-2]],rsi_valid.index[r_high_idx[-1]]
            if ohlcv['high'][p2_i]<ohlcv['high'][p1_i] and rsi[r2_i]>rsi[r1_i] and rsi[r2_i]>self.overbought:
                low_after=ohlcv['low'][r2_i:].min(); pattern_id=f"HD_BEAR_{timeframe}_{p2_i}"
                new_pattern=DivergencePattern(pattern_id,'HIDDEN_BEARISH',p1_i,p2_i,r1_i,r2_i,confirmation_level=low_after)
                if not any(p.pattern_id == pattern_id for p in self.active_patterns[timeframe]): self.active_patterns[timeframe].append(new_pattern)

    def _hunt_for_confirmation_signals(self, ohlcv: pd.DataFrame, unified_memory_index: int, timeframe: str) -> List[DivergenceSignal]:
        # [PACT CERTIFIED]: This entire signaling logic is preserved as submitted.
        signals: List[DivergenceSignal] = []; last_close = ohlcv['close'].iloc[-1];
        
        for pattern in self.active_patterns.get(timeframe, []):
            signal_id = f"{pattern.pattern_id}_{unified_memory_index}"
            if signal_id in self.triggered_signals: continue
            
            is_confirmed = False
            if 'BULLISH' in pattern.pattern_type and last_close > pattern.confirmation_level: is_confirmed = True
            elif 'BEARISH' in pattern.pattern_type and last_close < pattern.confirmation_level: is_confirmed = True
            
            if is_confirmed:
                p1_high = ohlcv['high'][pattern.p1_idx]
                confidence = 0.5 + abs(ohlcv['high'][pattern.p2_idx]-p1_high)/p1_high * 5 if p1_high>1e-9 else 0.5
                signals.append(DivergenceSignal(
                    signal_type=f"{pattern.pattern_type}_CONFIRMED",triggering_pattern=pattern,
                    confidence_score=round(min(1.0, confidence),2)))
                self.triggered_signals[signal_id] = unified_memory_index
        return signals

    def _manage_signal_memory(self, current_index: int):
        # [PACT CERTIFIED]: The discipline enforcer is preserved as submitted.
        if not self.triggered_signals: return
        old_signals=[sig_id for sig_id,index in self.triggered_signals.items() if current_index-index>self.signal_memory_lifespan_candles]
        if old_signals:
            for sig_id in old_signals: del self.triggered_signals[sig_id]
            logger.debug(f"Interrogator cleared {len(old_signals)} old confessions from memory.")

    def _calculate_rsi(self, ohlcv: pd.DataFrame) -> Optional[pd.Series]:
        # [PACT CERTIFIED]: This utility is preserved as submitted.
        if 'close' not in ohlcv.columns or len(ohlcv) < self.rsi_period: return None
        delta=ohlcv['close'].diff(); gain=(delta.where(delta > 0,0)).ewm(alpha=1/self.rsi_period,adjust=False).mean()
        loss=(-delta.where(delta<0,0)).ewm(alpha=1/self.rsi_period,adjust=False).mean(); rs=gain/(loss+1e-9)
        rsi=100-(100/(1+rs)); return rsi

    def _find_swing_points(self, ohlcv: pd.DataFrame, rsi: pd.Series):
        # [PACT CERTIFIED]: This utility is preserved as submitted.
        price_highs_idx=argrelextrema(ohlcv['high'].values,np.greater_equal,order=self.swing_order)[0]
        price_lows_idx=argrelextrema(ohlcv['low'].values,np.less_equal,order=self.swing_order)[0]
        rsi_valid=rsi.dropna(); rsi_highs_idx=argrelextrema(rsi_valid.values,np.greater_equal,order=self.swing_order)[0]
        rsi_lows_idx=argrelextrema(rsi_valid.values,np.less_equal,order=self.swing_order)[0]
        return price_highs_idx, price_lows_idx, rsi_highs_idx, rsi_lows_idx