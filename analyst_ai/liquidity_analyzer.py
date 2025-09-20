# F:\ShadowVanguard_Legion_Godspeed\analyst_ai\liquidity_analyzer.py
# Version 15.0 - Prometheus, The Silent Ghost Hunter

import logging
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

# [PACT KEPT]: All core data model imports are PRESERVED.
from core.data_models import MarketDataFrame, FairValueGap, LiquiditySignal, LiquidityReport

logger = logging.getLogger("LiquidityAnalyzer")

class LiquidityAnalyzer:
    """
    THE SILENT GHOST HUNTER: This version marks a major upgrade in intelligence discipline.
    The Ghost Hunter is no longer permitted to report every minor spectral anomaly. It is
    now equipped with sophisticated filtering protocols (Volume & ATR-based sizing) to
    ensure it only reports Fair Value Gaps that are strategically significant. This
    dramatically reduces noise, enhances analytical clarity, and focuses the Legion's
    attention on high-impact liquidity voids. Operation: Radio Silence is complete.
    """
    def __init__(self, config: Dict[str, Any]):
        # [SURGICAL UPGRADE]: New parameters for noise reduction filters are added.
        self.config = config.get('liquidity_analyzer', {})
        self.analysis_timeframes = self.config.get('analysis_timeframes', ['5m', '15m', '1h'])
        self.tactical_timeframe = self.config.get('tactical_timeframe', '5m')
        self.confirmation_atr_multiplier = self.config.get('confirmation_atr_multiplier', 1.0)
        self.signal_memory_lifespan_candles = self.config.get('signal_memory_lifespan_candles', 500)
        
        # New Filter Parameters from settings.yaml
        self.min_fvg_size_atr_multiplier = self.config.get('min_fvg_size_atr_multiplier', 0.3)
        self.min_volume_multiplier = self.config.get('min_volume_multiplier', 1.5)
        self.volume_ma_period = self.config.get('volume_ma_period', 20)
        
        self.active_fvgs_by_tf: Dict[str, List[FairValueGap]] = {tf: [] for tf in self.analysis_timeframes}
        self.triggered_signals: Dict[str, int] = {}
        logger.info("[LiquidityAnalyzer] The Silent Ghost Hunter v15.0 is online. Noise filters engaged.")

    def analyze(self, mdf: MarketDataFrame) -> LiquidityReport:
        # [PACT KEPT]: The high-level analysis flow is 100% PRESERVED.
        report = LiquidityReport()
        tactical_df = mdf.ohlcv_multidim.get(self.tactical_timeframe)
        if tactical_df is None or tactical_df.empty: return report

        current_candle_index = len(tactical_df) - 1
        self._manage_signal_memory(current_candle_index)

        available_tfs = [tf for tf in mdf.ohlcv_multidim.keys() if tf in self.analysis_timeframes]
        for tf in available_tfs:
            df = mdf.ohlcv_multidim.get(tf)
            if df is not None and not df.empty and len(df) > self.volume_ma_period:
                # Pre-calculate necessary indicators for efficiency
                df['atr'] = self._calculate_atr(df)
                df['volume_ma'] = df['volume'].rolling(window=self.volume_ma_period).mean()
                self._update_fvgs_for_timeframe(df, timeframe=tf)

        # [PACT KEPT]: The reporting logic is PRESERVED.
        for tf, fvgs in self.active_fvgs_by_tf.items():
            if fvgs:
                if tf not in report.unfilled_fvgs:
                    report.unfilled_fvgs[tf] = {'bullish': [], 'bearish': []}
                for fvg in fvgs:
                    if fvg.event_type == 'BULLISH_FVG':
                        report.unfilled_fvgs[tf]['bullish'].append(fvg)
                    elif fvg.event_type == 'BEARISH_FVG':
                        report.unfilled_fvgs[tf]['bearish'].append(fvg)
        
        all_active_fvgs_flat_list: List[FairValueGap] = [fvg for tf_fvgs in self.active_fvgs_by_tf.values() for fvg in tf_fvgs]
        last_candle = tactical_df.iloc[-1]
        confirmation_signals_flat_list = self._hunt_for_confirmation_signals(all_active_fvgs_flat_list, last_candle, current_candle_index)

        if confirmation_signals_flat_list:
            for signal in confirmation_signals_flat_list:
                tf = signal.triggering_void.timeframe
                if tf not in report.confirmation_signals:
                    report.confirmation_signals[tf] = []
                report.confirmation_signals[tf].append(signal)

        if any(report.confirmation_signals.values()):
            total_signals = sum(len(s) for s in report.confirmation_signals.values())
            logger.info(f"!!! VOID REACTION DETECTED !!! {total_signals} clean signal(s) across all timeframes.")

        return report

    def _update_fvgs_for_timeframe(self, df: pd.DataFrame, timeframe: str):
        # [SURGICAL INTERVENTION]: FVG detection logic is now hardened with noise filters.
        if timeframe not in self.active_fvgs_by_tf: self.active_fvgs_by_tf[timeframe] = []
            
        last_close = df['close'].iloc[-1]
        surviving_fvgs = [fvg for fvg in self.active_fvgs_by_tf.get(timeframe, []) 
                          if not ((fvg.event_type == 'BULLISH_FVG' and last_close < fvg.price_low) or \
                                  (fvg.event_type == 'BEARISH_FVG' and last_close > fvg.price_high))]
        self.active_fvgs_by_tf[timeframe] = surviving_fvgs
        
        existing_void_ids = {v.void_id for v in self.active_fvgs_by_tf[timeframe]}
        
        for i in range(len(df) - 2):
            candle_A, candle_B, candle_C = df.iloc[i], df.iloc[i+1], df.iloc[i+2]
            new_fvg: Optional[FairValueGap] = None

            is_bullish_gap = candle_C['low'] > candle_A['high']
            is_bearish_gap = candle_A['low'] > candle_C['high']

            if is_bullish_gap or is_bearish_gap:
                fvg_high = candle_C['low'] if is_bullish_gap else candle_A['low']
                fvg_low = candle_A['high'] if is_bullish_gap else candle_C['high']
                fvg_height = fvg_high - fvg_low
                
                # --- Filter 1: Relative Size Check ---
                atr_at_creation = df['atr'].iloc[i+1]
                if atr_at_creation == 0 or fvg_height < (atr_at_creation * self.min_fvg_size_atr_multiplier):
                    continue # Skip FVG if it's too small relative to volatility

                # --- Filter 2: Volume Significance Check ---
                volume_ma_at_creation = df['volume_ma'].iloc[i+1]
                if volume_ma_at_creation == 0 or candle_C['volume'] < (volume_ma_at_creation * self.min_volume_multiplier):
                    continue # Skip if the confirming candle has insignificant volume
                
                # If filters passed, create the FVG
                event_type = 'BULLISH_FVG' if is_bullish_gap else 'BEARISH_FVG'
                void_id = f"{event_type[:4]}_{timeframe}_{i+1}"
                
                if void_id not in existing_void_ids:
                    new_fvg = FairValueGap(
                        void_id=void_id, event_type=event_type,
                        price_low=fvg_low, price_high=fvg_high,
                        timeframe=timeframe, created_at_index=i + 1)
            
            if new_fvg:
                self.active_fvgs_by_tf[timeframe].append(new_fvg)
                existing_void_ids.add(new_fvg.void_id)
                # This log will now be much rarer and more significant
                logger.info(f"STRATEGIC VOID DETECTED: New {new_fvg.event_type} on {new_fvg.timeframe} at ({new_fvg.price_low:.2f}, {new_fvg.price_high:.2f})")

    # [PACT KEPT]: All remaining methods are preserved.
    def _calculate_atr(self, ohlcv_df: pd.DataFrame, period: int = 14) -> pd.Series:
        df = ohlcv_df.copy(); df['h-l'] = df['high'] - df['low']; df['h-pc'] = abs(df['high'] - df['close'].shift(1)); df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        tr = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        return tr.ewm(alpha=1/period, adjust=False).mean()

    def _hunt_for_confirmation_signals(self, all_active_fvgs: List[FairValueGap], current_candle: pd.Series, current_candle_index: int) -> List[LiquiditySignal]:
        signals: List[LiquiditySignal] = []
        if pd.isna(current_candle.get('atr')): return signals
        confirmation_body_size = current_candle['atr'] * self.confirmation_atr_multiplier
        for fvg in all_active_fvgs:
            signal_id = f"{fvg.void_id}_{current_candle_index}"
            if signal_id in self.triggered_signals: continue
            signal_fired = False
            if fvg.event_type == 'BULLISH_FVG' and current_candle['low'] <= fvg.price_high:
                if current_candle['close'] > current_candle['open'] and (current_candle['close'] - current_candle['open']) >= confirmation_body_size:
                    signals.append(LiquiditySignal(signal_type='BULLISH_FVG_CONFIRMATION', triggering_void=fvg, confidence_score=0.8)); signal_fired = True
            elif fvg.event_type == 'BEARISH_FVG' and current_candle['high'] >= fvg.price_low:
                if current_candle['close'] < current_candle['open'] and (current_candle['open'] - current_candle['close']) >= confirmation_body_size:
                    signals.append(LiquiditySignal(signal_type='BEARISH_FVG_CONFIRMATION', triggering_void=fvg, confidence_score=0.8)); signal_fired = True
            if signal_fired: self.triggered_signals[signal_id] = current_candle_index
        return signals
        
    def _manage_signal_memory(self, current_index: int):
        if not self.triggered_signals: return
        old_signals = [sig_id for sig_id, index in self.triggered_signals.items() if current_index - index > self.signal_memory_lifespan_candles]
        if old_signals:
            for sig_id in old_signals: del self.triggered_signals[sig_id]
            logger.debug(f"Ghost Buster cleared {len(old_signals)} old signals from memory.")