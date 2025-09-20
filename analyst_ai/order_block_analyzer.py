# F:\ShadowVanguard_Legion_Godspeed\analyst_ai\order_block_analyzer.py
# Version 8.3 - Prometheus, The Universal Cipher

import logging
from typing import List, Dict, Tuple, Optional, Any
import pandas as pd

# [SURGICAL INTERVENTION]: The Cipher now speaks the universal language of the Legion.
# It imports its blueprints directly from the central encyclopedia, ensuring perfect protocol synchronization.
from core.data_models import MarketDataFrame, OrderBlock, OBInteractionSignal, OrderBlockReport

logger = logging.getLogger("OrderBlockAnalyzer")

class OrderBlockAnalyzer:
    """
    THE UNIVERSAL CIPHER: This version completes the final protocol synchronization.
    The Cipher no longer uses its own local dialect. It now reads from and writes to
    the universal data models defined in `core.data_models`. This surgical change
    eliminates the `AttributeError` by ensuring the produced `OrderBlockReport`
    perfectly matches the format expected by the `StructureAnalyzer`.
    The Legion now speaks with one voice.
    """
    def __init__(self, config: Dict[str, Any]):
        # [PACT KEPT]: The core configuration logic is PRESERVED.
        self.config = config.get('order_block_analyzer', {})
        self.analysis_timeframes = self.config.get('analysis_timeframes', ['5m', '15m', '1h'])
        self.tactical_timeframe = self.config.get('tactical_timeframe', '5m')
        self.signal_memory_lifespan_candles = self.config.get('signal_memory_lifespan_candles', 500)
        
        # Internal state now uses the official OrderBlock model.
        self.active_blocks_by_tf: Dict[str, List[OrderBlock]] = {tf: [] for tf in self.analysis_timeframes}
        
        self.last_impulse_index: Dict[str, int] = {tf: 0 for tf in self.analysis_timeframes}
        self.triggered_signals: Dict[str, int] = {}
        logger.info("[OrderBlockAnalyzer] The Universal Cipher v8.3 is online. Speaking Legion Standard Protocol.")

    def analyze(self, mdf: MarketDataFrame) -> OrderBlockReport:
        # [SURGICAL INTERVENTION]: The reporting logic is updated to use the official, synchronized format.
        report = OrderBlockReport()
        tactical_df = mdf.ohlcv_multidim.get(self.tactical_timeframe)
        if tactical_df is None or tactical_df.empty: return report

        current_candle_index = len(tactical_df) - 1
        self._manage_signal_memory(current_candle_index)

        available_tfs = [tf for tf in mdf.ohlcv_multidim.keys() if tf in self.analysis_timeframes]
        for tf in available_tfs:
            df = mdf.ohlcv_multidim.get(tf)
            if df is not None and not df.empty and len(df) > 15:
                self._update_blocks_for_timeframe(df, timeframe=tf)

        # --- REPORTING RECONSTRUCTION ---
        # 1. Populate the `all_blocks` field in the new, correct format.
        for tf, blocks in self.active_blocks_by_tf.items():
            if blocks:
                if tf not in report.all_blocks:
                    report.all_blocks[tf] = {'bullish': [], 'bearish': []}
                for block in blocks:
                    if block.event_type == 'BULLISH_OB':
                        report.all_blocks[tf]['bullish'].append(block)
                    elif block.event_type == 'BEARISH_OB':
                        report.all_blocks[tf]['bearish'].append(block)

        # 2. Hunt for signals using the unified block list.
        all_active_blocks_flat_list: List[OrderBlock] = [block for tf_blocks in self.active_blocks_by_tf.values() for block in tf_blocks]
        current_candle = tactical_df.iloc[-1]
        interaction_signals_flat_list = self._hunt_for_interaction_signals(
            all_active_blocks_flat_list, current_candle, current_candle_index
        )
        
        # 3. Populate the `interaction_signals` field.
        if interaction_signals_flat_list:
            for signal in interaction_signals_flat_list:
                tf = signal.triggering_ob.timeframe
                if tf not in report.interaction_signals:
                    report.interaction_signals[tf] = []
                report.interaction_signals[tf].append(signal)

        if any(report.interaction_signals.values()):
            total_signals = sum(len(s) for s in report.interaction_signals.values())
            logger.info(f"!!! SONAR PING DETECTED !!! {total_signals} clean OB interactions across all timeframes.")

        return report

    def _update_blocks_for_timeframe(self, df: pd.DataFrame, timeframe: str):
        # [PACT KEPT]: The core Sonarlab logic is 100% PRESERVED.
        # Minor adjustments for new data model fields (`price_low`, `price_high`).
        if len(df) < 2: return
        if timeframe not in self.active_blocks_by_tf: self.active_blocks_by_tf[timeframe] = []
        if timeframe not in self.last_impulse_index: self.last_impulse_index[timeframe] = 0
            
        mitigation_candle = df.iloc[-2]
        mitigation_type = self.config.get('mitigation_type', 'Close')
        bullish_mitigation_price = mitigation_candle['close'] if mitigation_type == "Close" else mitigation_candle['low']
        bearish_mitigation_price = mitigation_candle['close'] if mitigation_type == "Close" else mitigation_candle['high']

        surviving_blocks = []
        for ob in self.active_blocks_by_tf[timeframe]:
            is_mitigated = False
            # Using new fields: price_low, price_high
            if ob.event_type == 'BULLISH_OB' and bullish_mitigation_price < ob.price_low: is_mitigated = True
            elif ob.event_type == 'BEARISH_OB' and bearish_mitigation_price > ob.price_high: is_mitigated = True
            if not is_mitigated: surviving_blocks.append(ob)
        self.active_blocks_by_tf[timeframe] = surviving_blocks

        sensitivity = self.config.get('sensitivity', 0.28)
        roc_period = 4
        if len(df) < roc_period + 1: return
        
        df_copy = df.copy()
        df_copy['roc'] = (df_copy['open'] - df_copy['open'].shift(roc_period)) / df_copy['open'].shift(roc_period)
        
        last_roc, prev_roc = df_copy['roc'].iloc[-1], df_copy['roc'].iloc[-2]
        current_bar_index = len(df_copy) - 1
        impulse_detected, impulse_type_suffix = False, None

        if prev_roc >= -sensitivity and last_roc < -sensitivity: impulse_detected, impulse_type_suffix = True, 'BEARISH'
        if prev_roc <= sensitivity and last_roc > sensitivity: impulse_detected, impulse_type_suffix = True, 'BULLISH'

        if impulse_detected and (current_bar_index - self.last_impulse_index.get(timeframe, 0) > 5):
            self.last_impulse_index[timeframe] = current_bar_index
            
            source_candle_index = -1
            for i in range(4, 16):
                lookback_index = current_bar_index - i
                if lookback_index < 0: break
                candle = df.iloc[lookback_index]
                is_opposing_candle = (impulse_type_suffix == 'BULLISH' and candle['close'] < candle['open']) or \
                                     (impulse_type_suffix == 'BEARISH' and candle['close'] > candle['open'])
                if is_opposing_candle:
                    source_candle_index = lookback_index; break

            if source_candle_index != -1:
                source_candle = df.iloc[source_candle_index]
                # Using the official OrderBlock model from data_models
                new_ob = OrderBlock(
                    block_id=f"{timeframe}_{impulse_type_suffix.lower()}_{source_candle_index}",
                    event_type=f"{impulse_type_suffix}_OB",
                    price_low=source_candle['low'],
                    price_high=source_candle['high'],
                    timeframe=timeframe,
                    created_at_index=source_candle_index
                )
                self.active_blocks_by_tf[timeframe].append(new_ob)
                logger.info(f"SONAR LOCK: New {new_ob.event_type} OB created on {new_ob.timeframe} at ({new_ob.price_low}, {new_ob.price_high})")

    def _hunt_for_interaction_signals(self, all_active_blocks: List[OrderBlock], current_candle: pd.Series, current_candle_index: int) -> List[OBInteractionSignal]:
        # [PACT KEPT]: Core signaling logic is preserved, now returns official signal type.
        signals: List[OBInteractionSignal] = []
        for ob in all_active_blocks:
            signal_id = f"{ob.block_id}_{current_candle_index}"
            if signal_id in self.triggered_signals: continue
            
            signal_fired = False
            # Using new fields: price_low, price_high
            if ob.event_type == 'BULLISH_OB' and current_candle['low'] <= ob.price_high:
                signals.append(OBInteractionSignal(signal_type='BULLISH_OB_INTERACTION', triggering_ob=ob, confidence_score=1.0)); signal_fired = True
            
            elif ob.event_type == 'BEARISH_OB' and current_candle['high'] >= ob.price_low:
                signals.append(OBInteractionSignal(signal_type='BEARISH_OB_INTERACTION', triggering_ob=ob, confidence_score=1.0)); signal_fired = True
            
            if signal_fired:
                self.triggered_signals[signal_id] = current_candle_index
        return signals

    def _manage_signal_memory(self, current_index: int):
        # [PACT KEPT]: The discipline enforcer is 100% PRESERVED.
        if not self.triggered_signals: return
        old_signals = [sig_id for sig_id, index in self.triggered_signals.items() if current_index - index > self.signal_memory_lifespan_candles]
        if old_signals:
            for sig_id in old_signals: del self.triggered_signals[sig_id]
            logger.debug(f"Cipher cleared {len(old_signals)} old signals from memory.")