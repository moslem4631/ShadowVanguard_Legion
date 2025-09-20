# F:\ShadowVanguard_Legion\intelligence\reward_designer.py
# Version 1.0 - The Legion's Doctrine & Ethics Officer (Initial Scaffolding)

import logging
from typing import Dict, Any

from core.data_models import PositionV2 as Position, MarketDataFrame

logger = logging.getLogger("RewardDesigner")

class RewardDesigner:
    """
    این ماژول، مسئول طراحی و محاسبه تابع پاداش (Reward Function) برای
    آموزش BattleLearner است.
    هدف، هدایت ربات به سمت سودآوری پایدار و هوشمندانه است.
    """
    def __init__(self, reward_config: Dict[str, float] = None):
        
        # در آینده، این تنظیمات از فایل config خوانده خواهند شد
        self.config = reward_config or {
            "pnl_weight": 1.0,           # ضریب اهمیت سود و زیان
            "sharpe_ratio_weight": 0.0,  # آرمان آینده: ضریب اهمیت نسبت شارپ
            "risk_weight": 0.0,          # آرمان آینده: ضریب تنبیه برای ریسک بالا
        }
        logger.info("[RewardDesigner] ✅ واحد طراح پاداش با ساختار اولیه آماده شد.")


    def calculate_reward(self, final_position_state: Position) -> float:
        """
        پاداش نهایی یک معامله را محاسبه می‌کند.
        
        Args:
            final_position_state (Position): وضعیت نهایی پوزیشن پس از بسته شدن.
            
        Returns:
            float: مقدار پاداش (می‌تواند منفی باشد).
        """
        try:
            # نسخه ۱.۰: پاداش فقط بر اساس سود و زیان درصدی است.
            # این یک محاسبه ساده و پایه است.
            base_reward = final_position_state.pnl_percentage
            
            # TODO (آرمان آینده): افزودن منطق پیچیده‌تر
            # sharpe_factor = self._calculate_sharpe_factor(...)
            # risk_penalty = self._calculate_risk_penalty(...)
            # final_reward = (base_reward * self.config['pnl_weight'] + 
            #                 sharpe_factor * self.config['sharpe_ratio_weight'] -
            #                 risk_penalty * self.config['risk_weight'])

            final_reward = base_reward
            
            logger.info(f"Calculated reward for position {final_position_state.position_id}: {final_reward:.4f}")
            return final_reward
            
        except Exception as e:
            logger.error(f"[RewardDesigner] ❌ خطا در محاسبه پاداش: {e}", exc_info=True)
            return 0.0

# --- END OF FILE ---