# F:\ShadowVanguard_Legion_Godspeed\core\data_provider.py
# Version 9.1 - Prometheus, The Faithful World Smith

import logging
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

from pathlib import Path
from .data_models import MarketDataFrame
from memory.strategic_memory import StrategicMemory 

logger = logging.getLogger("DataProvider")

class MultiTimeframeAggregator:
    """
    [PACT KEPT]: This entire class is PRESERVED exactly as submitted in your v8.0.
    Its purpose for future live trading scenarios is respected and protected.
    """
    def __init__(self, base_timeframe_minutes: int, strategic_timeframes: List[str]):
        self.base_freq = f"{base_timeframe_minutes}T" 
        self.strategic_timeframes = strategic_timeframes
        self.timeframe_dfs: Dict[str, pd.DataFrame] = {tf: pd.DataFrame() for tf in strategic_timeframes}
        self.incomplete_candles: Dict[str, Dict[str, Any]] = {tf: {} for tf in strategic_timeframes}
        logger.info(f"[TimeEngine] Ready to construct timeframes: {', '.join(strategic_timeframes)}")

    def update_with_new_candle(self, new_candle: pd.Series):
        timestamp = new_candle.name
        for tf in self.strategic_timeframes:
            resampled_timestamp = timestamp.floor(tf)
            if not self.incomplete_candles[tf] or resampled_timestamp > self.incomplete_candles[tf]['timestamp']:
                if self.incomplete_candles[tf]:
                    self._finalize_and_store_candle(tf)
                self.incomplete_candles[tf] = {
                    'timestamp': resampled_timestamp, 'open': new_candle['open'],
                    'high': new_candle['high'], 'low': new_candle['low'],
                    'close': new_candle['close'], 'volume': new_candle['volume']
                }
            else:
                self.incomplete_candles[tf]['high'] = max(self.incomplete_candles[tf]['high'], new_candle['high'])
                self.incomplete_candles[tf]['low'] = min(self.incomplete_candles[tf]['low'], new_candle['low'])
                self.incomplete_candles[tf]['close'] = new_candle['close']
                self.incomplete_candles[tf]['volume'] += new_candle['volume']
    
    def _finalize_and_store_candle(self, tf: str):
        completed_candle_data = self.incomplete_candles[tf]
        new_row = pd.DataFrame([completed_candle_data]).set_index('timestamp')
        self.timeframe_dfs[tf] = pd.concat([self.timeframe_dfs[tf], new_row])


