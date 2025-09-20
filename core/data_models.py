# F:\ShadowVanguard_Legion_Godspeed\core\data_models.py
# Version 7.4 - Prometheus, The Final Blueprint

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

# [PACT KEPT]: Enums are the unchanging law of the Legion.
from .market_enums import PositionSide, TacticalDecision, MarketRegime, MarketPersonality

# -----------------------------------------------------------------------------
# SECTION 1: Base Intelligence Reports
# -----------------------------------------------------------------------------
# [PACT KEPT]: These models are PRESERVED as they represent raw, non-timeframed intelligence.
@dataclass(slots=True)
class PowerReport:
     # [ORACLE OF TRUTH UPGRADE]: The old 'net_force' is now replaced by a single, synthesized judgment.
    true_net_force: float = 0.0 
    net_force_acceleration: float = 0.0
    book_imbalance: float = 0.0
    delta_joiners: float = 0.0
    price_velocity: float = 0.0
    absorption_signal: str = "NONE" # 'NONE', 'BULLISH', 'BEARISH'
    
@dataclass(slots=True)
class EmotionReport:
    dominant_mood: str = "NEUTRAL"; aggression: float = 0.5; caution: float = 0.5
    fear: float = 0.0; greed: float = 0.0; doubt: float = 0.0
    hysteria: float = 0.0; exhaustion: float = 0.0

# -----------------------------------------------------------------------------
# SECTION 2: Evolved "Complete Armory" Models with Multi-Timeframe Capability
# -----------------------------------------------------------------------------

# --- Order Block Intelligence ---
@dataclass(slots=True)
class OrderBlock:
    block_id: str
    event_type: str # BULLISH_OB, BEARISH_OB
    price_low: float
    price_high: float
    timeframe: str
    created_at_index: int
    status: str = 'unmitigated'

@dataclass(slots=True)
class OBInteractionSignal:
    signal_type: str; triggering_ob: OrderBlock; confidence_score: float
@dataclass(slots=True)
class OrderBlockReport:
    """ This report now stores intelligence organized by timeframe. """
    all_blocks: Dict[str, Dict[str, List[OrderBlock]]] = field(default_factory=dict) # {'5m': {'bullish': [], 'bearish': []}}
    interaction_signals: Dict[str, List[OBInteractionSignal]] = field(default_factory=dict)

# --- Fibonacci Intelligence ---
# [FINAL ENCYCLOPEDIA CORRECTION]: The `zone_id` field is added to the official FibonacciZone blueprint.
# This completes the synchronization with the Confluence Sniper (`fibonacci_helper.py`).
@dataclass(slots=True)
class FibonacciZone:
    zone_id: str
    price_range: Tuple[float, float]
    strength: float
    is_bullish: bool
    source_level: float
    reasons: List[str]

@dataclass(slots=True)
class FibonacciSignal:
    signal_type: str; triggering_zone: FibonacciZone; confidence_score: float

@dataclass(slots=True)
class FibonacciReport:
    """ This report now stores intelligence organized by timeframe. """
    active_zones: Dict[str, List[FibonacciZone]] = field(default_factory=dict)
    confirmation_signals: Dict[str, List[FibonacciSignal]] = field(default_factory=dict)

# --- Divergence Intelligence ---
@dataclass(slots=True)
class DivergencePattern:
    pattern_type: str; p1_idx: int; p2_idx: int; m1_idx: int; m2_idx: int
    confirmation_level: float
@dataclass(slots=True)
class DivergenceSignal:
    signal_type: str; triggering_pattern: DivergencePattern; confidence_score: float
@dataclass(slots=True)
class DivergenceReport:
    """ This report now stores intelligence organized by timeframe. """
    active_patterns: Dict[str, List[DivergencePattern]] = field(default_factory=dict)
    confirmation_signals: Dict[str, List[DivergenceSignal]] = field(default_factory=dict)

# --- Liquidity Intelligence ---
@dataclass(slots=True)
class FairValueGap:
    void_id: str
    event_type: str # BULLISH_FVG, BEARISH_FVG
    price_low: float
    price_high: float
    timeframe: str
    created_at_index: int
    status: str = 'unfilled'

