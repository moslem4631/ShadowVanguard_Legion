# F:\ShadowVanguard_Legion\memory\experience_memory.py
# Version 4.4 - Prometheus: Unified with the central data constitution.

import logging
from typing import Dict, Any, List, Optional
from collections import deque
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import NotFittedError

# AI-UPGRADE: وارد کردن مدل‌ها از یک منبع واحد و مرکزی
from core.data_models import TacticalSignal, PositionV2 as Position, PowerReport, EmotionReport, Experience
from core.market_enums import TacticalDecision, MarketRegime

logger = logging.getLogger("ExperienceMemory")

# AI-FIX: تعریف تکراری Experience حذف شد. اکنون از نسخه مرکزی استفاده می‌شود.

class ExperienceMemory:
    """
    The Legion's archives. It stores battle experiences, learns from them,
    and provides wisdom from past encounters. Now fully aligned with the core constitution.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_size = self.config.get('max_size', 2000)
        self.scaler_refit_interval = self.config.get('refit_interval', 100)
        
        self.memory = deque(maxlen=self.max_size)
        self.scaler = StandardScaler()
        self.operations_since_refit = 0
        
        logger.info(f"[ExperienceMemory] Unified Archives v4.4 ready. Capacity: {self.max_size}.")

    def remember(self, experience: Experience):
        self.memory.append(experience)
        self.operations_since_refit += 1
        if self.operations_since_refit >= self.scaler_refit_interval:
            self.refit_scaler()
    
    def prime_with_history(self, history_df: pd.DataFrame, structure_analyzer, power_scanner):
        """
        Primes the memory with simplified experiences from historical data.
        """
        logger.info(f"Priming memory with {len(history_df)} historical records...")
        if history_df.empty: return
        
        for i in range(1, len(history_df)):
            outcome = (history_df['close'].iloc[i] / history_df['close'].iloc[i-1]) - 1
            
            # This is a very simplified state for priming purposes.
            simple_state = {
                'power_report': PowerReport(net_force=(history_df['volume'].iloc[i] * np.sign(outcome))),
                'emotion_report': EmotionReport(),
                'market_regime': MarketRegime.UNCERTAIN
            }
            exp = Experience(state=simple_state, action=TacticalDecision.HOLD, outcome=outcome)
            self.memory.append(exp)
        
        logger.info("Memory priming complete. Initial scaler fitting...")
        self.refit_scaler()

    def refit_scaler(self):
        """Trains the feature scaler on all current experiences in memory."""
        if len(self.memory) < 20: 
            logger.debug("Not enough experiences to refit the scaler yet.")
            return

        try:
            all_vectors = [vec for exp in self.memory if (vec := self._state_to_vector(exp.state)) is not None]
            if all_vectors:
                self.scaler.fit(all_vectors)
                self.operations_since_refit = 0
                logger.info(f"Adaptive feature scaler has been successfully refitted on {len(all_vectors)} experiences.")
        except Exception as e:
            logger.error(f"Failed to refit scaler: {e}", exc_info=True)
            
    def find_similar_pattern(self, current_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Finds the most successful similar past experience."""
        try:
            current_vector = self._get_scaled_vector(current_state)
            if current_vector is None: return None
        except (NotFittedError, ValueError):
             logger.warning("Memory scaler not ready or invalid data. Historical analysis skipped.")
             return None

        best_match_info = None
        best_similarity_score = -float('inf') 

        for exp in self.memory:
            if exp.action == TacticalDecision.WAIT or not exp.state: continue
            
            exp_vector = self._get_scaled_vector(exp.state)
            if exp_vector is None: continue
                
            similarity = self._calculate_cosine_similarity(current_vector, exp_vector)
            
            weighted_score = similarity * (1 + exp.outcome)
            
            if weighted_score > best_similarity_score:
                best_similarity_score = weighted_score
                best_match_info = {
                    "decision": exp.action,
                    "confidence": round(min(1.0, similarity), 2),
                    "reason": f"Historical match (sim: {similarity:.2f}, outcome: {exp.outcome:.2%})"
                }
        
        min_similarity_threshold = self.config.get('min_similarity_threshold', 0.7)
        if best_match_info and best_match_info['confidence'] > min_similarity_threshold:
            logger.info(f"Memory Recall: Suggesting '{best_match_info['decision'].name}' with confidence {best_match_info['confidence']:.2f}")
            return best_match_info
        
        return None

    def _state_to_vector(self, state: Dict[str, Any]) -> Optional[np.ndarray]:
        try:
            power = state.get('power_report') or PowerReport()
            emotion = state.get('emotion_report') or EmotionReport()
            regime = state.get('market_regime') or MarketRegime.UNCERTAIN
            
            all_regimes = list(MarketRegime)
            regime_vector = [1.0 if regime == r else 0.0 for r in all_regimes]

            feature_vector = [
                power.net_force, power.confidence, power.price_velocity,
                emotion.aggression, emotion.caution, emotion.fear, emotion.greed, emotion.doubt,
                emotion.hysteria, emotion.exhaustion
            ] + regime_vector
            
            return np.array(feature_vector, dtype=float)
        except Exception as e:
            logger.warning(f"Could not convert state to vector: {e}")
            return None

    def _get_scaled_vector(self, state: Dict[str, Any]) -> Optional[np.ndarray]:
        vector = self._state_to_vector(state)
        if vector is None: return None
        return self.scaler.transform(vector.reshape(1, -1))[0]

    def _calculate_cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        if vec_a is None or vec_b is None: return 0.0
        norm_a = np.linalg.norm(vec_a); norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0: return 0.0
        return max(0.0, float(np.dot(vec_a, vec_b) / (norm_a * norm_b)))