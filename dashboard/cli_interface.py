# F:\ShadowVanguard_Legion_Godspeed\dashboard\cli_interface.py
# Version 7.0 - Prometheus, The Oracle's Herald

import logging
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich.text import Text

# [PACT KEPT]: All imports from your v6.0 are 100% PRESERVED.
from core.data_models import (
    MarketDataFrame, StructureReport, PowerReport, EmotionReport, 
    TacticalSignal, PositionV2, FibonacciReport, DivergenceReport,
    OrderBlockReport, LiquidityReport
)
from core.market_enums import TacticalDecision, PositionSide
from risk_manager.capital_allocator import CapitalAllocator

logger = logging.getLogger("CliInterface")

class CliInterface:
    """
    THE ORACLE'S HERALD: The final, perfected version of the War Room. This Herald
    no longer speaks of the obsolete 'NetForce'. It now announces the Oracle's final,
    synthesized judgment ('TrueNetForce') and displays all critical counter-intelligence
    signals. The communication from the battlefield to the Commander is now pure,
    unambiguous, and complete. The final protocol mismatch is resolved.
    """
    def __init__(self):
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        self.console = Console()
        logger.info("[CliInterface] The Oracle's Herald v7.0 is ready.")

    def display_welcome_message(self):
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        panel = Panel(Text("ShadowVanguard: The Legion is Awake.\nAwaiting command...", justify="center", style="bold cyan"),
            title="Operation Command", border_style="bold magenta")
        self.console.print(panel)
        
    def get_confirmation(self, message: str) -> bool:
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        panel = Panel(Text(f"{message}\nType 'y' to confirm or 'n' to abort.", justify="center"), border_style="yellow")
        self.console.print(panel)
        choice = self.console.input("> ").lower()
        return choice == 'y'

    def display_full_dashboard(
            self,
            mdf: MarketDataFrame,
            structure_report: Optional[StructureReport], power_report: Optional[PowerReport],
            emotion_report: Optional[EmotionReport], ob_report: Optional[OrderBlockReport],
            liq_report: Optional[LiquidityReport], fib_report: Optional[FibonacciReport],
            div_report: Optional[DivergenceReport], final_decision: TacticalDecision,
            signal: Optional[TacticalSignal], active_positions: List[PositionV2],
            capital_allocator: CapitalAllocator, strategic_map: Optional[Dict[str, Any]] = None):
        # [PACT KEPT]: This entire method is PRESERVED exactly as submitted in v6.0.
        # The change is ONLY in the sub-method it calls (_create_power_panel).
        layout = Layout(name="root"); layout.split(Layout(name="header", size=3), Layout(ratio=1, name="main"))
        layout["main"].split_row(Layout(name="left_intel", ratio=4), Layout(name="operations", ratio=3))
        operations_column = Layout(name="operations_column"); operations_column.split(
            self._create_positions_panel(active_positions), self._create_decision_panel(final_decision, signal),
            self._create_strategic_map_panel(strategic_map))
        layout["operations"].update(operations_column)
        if active_positions: avg_pnl_percent = sum(p.pnl_percentage for p in active_positions)/len(active_positions); pnl_text = f"Avg PnL: {avg_pnl_percent:+.2f}%"
        else: pnl_text = "Avg PnL: N/A"
        header_text=f"[bold]SHADOWVANGUARD LEGION - WAR ROOM[/bold]|Capital: ${capital_allocator.current_capital:,.2f}|{pnl_text}"
        layout["header"].update(Align.center(header_text, vertical="middle"))
        left_intel_column = Layout(name="left_intel_column"); left_intel_column.split(
            self._create_market_overview_panel(mdf, structure_report),
            self._create_power_panel(power_report), # This now calls the modernized version.
            self._create_intel_reports_panel(ob_report, liq_report, fib_report, div_report, emotion_report))
        layout["left_intel"].update(left_intel_column)
        self.console.clear(); self.console.print(layout)
    
    def display_final_report(self, capital_allocator: CapitalAllocator):
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        final_capital=capital_allocator.current_capital; initial_capital=capital_allocator.initial_capital
        pnl=final_capital-initial_capital; pnl_percent=(pnl/initial_capital)*100 if initial_capital > 0 else 0
        color="green" if pnl>=0 else "red"
        report_table=Table(title="[bold]Campaign Debriefing[/bold]",show_header=False,box=None)
        report_table.add_column(style="bold cyan"); report_table.add_column()
        report_table.add_row("Initial Capital:",f"${initial_capital:,.2f}")
        report_table.add_row("Final Capital:",f"[bold {color}]${final_capital:,.2f}[/bold {color}]")
        report_table.add_row("Total PnL:",f"[{color}]${pnl:,.2f} ({pnl_percent:+.2f}%)[/{color}]")
        self.console.print(Panel(report_table, border_style="bold blue", title="--- FINAL CAMPAIGN REPORT ---"))

    def _create_strategic_map_panel(self, strategic_map: Optional[Dict[str, Any]]) -> Panel:
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        if not strategic_map: return Panel(Align.center("[dim]Strategic Map Unavailable[/dim]"), title="[7] Alexandria Library", border_style="dim")
        text=Text(); ob_map=strategic_map.get('order_blocks',{}); total_obs=sum(len(v) for v in ob_map.values())
        liq_map=strategic_map.get('liquidity_voids',{}); total_liqs=sum(len(v) for v in liq_map.values())
        text.append(f"Historical Fortresses (OBs): [bold yellow]{total_obs}[/bold yellow]\n", style="white")
        text.append(f"Historical Vacuums (Voids): [bold cyan]{total_liqs}[/bold cyan]", style="white")
        return Panel(text, title="[7] Alexandria Library", border_style="bold yellow")

    def _create_market_overview_panel(self, mdf: MarketDataFrame, structure: Optional[StructureReport]) -> Panel:
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        structure=structure or StructureReport()
        grid=Table.grid(expand=True,padding=(0,1)); grid.add_column(justify="left",style="bold",ratio=1); grid.add_column(justify="right",ratio=1)
        price_data = mdf.ohlcv_multidim.get('5m'); price = price_data['close'].iloc[-1] if price_data is not None and not price_data.empty else 'N/A'
        price_text = f"{price:,.2f}" if isinstance(price, (int, float)) else price
        trend_color="green" if structure.primary_trend.get('1h')=='LONG' else "red" if structure.primary_trend.get('1h')=='SHORT' else "yellow"
        grid.add_row("Symbol:",f"[bold white]{getattr(mdf,'symbol','N/A')}[/bold white]")
        grid.add_row("Price:",f"[bold cyan]{price_text}[/bold cyan]")
        grid.add_row("1h Trend:",f"[{trend_color}]{structure.primary_trend.get('1h','N/A')}[/{trend_color}]")
        grid.add_row("Personality:",f"[yellow]{getattr(structure.market_personality,'name','UNCERTAIN')} ({structure.personality_certainty:.2f})[/yellow]")
        return Panel(grid, title="[1] Market Overview", border_style="cyan")
        
    def _create_power_panel(self, power: Optional[PowerReport]) -> Panel:
        # --- [THE FINAL MODERNIZATION]: The Power Panel is rebuilt to speak the Oracle's true language. ---
        power = power or PowerReport()
        grid = Table.grid(expand=True, padding=(0,1))
        grid.add_column(justify="left", style="bold", ratio=2)
        grid.add_column(justify="right", ratio=3)
        
        # 1. Display the final judgment: TrueNetForce
        force_color = "green" if power.true_net_force > 0 else "red" if power.true_net_force < 0 else "dim"
        grid.add_row("Oracle's Judgment:", f"[{force_color}]{power.true_net_force:,.2f}[/{force_color}]")

        # 2. Display the raw evidence for the Commander's review
        imbalance_str = f"{power.book_imbalance:+.2f}"
        tape_str = f"{power.delta_joiners:+.2f}"
        evidence_text = Text.assemble(("Book Intent: ", "dim"), (imbalance_str, "white"), (" | Tape Action: ", "dim"), (tape_str, "white"))
        grid.add_row("Evidence:", evidence_text)
        
        # 3. Display critical counter-intelligence alerts
        absorption = power.absorption_signal
        if absorption != "NONE":
            absorb_color = "bold green" if "BULLISH" in absorption else "bold red"
            grid.add_row("Counter-Intel:", f"[{absorb_color}]{absorption} ABSORPTION DETECTED[/{absorb_color}]")
        
        return Panel(grid, title="[3] Oracle's Insight", border_style="magenta")

    def _create_intel_reports_panel(
        self, ob: Optional[OrderBlockReport], liq: Optional[LiquidityReport], 
        fib: Optional[FibonacciReport], div: Optional[DivergenceReport], emo: Optional[EmotionReport]
    ) -> Panel:
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        emo = emo or EmotionReport(); grid = Table.grid(expand=True,padding=(0,1))
        grid.add_column(justify="left",style="bold",ratio=2); grid.add_column(justify="right",ratio=1)
        ob_signals=sum(len(v) for v in ob.interaction_signals.values()) if ob else 0
        liq_signals=sum(len(v) for v in liq.confirmation_signals.values()) if liq else 0
        fib_signals=sum(len(v) for v in fib.confirmation_signals.values()) if fib else 0
        div_signals=sum(len(v) for v in div.confirmation_signals.values()) if div else 0
        grid.add_row("Emotion:",f"[bold magenta]{emo.dominant_mood}[/bold magenta]")
        grid.add_row("Sonar Pings (OB):",f"[bold yellow]{ob_signals}[/bold yellow]" if ob_signals else "[dim]None[/dim]")
        grid.add_row("Void Reactions (FVG):",f"[bold cyan]{liq_signals}[/bold cyan]" if liq_signals else "[dim]None[/dim]")
        grid.add_row("Sniper Shots (Fib):",f"[bold green]{fib_signals}[/bold green]" if fib_signals else "[dim]None[/dim]")
        grid.add_row("Confessions (Div):",f"[bold red]{div_signals}[/bold red]" if div_signals else "[dim]None[/dim]")
        return Panel(grid, title="[4] Intel Signals", border_style="yellow")

    def _create_decision_panel(self, decision: TacticalDecision, signal: Optional[TacticalSignal]) -> Panel:
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        grid=Table.grid(expand=True,padding=(0,1)); grid.add_column(justify="center"); decision_color="bold yellow"
        if signal:
            if decision in [TacticalDecision.ADVANCE,TacticalDecision.SCALE_IN]: decision_color="bold green"
            elif decision in [TacticalDecision.RETREAT,TacticalDecision.FLIP_POSITION]: decision_color="bold red"
            grid.add_row(f"[{decision_color}]>>> {decision.name} <<<[/{decision_color}]", style="bold"); grid.add_row(f"Confidence: [bold]{signal.confidence:.2%}[/bold]", style="white"); grid.add_row(f"Source: [dim]{signal.source}[/dim]")
        else:
            decision_text = decision.name; grid.add_row(f"[{decision_color}]{decision_text}[/{decision_color}]")
            if decision == TacticalDecision.WAIT: grid.add_row("[dim]Awaiting tactical opportunity...[/dim]")
            else: grid.add_row("[dim]Holding position...[/dim]")
        return Panel(grid, title="[5] Tactical Command", border_style="green")
        
    def _create_positions_panel(self, positions: List[PositionV2]) -> Panel:
        # [PACT KEPT]: This method is PRESERVED exactly as submitted in v6.0.
        if not positions: return Panel(Align.center("[dim]No Active Positions[/dim]"), title="[6] Active Positions", border_style="blue")
        table = Table(show_header=True, header_style="bold blue", padding=(0,1))
        table.add_column("ID",justify="left",style="dim"); table.add_column("Side",justify="center"); table.add_column("Size",justify="right")
        table.add_column("Entry Price",justify="right"); table.add_column("PnL %",justify="right",style="bold");
        table.add_column("Cat. SL",justify="right",style="bold red"); table.add_column("Hedge Trap",justify="center",style="dim")
        for pos in positions:
            pnl_color="green" if pos.pnl_percentage >= 0 else "red"; side_color="green" if pos.side==PositionSide.LONG else "red"
            trap_status="Armed" if pos.hedge_trap and pos.hedge_trap.status=="ACTIVE" else "---"
            cat_sl_str=f"{pos.catastrophic_stop_loss:,.2f}" if pos.catastrophic_stop_loss else "N/A"
            table.add_row(pos.position_id[:8],f"[{side_color}]{pos.side.name}[/{side_color}]", f"{pos.size:.4f}", f"{pos.entry_price:,.2f}", 
                f"[{pnl_color}]{pos.pnl_percentage:+.2f}%[/{pnl_color}]", cat_sl_str, trap_status)
        return Panel(table, title="[6] Active Positions", border_style="blue")