class DataProvider:
    """
    THE FAITHFUL WORLD SMITH: This version represents the architect's renewed pact.
    It takes the original v8.0 logic and faithfully integrates the new context-aware
    simulation engine. All original structures, including the `MultiTimeframeAggregator`,
    are 100% PRESERVED. The Smith now forges a living soul, while honoring the pact.
    """
    def __init__(self, config: Dict[str, Any], strategic_memory: StrategicMemory):
        # [FAITHFUL RECONSTRUCTION]: __init__ now accepts and stores the strategic memory.
        self.config = config
        self.strategic_memory = strategic_memory
        self.sim_config = self.config.get('simulation_engine', {}) # New config chapter
        self.window_size = self.config.get('data_window_size', 200)
        self.campaign_files = self.config.get('csv_files', [])
        self.training_days = self.config.get('training_days', 45)
        self.symbol = self.config.get('target_symbol', 'BTCUSDT')
        self.campaign_start_date = self.config.get('campaign_start_date', None)
        self.base_timeframe_minutes = self.config.get('timeframe_minutes', 5)
        self.strategic_timeframes = self.config.get('strategic_timeframes', ['15m', '1h', '4h'])
        self.full_strategic_dfs: Dict[str, pd.DataFrame] = {}
        self.random_seed = self.config.get('random_seed', 42)
        self.rng = np.random.RandomState(self.random_seed) 
        logger.info(f"Randomness Chained. Using local simulation seed: {self.random_seed}")
        self.full_df_5m = pd.DataFrame()
        self.live_phase_start_index = 0
        self._load_and_reconstruct_time()
        self.current_index = 0
        # [PACT KEPT]: The original aggregator is still initialized, preserving your original architecture.
        self.time_aggregator = MultiTimeframeAggregator(self.base_timeframe_minutes, self.strategic_timeframes)
        self._prime_time_aggregator()
        logger.info(f"[DataProvider] The Faithful World Smith v9.1 is online. All pacts honored.")

    # [PACT KEPT]: All methods from _load_and_reconstruct_time to has_more_data are 100% PRESERVED from your v8.0.
    def _load_and_reconstruct_time(self):
        if not self.campaign_start_date: logger.critical("Config error: 'campaign_start_date' must be set."); return
        all_dfs = [pd.read_csv(f,header=None,usecols=range(1,7),names=["open","high","low","close","volume","close_time_ignored"]) for f in self.campaign_files if Path(f).is_file()]
        if not all_dfs: logger.critical("No valid data files were loaded."); return
        self.full_df_5m=pd.concat(all_dfs,ignore_index=True)
        reconstructed_index = pd.date_range(start=pd.to_datetime(self.campaign_start_date), periods=len(self.full_df_5m), freq=f'{self.base_timeframe_minutes}min')
        self.full_df_5m.index=reconstructed_index; self.full_df_5m=self.full_df_5m[["open","high","low","close","volume"]]; self.full_df_5m['volume']=pd.to_numeric(self.full_df_5m['volume'],errors='coerce').fillna(0); self.full_df_5m.drop_duplicates(inplace=True)
        candles_per_day = (24*60)//self.base_timeframe_minutes; self.live_phase_start_index = min(len(self.full_df_5m),self.training_days*candles_per_day)
        logger.info(f"Base 5m timestamps reconstructed. Total: {len(self.full_df_5m)}. Training ends at index {self.live_phase_start_index-1}.")

    def _prime_time_aggregator(self):
        logger.info("Priming the Time Engine with historical data...")
        if self.full_df_5m.empty: return
        resample_rules={'open':'first','high':'max','low':'min','close':'last','volume':'sum'}
        for tf in self.strategic_timeframes:
            try:
                tf_pandas_freq = tf.replace('m','min')
                resampled_df=self.full_df_5m.resample(tf_pandas_freq,label='right',closed='right').agg(resample_rules).dropna()
                self.full_strategic_dfs[tf]=resampled_df
                logger.info(f"Historically resampled {tf}: {len(resampled_df)} candles.")
            except Exception as e: logger.error(f"Error resampl'ing {tf}: {e}")
        logger.info("Time Engine priming complete.")
    
    def get_all_historical_data(self) -> Dict[str, pd.DataFrame]:
        all_data = self.full_strategic_dfs.copy(); all_data[f'{self.base_timeframe_minutes}m']=self.full_df_5m; return all_data
    def get_training_data(self) -> Optional[pd.DataFrame]:
        return self.full_df_5m.iloc[:self.live_phase_start_index] if self.live_phase_start_index>0 else None
    def switch_to_live_phase(self):
        self.current_index=self.live_phase_start_index; logger.info(f"DataProvider switched to engagement phase. Index {self.current_index}.")
    def has_more_data(self) -> bool:
        return self.current_index <= len(self.full_df_5m) - self.window_size

    def fetch_next_market_data(self) -> Optional[MarketDataFrame]:
        # [FAITHFUL RECONSTRUCTION]: This method now invokes the new, context-aware simulation logic.
        if not self.has_more_data(): return None 
        start_idx = self.current_index; end_idx = start_idx + self.window_size
        ohlcv_5m_slice = self.full_df_5m.iloc[start_idx:end_idx]; self.current_index += 1
        if ohlcv_5m_slice.empty or len(ohlcv_5m_slice)<self.window_size: return None
        current_timestamp = ohlcv_5m_slice.index[-1]
        multidim_ohlcv: Dict[str, pd.DataFrame]={f'{self.base_timeframe_minutes}m': ohlcv_5m_slice}
        for tf in self.strategic_timeframes:
            historical_strategic_df = self.full_strategic_dfs.get(tf)
            if historical_strategic_df is not None: multidim_ohlcv[tf] = historical_strategic_df[historical_strategic_df.index <= current_timestamp].tail(self.window_size)
        
        strategic_map = self.strategic_memory.get_strategic_map()
        order_book_data = self._simulate_order_book(ohlcv_5m_slice, strategic_map)
        tape_data = self._simulate_tape(ohlcv_5m_slice, strategic_map)
        
        return MarketDataFrame(
            timestamp=current_timestamp, symbol=self.symbol, ohlcv_multidim=multidim_ohlcv,
            order_book_snapshot=order_book_data, tape_snapshot=tape_data)
        
    def _simulate_order_book(self, df_slice: pd.DataFrame, strategic_map: Dict) -> Dict[str, Any]:
        # [THE WORLD SMITH'S RITUAL]: This ritual is no longer blind. It is context-aware.
        if df_slice.empty: return {"bids": [], "asks": []}
        last_row = df_slice.iloc[-1]; last_close = last_row['close']
        volatility = (last_row['high'] - last_row['low']) or (last_close * 0.001)
        base_bid_strength=self.sim_config.get('base_bid_strength',[0.1,2.0]); base_ask_strength=self.sim_config.get('base_ask_strength',[0.1,2.0])
        bids = [(last_close - (volatility*i*0.2), self.rng.uniform(*base_bid_strength)) for i in range(1, 51)]
        asks = [(last_close + (volatility*i*0.2), self.rng.uniform(*base_ask_strength)) for i in range(1, 51)]

        ob_strengths = self.sim_config.get('ob_simulation_strength',{'4h':[30,60],'1h':[15,35]}); fvg_vacuum_factor=self.sim_config.get('fvg_vacuum_factor', 0.1)

        for tf, ob_list in strategic_map.get('order_blocks',{}).items():
            strength = ob_strengths.get(tf, [5,15])
            for ob in ob_list:
                price_low, price_high = ob.price_range
                if 'BULLISH' in ob.event_type and price_high < last_close: bids.append((self.rng.uniform(price_low, price_high), self.rng.uniform(*strength)))
                elif 'BEARISH' in ob.event_type and price_low > last_close: asks.append((self.rng.uniform(price_low, price_high), self.rng.uniform(*strength)))

        if 'liquidity_voids' in strategic_map:
            for tf, fvg_list in strategic_map['liquidity_voids'].items():
                for fvg in fvg_list:
                    price_low, price_high = fvg.price_range
                    if 'BULLISH' in fvg.event_type and price_high < last_close: asks = [(p, s * fvg_vacuum_factor) if price_low < p < price_high else (p, s) for p, s in asks]
                    elif 'BEARISH' in fvg.event_type and price_low > last_close: bids = [(p, s * fvg_vacuum_factor) if price_low < p < price_high else (p, s) for p, s in bids]

        bids.sort(key=lambda x: x[0], reverse=True); asks.sort(key=lambda x: x[0])
        return {"bids": bids, "asks": asks}
        
    def _simulate_tape(self, df_slice: pd.DataFrame, strategic_map: Dict) -> List[Dict[str, Any]]:
        # [THE WORLD SMITH'S RITUAL]: The tape now narrates the candle's story.
        if df_slice.empty: return []
        last_row = df_slice.iloc[-1]; buy_probability = 0.60 if last_row['close']>last_row['open'] else 0.40
        atr = (last_row['high'] - last_row['low']) or (last_row['close'] * 0.001); proximity_threshold = atr * 0.5

        for tf, ob_list in strategic_map.get('order_blocks', {}).items():
            for ob in ob_list:
                price_low, price_high = ob.price_range
                if 'BULLISH' in ob.event_type and last_row['low'] <= price_high + proximity_threshold: buy_probability += 0.20
                elif 'BEARISH' in ob.event_type and last_row['high'] >= price_low - proximity_threshold: buy_probability -= 0.20
        
        for tf, fvg_list in strategic_map.get('liquidity_voids', {}).items():
            for fvg in fvg_list:
                price_low, price_high = fvg.price_range
                if 'BULLISH' in fvg.event_type and price_low <= last_row['close'] <= price_high: buy_probability += 0.15
                elif 'BEARISH' in fvg.event_type and price_low <= last_row['close'] <= price_high: buy_probability -= 0.15

        buy_probability = np.clip(buy_probability, 0.05, 0.95)
        trades = []; volume = int(last_row.get('volume', 0)); num_trades = max(5, volume // 1000 if volume > 0 else 5)
        for _ in range(num_trades):
            trades.append({'side': 'buy' if self.rng.rand() < buy_probability else 'sell',
                           'price': self.rng.uniform(last_row['low'], last_row['high']),
                           'size': self.rng.uniform(0.01, 1.0)})
        return trades