@dataclass(slots=True)
class LiquidityVoid: # This is a legacy or generic term, FVG is more specific
    void_id: str; event_type: str; price_range: Tuple[float, float]; timeframe: str
    created_at_index: int; status: str = 'unfilled'

@dataclass(slots=True)
class LiquiditySignal:
    signal_type: str; triggering_void: FairValueGap; confidence_score: float

@dataclass(slots=True)
class LiquidityReport:
    """ This report now stores intelligence organized by timeframe. """
    unfilled_fvgs: Dict[str, Dict[str, List[FairValueGap]]] = field(default_factory=dict) # {'5m': {'bullish': [], 'bearish': []}}
    confirmation_signals: Dict[str, List[LiquiditySignal]] = field(default_factory=dict)


# --- Structural Event Base Model ---
@dataclass(slots=True)
class StructuralEvent:
    event_type: str
    price_level: float; timestamp: pd.Timestamp; confidence: float = 1.0

# -----------------------------------------------------------------------------
# SECTION 3: The Grand Strategic Battle Map (Structure Report)
# -----------------------------------------------------------------------------
@dataclass(slots=True)
class StructureReport:
    """
    The main battle map, now capable of holding distinct strategic assessments
    for each operational timeframe (e.g., 5m tactical, 4h strategic).
    """
    market_personality: MarketPersonality = MarketPersonality.UNDEFINED
    personality_certainty: float = 0.0
    
    primary_trend: Dict[str, PositionSide] = field(default_factory=dict) # e.g., {'5m': PositionSide.LONG}
    market_regime: Dict[str, MarketRegime] = field(default_factory=dict)
    structural_narrative: Dict[str, List[StructuralEvent]] = field(default_factory=dict)
    
    range_high: Optional[float] = None
    range_low: Optional[float] = None
    
# -----------------------------------------------------------------------------
# SECTION 4: Operational Packages & Soldier's Soul
# -----------------------------------------------------------------------------
# [PACT KEPT]: These operational models are PRESERVED as is.

@dataclass(slots=True)
class HedgeTrap:
    order_id: str; trigger_price: float; size: float
    side: PositionSide; status: str = "ACTIVE"
    
@dataclass(slots=True)
class TacticalSignal:
    source: str; confidence: float; suggestion: TacticalDecision
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class PositionV2:
    # This is the full, battle-hardened soul of our soldier.
    position_id: str; symbol: str; side: PositionSide
    entry_price: float; size: float
    leverage: int = 1; strategic_intent: Optional[MarketRegime] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    exit_timestamp: Optional[datetime] = None
    status: str = "OPEN"; pnl_percentage: float = 0.0
    pnl_in_dollars: Optional[float] = None; exit_price: Optional[float] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    is_untracked: bool = False
    management_stop_loss: Optional[float] = None
    catastrophic_stop_loss: Optional[float] = None
    take_profit_levels: List[Tuple[float, float]] = field(default_factory=list)
    tps_hit: int = 0
    hedge_trap: Optional['HedgeTrap'] = None
    flip_count: int = 0

@dataclass(slots=True)
class Experience:
    state: Dict[str, Any] = field(default_factory=dict)
    action: TacticalDecision = TacticalDecision.WAIT
    outcome: float = 0.0
    position_details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

# -----------------------------------------------------------------------------
# SECTION 5: The Unified Intelligence Packet (The Vessel)
# -----------------------------------------------------------------------------
@dataclass
class MarketDataFrame:
    timestamp: datetime
    symbol: str
    ohlcv_multidim: Dict[str, pd.DataFrame] = field(default_factory=dict)
    order_book_snapshot: Optional[Dict[str, Any]] = field(default_factory=dict)
    tape_snapshot: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    power_report: Optional[PowerReport] = None
    emotion_report: Optional[EmotionReport] = None
    structure_report: Optional[StructureReport] = None
    ob_report: Optional[OrderBlockReport] = None
    fib_report: Optional[FibonacciReport] = None
    div_report: Optional[DivergenceReport] = None
    liq_report: Optional[LiquidityReport] = None