# F:\ShadowVanguard_Legion\strategies\liquidity_hunter.py
# Version 1.0 - The Legion's Elite Liquidity Hunting Unit

import logging
from typing import Dict, Any, List, Optional

from core.data_models import MarketDataFrame, TacticalSignal
from core.market_enums import TacticalDecision, PositionSide
from analyst_ai.pattern_detector import PatternDetector
from intelligence.power_scanner import PowerScanner
from intelligence.intent_recognizer import IntentRecognizer

logger = logging.getLogger("LiquidityHunter")

class LiquidityHunterStrategy:
    """
    پیاده‌سازی استراتژی تهاجمی "شکارچی نقدینگی".
    این استراتژی به دنبال ورود به معامله در نقاطی است که انتظار می‌رود
    حجم بالایی از حد ضررها (Stop-Losses) فعال شوند.
    """
    def __init__(self,
                 pattern_detector: PatternDetector,
                 power_scanner: PowerScanner,
                 intent_recognizer: IntentRecognizer,
                 config: Dict[str, Any]):
        
        self.pattern_detector = pattern_detector
        self.power_scanner = power_scanner
        self.intent_recognizer = intent_recognizer
        self.config = config
        
        self.confidence_threshold = self.config.get('hunter_min_confidence', 0.7)
        self.power_threshold = self.config.get('hunter_power_threshold', 20.0)
        
        logger.info("[LiquidityHunter] ✅ استراتژی شکارچی نقدینگی آماده عملیات است.")

    def generate_signal(self, mdf: MarketDataFrame) -> Optional[TacticalSignal]:
        """
        بازار را برای یافتن فرصت‌های شکار نقدینگی تحلیل می‌کند.
        
        Args:
            mdf (MarketDataFrame): داده‌های کامل بازار.
            
        Returns:
            Optional[TacticalSignal]: در صورت یافتن فرصت، یک سیگنال تاکتیکی برمی‌گرداند.
        """
        # 1. شناسایی الگوها و نقاط کلیدی ساختاری
        patterns = self.pattern_detector.analyze(mdf)
        
        # 2. بررسی فرصت شکار در بالای سقف‌ها (برای پوزیشن Short)
        signal = self._hunt_above_highs(mdf, patterns)
        if signal:
            return signal
            
        # 3. بررسی فرصت شکار در پایین کف‌ها (برای پوزیشن Long)
        signal = self._hunt_below_lows(mdf, patterns)
        if signal:
            return signal
            
        return None

    def _hunt_above_highs(self, mdf: MarketDataFrame, patterns: Dict) -> Optional[TacticalSignal]:
        """به دنبال فرصت فروش (Short) پس از یک حرکت به بالای یک سقف مهم می‌گردد."""
        
        # به دنبال آخرین رویداد شکست ساختار صعودی (BOS Up) بگرد
        bos_events = [event for event in patterns.get('bos_choch', []) if event['type'] == 'BOS' and event['direction'] == 'UP']
        
        if not bos_events:
            return None
            
        last_bos = bos_events[-1]
        
        # تحلیل قدرت و نیت در لحظه شکار
        power_report = self.power_scanner.scan(mdf)
        
        # شرط کمین: اگر بلافاصله پس از شکست سقف، قدرت به شدت به نفع فروشندگان تغییر کرد، این یک تله است
        if power_report.net_force < -self.power_threshold:
            
            confidence = power_report.confidence
            
            # تایید نهایی با اطمینان بالا
            if confidence >= self.confidence_threshold:
                logger.warning(f"🔫 فرصت شکار نقدینگی (Short) شناسایی شد! قدرت فروشندگان: {power_report.net_force}")
                return TacticalSignal(
                    source="LIQUIDITY_HUNT",
                    confidence=confidence,
                    suggestion=TacticalDecision.AMBUSH, # دستور تاکتیکی برای کمین
                    details={"side": PositionSide.SHORT.name, "entry_price": last_bos['price']}
                )
        return None

    def _hunt_below_lows(self, mdf: MarketDataFrame, patterns: Dict) -> Optional[TacticalSignal]:
        """به دنبال فرصت خرید (Long) پس از یک حرکت به پایین یک کف مهم می‌گردد."""
        
        # به دنبال آخرین رویداد شکست ساختار نزولی (BOS Down) بگرد
        bos_events = [event for event in patterns.get('bos_choch', []) if event['type'] == 'BOS' and event['direction'] == 'DOWN']

        if not bos_events:
            return None
        
        last_bos = bos_events[-1]
        
        power_report = self.power_scanner.scan(mdf)

        # شرط کمین: اگر بلافاصله پس از شکست کف، قدرت به شدت به نفع خریداران تغییر کرد
        if power_report.net_force > self.power_threshold:
            
            confidence = power_report.confidence
            
            if confidence >= self.confidence_threshold:
                logger.warning(f"🔫 فرصت شکار نقدینگی (Long) شناسایی شد! قدرت خریداران: {power_report.net_force}")
                return TacticalSignal(
                    source="LIQUIDITY_HUNT",
                    confidence=confidence,
                    suggestion=TacticalDecision.AMBUSH,
                    details={"side": PositionSide.LONG.name, "entry_price": last_bos['price']}
                )
        return None

# --- END OF FILE ---