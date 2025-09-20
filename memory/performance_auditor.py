# F:\ShadowVanguard_Legion_Godspeed\memory\performance_auditor.py
# Version 1.0 - Prometheus, The Grand Inquisitor

import logging
from collections import deque
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Legion Unit Imports
from core.data_models import PositionV2, TacticalSignal
from core.market_enums import MarketPersonality

logger = logging.getLogger("PerformanceAuditor")

# A simple dataclass to store the essence of a trade's outcome.
@dataclass(slots=True)
class TradeRecord:
    pnl_percentage: float
    personality_at_entry: MarketPersonality
    timestamp: datetime

# Enum to define the states of strategic alert.
class StrategicAlertLevel:
    NOMINAL = "NOMINAL"           # All systems are performing as expected.
    UNDERPERFORMANCE = "UNDERPERFORMANCE" # A strategy is failing, override is active.
    COOLDOWN = "COOLDOWN"             # Override period is over, returning to normal but monitoring closely.

class PerformanceAuditor:
    """
    This is "The Grand Inquisitor" of the legion, the ultimate layer of our
    Zero Trust architecture. It is a dispassionate, emotionless entity that
    judges strategies not by their theory, but by their RESULTS.

    - It maintains a short-term memory of recent trade outcomes.
    - It ruthlessly diagnoses patterns of consistent failure for a given strategy.
    - If a failure pattern is confirmed, it issues a "Strategic Override" alert,
      forcing the TacticalController to abandon the failing strategy, even if it
      appears theoretically sound, and switch to a defensive/counter-strategy.

    This makes our legion truly self-correcting and anti-fragile, capable of
    surviving not just market randomness, but its own strategic flaws.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the Auditor with its own strict protocols from the config.
        """
        self.protocol = config.get('performance_auditor_protocol', {})
        
        # How many recent trades to remember for the audit.
        memory_size = self.protocol.get('memory_size', 5)
        self.trade_history: deque[TradeRecord] = deque(maxlen=memory_size)

        # How many consecutive failures trigger an alert.
        self.failure_threshold_count = self.protocol.get('failure_threshold_count', 3)
        
        # How long an override remains in effect.
        cooldown_seconds = self.protocol.get('cooldown_period_seconds', 3600) # Default: 1 hour
        self.cooldown_delta = timedelta(seconds=cooldown_seconds)

        # The current state of the army.
        self.current_alert_level = StrategicAlertLevel.NOMINAL
        self.failing_personality: Optional[MarketPersonality] = None
        self.override_end_time: Optional[datetime] = None

        logger.info(
            f"[PerformanceAuditor] The Grand Inquisitor v1.0 has convened. "
            f"Watching last {memory_size} trades. Failure threshold: {self.failure_threshold_count}."
        )

    def record_closed_position(self, position: PositionV2):
        """
        The entry point for new evidence. The Auditor receives the closed position,
        extracts the necessary data, and adds it to its memory for judgment.
        """
        if not position.strategic_intent: # strategic_intent holds the regime, which maps to personality
            logger.warning("Auditor cannot record position with no strategic intent.")
            return

        # Translate the entry regime to the entry personality.
        # This is a simplification; a more robust mapping might be needed.
        entry_personality = MarketPersonality.MOMENTUM_DRIVEN
        if position.strategic_intent.name in ['TIGHT_RANGE', 'VOLATILE_RANGE']:
            entry_personality = MarketPersonality.MEAN_REVERTING

        record = TradeRecord(
            pnl_percentage=position.pnl_percentage,
            personality_at_entry=entry_personality,
            timestamp=position.exit_timestamp or datetime.utcnow()
        )
        self.trade_history.append(record)
        logger.info(f"Auditor has recorded new evidence: Trade PnL {record.pnl_percentage:+.2f}% under '{entry_personality.name}' personality.")
        
        # After recording new evidence, immediately re-evaluate the strategic situation.
        self._audit_performance()

    def _audit_performance(self):
        """
        The judgment process. The Auditor reviews the recent history to
        identify patterns of catastrophic failure.
        """
        # If we don't have enough data to meet the threshold, do nothing.
        if len(self.trade_history) < self.failure_threshold_count:
            return

        # Check for MOMENTUM strategy failure
        momentum_trades = [t for t in self.trade_history if t.personality_at_entry == MarketPersonality.MOMENTUM_DRIVEN]
        if len(momentum_trades) >= self.failure_threshold_count:
            # Check if the *last N* momentum trades were all failures.
            recent_momentum_failures = [t for t in momentum_trades[-self.failure_threshold_count:] if t.pnl_percentage < 0]
            if len(recent_momentum_failures) == self.failure_threshold_count:
                logger.critical(
                    f"!!! GRAND INQUISITOR VERDICT !!! Catastrophic failure pattern detected for "
                    f"'{MarketPersonality.MOMENTUM_DRIVEN.name}' strategy. Issuing Strategic Override."
                )
                self.current_alert_level = StrategicAlertLevel.UNDERPERFORMANCE
                self.failing_personality = MarketPersonality.MOMENTUM_DRIVEN
                self.override_end_time = datetime.utcnow() + self.cooldown_delta
                return

        # Check for MEAN_REVERTING strategy failure (can be added later)
        # ...

        # If no failure patterns are found, we can potentially lift an existing override.
        self._check_cooldown()


    def get_strategic_alert_status(self) -> Dict[str, Any]:
        """
        The public-facing method for the High Command to query the Auditor's
        current verdict on the state of the war.
        """
        # First, check if a cooldown period has expired.
        self._check_cooldown()

        return {
            "level": self.current_alert_level,
            "failing_personality": self.failing_personality
        }
        
    def _check_cooldown(self):
        """
        Checks if an active override's cooldown period has expired.
        """
        if self.current_alert_level == StrategicAlertLevel.UNDERPERFORMANCE and self.override_end_time:
            if datetime.utcnow() > self.override_end_time:
                logger.warning(
                    f"Cooldown for '{self.failing_personality.name}' override has expired. "
                    f"Returning to NOMINAL strategic state."
                )
                self.current_alert_level = StrategicAlertLevel.NOMINAL
                self.failing_personality = None
                self.override_end_time = None
                # Clear history after a cooldown to start fresh
                self.trade_history.clear()

# --- END OF FILE ---