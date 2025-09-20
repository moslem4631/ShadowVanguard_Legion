# F:\ShadowVanguard_Legion\execution_engine\order_executor.py
# Version 3.2 - Prometheus: The Loyal Lookout

import logging
import uuid
from typing import Dict, Optional, Protocol, List, Any

from core.data_models import PositionV2 as Position
from core.market_enums import PositionSide

logger = logging.getLogger("OrderExecutor")

class IOrderExecutor(Protocol):
    """
    The Official Contract for any execution unit. Now explicitly requires
    passing parent_position_id for conditional orders.
    """
    def place_order(self, symbol: str, side: PositionSide, size: float, order_type: str = 'MARKET', parent_position_id: Optional[str] = None, **kwargs) -> Optional[Dict]: ...
    def close_order(self, position_id: str, size: float, symbol: str, current_price: float) -> Optional[Dict]: ... # Added price for realism
    def cancel_order(self, order_id: str) -> bool: ...
    def check_triggered_stops(self, current_high: float, current_low: float) -> List[Dict]: ...


class SimulatedOrderExecutor(IOrderExecutor):
    """
    A simulated implementation. Version 3.2, "The Loyal Lookout", now correctly
    stamps the parent position ID on trap orders, ensuring the chain of command
    remains unbroken during counter-attacks.
    """
    def __init__(self):
        self.pending_orders: Dict[str, Dict[str, Any]] = {}
        logger.info("[SimulatedOrderExecutor] The Loyal Lookout v3.2 is active.")

    def place_order(self, symbol: str, side: PositionSide, size: float, order_type: str = 'MARKET', parent_position_id: Optional[str] = None, **kwargs) -> Optional[Dict]:
        """
        Simulates placing an order. STOP_MARKET orders now require and store the
        parent_position_id for perfect attribution upon triggering.
        """
        order_id = f"sim-{uuid.uuid4().hex[:10]}"
        logger.info(f"--- SIMULATING: Receiving Place Order command ---")
        
        if order_type.upper() == 'STOP_MARKET':
            trigger_price = kwargs.get('trigger_price')
            if not trigger_price:
                logger.error("STOP_MARKET order requires a 'trigger_price'. Order rejected.")
                return None
            
            # --- AI-UPGRADE: Precise Identification Protocol ---
            if not parent_position_id:
                logger.error("STOP_MARKET order (Hedge Trap) requires a 'parent_position_id'. Order rejected.")
                return None
            
            order_details = {
                'order_id': order_id, 'symbol': symbol, 'side': side.value, # Store as string for consistency
                'size': size, 'order_type': order_type, 'trigger_price': trigger_price,
                'status': 'PENDING',
                'parent_position_id': parent_position_id # Stamp the ID
            }
            self.pending_orders[order_id] = order_details
            logger.info(f"Placed PENDING {side.name} {order_type} for parent {parent_position_id} ({order_id}) | Size {size:.4f} @ Trigger {trigger_price:.2f}")
            return order_details

        elif order_type.upper() == 'MARKET':
            filled_price = kwargs.get('current_price', 60000.0) 
            logger.info(f"Placing IMMEDIATE {side.name} MARKET order of size {size:.8f}")
            return {
                "status": "FILLED", "order_id": order_id,
                "filled_price": filled_price, "filled_size": size
            }
        else:
            logger.error(f"Unsupported order type '{order_type}'. Order rejected.")
            return None

    def close_order(self, position_id: str, size: float, symbol: str, current_price: float) -> Optional[Dict]:
        """Simulates closing an existing position. Now returns a fill receipt for accuracy."""
        logger.info(f"--- SIMULATING: Closing Order for position {position_id} ---")
        logger.info(f"Closing {size:.8f} of position {position_id} for {symbol}")
        # Return a fill receipt similar to a market order
        return {
            "status": "FILLED", "order_id": f"close-{position_id}",
            "filled_price": current_price, "filled_size": size
        }

    def cancel_order(self, order_id: str) -> bool:
        """Simulates cancelling a pending order."""
        if order_id in self.pending_orders:
            logger.info(f"--- SIMULATING: Cancelling PENDING order {order_id} ---")
            del self.pending_orders[order_id]
            return True
        else:
            logger.warning(f"Attempted to cancel {order_id}, but not found in pending orders.")
            return False

    def check_triggered_stops(self, current_high: float, current_low: float) -> List[Dict]:
        """
        Checks if the current price has activated any pending STOP orders.
        The fill receipt now includes the parent position ID.
        """
        triggered_orders = []
        for order_id in list(self.pending_orders.keys()):
            order = self.pending_orders.get(order_id)
            if not order: continue

            is_triggered = False
            # Ensure side is compared correctly (it's now a string)
            if order['side'] == PositionSide.LONG.value and current_high >= order['trigger_price']:
                is_triggered = True
            elif order['side'] == PositionSide.SHORT.value and current_low <= order['trigger_price']:
                is_triggered = True
            
            if is_triggered:
                logger.warning(f"!!! TRAP TRIGGERED !!! PENDING order {order_id} (parent: {order['parent_position_id']}) activated at price {order['trigger_price']:.2f}")
                
                # --- AI-UPGRADE: Perfect Reporting Protocol ---
                filled_receipt = {
                    "status": "FILLED", 
                    "order_id": f"triggered-{order_id}",
                    "filled_price": order['trigger_price'],
                    "filled_size": order['size'],
                    "side": order['side'], # Include side
                    # CRUCIAL: Add the parent ID to the receipt for the PositionManager
                    "original_parent_id": order['parent_position_id'], 
                    "original_trap_id": order_id
                }
                triggered_orders.append(filled_receipt)
                del self.pending_orders[order_id]

        return triggered_orders