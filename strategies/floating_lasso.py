# F:\ShadowVanguard_Legion\strategies\floating_lasso.py
# Version 1.0 - The Legion's Legendary "Wild Horse" Taming Strategy

import logging
from typing import Dict, Any
from datetime import datetime

# در معماری جدید، این استراتژی نیازی به ایمپورت مستقیم از این ماژول‌ها ندارد.
# او دستوراتش را از TacticalController دریافت خواهد کرد.
from core.data_models import PositionV2 as Position, MarketDataFrame
from core.market_enums import PositionSide

logger = logging.getLogger("FloatingLasso")

class FloatingLassoStrategy:
    """
    پیاده‌سازی استراتژی پیشرفته "کمند شناور".
    این استراتژی یک پوزیشن هِج (معکوس) را برای محافظت از پوزیشن اصلی
    در برابر حرکات شدید و ناگهانی بازار مدیریت می‌کند.
    """
    def __init__(self, position_manager: Any, order_executor: Any, config: Dict[str, Any]):
        
        self.position_manager = position_manager
        self.order_executor = order_executor
        self.config = config
        
        self.activation_threshold_pnl_drop = self.config.get('lasso_pnl_drop_percent', -1.5)
        self.hedge_size_ratio = self.config.get('lasso_hedge_ratio', 0.5) # ۵۰٪ حجم پوزیشن اصلی

        logger.info(f"[FloatingLasso] ✅ استراتژی کمند شناور با آستانه افت سود {self.activation_threshold_pnl_drop}% آماده شد.")

    def manage_hedges(self, mdf: MarketDataFrame):
        """
        این متد در هر تیک از برنامه توسط حلقه اصلی فراخوانی می‌شود تا وضعیت را
        برای فعال‌سازی یا مدیریت کمندها بررسی کند.
        """
        if not self.position_manager.has_open_positions:
            return
            
        all_positions = self.position_manager.get_all_positions()
        
        for position in all_positions:
            # این استراتژی فقط روی پوزیشن‌های اصلی کار می‌کند، نه خود هِج‌ها
            if position.is_hedged or position.status == "HEDGE":
                continue

            # بررسی شرایط فعال‌سازی کمند
            if self._should_activate_lasso(position):
                logger.warning(f"🐎 اسب وحشی شد! افت شدید سود برای پوزیشن {position.position_id}. "
                               f"فعال‌سازی کمند شناور...")
                self._deploy_lasso(position, mdf)

    def _should_activate_lasso(self, position: Position) -> bool:
        """
        شرایط فعال‌سازی کمند را بررسی می‌کند.
        در نسخه اولیه، ما بر اساس یک افت شدید و ناگهانی در سود تصمیم می‌گیریم.
        """
        # آرمان آینده: این متد باید سیگنال‌هایی را از SynergyMonitor یا DeceptionDetector دریافت کند.
        
        # اگر سود درصد کمتر از آستانه مشخص شده باشد، کمند فعال می‌شود.
        if position.pnl_percentage < self.activation_threshold_pnl_drop:
            return True
        
        return False
        
    def _deploy_lasso(self, main_position: Position, mdf: MarketDataFrame):
        """
        یک پوزیشن هِج (کمند) را برای محافظت از پوزیشن اصلی ایجاد می‌کند.
        
        نکته معماری: این متد مستقیماً با صرافی کار نمی‌کند، بلکه یک درخواست
        به PositionManager می‌دهد تا پوزیشن جدید ثبت شود. مسئولیت ارسال
        واقعی سفارش با OrderExecutor است (که اینجا شبیه‌سازی می‌شود).
        """
        # تعیین جهت معکوس
        hedge_side = PositionSide.SHORT if main_position.side == PositionSide.LONG else PositionSide.LONG

        # محاسبه حجم پوزیشن هِج
        hedge_size = main_position.size * self.hedge_size_ratio
        
        # TODO (آرمان آینده): پیاده‌سازی منطق "پل مارجین".
        
        hedge_id = f"lasso-{main_position.position_id}"
        current_price = mdf.ohlcv['close'].iloc[-1]

        hedge_position = Position(
            position_id=hedge_id,
            symbol=main_position.symbol,
            side=hedge_side,
            entry_price=current_price,
            size=hedge_size,
            timestamp=datetime.now(),
            status="HEDGE"
        )
        
        # ثبت پوزیشن هِج در دفتر لجستیک
        self.position_manager.open_position(hedge_position)
        
        # علامت‌گذاری پوزیشن اصلی به عنوان "هِج شده"
        main_position.is_hedged = True
        main_position.lasso_order_id = hedge_id
        
        logger.info(f"✅ کمند شناور برای پوزیشن {main_position.position_id} با موفقیت فعال شد. "
                    f"پوزیشن هِج: {hedge_side.name} | حجم: {hedge_size}")


# --- END OF FILE ---