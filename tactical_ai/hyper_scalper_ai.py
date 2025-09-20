# F:\ShadowVanguard_Legion_Godspeed\tactical_ai\hyper_scalper_ai.py
# Version 8.0 - Prometheus, The Tactical Lookout

import logging
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

from core.data_models import MarketDataFrame, PowerReport, EmotionReport
from core.market_enums import PositionSide

logger = logging.getLogger("HyperScalperAI")

# --- [REVOLUTION I]: The New Intelligence Packet ---
# This unit no longer makes decisions. It produces high-quality, actionable intelligence.
# This dataclass IS its new product.

@dataclass
class TacticalImpulse:
    """ A pure, distilled report on the immediate tactical pulse of the market. """
    side: Optional[PositionSide] = None
    risk_level: Optional[str] = None # 'FULL', 'HALF', or 'SCOUT'
    confidence: float = 0.0
    raw_force_details: Dict[str, float] = field(default_factory=dict)

class HyperScalperAI:
    """
    THE TACTICAL LOOKOUT: The absolute pinnacle of specialization. This unit has been
    relieved of all command duties to focus on one single, critical mission: to sense
    the raw, instantaneous market pulse with unmatched speed and accuracy.

    - PURE SENSOR: It no longer makes decisions or processes complex strategic wisdom.
      Its sole purpose is to convert the raw PowerReport into a classified
      `TacticalImpulse`.

    - NO MORE VETO: The `decide_entry` method is abolished. The new `assess_impulse`
      method returns a *report*, not a command, permanently eliminating the
      "Soldier's Veto" and establishing a perfect chain of command.

    - BATTLE-TESTED LOGIC PRESERVED: The brilliant tiered-threshold logic for
      classifying impulse strength ('FULL', 'HALF', 'SCOUT') is fully preserved
      and now serves to enrich the tactical report sent to High Command.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        [SIMPLIFIED]: The constructor is now radically simplified. It no longer needs
        a connection to the War Council. It is an independent sensor.
        """
        self.protocol = config.get('hyper_scalper_protocol', {})
        self.ticks_since_last_strike = 0
        logger.info("[HyperScalperAI] The Tactical Lookout v8.0 is on the wall. Eyes open.")

    def assess_impulse(self, mdf: MarketDataFrame) -> TacticalImpulse:
        """
        [THE NEW CORE]: This method replaces `decide_entry`. It does not decide;
        it assesses, classifies, and reports.
        """
        # --- Step 1: Preliminary Tactical Checks (Preserved Wisdom) ---
        observation_candles = self.protocol.get('observation_candles', 5)
        self.ticks_since_last_strike += 1
        if self.ticks_since_last_strike < observation_candles:
            return TacticalImpulse() # Report no impulse
            
        emotion = mdf.emotion_report or EmotionReport()
        if emotion.exhaustion > self.protocol.get('exhaustion_veto_threshold', 0.90):
            logger.warning("LOOKOUT REPORTS: High market exhaustion. Impulse is unreliable.")
            self.ticks_since_last_strike = 0
            return TacticalImpulse()

        # --- Step 2: Sense the Raw Force ---
        power = mdf.power_report or PowerReport()
        raw_book_force, raw_tape_pressure = power.net_force, power.delta_joiners
        
        # --- Step 3: Classify the Force using Preserved Logic ---
        # The warrior's keen sense of scale is preserved.
        long_risk, _ = self._evaluate_raw_strike(raw_book_force, raw_tape_pressure, PositionSide.LONG)
        short_risk, _ = self._evaluate_raw_strike(raw_book_force, raw_tape_pressure, PositionSide.SHORT)
        
        side: Optional[PositionSide] = None
        risk_level: Optional[str] = None
        
        # Determine the strongest, valid impulse direction.
        if long_risk and not short_risk:
            side, risk_level = PositionSide.LONG, long_risk
        elif short_risk and not long_risk:
            side, risk_level = PositionSide.SHORT, short_risk
        elif long_risk and short_risk:
            side, risk_level = (PositionSide.LONG, long_risk) if abs(raw_book_force) >= abs(raw_book_force) else (PositionSide.SHORT, short_risk)
        
        # --- Step 4: File the Report ---
        if side:
            self.ticks_since_last_strike = 0
            logger.info(f"LOOKOUT REPORT: Detected {side.name} impulse, classified as {risk_level}.")
            return TacticalImpulse(
                side=side,
                risk_level=risk_level,
                confidence=power.confidence,
                raw_force_details={'book': raw_book_force, 'tape': raw_tape_pressure}
            )
        
        return TacticalImpulse() # Report no significant impulse


    # --- [PACT KEPT]: The tiered evaluation logic is preserved and repurposed. ---

    def _evaluate_raw_strike(self, raw_book: float, raw_tape: float, side_to_check: PositionSide) -> Tuple[Optional[str], Optional[PositionSide]]:
        """
        Evaluates the RAW force against thresholds to classify its strength.
        This is the preserved soul of the Enlightened Warrior's sense of scale.
        """
        assault_thresh = self.protocol.get('full_assault_thresholds', {})
        risk, side = self._check_signal_strength(raw_book, raw_tape, 'FULL', assault_thresh, side_to_check)
        if side: return risk, side

        probe_thresh = self.protocol.get('probing_attack_thresholds', {})
        risk, side = self._check_signal_strength(raw_book, raw_tape, 'HALF', probe_thresh, side_to_check)
        if side: return risk, side
        
        scout_thresh = self.protocol.get('scout_mission_thresholds', {})
        risk, side = self._check_signal_strength(raw_book, raw_tape, 'SCOUT', scout_thresh, side_to_check)
        if side: return risk, side
        
        return None, None

    def _check_signal_strength(self, book_force: float, tape_pressure: float, risk_level: str, thresholds: Dict, side_to_check: PositionSide) -> Tuple[Optional[str], Optional[PositionSide]]:
        """
        This core helper method is 100% PRESERVED. It now serves the classification purpose.
        """
        min_book = thresholds.get('min_book_force', 999)
        min_tape = thresholds.get('min_tape_pressure', 999)
        
        if side_to_check == PositionSide.LONG:
            if book_force > min_book and tape_pressure > min_tape:
                return risk_level, PositionSide.LONG
        
        elif side_to_check == PositionSide.SHORT:
            if book_force < -min_book and tape_pressure < -min_tape:
                return risk_level, PositionSide.SHORT

        return None, None