# F:\ShadowVanguard_Legion_Godspeed\execution_engine\live_order_executor.py
# Version 2.8 - The MEXC Enforcer

import logging
from typing import Dict, Any, Optional, List
import ccxt
from uuid import uuid4

from core.interface_book import IOrderExecutor
from core.market_enums import PositionSide

logger = logging.getLogger("LiveOrderExecutor")

class LiveOrderExecutor(IOrderExecutor):
    """
    THE MEXC ENFORCER: This version completes the ambassador's diplomatic training,
    officially adding the protocol for the MEXC forward base. It now understands how
    to correctly engage MEXC's sandbox environment, making the Legion's entire
    command chain fully prepared for Operation: New Hope.
    """
    def __init__(self, main_config: Dict[str, Any], live_config: Dict[str, Any], api_key: str, secret_key: str, passphrase: Optional[str], is_paper: bool):
        # [PACT KEPT]: Core configuration reading is preserved.
        self.live_config = live_config
        self.main_config = main_config
        
        self.exchange_id = self.live_config.get('exchange', 'mexc')
        self.market_type = self.live_config.get('market_type', 'swap')
        
        self.is_paper = is_paper
        self.pending_stops = {}
        
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            
            exchange_config = {
                'apiKey': api_key,
                'secret': secret_key,
                'password': passphrase,
                'options': { 'defaultType': self.market_type },
            }
            
            self.exchange = exchange_class(exchange_config)
            
            # [SURGICAL UPGRADE - MEXC DIPLOMACY PROTOCOL]:
            if is_paper:
                logger.warning(f"!!! OPERATING IN PAPER TRADING ({self.exchange_id.upper()} DEMO) MODE !!!")
                
                if self.exchange_id == 'okx':
                    self.exchange.headers = { 'x-simulated-trading': '1' }
                    logger.info("OKX-specific demo trading protocol enabled via headers.")
                    logger.warning("Skipping full market load to comply with OKX Demo API limitations.")

                elif self.exchange_id == 'kucoinfutures':
                    kucoin_sandbox_url = 'https://api-sandbox-futures.kucoin.com'
                    self.exchange.urls['api'] = {
                        'public': kucoin_sandbox_url, 'private': kucoin_sandbox_url,
                        'futuresPublic': kucoin_sandbox_url, 'futuresPrivate': kucoin_sandbox_url,
                    }
                    logger.info(f"Manual and COMPLETE sandbox route map set for KuCoin Futures.")
                    self.exchange.load_markets()
                
                # New protocol for our new forward base.
                elif self.exchange_id == 'mexc':
                    if self.exchange.has['sandbox']:
                        self.exchange.set_sandbox_mode(True)
                        logger.info(f"Standard sandbox mode enabled for MEXC. Loading markets...")
                        self.exchange.load_markets()
                    else:
                        logger.error(f"MEXC is selected, but ccxt reports no sandbox support for it.")
                        raise NotImplementedError(f"MEXC sandbox not supported by this ccxt version.")
                
                elif self.exchange.has['sandbox']:
                    self.exchange.set_sandbox_mode(True)
                    logger.info(f"Standard sandbox mode enabled for {self.exchange_id}. Loading markets...")
                    self.exchange.load_markets()
                
                else:
                    logger.error(f"Paper trading selected, but no specific demo protocol is defined for {self.exchange_id}.")
                    raise NotImplementedError(f"Demo mode protocol not implemented for {self.exchange_id}")
            else:
                logger.warning("!!! WARNING: OPERATING IN LIVE TRADING MODE WITH REAL CAPITAL !!!")
                self.exchange.load_markets() # Always load markets for live trading

        except Exception as e:
            logger.critical(f"Failed to initialize exchange '{self.exchange_id}': {e}", exc_info=True)
            raise
            
        logger.info(f"[LiveOrderExecutor] The MEXC Enforcer v2.8 online, connected to {self.exchange_id.upper()}.")

    # [PACT KEPT]: All order execution logic from v2.7 is 100% PRESERVED.
    
    def place_order(self, symbol: str, side: PositionSide, size: float, order_type: str, current_price: float, trigger_price: Optional[float] = None, parent_position_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        ccxt_side = 'buy' if side == PositionSide.LONG else 'sell'
        ccxt_order_type = order_type.lower()
        try:
            logger.info(f"PLACING LIVE ORDER: {ccxt_side.upper()} {size:.5f} {symbol} @ {ccxt_order_type}")
            params = {}
            order = None
            if self.exchange_id == 'okx':
                params['posSide'] = 'long' if side == PositionSide.LONG else 'short'
            if ccxt_order_type == 'market' or ccxt_order_type == 'limit':
                if ccxt_order_type == 'market':
                    order = self.exchange.create_order(symbol, ccxt_order_type, ccxt_side, size, params=params)
                else:
                    order = self.exchange.create_order(symbol, ccxt_order_type, ccxt_side, size, current_price, params=params)
            elif ccxt_order_type == 'stop_market':
                logger.warning("Simulating STOP_MARKET for paper trading.")
                order_id = f"sim-stop-{uuid4()}"
                self.pending_stops[order_id] = {'side': side, 'trigger': trigger_price, 'size': size, 'parent': parent_position_id, 'symbol': symbol}
                logger.info(f"Simulated STOP_MARKET armed. Order ID: {order_id}")
                order = {'id': order_id, 'status': 'open'}
            else:
                logger.error(f"Unsupported live order type: {order_type}")
                return None
            if order is None:
                logger.error("Exchange returned a NULL response for the order creation request.")
                return None
            return {
                "order_id": order['id'], "status": order.get('status', 'open').upper(),
                "filled_price": order.get('average', current_price), "filled_size": order.get('filled', 0.0),
                "original_parent_id": parent_position_id
            }
        except Exception as e:
            logger.critical(f"LIVE ORDER FAILED due to an exception: {e}", exc_info=True)
            return None

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        if order_id.startswith('sim-stop-'):
            if order_id in self.pending_stops:
                del self.pending_stops[order_id]; logger.info(f"Cancelled simulated stop order {order_id}.")
            return True
        try:
            logger.warning(f"Attempting to cancel live order {order_id} for {symbol}")
            self.exchange.cancel_order(order_id, symbol)
            return True
        except ccxt.OrderNotFound:
             logger.warning(f"Could not cancel order {order_id}: Already filled or cancelled.")
             return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False

    def close_order(self, order_id: str, size: float, symbol: str, price: float) -> Optional[Dict[str, Any]]:
        try:
            positions = self.exchange.fetch_positions([symbol])
            open_position = next((p for p in positions if float(p.get('contracts', 0)) > 0), None)
            if not open_position:
                logger.warning(f"Tried to close position for {symbol}, but no open position found."); return {"status": "FILLED"}
            
            current_side = open_position.get('side', 'long')
            close_side = 'buy' if current_side == 'short' else 'sell'
            
            params = {'reduceOnly': True}
            if self.exchange_id == 'okx':
                params['posSide'] = current_side
            logger.info(f"Closing {current_side.upper()} position for {symbol} by placing a {close_side.upper()} order.")
            order = self.exchange.create_order(symbol, 'market', close_side, size, params=params)
            
            return { "status": "FILLED", "filled_price": order.get('average', price), "order_id": order['id']}
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to execute live close for {symbol}: {e}")
            return None

    def check_triggered_stops(self, current_high: float, current_low: float, symbol: str) -> List[Dict[str, Any]]:
        if not self.is_paper: return []
        triggered = [];
        for order_id, stop_info in list(self.pending_stops.items()):
            if stop_info['symbol'] != symbol: continue
            is_triggered = False
            if stop_info['side'] == PositionSide.SHORT and current_high >= stop_info['trigger']: is_triggered = True
            elif stop_info['side'] == PositionSide.LONG and current_low <= stop_info['trigger']: is_triggered = True
            if is_triggered:
                logger.critical(f"!!! PAPER TRADING TRAP TRIGGERED !!! Stop order {order_id} activated.")
                triggered.append({
                    "order_id": f"triggered-{order_id}", "status": "FILLED",
                    "filled_price": stop_info['trigger'], "filled_size": stop_info['size'],
                    "original_parent_id": stop_info['parent'], "side": stop_info['side'].name
                })
                del self.pending_stops[order_id]
        return triggered