# F:\ShadowVanguard_Legion_Godspeed\main.py
# Version 26.0 - Prometheus, The Final Command Protocol

import logging
import time
import yaml 
import argparse
from pathlib import Path
from typing import Dict, Any, List
import sys
import os
from dotenv import load_dotenv

# [PACT KEPT]: All setup and pathing logic is 100% PRESERVED.
PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / 'config' / 'settings.yaml'
try:
    venv_path = PROJECT_ROOT / '.venv' / 'Lib' / 'site-packages'
    if venv_path.exists() and str(venv_path.resolve()) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT)); sys.path.insert(0, str(venv_path.resolve()))
except Exception as e:
    logging.warning(f"Could not automatically add venv path: {e}")
from utils.logger_config import setup_logging
setup_logging(PROJECT_ROOT)

# [PACT KEPT]: All necessary imports are PRESERVED.
from core.interface_book import IDataProvider, IOrderExecutor
from core.data_provider import DataProvider
from execution_engine.order_executor import SimulatedOrderExecutor
from core.live_data_provider import LiveDataProvider
from execution_engine.live_order_executor import LiveOrderExecutor
from core.data_models import MarketDataFrame 
from risk_manager.capital_allocator import CapitalAllocator
from risk_manager.perimeter_architect import PerimeterArchitect
from memory.strategic_memory import StrategicMemory
from memory.experience_memory import ExperienceMemory
from memory.performance_auditor import PerformanceAuditor
from execution_engine.position_manager import PositionManager
from analyst_ai.structure_analyzer import StructureAnalyzer
from intelligence.power_scanner import PowerScanner
from intelligence.synthetic_emotion import SyntheticEmotionEngine
from dashboard.cli_interface import CliInterface
from analyst_ai.order_block_analyzer import OrderBlockAnalyzer
from analyst_ai.liquidity_analyzer import LiquidityAnalyzer
from analyst_ai.fibonacci_helper import FibonacciHelper
from analyst_ai.divergence_detector import DivergenceDetector
from tactical_ai.tactical_controller import TacticalController
from core.market_enums import TacticalDecision
from analyst_ai.multi_timeframe_synthesizer import MultiTimeframeSynthesizer

logger = logging.getLogger("ShadowVanguardOracle")

def get_isolated_config_copy(full_config: Dict, key: str) -> Dict:
    # [PACT KEPT]: This utility is PRESERVED.
    if full_config is None: return {}
    config_slice = full_config.get(key, {})
    if config_slice is None: return {}
    return yaml.safe_load(yaml.dump(config_slice))

