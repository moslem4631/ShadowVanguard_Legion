# F:\ShadowVanguard_Legion\memory\feedback_processor.py
# Version 2.0 - The Legion's After-Action Review (AAR) Officer

import logging
from typing import Dict, Any

# وابستگی به ماژول‌های دیگر برای پردازش و ساخت آبجکت نهایی
from .experience_memory import Experience, ExperienceMemory
from core.data_models import PositionV2 as Position
from intelligence.battle_learner import BattleLearner
from intelligence.reward_designer import RewardDesigner

logger = logging.getLogger("FeedbackProcessor")

class FeedbackProcessor:
    """
    این واحد مسئول پردازش بازخورد نهایی یک معامله و تبدیل آن به
    یک "تجربه قابل یادگیری" برای ثبت در آرشیو جنگ و آموزش RL است.
    """
    def __init__(self, memory: ExperienceMemory, learner: BattleLearner, reward_designer: RewardDesigner):
        """
        Args:
            memory (ExperienceMemory): نمونه‌ای از حافظه مرکزی.
            learner (BattleLearner): نمونه‌ای از موتور یادگیری.
            reward_designer (RewardDesigner): نمونه‌ای از طراح پاداش.
        """
        self.memory = memory
        self.learner = learner
        self.reward_designer = reward_designer
        logger.info("[FeedbackProcessor] ✅ واحد پردازش بازخورد آماده و به واحدهای مربوطه متصل شد.")

    def process_trade_result(self, 
                             closed_position: Position,
                             initial_state: Dict[str, Any],
                             taken_action: Dict[str, Any],
                             final_state: Dict[str, Any]):
        """
        یک معامله بسته شده را پردازش کرده، آن را به تجربه تبدیل می‌کند،
        به حافظه می‌سپارد و به موتور یادگیری برای آموزش ارسال می‌کند.
        
        Args:
            closed_position (Position): آبجکت کامل پوزیشن بسته شده.
            initial_state (Dict): زمینه‌ای که در آن "تصمیم" گرفته شد.
            taken_action (Dict): "تصمیمی" که گرفته شد.
            final_state (Dict): زمینه بازار در لحظه بسته شدن پوزیشن.
        """
        try:
            # 1. ساختن آبجکت تجربه (Experience)
            # خروجی (Outcome) همان وضعیت نهایی پوزیشن است.
            experience = Experience(
                state=initial_state,
                action=taken_action,
                outcome=closed_position,
                timestamp=closed_position.timestamp # زمان بسته شدن پوزیشن
            )

            # 2. به خاطر سپردن تجربه در آرشیو جنگ
            self.memory.remember(experience)
            
            # 3. محاسبه پاداش هوشمند برای این تجربه
            reward = self.reward_designer.calculate_reward(closed_position)
            
            # 4. ارسال تجربه به آکادمی نظامی (BattleLearner) برای یادگیری
            # ما باید state ها را به فرمت hashable (مانند تاپل) تبدیل کنیم تا به عنوان کلید در q_table استفاده شوند.
            # (این منطق می‌تواند در آینده پیچیده‌تر شود)
            initial_state_tuple = self._convert_state_to_tuple(initial_state)
            final_state_tuple = self._convert_state_to_tuple(final_state)
            action_name = taken_action.get('decision', 'UNKNOWN_ACTION')

            self.learner.learn_from_experience(
                state=initial_state_tuple,
                action=action_name,
                reward=reward,
                next_state=final_state_tuple
            )
            
            logger.info(f"Feedback for position {closed_position.position_id} processed successfully.")

        except Exception as e:
            logger.error(f"[FeedbackProcessor] ❌ خطا در پردازش بازخورد: {e}", exc_info=True)


    def _convert_state_to_tuple(self, state: Dict[str, Any]) -> tuple:
        """
        یک دیکشنری state را به یک تاپل قابل هش برای استفاده در Q-Table تبدیل می‌کند.
        این یک پیاده‌سازی ساده اولیه است و می‌تواند بسیار هوشمندتر شود.
        """
        power_report = state.get('power_report')
        emotion_report = state.get('emotion_report')

        if not power_report or not emotion_report:
            return ("INCOMPLETE_STATE",)

        # ساخت تاپل از ویژگی‌های کلیدی
        state_tuple = (
            emotion_report.dominant_mood,
            round(power_report.confidence, 1), # گرد کردن برای کاهش فضای حالت
            int(power_report.net_force // 10)    # تقسیم برای کاهش فضای حالت
        )
        return state_tuple
        
# --- END OF FILE ---