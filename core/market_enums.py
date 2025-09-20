# F:\ShadowVanguard_Legion_Godspeed\core\market_enums.py
# Version 1.4 - The Unified Lexicon

from enum import Enum

class MarketPersonality(Enum):
    """
    A high-level strategic assessment of the market's character, determining which
    primary entry strategy (Momentum or Reversal) is appropriate.
    """
    UNDEFINED = "UNDEFINED"
    MOMENTUM_DRIVEN = "MOMENTUM_DRIVEN"
    MEAN_REVERTING = "MEAN_REVERTING"

class MarketRegime(Enum):
    """
    A more granular, tactical description of the current market state, derived from
    the new context-aware StructureAnalyzer.
    """
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    BULL_TREND_PULLBACK = "BULL_TREND_PULLBACK"
    BEAR_TREND_PULLBACK = "BEAR_TREND_PULLBACK"
    TIGHT_RANGE = "TIGHT_RANGE"
    UNCERTAIN = "UNCERTAIN"

class SignalSource(Enum):
    """منبع تولید سیگنال اولیه."""
    STRUCTURE_ANALYSIS = "STRUCTURE_ANALYSIS"
    PATTERN_RECOGNITION = "PATTERN_RECOGNITION"
    POWER_SURGE = "POWER_SURGE"
    DECEPTION_DETECTED = "DECEPTION_DETECTED"
    EMOTIONAL_EXTREME = "EMOTIONAL_EXTREME"

class TacticalDecision(Enum):
    """
    The lexicon of command. This is the complete and final set of actions the
    Supreme Commander can order.
    """
    ADVANCE = "ADVANCE"
    SCALE_IN = "SCALE_IN"
    HOLD = "HOLD"
    PARTIAL_EXIT = "PARTIAL_EXIT"
    ADJUST_STOP = "ADJUST_STOP"
    RETREAT = "RETREAT"
    FLIP_POSITION = "FLIP_POSITION"
    WAIT = "WAIT"

class OrderType(Enum):
    """انواع سفارشات قابل ارسال به صرافی."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"

# [CONSTITUTIONAL AMENDMENT]: The concept of "Neutrality" is now officially
# recognized within the Legion's core doctrine. This amendment resolves the
# philosophical conflict between the All-Seeing Historian's new wisdom and the
# old, binary laws of engagement.
class PositionSide(Enum):
    """جهت پوزیشن معاملاتی یا بایاس کلی بازار."""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL" # <-- THE MISSING CONCEPT, NOW SANCTIFIED

class MicroPattern(Enum):
    """الگوهای کندلی خرد برای تحلیل‌های ثانویه و تأییدی."""
    DOJI = "DOJI"
    HAMMER = "HAMMER"
    ENGULFING_BULLISH = "ENGULFING_BULLISH"
    ENGULFING_BEARISH = "ENGULFING_BEARISH"

# --- END OF FILE ---