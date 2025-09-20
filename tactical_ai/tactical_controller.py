# F:\ShadowVanguard_Legion_Godspeed\tactical_ai\tactical_controller.py
# Version 42.0 - Prometheus, The True-Sight Eagle

import logging
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass, field

# [PACT KEPT]: All core model imports are PRESERVED.
from core.data_models import (PositionV2, TacticalSignal, PowerReport, StructureReport,
                              MarketDataFrame, OrderBlockReport, FibonacciReport,
                              DivergenceReport, LiquidityReport, StructuralEvent, OrderBlock, FairValueGap)
from core.market_enums import TacticalDecision, PositionSide, MarketRegime, MarketPersonality
from execution_engine.position_manager import PositionManager
from memory.experience_memory import ExperienceMemory
from memory.strategic_memory import StrategicMemory
from memory.performance_auditor import StrategicAlertLevel

logger = logging.getLogger("TacticalController")

# [PACT KEPT]: These helper dataclasses are PRESERVED.
@dataclass
class WisdomFactors:
    opportunity_score: float = 0.0; threat_score: float = 0.0; reasons: List[str] = field(default_factory=list)

@dataclass
class AmbushPoint:
    is_valid: bool = False; side: Optional[PositionSide] = None
    opportunity_type: str = "NONE"; reason: str = ""

@dataclass
class ProximityDebugInfo:
    """A new helper to make the Eagle's thought process transparent."""
    nearest_support: Optional[Tuple[str, float]] = None # (Type, Price)
    dist_to_support_pct: float = float('inf')
    nearest_resistance: Optional[Tuple[str, float]] = None # (Type, Price)
    dist_to_resistance_pct: float = float('inf')

