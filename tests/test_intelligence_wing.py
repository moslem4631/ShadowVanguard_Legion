# F:\ShadowVanguard_Legion\tests\test_intelligence_wing.py
# Version 1.2 - Fixtures Corrected, Ready for War Games

import pytest
import pandas as pd
from datetime import datetime

# Import all components to be tested
from intelligence.power_scanner import PowerScanner
from intelligence.synthetic_emotion import SyntheticEmotionEngine
from intelligence.intent_recognizer import IntentRecognizer
from memory.experience_memory import ExperienceMemory
from core.data_models import MarketDataFrame, PowerReport
from core.market_enums import MarketRegime

# --- Test Fixtures: Setup reusable components for our tests ---

@pytest.fixture(scope="module")
def sample_config():
    """Provides a sample configuration dictionary for tests."""
    return {
        'power_scanner': {'depth': 5, 'base_tape_weight': 0.4},
        'emotion_engine': {'fear_net_force': -20.0, 'greed_net_force': 25.0, 'confidence_high': 0.7, 'confidence_low': 0.4},
        'intent_recognizer': {'power_strong': 25.0, 'power_weak': -20.0, 'confidence_high': 0.7, 'aggression_high': 0.7, 'fear_high': 0.7}
    }

@pytest.fixture(scope="module")
def experience_memory():
    """Provides a fresh instance of the memory unit."""
    return ExperienceMemory(max_size=100)

# --- NEW: Fixtures for our intelligence units ---
@pytest.fixture(scope="module")
def power_scanner(sample_config):
    """Provides an instance of the PowerScanner."""
    return PowerScanner(sample_config['power_scanner'])

@pytest.fixture(scope="module")
def emotion_engine(sample_config):
    """Provides an instance of the EmotionEngine."""
    return SyntheticEmotionEngine(sample_config['emotion_engine'])

@pytest.fixture(scope="module")
def intent_recognizer(experience_memory, sample_config):
    """Provides an instance of the IntentRecognizer linked to memory."""
    return IntentRecognizer(memory=experience_memory, config=sample_config['intent_recognizer'])
# ----------------------------------------------------


def create_advanced_market_scenario(price=100.0, net_force=-25.0, confidence=0.8, buy_volume=10.0, sell_volume=100.0):
    """A helper function to create a PowerReport for direct testing."""
    return PowerReport(
        net_force=net_force,
        confidence=confidence,
        group_behind_strength=buy_volume * 5,
        group_ahead_strength=sell_volume * 5
    )


# --- Upgraded Tests ---

def test_full_intelligence_pipeline_strong_bullish(emotion_engine, intent_recognizer):
    print("\n--- Testing Scenario: Strong Bullish Advance ---")
    # Arrange: Create a power report with strong bullish conditions
    power_report_bullish = create_advanced_market_scenario(net_force=30.0, confidence=0.8, buy_volume=120.0, sell_volume=20.0)

    # Act
    emotion_report = emotion_engine.analyze(power_report_bullish, MarketRegime.BULL_TREND)
    intent_report = intent_recognizer.recognize(power_report_bullish, emotion_report)

    # Assert
    assert emotion_report.dominant_mood == "GREED"
    assert intent_report['intention'] == 'BULLISH_ADVANCE'
    assert intent_report['confidence'] >= 0.7
    print("✓ Strong Bullish scenario test passed.")


def test_full_intelligence_pipeline_strong_bearish(emotion_engine, intent_recognizer):
    """
    Tests the bearish scenario by creating a rich context.
    The parameter name is changed to avoid conflict with the original test.
    """
    print("\n--- Testing Scenario: Strong Bearish Retreat (Calibrated) ---")
    # Arrange: Create a power report with strong bearish conditions
    power_report_bearish = create_advanced_market_scenario(net_force=-25.0, confidence=0.8, buy_volume=20.0, sell_volume=120.0)

    # Act:
    emotion_report = emotion_engine.analyze(power_report_bearish, MarketRegime.BEAR_TREND)
    intent_report = intent_recognizer.recognize(power_report_bearish, emotion_report)

    # Assert:
    assert emotion_report.dominant_mood == "FEAR", f"Emotion engine failed, expected FEAR but got {emotion_report.dominant_mood}"
    assert intent_report['intention'] == 'BEARISH_RETREAT', f"Expected BEARISH_RETREAT, but got {intent_report['intention']}"
    assert intent_report['confidence'] > 0.6, f"Expected high confidence, but got {intent_report['confidence']}"
    print("✓ Strong Bearish scenario test passed.")