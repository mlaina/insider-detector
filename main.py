#!/usr/bin/env python3
"""
Insider Trading Detector — Detecta actividad inusual en call options.

Uso:
  python main.py                    # Escaneo único de todas las listas
  python main.py --list tech        # Solo una lista
  python main.py --tickers AAPL TSLA  # Tickers específicos
  python main.py --watch            # Monitoreo continuo
  python main.py --threshold 60     # Cambiar umbral de alerta
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

import config
from scanner import scan_tickers

console = Console()
WATCHLIST_PATH = Path(__file__).parent / "watchlist.json"


def load_watchlist() -> dict:
    with open(WATCHLIST_PATH) as f:
        return json.load(f)


def resolve_tickers(args) -> list[str]:
    """Resuelve la lista de tickers según los argumentos."""
    if args.tickers:
        return [t.upper() for t in args.tickers]

    watchlist = load_watchlist()
    lists = watchlist.get("lists", {})

    if args.list:
        if args.list not in lists:
            console.print(f"[red]Lista '{args.list}' no encontrada. Disponibles: {', '.join(lists.keys())}[/red]")
            sys.exit(1)
        return lists[args.list]

    # Todas las listas
    all_tickers = []
    for tickers in lists.values():
        all_tickers.extend(t for t in tickers if t not in all_tickers)
    return all_tickers


def display_alerts(df, scan_time: str):
    """Muestra las alertas en una tabla rich."""
    if df.empty:
        console.print(Panel(
            "[yellow]No se detectó actividad inusual en este escaneo.[/yellow]",
            title=f"Scan {scan_time}",
        ))
        return

    # Resumen
    high = len(df[df["score"] >= 75])
    medium = len(df[(df["score"] >= 50) & (df["score"] < 75)])

    header = Text()
    header.append(f"  {len(df)} alertas", style="bold")
    header.append(f"  |  ", style="dim")
    header.append(f"🔴 {high} alta", style="bold red")
    header.append(f"  ", style="dim")
    header.append(f"🟡 {medium} media", style="bold yellow")

    console.print(Panel(header, title=f"Scan {scan_time}", border_style="green"))

    table = Table(show_header=True, header_style="bold cyan", show_lines=False)
    table.add_column("Score", justify="right", width=6)
    table.add_column("Ticker", width=7)
    table.add_column("Strike", justify="right", width=8)
    table.add_column("Spot", justify="right", width=8)
    table.add_column("OTM%", justify="right", width=6)
    table.add_column("Exp", width=12)
    table.add_column("DTE", justify="right", width=4)
    table.add_column("Vol", justify="right", width=8)
    table.add_column("OI", justify="right", width=8)
    table.add_column("V/OI", justify="right", width=6)
    table.add_column("IV%", justify="right", width=6)
    table.add_column("Notional $", justify="right", width=12)

    for _, row in df.iterrows():
        score = row["score"]
        if score >= 75:
            score_style = "bold red"
        elif score >= 60:
            score_style = "bold yellow"
        else:
            score_style = "white"

        notional = f"${row['notional']:,.0f}"

        table.add_row(
            f"[{score_style}]{score:.0f}[/{score_style}]",
            f"[bold]{row['ticker']}[/bold]",
            f"{row['strike']:.1f}",
            f"{row['spot']:.2f}",
            f"{row['otm_pct']:.1f}%",
            row["expiration"],
            str(row["dte"]),
            f"{row['volume']:,}",
            f"{row['open_interest']:,}",
            f"{row['vol_oi_ratio']:.1f}",
            f"{row['implied_vol']:.0f}%",
            notional,
        )

    console.print(table)

    # Top alertas con contexto
    if high > 0:
        console.print()
        console.print("[bold red]⚠ ALERTAS ALTAS:[/bold red]")
        for _, row in df[df["score"] >= 75].iterrows():
            console.print(
                f"  [bold]{row['ticker']}[/bold] — "
                f"Strike ${row['strike']:.0f} (OTM {row['otm_pct']:.1f}%) exp {row['expiration']} — "
                f"Vol {row['volume']:,} vs OI {row['open_interest']:,} (ratio {row['vol_oi_ratio']:.1f}x) — "
                f"Notional [bold]${row['notional']:,.0f}[/bold]"
            )


def run_scan(tickers: list[str], threshold: int):
    """Ejecuta un escaneo."""
    config.ALERT_THRESHOLD = threshold
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    console.print(f"\n[dim]Escaneando {len(tickers)} tickers: {', '.join(tickers)}...[/dim]")

    df = scan_tickers(tickers)
    display_alerts(df, scan_time)
    return df


def main():
    parser = argparse.ArgumentParser(description="Insider Trading Detector — Opciones Call")
    parser.add_argument("--list", "-l", type=str, help="Nombre de la lista del watchlist (tech, pharma, finance)")
    parser.add_argument("--tickers", "-t", nargs="+", help="Tickers específicos a escanear")
    parser.add_argument("--watch", "-w", action="store_true", help="Monitoreo continuo")
    parser.add_argument("--threshold", type=int, default=50, help="Umbral mínimo de alerta (0-100)")
    parser.add_argument("--interval", type=int, default=config.SCAN_INTERVAL_MINUTES, help="Intervalo de escaneo en minutos (modo watch)")

    args = parser.parse_args()
    tickers = resolve_tickers(args)

    console.print(Panel(
        "[bold]Insider Trading Detector[/bold]\n"
        "Detecta actividad inusual en call options que puede indicar insider trading",
        border_style="blue",
    ))

    if args.watch:
        console.print(f"[green]Modo monitoreo activo — escaneo cada {args.interval} minutos. Ctrl+C para salir.[/green]\n")
        try:
            while True:
                run_scan(tickers, args.threshold)
                console.print(f"\n[dim]Próximo escaneo en {args.interval} minutos...[/dim]")
                time.sleep(args.interval * 60)
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoreo detenido.[/yellow]")
    else:
        run_scan(tickers, args.threshold)


if __name__ == "__main__":
    main()