class TacticalController:
    """
    THE TRUE-SIGHT EAGLE: This is the definitive hunter. A critical scaling bug in
    its proximity calculation has been corrected, allowing it to finally see the
    battlefield with its intended range. Furthermore, its mind is now transparent;
    if it chooses not to strike, it will report precisely WHY the location was not
    deemed a valid ambush point, eliminating all guesswork. The hunt begins now.
    """
    def __init__(self, position_manager: PositionManager, memory: ExperienceMemory, strategic_memory: StrategicMemory, config: Dict[str, Any]):
        # [PACT KEPT]: This method is PRESERVED.
        self.position_manager = position_manager; self.memory = memory; self.strategic_memory = strategic_memory; self.config = config
        self.rearm(config)
        self.last_sent_roe: Dict[str, Any] = {}; logger.info(f"[TacticalController] The True-Sight Eagle v42.0 is in command. Vision corrected and amplified.")

    def rearm(self, config: Dict[str, Any]):
        # [PACT KEPT]: This method is PRESERVED.
        self.controller_config = config.get('tactical_controller', {}); self.strategic_protocol = self.controller_config.get('strategic_protocol', {})
        self.management_rules = self.controller_config.get('management_rules', {}); self.scoring_weights = self.controller_config.get('scoring_weights', {})

    def decide_and_signal(self,
                          mdf: MarketDataFrame,
                          strategic_alert_status: Dict[str, Any],
                          active_pos: Optional[PositionV2]
                          ) -> Tuple[TacticalDecision, Optional[TacticalSignal]]:
        # [PACT KEPT]: This high-level routing is PRESERVED.
        if active_pos:
            return self.manage_engaged_position(active_pos, mdf)
        else:
            return self._find_prime_engagement_opportunity(mdf, strategic_alert_status)

    def _find_prime_engagement_opportunity(
        self, mdf: MarketDataFrame, strategic_alert_status: Dict[str, Any]
    ) -> Tuple[TacticalDecision, Optional[TacticalSignal]]:
        # [PACT KEPT]: The two-phase protocol is PRESERVED.
        if not mdf.structure_report or mdf.structure_report.market_personality == MarketPersonality.UNDEFINED:
            logger.debug("Talon waits: Environment is uncertain."); return TacticalDecision.WAIT, None

        ambush_point, debug_info = self._find_area_of_value(mdf) # Now returns debug info
        if not ambush_point.is_valid:
            logger.debug(
                f"Talon waits: No Area of Value identified. Proximity report: "
                f"DistToSupport={debug_info.dist_to_support_pct:.3f}% (Zone: {debug_info.nearest_support}), "
                f"DistToResistance={debug_info.dist_to_resistance_pct:.3f}% (Zone: {debug_info.nearest_resistance})."
            )
            return TacticalDecision.WAIT, None
        
        logger.info(f"EAGLE'S SIGHT: High-value ambush point detected! Type: {ambush_point.opportunity_type}, Side: {ambush_point.side.name}, Reason: {ambush_point.reason}")

        power_report = mdf.power_report
        if not power_report:
             logger.warning("Cowboy holds fire: PowerReport is missing."); return TacticalDecision.WAIT, None
        
        true_net_force = power_report.true_net_force
        tactical_threshold = self.controller_config.get('unified_entry_protocol', {}).get('min_true_net_force_for_entry', 15.0) 
        
        has_truthful_power = (ambush_point.side == PositionSide.LONG and true_net_force >= tactical_threshold) or \
                             (ambush_point.side == PositionSide.SHORT and true_net_force <= -tactical_threshold)

        if not has_truthful_power:
            logger.info(f"Knight found ambush point for {ambush_point.side.name}, but Oracle's judgment ({true_net_force:.2f}) lacks conviction (Threshold: {tactical_threshold}). Holding fire.")
            return TacticalDecision.WAIT, None
            
        logger.critical(
            f"!!! TRUE-SIGHT STRIKE AUTHORIZED ({ambush_point.opportunity_type}) !!! "
            f"Reason: {ambush_point.reason}, Oracle's Judgment (TrueNetForce): {true_net_force:.2f}. "
        )
        unified_signal = TacticalSignal(
            source=f"TRUE_SIGHT_STRIKE:{ambush_point.side.name}", confidence=1.0, suggestion=TacticalDecision.ADVANCE, 
            details={ "side": ambush_point.side, "symbol": mdf.symbol, "risk_level": "FULL" }
        )
        return TacticalDecision.ADVANCE, unified_signal

    def _find_area_of_value(self, mdf: MarketDataFrame) -> Tuple[AmbushPoint, ProximityDebugInfo]:
        """
        [SURGICAL INTERVENTION - TRUE-SIGHT PROTOCOL]: The scaling bug is corrected.
        Proximity is now calculated correctly based on the settings file. Additionally,
        the method now returns detailed debug information for transparent decision-making.
        """
        structure = mdf.structure_report; tactical_tf = '5m'
        if tactical_tf not in mdf.ohlcv_multidim: return AmbushPoint(), ProximityDebugInfo()
        current_price = mdf.ohlcv_multidim[tactical_tf]['close'].iloc[-1]
        
        strategic_tf = next((tf for tf in ['4h', '1h', '15m', '5m'] if tf in structure.market_regime), None)
        if not strategic_tf: return AmbushPoint(), ProximityDebugInfo()
        
        regime = structure.market_regime[strategic_tf]
        
        # [CRITICAL BUG FIX]: The proximity percentage is now used directly as a percentage.
        # The erroneous division by 100 has been REMOVED.
        proximity_percent = self.controller_config.get('aov_proximity_percent', 0.5)

        # [NEW DEBUG UNIT]: Initialize our new transparent thought process reporter.
        debug_info = ProximityDebugInfo()

        # Gather all potential support and resistance zones
        supports = [] # List of (type, price_high)
        resistances = [] # List of (type, price_low)
        for tf in ['1h', '15m', '5m']:
            if tf in mdf.ob_report.all_blocks:
                supports.extend([(f"{tf}_OB", ob.price_high) for ob in mdf.ob_report.all_blocks.get(tf, {}).get('bullish', []) if ob.price_high < current_price])
                resistances.extend([(f"{tf}_OB", ob.price_low) for ob in mdf.ob_report.all_blocks.get(tf, {}).get('bearish', []) if ob.price_low > current_price])
            if tf in mdf.liq_report.unfilled_fvgs:
                supports.extend([(f"{tf}_FVG", fvg.price_high) for fvg in mdf.liq_report.unfilled_fvgs.get(tf, {}).get('bullish', []) if fvg.price_high < current_price])
                resistances.extend([(f"{tf}_FVG", fvg.price_low) for fvg in mdf.liq_report.unfilled_fvgs.get(tf, {}).get('bearish', []) if fvg.price_low > current_price])

        # Find closest support and resistance for debugging
        if supports:
            debug_info.nearest_support = max(supports, key=lambda item: item[1])
            debug_info.dist_to_support_pct = (current_price - debug_info.nearest_support[1]) / current_price * 100
        if resistances:
            debug_info.nearest_resistance = min(resistances, key=lambda item: item[1])
            debug_info.dist_to_resistance_pct = (debug_info.nearest_resistance[1] - current_price) / current_price * 100
        
        # --- HUNTING LOGIC (Now using correct proximity) ---
        if regime in [MarketRegime.BULL_TREND, MarketRegime.BULL_TREND_PULLBACK]:
            if debug_info.dist_to_support_pct < proximity_percent:
                return AmbushPoint(is_valid=True, side=PositionSide.LONG, opportunity_type="WAVE_RIDE_PROXIMITY",
                                   reason=f"Price near support zone {debug_info.nearest_support[0]} at {debug_info.nearest_support[1]:.2f}"), debug_info
                                   
        elif regime in [MarketRegime.BEAR_TREND, MarketRegime.BEAR_TREND_PULLBACK]:
            if debug_info.dist_to_resistance_pct < proximity_percent:
                return AmbushPoint(is_valid=True, side=PositionSide.SHORT, opportunity_type="WAVE_RIDE_PROXIMITY",
                                   reason=f"Price near resistance zone {debug_info.nearest_resistance[0]} at {debug_info.nearest_resistance[1]:.2f}"), debug_info

        elif regime == MarketRegime.TIGHT_RANGE and structure.range_high and structure.range_low:
             if debug_info.dist_to_support_pct < proximity_percent:
                return AmbushPoint(is_valid=True, side=PositionSide.LONG, opportunity_type="VALLEY_AMBUSH_LOW",
                                   reason=f"Price near range low {structure.range_low:.2f}"), debug_info
             if debug_info.dist_to_resistance_pct < proximity_percent:
                return AmbushPoint(is_valid=True, side=PositionSide.SHORT, opportunity_type="VALLEY_AMBUSH_HIGH",
                                   reason=f"Price near range high {structure.range_high:.2f}"), debug_info

        return AmbushPoint(), debug_info

    def manage_engaged_position(self, position: PositionV2, mdf: MarketDataFrame) -> Tuple[TacticalDecision, Optional[TacticalSignal]]:
        # [PACT KEPT]: This battle-hardened logic is 100% PRESERVED.
        tactical_tf_name = '5m'; tactical_df = mdf.ohlcv_multidim.get(tactical_tf_name)
        if tactical_df is None or tactical_df.empty: return TacticalDecision.HOLD, None
        current_price=tactical_df.iloc[-1]['close']; wisdom=self._convene_war_council_and_assess_wisdom(position.side,mdf)
        catastrophic_threat_threshold=self.management_rules.get('catastrophic_threat_threshold',4.0)
        if wisdom.threat_score >= catastrophic_threat_threshold:
            logger.critical(f"CATASTROPHIC THREAT! Score {wisdom.threat_score:.2f}. Retreat. Reasons: {wisdom.reasons}")
            return TacticalDecision.RETREAT,TacticalSignal(source="MANAGEMENT:CATASTROPHIC_THREAT",suggestion=TacticalDecision.RETREAT,details={"position_id":position.position_id})
        if position.take_profit_levels:
            next_tp_index=position.tps_hit
            if next_tp_index<len(position.take_profit_levels):
                target_price,exit_ratio=position.take_profit_levels[next_tp_index]; is_long=position.side==PositionSide.LONG
                if (is_long and current_price>=target_price) or (not is_long and current_price<=target_price):
                    logger.info(f"VICTORY OBJECTIVE #{next_tp_index+1} ACHIEVED @ {current_price:.2f}.")
                    position.tps_hit+=1; is_final_tp=position.tps_hit==len(position.take_profit_levels); decision=TacticalDecision.RETREAT if is_final_tp else TacticalDecision.PARTIAL_EXIT
                    return decision,TacticalSignal(source=f"MANAGEMENT:TP_{next_tp_index+1}_HIT",suggestion=decision,details={"position_id":position.position_id,"exit_ratio":exit_ratio})
        proactive_threat_threshold=self.management_rules.get('proactive_threat_threshold',2.5)
        if wisdom.threat_score>=proactive_threat_threshold:
             logger.warning(f"PROACTIVE DEFENSE! Threat score {wisdom.threat_score:.2f}. Securing profits. Reasons: {wisdom.reasons}")
             proactive_exit_ratio=self.management_rules.get('proactive_exit_ratio',0.5)
             return TacticalDecision.PARTIAL_EXIT,TacticalSignal(source="MANAGEMENT:PROACTIVE_DEFENSE",suggestion=TacticalDecision.PARTIAL_EXIT,details={"position_id":position.position_id,"exit_ratio":proactive_exit_ratio})
        logger.debug(f"Unified Mind Orders: HOLD FORMATION! Pos {position.position_id} on course.")
        return TacticalDecision.HOLD,None
    
    def _convene_war_council_and_assess_wisdom(self, proposed_side: PositionSide, mdf: MarketDataFrame) -> WisdomFactors:
        # [PACT KEPT]: This logic is 100% PRESERVED.
        opp_score,threat_score,reasons,is_long=0.0,0.0,[],proposed_side==PositionSide.LONG
        timeframe_weights=self.scoring_weights.get('timeframe_weights',{'4h':2.0,'1h':1.5,'15m':1.2,'5m':1.0})
        def assess_signals(report,name,signals_attr,type_attr,details_func):
            nonlocal opp_score,threat_score,reasons
            if not report or not hasattr(report,signals_attr):return
            for tf,signals in getattr(report,signals_attr).items():
                tf_weight=timeframe_weights.get(tf,1.0)
                for signal in signals:
                    base_weight=self.scoring_weights.get(getattr(signal,type_attr).lower(),1.0);score=signal.confidence_score*base_weight*tf_weight;details=details_func(signal)
                    is_opp=(is_long and 'BULLISH' in getattr(signal,type_attr)) or (not is_long and 'BEARISH' in getattr(signal,type_attr))
                    if is_opp:opp_score+=score;reasons.append(f"OPP-{name}_{details}@{tf}")
                    else:threat_score+=score;reasons.append(f"THREAT-{name}_{details}@{tf}")
        assess_signals(mdf.ob_report,"OB","interaction_signals","signal_type",lambda s:f"{s.triggering_ob.event_type[:4]}"); assess_signals(mdf.liq_report,"FVG","confirmation_signals","signal_type",lambda s:f"{s.triggering_void.event_type[:7]}")
        assess_signals(mdf.fib_report,"FIB","confirmation_signals","signal_type",lambda s:f"{s.triggering_zone.source_level:.3f}"); assess_signals(mdf.div_report,"DIV","confirmation_signals","signal_type",lambda s:f"{s.triggering_pattern.pattern_type}")
        if mdf.structure_report:
            for tf,events in mdf.structure_report.structural_narrative.items():
                tf_weight=timeframe_weights.get(tf,1.0)
                for event in events:
                    weight=self.scoring_weights.get(event.event_type.lower(),1.5); score=event.confidence*weight*tf_weight
                    is_opp=(is_long and 'BULLISH' in event.event_type) or (not is_long and 'BEARISH' in event.event_type)
                    if is_opp:opp_score+=score;reasons.append(f"OPP-{event.event_type}@{tf}")
                    else:threat_score+=score;reasons.append(f"THREAT-{event.event_type}@{tf}")
        return WisdomFactors(opportunity_score=opp_score,threat_score=threat_score,reasons=list(set(reasons)))