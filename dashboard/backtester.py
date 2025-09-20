# F:\ShadowVanguard_Legion\dashboard\backtester.py
# Version 1.2 - Final Sync with Legion Architecture

import logging
from typing import Dict, Any
from copy import deepcopy

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.data_provider import DataProvider
from core.data_models import PositionV2 as Position
from core.market_enums import PositionSide, TacticalDecision
from analyst_ai.structure_analyzer import StructureAnalyzer
from analyst_ai.pattern_detector import PatternDetector
from intelligence.power_scanner import PowerScanner
from intelligence.synthetic_emotion import SyntheticEmotionEngine
from intelligence.intent_recognizer import IntentRecognizer
from risk_manager.capital_allocator import CapitalAllocator
from risk_manager.stop_loss_manager import StopLossManager
from execution_engine.position_manager import PositionManager
from tactical_ai.tactical_controller import TacticalController
from memory.experience_memory import ExperienceMemory

logger = logging.getLogger("Backtester")
console = Console()

class Backtester:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # --- FINALIZED: Initialize components like in main.py ---
        self.data_provider = DataProvider(self.config.get('data_provider', {}))
        self.memory = ExperienceMemory(self.config.get('memory', {}).get('max_size', 1000))
        
        self.power_scanner = PowerScanner(self.config.get('power_scanner', {}))
        self.emotion_engine = SyntheticEmotionEngine(self.config.get('emotion_engine', {}))
        self.intent_recognizer = IntentRecognizer(memory=self.memory, thresholds=self.config.get('intent_recognizer', {}))
        
        self.capital_allocator = CapitalAllocator(self.config.get('capital_allocator', {}))
        self.stop_loss_manager = StopLossManager(self.config.get('stop_loss_manager', {}))
        
        self.position_manager = PositionManager()

        self.tactical_controller = TacticalController(
            position_manager=self.position_manager,
            config=self.config.get('tactical_controller', {})
        )

        self.capital = self.config.get('initial_capital', 10000.0)
        self.trade_history: list[Position] = []
        self.symbol = self.config.get('target_symbol', 'BTCUSDT')

    def run(self):
        logger.info("--- [ STARTING HISTORICAL WAR GAMES ] ---")
        tick_count = 0
        while True:
            mdf = self.data_provider.fetch_market_data(self.symbol)
            if mdf is None:
                logger.info("--- [ END OF HISTORICAL DATA REACHED ] ---")
                break
                
            current_price = mdf.ohlcv['close'].iloc[-1]
            self.position_manager.update_all_positions_pnl({self.symbol: current_price})

            # --- FINALIZED: Follows new command chain ---
            power_report = self.power_scanner.scan(mdf)
            emotion_report = self.emotion_engine.analyze(power_report)
            intent_report = self.intent_recognizer.recognize(power_report, emotion_report)

            decision, signal = self.tactical_controller.generate_decision(power_report, emotion_report, intent_report, self.symbol)

            if decision == TacticalDecision.ADVANCE:
                self._execute_open(signal, mdf)
            elif decision == TacticalDecision.RETREAT:
                self._execute_close(mdf)
            
            tick_count += 1
            if tick_count % 500 == 0: console.print(f"Processed {tick_count} candles...")
                
        self._generate_report()

    def _execute_open(self, signal, mdf):
        side_str = signal.details.get("side", "LONG").upper()
        side = PositionSide[side_str]
        entry_price = mdf.ohlcv['close'].iloc[-1]
        stop_loss_price = self.stop_loss_manager.calculate_initial_stop_loss(side, entry_price, mdf)
        position_size = self.capital_allocator.calculate_position_size(
            total_capital=self.capital, entry_price=entry_price,
            stop_loss_price=stop_loss_price, signal=signal
        )
        if position_size > 0:
            new_position = Position(
                position_id=f"trade-{len(self.trade_history) + 1}",
                symbol=self.symbol, side=side, entry_price=entry_price,
                size=position_size, timestamp=mdf.timestamp
            )
            self.position_manager.open_position(new_position)

    def _execute_close(self, mdf):
        current_price = mdf.ohlcv['close'].iloc[-1]
        positions_to_close = self.position_manager.get_positions_by_symbol(self.symbol)
        for position in positions_to_close:
            position.pnl_percentage = ((current_price / position.entry_price) - 1) * 100 if position.side == PositionSide.LONG else ((position.entry_price / current_price) - 1) * 100
            closed_pos = self.position_manager.close_position(position.position_id)
            if closed_pos:
                self.trade_history.append(deepcopy(closed_pos))
    
    def _generate_report(self):
        console.print(Panel("[bold green]BACKTESTING REPORT[/bold green]", expand=False))
        total_trades = len(self.trade_history)
        if total_trades == 0:
            console.print("No trades were executed.")
            return

        wins = [t for t in self.trade_history if t.pnl_percentage > 0]
        losses = [t for t in self.trade_history if t.pnl_percentage <= 0]
        
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        total_pnl = sum(t.pnl_percentage for t in self.trade_history)
        gross_profit = sum(t.pnl_percentage for t in wins)
        gross_loss = abs(sum(t.pnl_percentage for t in losses))
        profit_factor = gross_profit / max(gross_loss, 1e-9)

        summary_table = Table(title="Performance Summary")
        summary_table.add_column("Metric", style="cyan"); summary_table.add_column("Value", style="white")
        summary_table.add_row("Total Trades", str(total_trades))
        summary_table.add_row("Win Rate", f"{win_rate:.2f}%")
        summary_table.add_row("Total Net PnL %", f"{total_pnl:.2f}%")
        summary_table.add_row("Profit Factor", f"{profit_factor:.2f}")
        console.print(summary_table)

if __name__ == '__main__':
    from main import load_config
    try:
        config = load_config()
        backtester = Backtester(config=config)
        backtester.run()
    except Exception as e:
        logger.critical(f"Failed to run backtester: {e}", exc_info=True)