class ShadowVanguardOracle:
    """
    THE FINAL COMMAND PROTOCOL: This is the definitive, battle-hardened version of the
    command center. Its universal protocol is now fully robust, intelligently handling
    optional credentials like passphrases. It is prepared for deployment on any
    battlefield defined in its constitution, starting with the MEXC campaign.
    """
    def __init__(self, config: Dict):
        # [PACT KEPT]: The overall structure is PRESERVED.
        self.config = config
        self.simulation_mode = self.config.get('simulation_mode', 'backtest')
        logger.info(f"--- OPERATION MODE: {self.simulation_mode.upper()} ---")

        self.data_provider: IDataProvider
        self.order_executor: IOrderExecutor

        if self.simulation_mode == 'backtest':
            logger.info("Assembling Backtest Simulation Corps...")
            dp_config = get_isolated_config_copy(self.config, 'data_provider')
            self.data_provider = DataProvider(dp_config)
            self.order_executor = SimulatedOrderExecutor()
        else: # paper or live
            live_config = get_isolated_config_copy(self.config, 'live_engine')
            exchange_name = live_config.get('exchange', 'unknown')
            logger.info(f"Assembling Live Operations Corps for {exchange_name.upper()}...")
            
            load_dotenv()
            
            api_key = os.getenv(live_config.get('api_key_env'))
            secret_key = os.getenv(live_config.get('secret_key_env'))

            # [SURGICAL UPGRADE]: Intelligent passphrase handling.
            # It only tries to load a passphrase if it's defined in the settings.
            passphrase_env_name = live_config.get('passphrase_env')
            passphrase = os.getenv(passphrase_env_name) if passphrase_env_name else None

            if not api_key or not secret_key:
                logger.critical(f"FATAL: Live mode for {exchange_name} requires at least API_KEY and SECRET_KEY in .env file.")
                raise ValueError("Missing core API credentials.")

            # Specific check for exchanges that we know require a passphrase
            if passphrase_env_name and not passphrase:
                 logger.critical(f"FATAL: {exchange_name} requires a {passphrase_env_name} in the .env file, but it was not found.")
                 raise ValueError(f"Missing PASSPHRASE for {exchange_name}.")

            is_paper_trading = (self.simulation_mode == 'paper')
            
            self.data_provider = LiveDataProvider(self.config, live_config, api_key, secret_key, passphrase, is_paper_trading)
            self.order_executor = LiveOrderExecutor(self.config, live_config, api_key, secret_key, passphrase, is_paper_trading)
        
        logger.info("Ambassadors for the designated world have been commissioned.")

        # [PACT KEPT]: All officer assembly logic from here is PRESERVED.
        logger.info("Initializing the Citadel...")
        self.strategic_memory = StrategicMemory(get_isolated_config_copy(self.config, 'memory'))
        if isinstance(self.data_provider, DataProvider):
            self.data_provider.strategic_memory = self.strategic_memory

        self.experience_memory = ExperienceMemory(get_isolated_config_copy(self.config, 'memory'))
        self.performance_auditor = PerformanceAuditor(get_isolated_config_copy(self.config, 'memory'))
        initial_capital = self.config.get('initial_capital', 10000.0)
        self.capital_allocator = CapitalAllocator(initial_capital, get_isolated_config_copy(self.config, 'capital_allocator'))
        self.perimeter_architect = PerimeterArchitect(get_isolated_config_copy(self.config, 'risk_manager'))
        self.position_manager = PositionManager(
            self.order_executor, self.capital_allocator, self.perimeter_architect, self.experience_memory,
            config=yaml.safe_load(yaml.dump(self.config)),
            on_position_closed_callback=self.performance_auditor.record_closed_position
        )
        logger.info("Recruiting the Intelligence Wing...")
        self.time_oracle = MultiTimeframeSynthesizer(get_isolated_config_copy(self.config, 'analyst_ai'))
        self.structure_analyzer = StructureAnalyzer(get_isolated_config_copy(self.config, 'analyst_ai'))
        self.power_scanner = PowerScanner(get_isolated_config_copy(self.config, 'power_scanner'))
        self.emotion_engine = SyntheticEmotionEngine(get_isolated_config_copy(self.config, 'synthetic_emotion'))
        self.ob_analyzer = OrderBlockAnalyzer(get_isolated_config_copy(self.config, 'analyst_ai'))
        self.liq_analyzer = LiquidityAnalyzer(get_isolated_config_copy(self.config, 'analyst_ai'))
        self.fib_sniper = FibonacciHelper(get_isolated_config_copy(self.config, 'analyst_ai'))
        self.interrogator = DivergenceDetector(get_isolated_config_copy(self.config, 'analyst_ai'))
        self.supreme_commander = TacticalController(
            self.position_manager, self.experience_memory, self.strategic_memory,
            yaml.safe_load(yaml.dump(self.config))
        )
        self.cli = CliInterface()
        self.symbol = self.config.get('target_symbol', 'BTC/USDT:USDT')
        logger.info(f"All units initialized. Final Command Protocol synchronized for {self.config.get('live_engine', {}).get('exchange', 'backtest')}.")
        
    # [PACT KEPT]: The remainder of the file is PRESERVED.
    def run_simulation(self):
        self.cli.display_welcome_message()
        if not self.config.get('auto_start', False):
             if not self.cli.get_confirmation("Do you authorize the start of the operation?"):
                logger.warning("Operation aborted by the Commander."); return
        
        if self.simulation_mode == 'backtest':
            self.phase_zero_historical_wisdom()
        else:
            logger.info("="*20 + " [ PHASE 0: LIVE WARMUP ] " + "="*20)
            if isinstance(self.data_provider, LiveDataProvider):
                initial_mdf = self.data_provider.fetch_next_market_data()
                if initial_mdf:
                    enriched_mdf = self.time_oracle.synthesize(initial_mdf)
                    self.strategic_memory.build_from_history(enriched_mdf, ob_analyzer=self.ob_analyzer, liq_analyzer=self.liq_analyzer)
                    logger.info("Live mode warmup and strategic map built successfully.")
                else:
                    logger.critical("Live warmup FAILED. Cannot proceed with engagement."); return
            else:
                 logger.critical("Configuration Mismatch: Live mode selected but LiveDataProvider is not active."); return

        self.phase_one_knowledge_acquisition()
        self.phase_two_engagement()
        logger.info("="*25 + " [ CAMPAIGN FINISHED ] " + "="*25)
        self.cli.display_final_report(self.capital_allocator)

    def phase_zero_historical_wisdom(self):
        if not isinstance(self.data_provider, DataProvider):
            logger.warning("Skipping Phase 0 as it is intended for backtest mode only."); return
        logger.info("="*20 + " [ PHASE 0: THE REMEMBERING ] " + "="*20)
        historical_dict = self.data_provider.get_all_historical_data()
        dp_config = get_isolated_config_copy(self.config, 'data_provider')
        base_tf = dp_config.get('timeframe_minutes', 5)
        base_tf_str = f"{base_tf}m"
        base_tf_df = historical_dict.get(base_tf_str)
        if not historical_dict or base_tf_df is None or base_tf_df.empty:
             logger.error("Cannot build historical wisdom."); return
        last_timestamp = historical_dict[base_tf_str].index[-1]
        historical_mdf = MarketDataFrame(timestamp=last_timestamp, symbol=self.symbol, ohlcv_multidim=historical_dict)
        enriched_mdf = self.time_oracle.synthesize(historical_mdf)
        self.strategic_memory.build_from_history(enriched_mdf, ob_analyzer=self.ob_analyzer, liq_analyzer=self.liq_analyzer)
        logger.info("The timeless strategic map has been built.")
        
    def phase_one_knowledge_acquisition(self):
        logger.info("="*20 + " [ PHASE 1: TACTICAL TRAINING (Future Use) ] " + "="*20)
        
    def phase_two_engagement(self):
        logger.info("="*20 + " [ PHASE 2: GODSPEED ENGAGEMENT ] " + "="*20)
        try:
            while self.data_provider.has_more_data():
                self._tick()
                interval = self.config.get('tick_interval_seconds', 0.0) if self.simulation_mode != 'backtest' else 0.0
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("\nOperation manually halted by the Commander.")
        except Exception as e:
            logger.critical(f"CRITICAL FAILURE IN ENGAGEMENT LOOP: {e}", exc_info=True)

    def _tick(self):
        mdf = self.data_provider.fetch_next_market_data()
        if mdf is None: return
        mdf = self.time_oracle.synthesize(mdf)
        log_tick_info = False
        if self.simulation_mode == 'backtest' and isinstance(self.data_provider, DataProvider) and hasattr(self.data_provider, 'current_index') and self.data_provider.current_index % 10 == 0:
            log_tick_info = True
        if log_tick_info:
             logger.debug("-" * 25 + f" [ BATTLE TICK #{self.data_provider.current_index} ] " + "-" * 25)
        
        mdf.ob_report = self.ob_analyzer.analyze(mdf)
        mdf.liq_report = self.liq_analyzer.analyze(mdf)
        mdf.fib_report = self.fib_sniper.analyze(mdf)
        mdf.div_report = self.interrogator.analyze(mdf)
        mdf.structure_report = self.structure_analyzer.analyze(mdf)
        mdf.power_scanner = self.power_scanner.scan(mdf)
        mdf.emotion_report = self.emotion_engine.analyze(mdf)
        active_position = self.position_manager.get_active_position_for_symbol(self.symbol)
        strategic_alert_status = self.performance_auditor.get_strategic_alert_status()
        final_decision, signal = self.supreme_commander.decide_and_signal(
            mdf=mdf, strategic_alert_status=strategic_alert_status, active_pos=active_position)
        if signal and final_decision not in [TacticalDecision.WAIT, TacticalDecision.HOLD]:
             self.position_manager.execute_tactical_decision(final_decision, signal, mdf)
        dp_config = get_isolated_config_copy(self.config, 'data_provider')
        base_tf_minutes = dp_config.get('timeframe_minutes', 5)
        base_tf_name = f"{base_tf_minutes}m"
        tactical_df = mdf.ohlcv_multidim.get(base_tf_name)
        if tactical_df is not None and not tactical_df.empty:
            last_candle = tactical_df.iloc[-1]
            current_price, current_high, current_low = last_candle['close'], last_candle['high'], last_candle['low']
            self.position_manager.update_all_positions_pnl(current_price)
            triggered_traps = self.order_executor.check_triggered_stops(current_high=current_high, current_low=current_low, symbol=self.symbol)
            if triggered_traps: self.position_manager.handle_triggered_traps(triggered_traps, mdf)
        log_dashboard_info = False
        if self.simulation_mode == 'backtest' and isinstance(self.data_provider, DataProvider) and hasattr(self.data_provider, 'current_index') and self.data_provider.current_index % 50 == 0:
            log_dashboard_info = True
        if log_dashboard_info:
            self.cli.display_full_dashboard(
                mdf=mdf, structure_report=mdf.structure_report, power_report=mdf.power_report,
                emotion_report=mdf.emotion_report, ob_report=mdf.ob_report, fib_report=mdf.fib_report,
                div_report=mdf.div_report, liq_report=mdf.liq_report, final_decision=final_decision,
                signal=signal, active_positions=self.position_manager.get_all_positions(),
                capital_allocator=self.capital_allocator, strategic_map=self.strategic_memory.get_strategic_map()
            )

    @staticmethod
    def load_config(config_path_str: str = 'config/settings.yaml') -> Dict[str, Any]:
        path = Path(config_path_str);
        if not path.is_absolute(): path = PROJECT_ROOT / path
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True); default_config={'initial_capital':10000.0}
            with open(path, 'w', encoding='utf-8') as f: yaml.dump(default_config, f, sort_keys=False, indent=2)
            logger.warning(f"Config file not found. A default '{path}' has been created.")
            return default_config
        with open(path, 'r', encoding='utf-8') as f: config = yaml.safe_load(f)
        if 'data_provider' in config and 'csv_files' in config['data_provider']:
            config['data_provider']['csv_files']=[str(PROJECT_ROOT/p) for p in config['data_provider']['csv_files']]
        logger.info(f"Configuration loaded from '{path}'.")
        return config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowVanguard - The Oracle Engine")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to master configuration file.")
    args = parser.parse_args()
    try:
        master_config = ShadowVanguardOracle.load_config(args.config)
        oracle_bot = ShadowVanguardOracle(config=master_config)
        oracle_bot.run_simulation()
    except Exception as e:
        logger.critical(f"Bot failed to initialize or run. Aborting. Reason: {e}", exc_info=True)