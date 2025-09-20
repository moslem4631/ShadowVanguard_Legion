# F:\ShadowVanguard_Legion_Godspeed\risk_manager\perimeter_architect.py
# Version 8.1 - Prometheus, The Unified Strategist

import logging
from typing import Dict, Any, Optional, Tuple, List
import pandas as pd
import numpy as np
from dataclasses import dataclass, field

# [PACT KEPT]: All original imports are PRESERVED.
from core.data_models import (MarketDataFrame, PositionV2, StructureReport, PowerReport, 
                              OrderBlockReport, FibonacciReport, LiquidityReport, StructuralEvent)
from core.market_enums import PositionSide, MarketRegime

logger = logging.getLogger("PerimeterArchitect")

@dataclass(slots=True)
class BattlePerimeters:
    # [PACT KEPT]: This model is PRESERVED.
    management_sl: float
    catastrophic_sl: float
    take_profit_levels: List[Tuple[float, float]] = field(default_factory=list)

class PerimeterArchitect:
    """
    THE UNIFIED STRATEGIST: This version completes the final protocol synchronization for
    the command staff. The Grand Strategist now speaks the universal Legion language,
    correctly interpreting modern `OrderBlock` and `Liquidity` reports with the correct
    `all_blocks` and `unfilled_fvgs` structure. This surgical fix eliminates the final
    `AttributeError`, allowing a strike command to be fully translated into actionable
    battle perimeters. The entire command chain is now unified.
    """
    def __init__(self, config: Dict[str, Any]):
        # [PACT KEPT]: The original constructor logic is PRESERVED.
        self.config = config
        self.pa_config = self.config.get('perimeter_architect', {})
        self.tp_config = self.config.get('take_profit_engine', {})
        self.atr_period = self.pa_config.get('atr_period', 14)
        self.base_atr_multiplier = self.pa_config.get('atr_multiplier', 2.0)
        self.range_atr_multiplier = self.pa_config.get('range_atr_multiplier', 4.5)
        self.catastrophic_atr_extension = self.pa_config.get('catastrophic_atr_extension', 1.0)
        self.strategic_timeframes = self.pa_config.get('strategic_timeframes', ['4h', '1h'])
        self.tactical_timeframe = self.pa_config.get('tactical_timeframe', '5m')
        logger.info("[PerimeterArchitect] The Unified Strategist v8.1 deployed. All blueprints are synchronized.")

    def _get_all_structural_points(
        self, side: PositionSide, structure: Optional[StructureReport], 
        ob_report: Optional[OrderBlockReport], liq_report: Optional[LiquidityReport],
        timeframes: List[str]
    ) -> List[float]:
        """
        [PROTOCOL SYNCHRONIZATION]: This utility is now updated to read the modern,
        universal `all_blocks` and `unfilled_fvgs` report formats.
        """
        points = []
        is_long = side == PositionSide.LONG

        for tf in timeframes:
            # Gather from StructureReport (Swings)
            if structure and structure.structural_narrative:
                swing_type_fragment = 'LOW' if is_long else 'HIGH'
                events = structure.structural_narrative.get(tf, [])
                points.extend([event.price_level for event in events if swing_type_fragment in event.event_type])

            # Gather from OrderBlockReport (Corrected)
            if ob_report and ob_report.all_blocks:
                block_side = 'bullish' if is_long else 'bearish'
                blocks_for_tf = ob_report.all_blocks.get(tf, {}).get(block_side, [])
                if is_long:
                    points.extend([block.price_low for block in blocks_for_tf])
                else: # SHORT
                    points.extend([block.price_high for block in blocks_for_tf])
            
            # Gather from LiquidityReport (Corrected)
            if liq_report and liq_report.unfilled_fvgs:
                fvg_side = 'bullish' if is_long else 'bearish'
                voids_for_tf = liq_report.unfilled_fvgs.get(tf, {}).get(fvg_side, [])
                if is_long:
                     # For a long, a bullish FVG's top is a support level
                     points.extend([v.price_high for v in voids_for_tf])
                else: # SHORT
                     # For a short, a bearish FVG's bottom is a resistance level
                     points.extend([v.price_low for v in voids_for_tf])
        
        return sorted(list(set(points)), reverse=is_long)

    def _find_optimal_sl_point(
        self, side: PositionSide, entry_price: float, ohlcv_df: pd.DataFrame,
        structure: Optional[StructureReport], ob_report: Optional[OrderBlockReport],
        liq_report: Optional[LiquidityReport]
    ) -> float:
        # [PACT KEPT]: This battle-hardened logic is PRESERVED.
        is_long = side == PositionSide.LONG
        atr = self._calculate_atr(ohlcv_df)
        if atr < 1e-9: atr = entry_price * 0.005 

        htf_points = self._get_all_structural_points(side, structure, ob_report, liq_report, self.strategic_timeframes)
        valid_htf_structures = [p for p in htf_points if p < entry_price] if is_long else [p for p in htf_points if p > entry_price]
        if valid_htf_structures:
            best_htf_structure = max(valid_htf_structures) if is_long else min(valid_htf_structures)
            sl_point = best_htf_structure - (atr * 0.2) if is_long else best_htf_structure + (atr * 0.2)
            logger.info(f"Unified Strategist placed SL based on HTF structure at {best_htf_structure:.4f}.")
            return sl_point

        tactical_points = self._get_all_structural_points(side, structure, ob_report, liq_report, [self.tactical_timeframe])
        valid_tactical_structures = [p for p in tactical_points if p < entry_price] if is_long else [p for p in tactical_points if p > entry_price]
        if valid_tactical_structures:
            best_tactical_structure = max(valid_tactical_structures) if is_long else min(valid_tactical_structures)
            sl_point = best_tactical_structure - (atr * 0.2) if is_long else best_tactical_structure + (atr * 0.2)
            logger.info(f"No HTF support. Placed SL based on Tactical structure at {best_tactical_structure:.4f}.")
            return sl_point
            
        logger.warning("No valid structural points found for SL placement. Falling back to ATR.")
        sl_distance = atr * self.base_atr_multiplier
        return entry_price - sl_distance if is_long else entry_price + sl_distance
    
    def _find_strategic_targets(
        self, side: PositionSide, entry_price: float, catastrophic_sl: float,
        structure: Optional[StructureReport], ob_report: Optional[OrderBlockReport],
        liq_report: Optional[LiquidityReport]
    ) -> List[Tuple[float, float]]:
        # [PACT KEPT]: This battle-hardened logic is PRESERVED.
        is_long = side == PositionSide.LONG
        opposing_side = PositionSide.SHORT if is_long else PositionSide.LONG
        
        all_timeframes = self.strategic_timeframes + [self.tactical_timeframe]
        opposing_points = self._get_all_structural_points(opposing_side, structure, ob_report, liq_report, all_timeframes)
        
        valid_targets = [p for p in opposing_points if p > entry_price] if is_long else [p for p in opposing_points if p < entry_price]
        targets = []
        if valid_targets: targets.extend(valid_targets[:2])
        
        risk_per_unit = abs(entry_price - catastrophic_sl)
        if risk_per_unit > 1e-9:
            min_rr = self.tp_config.get('min_rr_target', 1.5)
            rr_target_price = entry_price + (risk_per_unit * min_rr) if is_long else entry_price - (risk_per_unit * min_rr)
            if not targets or (is_long and rr_target_price > targets[-1]) or (not is_long and rr_target_price < targets[-1]):
                 targets.append(rr_target_price)

        if not targets: 
            logger.warning("No valid TP targets found (structural or RR).")
            return []
        
        unique_targets = sorted(list(set(targets)), reverse=not is_long)
        strategy = self.tp_config.get('exit_strategy', {'TP1': 0.5, 'TP2': 0.5})
        take_profit_levels: List[Tuple[float, float]] = []
        
        if len(unique_targets) >= 1 and 'TP1' in strategy:
            take_profit_levels.append((round(unique_targets[0], 8), strategy['TP1']))
        if len(unique_targets) >= 2 and 'TP2' in strategy:
            take_profit_levels.append((round(unique_targets[1], 8), strategy['TP2']))
            
        logger.info(f"Unified Strategist plans offensive for {side.name}: {len(take_profit_levels)} objective(s) identified.")
        return take_profit_levels

    def determine_battle_perimeters(
        self, side: PositionSide, entry_price: float,
        mdf: MarketDataFrame
    ) -> Optional[BattlePerimeters]:
        # [PACT KEPT]: This method is PRESERVED.
        ohlcv_df = mdf.ohlcv_multidim.get(self.tactical_timeframe)
        if ohlcv_df is None or ohlcv_df.empty:
            logger.error(f"Tactical timeframe '{self.tactical_timeframe}' data missing for perimeter calculation.")
            return None
            
        optimal_sl_point = self._find_optimal_sl_point(
            side, entry_price, ohlcv_df, 
            mdf.structure_report, mdf.ob_report, mdf.liq_report
        )
        
        atr = self._calculate_atr(ohlcv_df)
        if atr < 1e-9:
             logger.warning("ATR is zero. Cannot architect perimeters. Systems offline.")
             return None

        management_sl = optimal_sl_point
        moat_distance = atr * self.catastrophic_atr_extension
        catastrophic_sl = management_sl - moat_distance if side == PositionSide.LONG else management_sl + moat_distance

        take_profit_levels = self._find_strategic_targets(
            side, entry_price, catastrophic_sl, 
            mdf.structure_report, mdf.ob_report, mdf.liq_report
        )
        
        return BattlePerimeters(
            management_sl=round(management_sl, 8),
            catastrophic_sl=round(catastrophic_sl, 8),
            take_profit_levels=take_profit_levels
        )

    def _calculate_atr(self, ohlcv_df: pd.DataFrame) -> float:
        # [PACT KEPT]: This utility is PRESERVED.
        if len(ohlcv_df) < self.atr_period + 1: return np.mean(ohlcv_df['high'] - ohlcv_df['low']) if not ohlcv_df.empty else 0.0
        df = ohlcv_df.copy(); df['h-l'] = df['high'] - df['low']; df['h-pc'] = abs(df['high'] - df['close'].shift(1)); df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        tr = df[['h-l', 'h-pc', 'l-pc']].max(axis=1); atr = tr.ewm(alpha=1/self.atr_period, adjust=False).mean()
        return atr.iloc[-1] if pd.notna(atr.iloc[-1]) else 0.0
    
    def update_trailing_stop_loss(self, position: PositionV2, current_price: float) -> Optional[float]:
        # [PACT KEPT]: This method is PRESERVED.
        return None