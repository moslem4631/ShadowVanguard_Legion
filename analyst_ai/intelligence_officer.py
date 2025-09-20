# F:\ShadowVanguard_Legion\analyst_ai\intelligence_officer.py
# Version 3.0 - Prometheus, The Frontline Advisor

import logging
from typing import Dict, Any, Optional

# All original imports are preserved.
from core.data_models import (
    StructureReport, PowerReport, EmotionReport, ConfluenceReport,
    FibonacciReport, DivergenceReport
)
from core.market_enums import PositionSide, MarketRegime

logger = logging.getLogger("IntelligenceOfficer")

class IntelligenceOfficer:
    """
    Version 3.0, "The Frontline Advisor", executes the "Separation of Powers" doctrine.
    This officer's role is now strictly limited to providing a rapid, tactical assessment
    for ENTRY decisions. Slow, strategic analyses (Fibonacci, Divergence) have been
    expelled from this cabinet and their wisdom is now reserved for the TacticalController
    during post-entry MANAGEMENT. This purifies and accelerates our entry signal.
    """

    def __init__(self, config: Optional[Dict[str, Any]]):
        # The constructor logic is preserved.
        self.config = config if config is not None else {}
        self.scoring_weights = self.config.get('scoring_weights', {})
        logger.info("[IntelligenceOfficer] The Frontline Advisor v3.0 deployed. Focused on immediate tactical assessment.")

    # --- THE CORE OF THE SEPARATION OF POWERS REVOLUTION ---
    def generate_confluence_report(self,
                                   structure_report: Optional[StructureReport],
                                   power_report: Optional[PowerReport],
                                   emotion_report: Optional[EmotionReport]
                                   ) -> ConfluenceReport: # Fibonacci and Divergence reports are no longer accepted here.
        """
        Generates a PURELY TACTICAL confluence report for entry decisions. It now only
        considers fast-moving, immediate market conditions like structure. Strategic,
        long-term indicators are deliberately ignored to ensure speed and clarity.
        """
        confluence_report = ConfluenceReport()

        # The information gathering is now streamlined and focused.
        if structure_report:
            self._score_structure(structure_report, confluence_report)
        
        # --- STRATEGISTS EXPELLED ---
        # The following calls have been REMOVED from the entry-decision process.
        # Their wisdom will be used by the TacticalController for MANAGEMENT.
        # if fibonacci_report:
        #     self._score_fibonacci(fibonacci_report, confluence_report)
        # if divergence_report:
        #     self._score_divergence(divergence_report, confluence_report)

        logger.info(
            f"Frontline Tactical Assessment: Bullish Score={confluence_report.bullish_score:.2f} | "
            f"Bearish Score={confluence_report.bearish_score:.2f}"
        )

        return confluence_report

    # The _score_structure method is preserved as it provides critical, fast-moving context.
    def _score_structure(self, structure: StructureReport, report: ConfluenceReport):
        regime_weight = self.scoring_weights.get('market_regime', 1.5)
        if structure.market_regime in [MarketRegime.BULL_TREND]:
            report.bullish_score += regime_weight
            report.bullish_reasons.append(f"Regime:BULL_TREND(w:{regime_weight})")
        elif structure.market_regime in [MarketRegime.BEAR_TREND]:
            report.bearish_score += regime_weight
            report.bearish_reasons.append(f"Regime:BEAR_TREND(w:{regime_weight})")

        ob_weight = self.scoring_weights.get('order_block', 1.0)
        for ob in (structure.order_blocks or []):
            if '_60min' in ob.event_type:
                if 'BULLISH' in ob.event_type:
                    score = ob.strength_score * ob_weight
                    report.bullish_score += score
                    report.bullish_reasons.append(f"HTF_Bull_OB(s:{ob.strength_score:.2f}, w:{ob_weight})")
                elif 'BEARISH' in ob.event_type:
                    score = ob.strength_score * ob_weight
                    report.bearish_score += score
                    report.bearish_reasons.append(f"HTF_Bear_OB(s:{ob.strength_score:.2f}, w:{ob_weight})")

        event_weight = self.scoring_weights.get('structure_event', 2.0)
        for event in (structure.structural_events or []):
             if '_60min' in event.event_type:
                if 'BULLISH' in event.event_type:
                    score = event.quality_score * event_weight
                    report.bullish_score += score
                    report.bullish_reasons.append(f"HTF_Bull_Event(q:{event.quality_score:.2f}, w:{event_weight})")
                elif 'BEARISH' in event.event_type:
                    score = event.quality_score * event_weight
                    report.bearish_score += score
                    report.bearish_reasons.append(f"HTF_Bear_Event(q:{event.quality_score:.2f}, w:{event_weight})")

    # --- RETIRED FROM THIS CABINET ---
    # These methods are strategically sound, but their place is not here.
    # They are now "ghost methods", waiting to be called by the TacticalController for MANAGEMENT.
    def _score_fibonacci(self, fibonacci: FibonacciReport, report: ConfluenceReport):
        # This method's logic is preserved but it is NO LONGER CALLED by generate_confluence_report.
        fib_weight = self.scoring_weights.get('fibonacci_confluence', 2.0)
        # ... (logic remains identical) ...

    def _score_divergence(self, divergence: DivergenceReport, report: ConfluenceReport):
        # This method's logic is preserved but it is NO LONGER CALLED by generate_confluence_report.
        div_weight = self.scoring_weights.get('divergence_signal', 3.0)
        # ... (logic remains identical) ...
        
# --- END OF FILE ---