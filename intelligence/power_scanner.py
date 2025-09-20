# F:\ShadowVanguard_Legion_Godspeed\intelligence\power_scanner.py
# Version 9.1 - Prometheus, The Adrenaline Protocol

import logging
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np

from core.data_models import MarketDataFrame, PowerReport

logger = logging.getLogger("PowerScanner")

class PowerScanner:
    """
    THE ORACLE OF TRUTH (v9.1 - Adrenaline Protocol): This version introduces a
    critical dual-mode capability. While retaining its high-fidelity synthesis engine for
    backtesting (using simulated order book data), it now includes a tactical
    "Adrenaline Protocol". When deployed in a live/paper environment without a direct
    WebSocket feed, this protocol ESTIMATES the net force based on OHLCV momentum—candle
    body size and volume analysis—injecting a realistic, actionable power reading to
    break the tactical deadlock and allow for live machinery testing.
    """
    def __init__(self, config: Dict[str, Any] = None):
        # [PACT KEPT]: The original constructor logic is PRESERVED.
        config = config or {}
        self.ps_config = config.get('power_scanner', {})
        self.depth = self.ps_config.get('order_book_depth', 50)
        self.tactical_tf = self.ps_config.get('tactical_timeframe', '5m')
        self.book_weight_decay = self.ps_config.get('book_weight_decay', 0.85)
        self.absorption_volume_threshold = self.ps_config.get('absorption_volume_threshold', 10.0)
        self.tape_confirmation_multiplier = self.ps_config.get('tape_confirmation_multiplier', 1.5)
        self.absorption_veto_strength = self.ps_config.get('absorption_veto_strength', 2.0)

        self.last_book_net_force: float = 0.0
        self.volatility_window = 14
        self.last_order_book_snapshot: Optional[Dict[str, Any]] = None
        
        # New parameters for Adrenaline Protocol
        self.adr_config = self.ps_config.get('adrenaline_protocol', {})
        self.adr_volume_ma_period = self.adr_config.get('volume_ma_period', 20)
        self.adr_atr_period = self.adr_config.get('atr_period', 14)
        self.adr_force_multiplier = self.adr_config.get('force_multiplier', 100)

        logger.info(f"[PowerScanner] The Oracle of Truth v9.1 (Adrenaline Protocol) is online.")

    def scan(self, mdf: MarketDataFrame) -> PowerReport:
        # [SURGICAL UPGRADE]: A mode-switch is installed at the heart of the Oracle.
        tactical_ohlcv = mdf.ohlcv_multidim.get(self.tactical_tf)

        try:
            if tactical_ohlcv is None or tactical_ohlcv.empty:
                logger.warning(f"PowerScanner: Tactical timeframe '{self.tactical_tf}' not found. Aborting.")
                return PowerReport()
            
            # --- MODE SWITCH ---
            is_live_simulation = not mdf.order_book_snapshot and not mdf.tape_snapshot
            
            if is_live_simulation:
                # --- Adrenaline Protocol Activated (Live/Paper Mode) ---
                logger.debug("Live mode detected. Engaging Adrenaline Protocol (OHLCV-based force estimation).")
                return self._estimate_force_from_ohlcv(tactical_ohlcv)
            else:
                # --- High-Fidelity Synthesis Activated (Backtest Mode) ---
                book_support, book_resistance, book_imbalance = self._analyze_book_potential(mdf)
                tape_buying, tape_selling = self._analyze_tape_action(mdf)
                absorption_signal = self._detect_absorption(mdf, tape_buying, tape_selling)
                true_net_force = self._synthesize_true_net_force(book_imbalance, tape_buying - tape_selling, absorption_signal)
                log_message = (
                    f"TruthSight Scan (Backtest Mode): TrueNetForce={true_net_force:,.2f} "
                    f"(Book Imbalance:{book_imbalance:.2f} | Tape Pressure:{tape_buying-tape_selling:,.2f} | "
                    f"Absorption: {absorption_signal})"
                )
            
            net_force_acceleration = true_net_force - self.last_book_net_force
            self.last_book_net_force = true_net_force
            price_velocity = self._calculate_price_velocity(tactical_ohlcv)
            
            logger.info(log_message)

            report = PowerReport(
                true_net_force=round(true_net_force, 2),
                net_force_acceleration=round(net_force_acceleration, 2),
                book_imbalance=round(book_imbalance, 2),
                delta_joiners=round(tape_buying - tape_selling, 2),
                price_velocity=round(price_velocity, 6),
                absorption_signal=absorption_signal
            )
            self.last_order_book_snapshot = mdf.order_book_snapshot
            return report

        except Exception as e:
            logger.error(f"[PowerScanner] Critical error in scan: {e}", exc_info=True)
            return PowerReport()

    def _estimate_force_from_ohlcv(self, df_ohlcv: pd.DataFrame) -> PowerReport:
        """
        [ADRENALINE INJECTION]: Estimates TrueNetForce based on candle momentum and volume.
        This provides an actionable, albeit less precise, power reading for live testing.
        """
        if len(df_ohlcv) < self.adr_volume_ma_period + 1: return PowerReport()
        
        df = df_ohlcv.copy()
        last_candle = df.iloc[-1]
        
        # Calculate ATR for volatility context
        tr = pd.DataFrame(index=df.index)
        tr['h-l'] = df['high'] - df['low']; tr['h-pc'] = abs(df['high'] - df['close'].shift(1)); tr['l-pc'] = abs(df['low'] - df['close'].shift(1))
        atr = tr[['h-l', 'h-pc', 'l-pc']].max(axis=1).ewm(span=self.adr_atr_period, adjust=False).mean()
        last_atr = atr.iloc[-1]
        
        # Calculate Volume MA for context
        volume_ma = df['volume'].rolling(window=self.adr_volume_ma_period).mean()
        last_volume_ma = volume_ma.iloc[-1]

        # Calculate force components
        body_size = last_candle['close'] - last_candle['open']
        
        # Normalized Body Size (how strong was the move compared to recent volatility?)
        norm_body = (body_size / last_atr) if last_atr > 0 else 0
        
        # Normalized Volume (how strong was the conviction compared to recent activity?)
        norm_volume = (last_candle['volume'] / last_volume_ma) if last_volume_ma > 0 else 1
        
        # Combine factors to create a force score
        estimated_force = norm_body * norm_volume * self.adr_force_multiplier
        
        # Clean up extreme values
        estimated_force = np.clip(estimated_force, -100, 100)

        price_velocity = self._calculate_price_velocity(df)
        
        logger.info(
            f"TruthSight Scan (Adrenaline Protocol): TrueNetForce={estimated_force:,.2f} "
            f"(NormBody:{norm_body:.2f}, NormVol:{norm_volume:.2f})"
        )

        return PowerReport(
            true_net_force=round(estimated_force, 2),
            price_velocity=round(price_velocity, 6),
            # Other fields are irrelevant in this mode
            net_force_acceleration=0.0, book_imbalance=0.0,
            delta_joiners=0.0, absorption_signal="NONE"
        )
    
    # [PACT KEPT]: All original high-fidelity analysis methods are PRESERVED below for backtesting.
    def _synthesize_true_net_force(self, book_imbalance: float, tape_pressure: float, absorption: str) -> float:
        base_force = book_imbalance * 100
        if (base_force > 0 and tape_pressure > 0) or (base_force < 0 and tape_pressure < 0):
            base_force *= self.tape_confirmation_multiplier
        elif (base_force > 0 and tape_pressure < 0) or (base_force < 0 and tape_pressure > 0):
             base_force /= self.tape_confirmation_multiplier
        if absorption == "BULLISH":
            base_force = max(base_force, 0) + self.absorption_veto_strength * 100
        elif absorption == "BEARISH":
            base_force = min(base_force, 0) - self.absorption_veto_strength * 100
        return base_force

    def _calculate_weighted_volume(self, orders: List[Tuple[float, float]]) -> float:
        weighted_volume = 0.0
        for i, (price, size) in enumerate(orders[:self.depth]):
            weight = self.book_weight_decay ** i
            weighted_volume += size * weight
        return weighted_volume

    def _analyze_book_potential(self, mdf: MarketDataFrame) -> Tuple[float, float, float]:
        order_book = mdf.order_book_snapshot or {}; book_bids = order_book.get("bids",[]); book_asks=order_book.get("asks",[])
        if not book_bids or not book_asks: return 0.0, 0.0, 0.0
        weighted_bid_volume = self._calculate_weighted_volume(book_bids)
        weighted_ask_volume = self._calculate_weighted_volume(book_asks)
        total_volume = weighted_bid_volume + weighted_ask_volume
        imbalance = 0.0
        if total_volume > 1e-9: imbalance = (weighted_bid_volume - weighted_ask_volume) / total_volume
        return weighted_bid_volume, weighted_ask_volume, imbalance

    def _analyze_tape_action(self, mdf: MarketDataFrame) -> Tuple[float, float]:
        tape = mdf.tape_snapshot or [];
        if not tape: return 0.0, 0.0
        buy_volume=sum(t.get('size', 0) for t in tape if t.get('side')=='buy')
        sell_volume=sum(t.get('size', 0) for t in tape if t.get('side')=='sell')
        return buy_volume, sell_volume

    def _detect_absorption(self, mdf: MarketDataFrame, tape_buying: float, tape_selling: float) -> str:
        current_book=mdf.order_book_snapshot
        if not self.last_order_book_snapshot or not current_book or not current_book.get("bids") or not current_book.get("asks"): return "NONE"
        last_top_bid=self.last_order_book_snapshot.get("bids",[[0]])[0][0]; last_top_ask=self.last_order_book_snapshot.get("asks",[[0]])[0][0]
        current_top_bid=current_book["bids"][0][0]; current_top_ask=current_book["asks"][0][0]
        if tape_selling >= self.absorption_volume_threshold and current_top_bid >= last_top_bid:
            logger.warning("COUNTER-INTEL: Bullish Absorption detected! Heavy selling pressure is being absorbed.")
            return "BULLISH"
        if tape_buying >= self.absorption_volume_threshold and current_top_ask <= last_top_ask:
            logger.warning("COUNTER-INTEL: Bearish Absorption detected! Heavy buying pressure is being absorbed.")
            return "BEARISH"
        return "NONE"
    
    def _calculate_price_velocity(self, ohlcv: pd.DataFrame) -> float:
        if len(ohlcv)<self.volatility_window+1: return 0.0
        try:
            df = ohlcv.copy(); high,low,close=df['high'],df['low'],df['close']; df['tr1']=abs(high-low); df['tr2']=abs(high-close.shift(1)); df['tr3']=abs(low-close.shift(1))
            tr=df[['tr1','tr2','tr3']].max(axis=1); atr=tr.ewm(alpha=1/self.volatility_window, adjust=False).mean()
            last_atr=atr.iloc[-1]; current_price=ohlcv['close'].iloc[-1]
            return (last_atr/current_price) if current_price>0 else 0.0
        except Exception: return 0.0