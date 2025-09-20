# F:\ShadowVanguard_Legion\intelligence\battle_learner.py
# Version 2.1 - Prometheus Project: The Connected War College

import logging
from typing import Dict, Any, Tuple, List
from collections import defaultdict
import random

from core.market_enums import TacticalDecision
from .reward_designer import RewardDesigner

logger = logging.getLogger("BattleLearner")

class BattleLearner:
    """
    This module is the single source of truth for learning from battle experiences
    using Reinforcement Learning. It's now connected to the RewardDesigner.
    """
    def __init__(self, reward_designer: RewardDesigner, config: Dict[str, Any] = None):
        """
        Args:
            reward_designer (RewardDesigner): The unit responsible for calculating smart rewards.
            config (Dict): Configuration for RL parameters.
        """
        config = config or {}
        self.alpha = config.get('alpha', 0.1)  # Learning Rate
        self.gamma = config.get('gamma', 0.9)  # Discount Factor
        self.epsilon = config.get('epsilon', 0.1) # Exploration Rate
        
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.reward_designer = reward_designer

        # Actions are now dynamically sourced from the official legion doctrine
        self.available_actions = [decision.name for decision in TacticalDecision if decision.name not in ["HEDGE"]]
        
        logger.info(f"[BattleLearner] War College (RL) is ready and linked to Reward Designer. "
                    f"Params: a={self.alpha}, g={self.gamma}, e={self.epsilon}")

    def get_optimal_action(self, state: Tuple) -> str:
        """
        Selects the best action for a given state using the Epsilon-Greedy strategy.
        """
        if random.uniform(0, 1) < self.epsilon:
            action = random.choice(self.available_actions)
            logger.info(f"RL decided to EXPLORE: {action}")
            return action
        
        q_values = self.q_table.get(state)
        if not q_values:
            return random.choice(self.available_actions)

        optimal_action = max(q_values, key=q_values.get)
        logger.info(f"RL decided to EXPLOIT: {optimal_action} (Q-Value: {q_values[optimal_action]:.4f})")
        return optimal_action

    def learn_from_experience(self, state: Tuple, action: str, outcome: Dict[str, Any], next_state: Tuple):
        """
        Updates the Q-Table based on a new experience. This method implements the Bellman equation.
        It now uses the RewardDesigner to get a smart reward.
        """
        try:
            # 1. Calculate a smart reward instead of using a raw value
            reward = self.reward_designer.calculate_reward(outcome) 

            # 2. Get the current Q-value for the (state, action) pair
            current_q = self.q_table[state][action]
            
            # 3. Find the best possible Q-value for the next state
            next_max_q = max(self.q_table[next_state].values()) if self.q_table.get(next_state) else 0.0

            # 4. Q-Learning update equation
            new_q = current_q + self.alpha * (reward + self.gamma * next_max_q - current_q)

            self.q_table[state][action] = new_q
            logger.info(f"Learning complete for state {state}, action {action}. Q-Value updated from {current_q:.4f} to {new_q:.4f} with reward {reward:.4f}")

        except Exception as e:
            logger.error(f"[BattleLearner] Error during learning process: {e}", exc_info=True)

    def get_q_table_snapshot(self) -> Dict:
        """Returns a copy of the current Q-Table for analysis or persistence."""
        return dict(self.q_table)

# --- END OF FILE ---