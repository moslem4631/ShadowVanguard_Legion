# F:\ShadowVanguard_Legion_Godspeed\analyst_ai\structure_analyzer.py
# Version 15.1 - Prometheus, The Comprehensive Historian (CORRECTED & VERIFIED)

import logging
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass
import numpy as np

# [PACT KEPT]: All original model imports are PRESERVED.
from core.data_models import MarketDataFrame, StructureReport, StructuralEvent, OrderBlock, FairValueGap
from core.market_enums import MarketRegime, PositionSide, MarketPersonality

logger = logging.getLogger("StructureAnalyzer")

@dataclass
class StrategicContext:
    # [PACT KEPT]: This helper class is PRESERVED.
    timeframe: str
    last_price: float
    nearest_support: Optional[OrderBlock] = None
    nearest_resistance: Optional[OrderBlock] = None
    nearby_bullish_fvg: Optional[FairValueGap] = None
    nearby_bearish_fvg: Optional[FairValueGap] = None
    distance_to_support: float = float('inf')
    distance_to_resistance: float = float('inf')


class StructureAnalyzer:
    """
    THE COMPREHENSIVE HISTORIAN: This version resolves the final communication breakdown.
    The Historian is now mandated to provide a dual-perspective report: one primary
    strategic verdict from the most relevant high timeframe, AND a mandatory tactical
    assessment for the base timeframe ('5m'). This ensures units like the Psychologist
    always receive the tactical context they need, awakening all senses of the Legion.
    """
    def __init__(self, config: Dict[str, Any]):
        # [PACT KEPT]: The structure of this method is 100% PRESERVED.
        self.config = config
        self.context_config = self.config.get('context_awareness', {})
        self.proximity_threshold_percent = self.context_config.get('proximity_threshold_percent', 0.5) 
        # [NEW DOCTRINE]: Define the mandatory tactical timeframe.
        self.tactical_timeframe = '5m'
        logger.info(f"[StructureAnalyzer] The Comprehensive Historian v15.1 is online. Reports are now dual-perspective.")

    def analyze(self, mdf: MarketDataFrame) -> StructureReport:
        # [SURGICAL INTERVENTION]: The reporting logic is now dual-perspective.
        report = StructureReport()
        available_timeframes = list(mdf.ohlcv_multidim.keys())
        if not available_timeframes:
            logger.warning("No OHLCV data for analysis. Aborting."); return report
        
        context_map: Dict[str, StrategicContext] = {}
        for tf in available_timeframes:
            df = mdf.ohlcv_multidim.get(tf)
            if df is None or df.empty or len(df) < 2: continue
            
            context = self._build_strategic_context(tf, df, mdf)
            context_map[tf] = context

        # --- Phase 1: Get the Primary STRATEGIC Verdict ---
        final_personality, certainty, strategic_context = self._synthesize_final_verdict(context_map)
        report.market_personality = final_personality
        report.personality_certainty = certainty
        
        if strategic_context:
            tf = strategic_context.timeframe
            report.primary_trend[tf] = self._infer_primary_trend(strategic_context)
            report.market_regime[tf] = self._determine_regime_from_context(strategic_context)
            if report.market_regime.get(tf) == MarketRegime.TIGHT_RANGE:
                report.range_high = strategic_context.nearest_resistance.price_high if strategic_context.nearest_resistance else None
                report.range_low = strategic_context.nearest_support.price_low if strategic_context.nearest_support else None
        
        # --- Phase 2: MANDATORY Tactical Assessment ---
        # This ensures the Psychologist always gets its required intel.
        if self.tactical_timeframe in context_map:
            tactical_context = context_map[self.tactical_timeframe]
            # Avoid overwriting if strategic context was already the tactical one
            if self.tactical_timeframe not in report.market_regime:
                 report.market_regime[self.tactical_timeframe] = self._determine_regime_from_context(tactical_context)
            if self.tactical_timeframe not in report.primary_trend:
                 report.primary_trend[self.tactical_timeframe] = self._infer_primary_trend(tactical_context)
        else:
             logger.warning(f"Mandatory tactical context for '{self.tactical_timeframe}' could not be generated.")

        log_regime_tf = strategic_context.timeframe if strategic_context else 'N/A'
        log_regime = report.market_regime.get(log_regime_tf, MarketRegime.UNCERTAIN).name
        logger.info(
            f"CONTEXTUAL INTEL: Final Ruling={report.market_personality.name} (Cert: {report.personality_certainty:.2f}). "
            f"Strategic Context on [{log_regime_tf}]: Regime: {log_regime}"
        )
        return report

    def _build_strategic_context(self, timeframe: str, df: pd.DataFrame, mdf: MarketDataFrame) -> StrategicContext:
        """Creates a snapshot of the current price relative to key strategic zones."""
        last_price = df['close'].iloc[-1]
        context = StrategicContext(timeframe=timeframe, last_price=last_price)

        # Find nearest support (Bullish OB)
        bullish_obs = mdf.ob_report.all_blocks.get(timeframe, {}).get('bullish', [])
        if bullish_obs:
            valid_supports = [ob for ob in bullish_obs if ob.price_high < last_price]
            if valid_supports:
                context.nearest_support = min(valid_supports, key=lambda ob: last_price - ob.price_high)
                context.distance_to_support = (last_price - context.nearest_support.price_high) / last_price * 100

        # Find nearest resistance (Bearish OB)
        bearish_obs = mdf.ob_report.all_blocks.get(timeframe, {}).get('bearish', [])
        if bearish_obs:
            valid_resistances = [ob for ob in bearish_obs if ob.price_low > last_price]
            if valid_resistances:
                context.nearest_resistance = min(valid_resistances, key=lambda ob: ob.price_low - last_price)
                context.distance_to_resistance = (context.nearest_resistance.price_low - last_price) / last_price * 100
        
        # Check for nearby FVGs (these act as magnets)
        if mdf.liq_report and mdf.liq_report.unfilled_fvgs:
            bullish_fvgs = mdf.liq_report.unfilled_fvgs.get(timeframe, {}).get('bullish', [])
            bearish_fvgs = mdf.liq_report.unfilled_fvgs.get(timeframe, {}).get('bearish', [])
            if bullish_fvgs:
                context.nearby_bullish_fvg = min(bullish_fvgs, key=lambda fvg: abs(fvg.price_high - last_price))
            if bearish_fvgs:
                context.nearby_bearish_fvg = min(bearish_fvgs, key=lambda fvg: abs(fvg.price_low - last_price))

        return context

    def _synthesize_final_verdict(self, context_map: Dict[str, StrategicContext]) -> Tuple[MarketPersonality, float, Optional[StrategicContext]]:
        """
        The new Intel Council. It reviews context reports from all timeframes
        and issues a final, unified ruling on the market's personality.
        """
        # Prioritize higher timeframes for the big picture
        for tf in ['4h', '1h', '15m', '5m']:
            if tf not in context_map:
                continue

            context = context_map[tf]
            is_near_support = context.distance_to_support < self.proximity_threshold_percent
            is_near_resistance = context.distance_to_resistance < self.proximity_threshold_percent
            
            # --- Ranging/Mean-Reverting Logic ---
            if context.nearest_support and context.nearest_resistance:
                total_range = context.nearest_resistance.price_high - context.nearest_support.price_low
                if not is_near_support and not is_near_resistance and total_range > 0:
                    mid_point = context.nearest_support.price_low + total_range / 2
                    if abs(context.last_price - mid_point) / total_range < 0.25:
                        return MarketPersonality.MEAN_REVERTING, 0.75, context
                
                if is_near_support or is_near_resistance:
                    return MarketPersonality.MEAN_REVERTING, 0.9, context

            # --- Trending/Momentum Logic ---
            if not context.nearest_resistance and (context.nearby_bullish_fvg or context.nearest_support):
                return MarketPersonality.MOMENTUM_DRIVEN, 0.7, context
            if not context.nearest_support and (context.nearby_bearish_fvg or context.nearest_resistance):
                return MarketPersonality.MOMENTUM_DRIVEN, 0.7, context

        return MarketPersonality.UNDEFINED, 0.0, context_map.get(self.tactical_timeframe)

    def _determine_regime_from_context(self, context: StrategicContext) -> MarketRegime:
        """Determines the tactical regime based on the strategic context."""
        is_near_support = context.distance_to_support < self.proximity_threshold_percent
        is_near_resistance = context.distance_to_resistance < self.proximity_threshold_percent
        
        if context.nearest_support and context.nearest_resistance:
            return MarketRegime.TIGHT_RANGE

        if is_near_support and not is_near_resistance:
            return MarketRegime.BULL_TREND_PULLBACK
            
        if is_near_resistance and not context.nearest_support:
            return MarketRegime.BEAR_TREND_PULLBACK

        if context.last_price > (context.nearest_support.price_high if context.nearest_support else -1):
            return MarketRegime.BULL_TREND

        if context.last_price < (context.nearest_resistance.price_low if context.nearest_resistance else float('inf')):
            return MarketRegime.BEAR_TREND
            
        return MarketRegime.UNCERTAIN

    def _infer_primary_trend(self, context: StrategicContext) -> PositionSide:
        """Infers the primary trend direction from the strategic context."""
        if context.nearest_support and context.nearest_resistance:
            dist_to_ceil = context.distance_to_resistance
            dist_to_floor = context.distance_to_support
            if dist_to_ceil == float('inf') and dist_to_floor == float('inf'):
                return PositionSide.NEUTRAL
            return PositionSide.LONG if dist_to_ceil > dist_to_floor else PositionSide.SHORT

        if context.nearest_support and not context.nearest_resistance:
            return PositionSide.LONG 
        if context.nearest_resistance and not context.nearest_support:
            return PositionSide.SHORT
            
        return PositionSide.NEUTRAL