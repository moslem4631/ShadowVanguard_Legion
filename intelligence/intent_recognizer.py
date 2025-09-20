# F:\ShadowVanguard_Legion\intelligence\intent_recognizer.py
# Version 4.1 - Hardened against None-type responses from memory.

import logging
from typing import Dict, Any, Tuple, Optional

from core.data_models import PowerReport, EmotionReport
from core.market_enums import TacticalDecision
from memory.experience_memory import ExperienceMemory

logger = logging.getLogger("IntentRecognizer")

class IntentRecognizer:
    def __init__(self, memory: ExperienceMemory, config: Dict[str, Any]):
        self.memory = memory
        self.config = config or {}
        self.weights = self.config.get('intent_weights', {
            'BULL_ADVANCE': {'net_force': 0.5, 'confidence': 0.3, 'greed': 0.2},
            'BEAR_RETREAT': {'net_force': -0.5, 'confidence': 0.3, 'fear': 0.2},
            'LIQUIDITY_HUNT': {'doubt': 0.4, 'exhaustion': 0.4, 'confidence_inv': 0.2},
        })
        logger.info("[IntentRecognizer] Cognitive Fusion Engine v4.1 hardened and ready.")

    def recognize(self, power: PowerReport, emotion: EmotionReport) -> Dict[str, Any]:
        try:
            intent_scores = {
                "BULLISH_ADVANCE": self._score_bullish_advance(power, emotion),
                "BEARISH_RETREAT": self._score_bearish_retreat(power, emotion),
                "LIQUIDITY_HUNT": self._score_liquidity_hunt(power, emotion)
            }
            base_intention = max(intent_scores, key=intent_scores.get)
            base_confidence = intent_scores[base_intention]
            
            current_state = {'power_report': power, 'emotion_report': emotion}
            historical_match = self.memory.find_similar_pattern(current_state)
            
            return self._hybrid_decision(base_intention, base_confidence, historical_match)
        except Exception as e:
            logger.error(f"[IntentRecognizer] Error during intent recognition: {e}", exc_info=True)
            return self._create_report("ERROR", 0.0, "System error in recognition")

    def _score_bullish_advance(self, power: PowerReport, emotion: EmotionReport) -> float:
        w = self.weights.get('BULL_ADVANCE', {})
        score = (power.net_force / 50 * w.get('net_force', 0.5)) + \
                (power.confidence * w.get('confidence', 0.3)) + \
                (emotion.greed * w.get('greed', 0.2))
        return max(0, score)

    def _score_bearish_retreat(self, power: PowerReport, emotion: EmotionReport) -> float:
        w = self.weights.get('BEAR_RETREAT', {})
        score = (-power.net_force / 50 * w.get('net_force', -0.5)) + \
                (power.confidence * w.get('confidence', 0.3)) + \
                (emotion.fear * w.get('fear', 0.2))
        return max(0, score)

    def _score_liquidity_hunt(self, power: PowerReport, emotion: EmotionReport) -> float:
        w = self.weights.get('LIQUIDITY_HUNT', {})
        score = (emotion.doubt * w.get('doubt', 0.4)) + \
                (hasattr(emotion, 'exhaustion') and emotion.exhaustion * w.get('exhaustion', 0.4)) + \
                ((1 - power.confidence) * w.get('confidence_inv', 0.2))
        return max(0, score)

    def _hybrid_decision(self, base_intent: str, base_conf: float, hist_match: Optional[Dict]) -> Dict[str, Any]:
        memory_override_threshold = self.config.get('memory_override_confidence', 0.7)
        
        if hist_match and hist_match['confidence'] > memory_override_threshold:
            final_intent = hist_match['decision'].name
            final_conf = (hist_match['confidence'] * 0.7) + (base_conf * 0.3)
            reason = f"Memory Override: Historical pattern suggested '{final_intent}'."
        else:
            final_intent = base_intent
            final_conf = base_conf
            reason = f"Real-time Analysis: '{base_intent}' scored highest."
            
        return self._create_report(final_intent, final_conf, reason)

    def _create_report(self, intention: str, confidence: float, reason: str) -> Dict[str, Any]:
        final_confidence = round(min(max(confidence, 0.0), 1.0), 2)
        logger.info(f"Intent Finalized: {intention} (Confidence: {final_confidence:.2f})")
        return {"intention": intention, "confidence": final_confidence, "reason": reason}