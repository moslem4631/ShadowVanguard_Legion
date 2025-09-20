# F:\ShadowVanguard_Legion_Godspeed\memory\strategic_memory.py
# Version 2.2 - Prometheus, The Enlightened Historian

import logging
import pandas as pd
from typing import Dict, Any, List

# [PACT KEPT]: The new, correct alliances are preserved.
# [SURGICAL UPGRADE]: Import the official blueprints for perfect type hinting and understanding.
from core.data_models import MarketDataFrame, OrderBlock, FairValueGap
from analyst_ai.order_block_analyzer import OrderBlockAnalyzer
from analyst_ai.liquidity_analyzer import LiquidityAnalyzer

logger = logging.getLogger("StrategicMemory")


class StrategicMemory:
    """
    THE ENLIGHTENED HISTORIAN: This version resolves the final, critical type mismatch.
    The Historian's archival process is now fully aligned with the universal reporting
    protocol of the Legion. It correctly reads the `all_blocks` and `unfilled_fvgs` fields
    from modern reports, ensuring the foundational strategic map is built upon a unified
    and consistent truth. The last echo of the old language is gone.
    """

    def __init__(self, config: Dict[str, Any]):
        # [PACT KEPT]: This method is PRESERVED exactly as submitted, with type hint corrections.
        self.protocol = config.get('strategic_memory_protocol', {})
        self.timeframes_to_archive: List[str] = self.protocol.get('timeframes', ['1h', '4h'])
        # [SURGICAL UPGRADE]: Archives are now correctly typed with official blueprints.
        self.historical_order_blocks: Dict[str, List[OrderBlock]] = {tf: [] for tf in self.timeframes_to_archive}
        self.historical_liquidity_voids: Dict[str, List[FairValueGap]] = {tf: [] for tf in self.timeframes_to_archive}

        logger.info("[StrategicMemory] The Enlightened Historian v2.2 is founded. The past is now perfectly clear.")

    def build_from_history(
        self,
        full_historical_mdf: MarketDataFrame, 
        ob_analyzer: OrderBlockAnalyzer,
        liq_analyzer: LiquidityAnalyzer
    ):
        """
        [THE STANDARD ARCHIVAL PROTOCOL]: The archival process is now commanded
        using the standard intelligence packet and modern reporting formats.
        """
        logger.info(f"The Great Archival begins. Analyzing history across: {', '.join(self.timeframes_to_archive)}...")

        if not full_historical_mdf.ohlcv_multidim:
            logger.error("No historical OHLCV data found in the vessel. The strategic map will be empty.")
            return

        # --- Generate comprehensive reports ONCE on the entire historical dataset for efficiency ---
        ob_report = ob_analyzer.analyze(full_historical_mdf)
        liq_report = liq_analyzer.analyze(full_historical_mdf)

        # --- Archive Order Blocks using the new, universal protocol ---
        if ob_report and ob_report.all_blocks:
            for tf in self.timeframes_to_archive:
                # [SURGICAL INTERVENTION]: Logic now correctly accesses the new nested dictionary structure.
                if tf in ob_report.all_blocks:
                    bullish_blocks = ob_report.all_blocks[tf].get('bullish', [])
                    bearish_blocks = ob_report.all_blocks[tf].get('bearish', [])
                    all_tf_blocks = bullish_blocks + bearish_blocks
                    self.historical_order_blocks[tf] = sorted(all_tf_blocks, key=lambda b: b.created_at_index)
                    logger.info(f"Archived {len(all_tf_blocks)} significant Order Blocks for {tf} timeframe.")

        # --- Archive Liquidity Voids (FVGs) using the new, universal protocol ---
        if liq_report and liq_report.unfilled_fvgs:
            for tf in self.timeframes_to_archive:
                 # [SURGICAL INTERVENTION]: Logic now correctly accesses the new `unfilled_fvgs` structure.
                if tf in liq_report.unfilled_fvgs:
                    bullish_fvgs = liq_report.unfilled_fvgs[tf].get('bullish', [])
                    bearish_fvgs = liq_report.unfilled_fvgs[tf].get('bearish', [])
                    all_tf_fvgs = bullish_fvgs + bearish_fvgs
                    self.historical_liquidity_voids[tf] = sorted(all_tf_fvgs, key=lambda v: v.created_at_index)
                    logger.info(f"Archived {len(all_tf_fvgs)} significant Liquidity Voids for {tf} timeframe.")

        logger.info("The Great Archival is complete. The strategic map is now timeless and consistent.")
        
    def get_strategic_map(self) -> Dict[str, Any]:
        """
        [PACT KEPT]: This method is PRESERVED, with a minor rename for clarity.
        """
        return {
            'order_blocks': self.historical_order_blocks,
            'fvgs': self.historical_liquidity_voids  # Renamed from 'liquidity_voids' for consistency
        }