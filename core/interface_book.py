# F:\ShadowVanguard_Legion_Godspeed\core\interface_book.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from .data_models import MarketDataFrame

class IDataProvider(ABC):
    @abstractmethod
    def fetch_next_market_data(self) -> Optional[MarketDataFrame]:
        """Fetches the next available market data tick."""
        pass
    
    @abstractmethod
    def has_more_data(self) -> bool:
        """Returns True if there is more data to process."""
        pass

class IOrderExecutor(ABC):
    @abstractmethod
    def place_order(self, symbol: str, side: Any, size: float, order_type: str, current_price: float, trigger_price: Optional[float] = None, parent_position_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Places a new order on the exchange."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancels an existing order."""
        pass
        
    @abstractmethod
    def close_order(self, order_id: str, size: float, symbol: str, price: float) -> Optional[Dict[str, Any]]:
        """Closes an existing order (often a market order)."""

    @abstractmethod
    def check_triggered_stops(self, current_high: float, current_low: float) -> List[Dict[str, Any]]:
        """Checks if any pending stop orders have been triggered."""
        pass