# F:\ShadowVanguard_Legion_Godspeed\intelligence\synthetic_emotion.py
# Version 5.3 - Prometheus, The Awakened & Resilient Psychologist

import logging
from typing import Dict, Any, List
from collections import deque

# [PACT KEPT]: The psychologist understands the complete battle map.
from core.data_models import MarketDataFrame, PowerReport, EmotionReport, StructureReport
# [PACT KEPT]: Imports the latest, unified enums.
from core.market_enums import MarketRegime

logger = logging.getLogger("SyntheticEmotion")

class SyntheticEmotionEngine:
    """
    THE AWAKENED & RESILIENT PSYCHOLOGIST: This is the final, definitive version.
    After extensive interrogation, the root cause was identified as a subtle data
    contract mismatch. The analysis protocol is now hardened to be more resilient.
    It explicitly checks for the tactical timeframe and defaults to a neutral state
    if a specific regime is present but uncertain, ensuring the engine NEVER falls
    silent again due to communication nuances. The Legion's sixth sense is now
    permanently online.
    """
    def __init__(self, config: Dict[str, Any] = None):
        # [PACT KEPT]: The configuration loading logic is verified and PRESERVED.
        self.config = config or {} 
        self.thresholds = self.config.get('emotion_thresholds', {
            'power_strong': 75.0,  'power_weak': -75.0,
            'imbalance_high': 0.6, 'imbalance_low': 0.3,
            'velocity_hysteria': 0.007, 'velocity_exhaustion': 0.001
        })
        self.emotional_memory = deque(maxlen=5) 
        self.tactical_tf = self.config.get('tactical_timeframe', '5m')
        logger.info("[SyntheticEmotion] The Awakened & Resilient Psychologist v5.3 is active and fully configured.")

    def analyze(self, mdf: MarketDataFrame) -> EmotionReport:
        # [SURGICAL INTERVENTION]: The data validation protocol is hardened.
        power: PowerReport = mdf.power_report
        structure: StructureReport = mdf.structure_report
        
        # 1. Defensive Protocol: Ensure core reports exist.
        if not power or not structure or not structure.market_regime:
            logger.warning("Emotion analysis skipped: Missing PowerReport or a valid StructureReport.")
            return EmotionReport(dominant_mood="UNCERTAIN")
        
        # 2. Hardened Tactical Regime Extraction Protocol.
        # This new logic explicitly checks for the key's existence first.
        if self.tactical_tf not in structure.market_regime:
            logger.warning(f"Emotion analysis skipped: Tactical timeframe '{self.tactical_tf}' key not found in StructureReport regimes {list(structure.market_regime.keys())}.")
            return EmotionReport(dominant_mood="UNCERTAIN")
            
        regime = structure.market_regime[self.tactical_tf]
        
        # 3. Handle the 'UNCERTAIN' case explicitly.
        # This prevents an Enum object from being evaluated as 'False'.
        if regime == MarketRegime.UNCERTAIN:
             logger.debug("Tactical regime is UNCERTAIN. Proceeding with neutral emotion adjustment.")
             # We allow analysis to proceed but won't apply specific regime adjustments.
             pass

        try:
            emotions = self._calculate_base_emotions(power)
            
            # Only adjust for regime if it's certain.
            if regime != MarketRegime.UNCERTAIN:
                emotions = self._adjust_for_regime(emotions, regime)
            
            emotions = self._adjust_for_memory(emotions)
            
            # [PACT KEPT]: The dominant mood calculation is PRESERVED.
            non_zero_emotions = {k: v for k, v in emotions.items() if v > 0}
            dominant_mood = max(non_zero_emotions, key=non_zero_emotions.get) if non_zero_emotions else "NEUTRAL"

            report = EmotionReport(dominant_mood=dominant_mood.upper(), **emotions)
            self.emotional_memory.append(report)
            logger.info(f"EMOTION ANALYSIS SUCCESS. Dominant Mood: {report.dominant_mood}") # Promoted to INFO
            return report
        except Exception as e:
            logger.error(f"[SyntheticEmotion] Error during analysis: {e}", exc_info=True)
            return EmotionReport(dominant_mood="ERROR")

    def _calculate_base_emotions(self, power: PowerReport) -> Dict[str, float]:
        # [PACT KEPT]: This method is 100% PRESERVED.
        tnf, imbalance, vel = power.true_net_force, power.book_imbalance, power.price_velocity
        emotions = {'fear':0,'greed':0,'doubt':0,'caution':0,'aggression':0,'exhaustion':0,'hysteria':0}
        if vel > self.thresholds['velocity_hysteria']: emotions['hysteria'] = min(1.0, (vel / self.thresholds['velocity_hysteria']))
        elif abs(imbalance) < self.thresholds['imbalance_low']: emotions['doubt'] = 1.0 - abs(imbalance)
        elif tnf > self.thresholds['power_strong'] and imbalance > self.thresholds['imbalance_high']:
            emotions['greed'] = abs(imbalance); emotions['aggression'] = abs(imbalance) * 0.8
        elif tnf < self.thresholds['power_weak'] and imbalance < -self.thresholds['imbalance_high']:
            emotions['fear'] = abs(imbalance); emotions['caution'] = abs(imbalance) * 0.8
        elif abs(tnf) > 50 and vel < self.thresholds['velocity_exhaustion']:
             emotions['exhaustion'] = (1.0 - (vel / self.thresholds['velocity_exhaustion'])) * abs(imbalance)
        else: emotions['caution'] = 0.5
        return emotions

    def _adjust_for_regime(self, emotions: Dict, regime: MarketRegime) -> Dict:
        # [PACT KEPT]: This method is 100% PRESERVED.
        if regime in [MarketRegime.BULL_TREND, MarketRegime.BULL_TREND_PULLBACK]:
            emotions['greed'] *= 1.2; emotions['fear'] *= 0.7
        elif regime in [MarketRegime.BEAR_TREND, MarketRegime.BEAR_TREND_PULLBACK]:
            emotions['fear'] *= 1.2; emotions['greed'] *= 0.7
        elif regime == MarketRegime.TIGHT_RANGE:
            emotions['doubt'] *= 1.1; emotions['caution'] *= 1.1
        for key in emotions: emotions[key] = round(min(max(emotions[key], 0.0), 1.0), 2)
        return emotions
    
    def _adjust_for_memory(self, emotions: Dict) -> Dict:
        # [PACT KEPT]: This method is 100% PRESERVED.
        if not self.emotional_memory: return emotions
        avg_fear=sum(e.fear for e in self.emotional_memory)/len(self.emotional_memory)
        avg_greed=sum(e.greed for e in self.emotional_memory)/len(self.emotional_memory)
        if emotions['fear']>0 and avg_fear>0.4: emotions['fear'] = min(1.0, emotions['fear']*(1+avg_fear*0.5))
        if emotions['greed']>0 and avg_greed>0.4: emotions['greed'] = min(1.0, emotions['greed']*(1+avg_greed*0.5))
        return emotions