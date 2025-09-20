# F:\ShadowVanguard_Legion_Godspeed\execution_engine\position_manager.py
# Version 14.2 - Prometheus, The Synchronized Scribe

import logging
from typing import Dict, Optional, List, Any, Callable
from uuid import uuid4
from datetime import datetime
from dataclasses import asdict

# [PACT KEPT]: All imports are preserved exactly from your v14.1.
from core.data_models import (PositionV2 as Position, TacticalSignal, MarketDataFrame, 
                              Experience, HedgeTrap, PositionV2, OrderBlockReport)
from core.market_enums import TacticalDecision, PositionSide, MarketRegime
from risk_manager.capital_allocator import CapitalAllocator
from risk_manager.perimeter_architect import PerimeterArchitect, BattlePerimeters 
from memory.experience_memory import ExperienceMemory
from .order_executor import IOrderExecutor 

logger = logging.getLogger("PositionManager")

class PositionManager:
    """
    THE SYNCHRONIZED SCRIBE: This version completes the final protocol synchronization for
    the entire Legion. The Scribe's Alchemist's Lasso logic is now updated to read
    the modern `true_net_force` from the PowerReport. This was the final communication
    mismatch. With this fix, a strike command can be fully received, architected,
    and executed with a fully armed counter-attack plan. The entire command chain,
    from intel to execution, is now perfectly unified.
    """
    def __init__(self, 
                 order_executor: IOrderExecutor, 
                 capital_allocator: CapitalAllocator, 
                 perimeter_architect: PerimeterArchitect,
                 memory: ExperienceMemory,
                 config: Dict[str, Any],
                 on_position_closed_callback: Optional[Callable[[PositionV2], None]] = None
                 ):
        
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v14.1.
        self.ee_config = config.get('execution_engine', {})
        self.lasso_config = self.ee_config.get('alchemist_lasso', {})
        self.max_flips_allowed = self.lasso_config.get('max_flips_allowed', 1)
        self.active_positions: Dict[str, PositionV2] = {} 
        self.order_executor = order_executor
        self.capital_allocator = capital_allocator
        self.perimeter_architect = perimeter_architect
        self.memory = memory
        self.leverage = self.ee_config.get('leverage', 1)
        self.on_position_closed_callback = on_position_closed_callback
        # Correctly get the tactical timeframe from the main config structure
        self.tactical_tf = config.get('data_provider', {}).get('timeframe_minutes', 5)
        self.tactical_tf_str = f"{self.tactical_tf}m"
        logger.info(f"[PositionManager] The Synchronized Scribe v14.2 is online. All communications are standard.")
    
    def _calculate_intelligent_flip_size(self, original_size: float, mdf: MarketDataFrame) -> float:
        # [PROTOCOL SYNCHRONIZATION]: The Alchemist's brain is updated to read the modern Oracle's judgment.
        multiplier = self.lasso_config.get('flip_size_multiplier', 1.5)
        
        # Reads the correct, modern `true_net_force` attribute.
        true_net_force = mdf.power_report.true_net_force if mdf.power_report else 0
        
        threshold = self.lasso_config.get('full_power_flip_threshold', 500.0)
        
        if abs(true_net_force) >= threshold:
            multiplier = 2.0
            logger.info(f"Full-power flip justified. TrueNetForce ({abs(true_net_force):.2f}) exceeds threshold ({threshold}).")
        else:
            logger.warning(f"Conservative flip. TrueNetForce ({abs(true_net_force):.2f}) below threshold. Using multiplier {multiplier}.")
        return original_size * multiplier

    def _execute_hedge_trap(self, position: PositionV2, mdf: MarketDataFrame):
        # [PACT KEPT]: This method is PRESERVED.
        if not position.catastrophic_stop_loss: return
        trigger_price=position.catastrophic_stop_loss; flip_side=PositionSide.SHORT if position.side==PositionSide.LONG else PositionSide.LONG
        flip_size=self._calculate_intelligent_flip_size(position.size, mdf)
        hedge_order_result = self.order_executor.place_order(symbol=position.symbol, side=flip_side, size=flip_size, order_type='STOP_MARKET', trigger_price=trigger_price, parent_position_id=position.position_id)
        if hedge_order_result and hedge_order_result.get("order_id"):
            trap_id = hedge_order_result["order_id"]
            position.hedge_trap=HedgeTrap(order_id=trap_id, trigger_price=trigger_price, size=flip_size, side=flip_side)
            logger.info(f"ALCHEMIST'S Hedge Trap SET for {position.position_id}: Size {flip_size:.4f} at Cat SL {trigger_price:.2f}")
        else: 
            logger.error(f"Failed to set ALCHEMIST'S hedge trap for position {position.position_id}!")
    
    def _execute_new_entry(self, symbol: str, signal: TacticalSignal, mdf: MarketDataFrame):
        # [PACT KEPT]: The protocol for birthing a new soldier is PRESERVED.
        tactical_df = mdf.ohlcv_multidim.get(self.tactical_tf_str)
        if tactical_df is None or tactical_df.empty:
            logger.error("Cannot execute new entry: Tactical OHLCV data is missing."); return
        current_price = tactical_df['close'].iloc[-1]; side = signal.details.get('side', PositionSide.LONG)

        battle_plan = self.perimeter_architect.determine_battle_perimeters(side=side, entry_price=current_price, mdf=mdf)
        if not battle_plan: 
            logger.error("Battle plan could not be architected. Entry aborted."); return

        management_sl, catastrophic_sl, take_profit_levels = (
            battle_plan.management_sl, battle_plan.catastrophic_sl, battle_plan.take_profit_levels)
        
        ticket = self.capital_allocator.request_allocation(signal, catastrophic_sl, current_price)
        if not ticket: logger.warning(f"Allocation denied for {symbol}."); return

        position_size = ticket.allocated_amount / current_price if current_price > 0 else 0
        order_result = self.order_executor.place_order(symbol, side, position_size, 'MARKET', current_price=current_price)
        
        if order_result and order_result.get("status") == "FILLED":
            pos_id = order_result["order_id"]
            initial_intent = mdf.structure_report.market_regime.get(self.tactical_tf_str) if mdf.structure_report and mdf.structure_report.market_regime else MarketRegime.UNCERTAIN
            
            new_position = PositionV2(
                position_id=pos_id, symbol=symbol, side=side, entry_price=order_result["filled_price"],
                size=order_result["filled_size"], management_stop_loss=management_sl, 
                catastrophic_stop_loss=catastrophic_sl, take_profit_levels=take_profit_levels,
                leverage=self.leverage, strategic_intent=initial_intent, timestamp=datetime.utcnow(), flip_count=0)
            
            self._execute_hedge_trap(new_position, mdf) 
            self.active_positions[pos_id] = new_position
            self.capital_allocator.confirm_and_link_ticket(ticket.ticket_id, new_position)
            logger.info(f"ADVANCE EXECUTED: Pos {pos_id} born ({side.name}) with intent '{initial_intent.name if initial_intent else 'N/A'}' and a full battle plan.")
        else:
             self.capital_allocator.release_capital_by_ticket_id(ticket.ticket_id)
             
    def _create_and_fully_onboard_new_position(self, pos_id: str, symbol: str, side: PositionSide, entry_price: float, size: float, mdf: MarketDataFrame, parent_flip_count: int, is_untracked: bool = False) -> Optional[PositionV2]:
        # [PACT KEPT]: The protocol for onboarding a flipped soldier is PRESERVED.
        tactical_df = mdf.ohlcv_multidim.get(self.tactical_tf_str)
        if tactical_df is None or tactical_df.empty:
            logger.error("Cannot onboard new position: Tactical OHLCV data is missing."); self.order_executor.close_order(pos_id, size, symbol, entry_price); return None
            
        final_intent = mdf.structure_report.market_regime.get(self.tactical_tf_str) if mdf.structure_report and mdf.structure_report.market_regime else MarketRegime.UNCERTAIN
        battle_plan = self.perimeter_architect.determine_battle_perimeters(side=side, entry_price=entry_price, mdf=mdf)
            
        if not battle_plan:
            logger.error(f"FATAL: Could not architect plan for flipped pos {pos_id}. Closing immediately."); self.order_executor.close_order(pos_id, size, symbol, entry_price); return None

        new_mgmt_sl, new_cat_sl, new_tp_levels = (
            battle_plan.management_sl, battle_plan.catastrophic_sl, battle_plan.take_profit_levels)

        new_flip_count = parent_flip_count + 1
        new_position = PositionV2(
            position_id=pos_id, symbol=symbol, side=side, entry_price=entry_price, size=size, timestamp=datetime.utcnow(), 
            is_untracked=is_untracked, leverage=self.leverage, strategic_intent=final_intent,
            management_stop_loss=new_mgmt_sl, catastrophic_stop_loss=new_cat_sl,
            take_profit_levels=new_tp_levels, flip_count=new_flip_count)
            
        allocation_signal = TacticalSignal(source="FLIP_CREATION", confidence=1.0, suggestion=TacticalDecision.FLIP_POSITION)
        ticket = self.capital_allocator.request_allocation(allocation_signal, new_cat_sl, entry_price)
        if not ticket:
             logger.error(f"FATAL: Capital denied for flipped pos {pos_id}. Closing immediately."); self.order_executor.close_order(pos_id, size, symbol, entry_price); return None
             
        self.capital_allocator.confirm_and_link_ticket(ticket.ticket_id, new_position)
        self._execute_hedge_trap(new_position, mdf)
        self.active_positions[pos_id] = new_position
        logger.info(f"AWARE ONBOARDING COMPLETE: Flipped pos {pos_id} ready with new battle plan and flip count {new_flip_count}.")
        return new_position

    # [PACT KEPT]: The rest of the file is PRESERVED.
    def _execute_flip(self, position_to_flip: PositionV2, mdf: MarketDataFrame):
        tactical_df = mdf.ohlcv_multidim.get(self.tactical_tf_str)
        if tactical_df is None or tactical_df.empty: logger.error("Cannot execute flip: Tactical OHLCV data is missing."); return
        logger.warning(f"Executing MANUAL ALCHEMIST'S FLIP from {position_to_flip.side.name} for pos {position_to_flip.position_id}")
        self._cancel_hedge_trap(position_to_flip); current_price = tactical_df['close'].iloc[-1]
        flip_side = PositionSide.SHORT if position_to_flip.side == PositionSide.LONG else PositionSide.LONG
        flip_size=self._calculate_intelligent_flip_size(position_to_flip.size, mdf)
        flip_order_result = self.order_executor.place_order(position_to_flip.symbol, flip_side, flip_size, 'MARKET', current_price=current_price)
        if flip_order_result and flip_order_result.get("status") == "FILLED":
            old_pos_id=position_to_flip.position_id; new_pos_id=flip_order_result["order_id"]; filled_price=flip_order_result["filled_price"]
            logger.info(f"FLIP successful: Pos {old_pos_id} -> {new_pos_id} at {filled_price:.2f}.")
            new_size = flip_order_result["filled_size"] - position_to_flip.size
            if new_size < 1e-8: self._execute_full_close(position_to_flip, mdf, is_part_of_flip=False, exit_price_override=filled_price); return
            self._execute_full_close(position_to_flip, mdf, is_part_of_flip=True, exit_price_override=filled_price)
            self._create_and_fully_onboard_new_position(
                pos_id=new_pos_id, symbol=position_to_flip.symbol, side=flip_side, entry_price=filled_price, 
                size=new_size, mdf=mdf, parent_flip_count=position_to_flip.flip_count, is_untracked=True
            )
        else: logger.error(f"Manual ALCHEMIST'S flip FAILED for {position_to_flip.position_id}."); self._execute_hedge_trap(position_to_flip, mdf)

    def handle_triggered_traps(self, triggered_traps: List[Dict], mdf: MarketDataFrame):
        for fill_receipt in triggered_traps:
            parent_id = fill_receipt.get("original_parent_id"); original_position = self.active_positions.get(parent_id)
            if not original_position: logger.error(f"CRITICAL: Trap for {parent_id} triggered, but position not found!"); continue
            
            intent_at_birth = original_position.strategic_intent
            is_trend_mission = intent_at_birth in [MarketRegime.BULL_TREND, MarketRegime.BEAR_TREND]
            filled_price = fill_receipt['filled_price']

            if is_trend_mission and original_position.flip_count < self.max_flips_allowed:
                logger.critical(f"!!! ALCHEMIST'S COUNTER-ATTACK (INTENT: TREND) !!! Trap for pos {original_position.position_id} triggered! Flip #{original_position.flip_count + 1} initiated.")
                new_pos_id=fill_receipt["order_id"]; new_pos_size=fill_receipt["filled_size"]-original_position.size; flip_side=PositionSide(fill_receipt["side"])
                self._execute_full_close(original_position, mdf, is_part_of_flip=True, exit_price_override=filled_price)
                self._create_and_fully_onboard_new_position(
                    pos_id=new_pos_id, symbol=original_position.symbol, side=flip_side, entry_price=filled_price, 
                    size=new_pos_size, mdf=mdf, parent_flip_count=original_position.flip_count, is_untracked=True)
            else:
                retreat_reason = f"Flip limit of {self.max_flips_allowed} reached" if is_trend_mission else "INTENT: RANGE/UNCERTAIN"
                logger.warning(f"FORCED STRATEGIC RETREAT ({retreat_reason}): Cat SL for pos {original_position.position_id} hit. Closing, NOT flipping.")
                self._execute_full_close(original_position, mdf, is_part_of_flip=False, exit_price_override=filled_price)

    def execute_tactical_decision(self, decision: TacticalDecision, signal: TacticalSignal, mdf: MarketDataFrame):
        symbol=signal.details.get('symbol',mdf.symbol); active_position=self.get_active_position_for_symbol(symbol)
        if not active_position:
            if decision==TacticalDecision.ADVANCE: self._execute_new_entry(symbol, signal, mdf)
        else:
            if signal.details.get("position_id") and signal.details["position_id"] != active_position.position_id: return
            if decision==TacticalDecision.FLIP_POSITION: self._execute_flip(active_position, mdf)
            elif decision==TacticalDecision.RETREAT: self._execute_full_close(active_position, mdf)
            elif decision==TacticalDecision.SCALE_IN: self._execute_scale_in(active_position, signal, mdf)
            elif decision==TacticalDecision.PARTIAL_EXIT: self._execute_partial_exit(active_position, signal, mdf)

    def _cancel_hedge_trap(self, position: PositionV2):
        if position.hedge_trap and position.hedge_trap.status == "ACTIVE":
            if self.order_executor.cancel_order(position.hedge_trap.order_id): position.hedge_trap.status = "CANCELLED"
            else: logger.error(f"Failed to cancel hedge trap order {position.hedge_trap.order_id}.")
            
    def _execute_scale_in(self, position: PositionV2, signal: TacticalSignal, mdf: MarketDataFrame):
        tactical_df = mdf.ohlcv_multidim.get(self.tactical_tf_str)
        if tactical_df is None or tactical_df.empty: logger.error("Cannot execute scale-in."); return
        logger.info(f"Executing SCALE-IN for position {position.position_id}"); scale_ratio=signal.details.get('scale_in_ratio', 0.5)
        if not (0<scale_ratio<=2.0): return
        additional_size=position.size*scale_ratio; current_price=tactical_df['close'].iloc[-1]; self._cancel_hedge_trap(position)
        allocation_signal = TacticalSignal(source="SCALE_IN_REINFORCEMENT", confidence=signal.confidence, suggestion=TacticalDecision.SCALE_IN)
        if position.catastrophic_stop_loss is None: self._execute_hedge_trap(position, mdf); return
        ticket=self.capital_allocator.request_allocation(allocation_signal,position.catastrophic_stop_loss,current_price)
        if not ticket: self._execute_hedge_trap(position, mdf); return
        order_result=self.order_executor.place_order(position.symbol, position.side, additional_size, 'MARKET', current_price=current_price)
        if order_result and order_result.get("status") == "FILLED":
            filled_size=order_result["filled_size"]; filled_price=order_result["filled_price"]; new_total_size=position.size+filled_size
            new_avg_price=((position.size*position.entry_price)+(filled_size*filled_price))/new_total_size
            position.entry_price, position.size = new_avg_price, new_total_size
            battle_plan=self.perimeter_architect.determine_battle_perimeters(side=position.side, entry_price=new_avg_price, mdf=mdf)
            if battle_plan:
                position.management_stop_loss, position.catastrophic_stop_loss, position.take_profit_levels = (
                    battle_plan.management_sl, battle_plan.catastrophic_sl, battle_plan.take_profit_levels)
            self._execute_hedge_trap(position,mdf); self.capital_allocator.confirm_and_link_ticket(ticket.ticket_id, position)
        else: self.capital_allocator.release_capital_by_ticket_id(ticket.ticket_id); self._execute_hedge_trap(position,mdf)

    def _execute_full_close(self, position_to_close: PositionV2, mdf: MarketDataFrame, is_part_of_flip: bool = False, exit_price_override: Optional[float] = None):
        tactical_df=mdf.ohlcv_multidim.get(self.tactical_tf_str)
        exit_price = exit_price_override if exit_price_override is not None else (tactical_df['close'].iloc[-1] if tactical_df is not None and not tactical_df.empty else position_to_close.entry_price)
        if not is_part_of_flip: self._cancel_hedge_trap(position_to_close)
        order_success=True
        if not is_part_of_flip:
            close_order_result=self.order_executor.close_order(position_to_close.position_id,position_to_close.size,position_to_close.symbol,exit_price)
            order_success=close_order_result and close_order_result.get("status") == "FILLED"
            if order_success: exit_price=close_order_result.get("filled_price", exit_price)
        position_to_close.exit_price=exit_price; position_to_close.exit_timestamp = datetime.utcnow()
        self.update_single_position_pnl(position_to_close, exit_price)
        if order_success and position_to_close.position_id in self.active_positions:
            closed_pos=self.active_positions.pop(position_to_close.position_id)
            closed_pos.status="CLOSED"; self.capital_allocator.release_capital(closed_pos)
            log_prefix="FLIP-TRANSITION" if is_part_of_flip else "RETREAT EXECUTED"
            logger.info(f"{log_prefix}: Pos {closed_pos.position_id} closed. PnL: ${closed_pos.pnl_in_dollars:.2f} ({closed_pos.pnl_percentage:+.2f}%) @ {closed_pos.exit_price:.2f}")
            self.memory.remember(Experience(state={'power':asdict(mdf.power_report), 'emotion':asdict(mdf.emotion_report), 'structure':asdict(mdf.structure_report)}, action=TacticalDecision.FLIP_POSITION if is_part_of_flip else TacticalDecision.RETREAT, outcome=closed_pos.pnl_percentage/100.0, position_details=asdict(closed_pos)))
            if self.on_position_closed_callback:
                try: self.on_position_closed_callback(PositionV2(**asdict(closed_pos)))
                except Exception as e: logger.error(f"Failed to submit performance report for Pos {closed_pos.position_id}: {e}")

    def _execute_partial_exit(self, position: PositionV2, signal: TacticalSignal, mdf: MarketDataFrame):
        tactical_df=mdf.ohlcv_multidim.get(self.tactical_tf_str)
        if tactical_df is None or tactical_df.empty: logger.error("Cannot execute partial exit."); return
        exit_ratio = signal.details.get('exit_ratio', 0.5); logger.info(f"Executing PARTIAL-EXIT of {exit_ratio*100:.0f}% for position {position.position_id}")
        if not (0<exit_ratio<1.0): return
        exit_size=position.size*exit_ratio; current_price=tactical_df['close'].iloc[-1]; self._cancel_hedge_trap(position)
        exit_side=PositionSide.SHORT if position.side==PositionSide.LONG else PositionSide.LONG
        order_result=self.order_executor.place_order(position.symbol, exit_side, exit_size, 'MARKET', current_price=current_price)
        if order_result and order_result.get("status") == "FILLED":
            filled_price=order_result["filled_price"]; realized_pnl=(filled_price-position.entry_price)*exit_size*(position.leverage or 1)
            cost_basis_of_exit=exit_size*position.entry_price; self.capital_allocator.release_partial_capital(position.position_id,cost_basis_of_exit,realized_pnl)
            remaining_size=position.size - order_result["filled_size"]
            MINIMUM_VIABLE_SIZE=1e-8
            if remaining_size < MINIMUM_VIABLE_SIZE: self._execute_full_close(position,mdf,is_part_of_flip=False,exit_price_override=filled_price); return
            position.size=remaining_size; self._execute_hedge_trap(position, mdf)
        else: self._execute_hedge_trap(position,mdf)
        
    def update_all_positions_pnl(self, current_price: float):
        for pos in list(self.active_positions.values()): self.update_single_position_pnl(pos, current_price)
    def update_single_position_pnl(self, position: PositionV2, current_price: float):
        if position.entry_price == 0: return
        pnl_ratio_raw = (current_price / position.entry_price)-1 if position.side==PositionSide.LONG else (position.entry_price / current_price)-1
        leverage=position.leverage or 1; pnl_ratio_leveraged=pnl_ratio_raw*leverage
        position.pnl_percentage=pnl_ratio_leveraged*100; position.pnl_in_dollars=(position.size*position.entry_price)*pnl_ratio_leveraged
    def get_all_positions(self) -> List[PositionV2]: return list(self.active_positions.values())
    def get_active_position_for_symbol(self, symbol: str) -> Optional[PositionV2]: return next((pos for pos in self.active_positions.values() if pos.symbol == symbol), None)