#!/usr/bin/env python3
"""
Insider Trading Detector — Web App

Uso:
  python app.py                     # http://localhost:8000
  python app.py --port 3000
"""

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

from scanner import scan_tickers, scan_ticker
from tickers import get_index_tickers, list_indices, INDICES
from context import get_ticker_context, apply_context_penalty
import config

app = FastAPI(title="Insider Trading Detector")

WATCHLIST_PATH = Path(__file__).parent / "watchlist.json"
STATIC_DIR = Path(__file__).parent / "static"
SCANS_DIR = Path(__file__).parent / "scans"


def load_watchlist() -> dict:
    with open(WATCHLIST_PATH) as f:
        return json.load(f)


@app.get("/", response_class=HTMLResponse)
async def index():
    with open(STATIC_DIR / "index.html") as f:
        return f.read()


@app.get("/how-it-works", response_class=HTMLResponse)
async def how_it_works():
    with open(STATIC_DIR / "how-it-works.html") as f:
        return f.read()


@app.get("/api/watchlist")
async def get_watchlist():
    return load_watchlist()


@app.post("/api/watchlist/{list_name}")
async def update_watchlist(list_name: str, tickers: list[str]):
    wl = load_watchlist()
    wl["lists"][list_name] = [t.upper() for t in tickers]
    with open(WATCHLIST_PATH, "w") as f:
        json.dump(wl, f, indent=2)
    return {"ok": True}


@app.delete("/api/watchlist/{list_name}")
async def delete_watchlist(list_name: str):
    wl = load_watchlist()
    wl["lists"].pop(list_name, None)
    with open(WATCHLIST_PATH, "w") as f:
        json.dump(wl, f, indent=2)
    return {"ok": True}


@app.get("/api/indices")
async def get_indices():
    """Devuelve los índices disponibles y su tamaño."""
    return {"indices": list_indices()}


def _source_label(list_name: str | None, tickers_str: str | None, index: str | None) -> str:
    """Genera un label legible para la fuente del escaneo."""
    if tickers_str:
        tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
        return f"custom_{'_'.join(tickers[:5])}" if len(tickers) <= 5 else f"custom_{len(tickers)}_tickers"
    if index:
        return index
    if list_name:
        return f"watchlist_{list_name}"
    return "all_watchlists"


def _save_scan(result: dict, source: str):
    """Guarda el resultado del escaneo en scans/."""
    SCANS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{ts}_{source}.json"
    with open(SCANS_DIR / filename, "w") as f:
        json.dump(result, f, indent=2, default=str)


def _resolve_tickers(list_name: str | None, tickers_str: str | None, index: str | None) -> list[str]:
    """Resuelve la lista de tickers según parámetros."""
    if tickers_str:
        return [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    if index:
        return get_index_tickers(index)
    if list_name:
        wl = load_watchlist()
        return wl["lists"].get(list_name, [])
    # Default: todas las watchlists
    wl = load_watchlist()
    result = []
    for t_list in wl["lists"].values():
        result.extend(t for t in t_list if t not in result)
    return result


async def _enrich_with_context(alerts: list[dict], insights: list[dict]) -> dict:
    """Enriquece alertas e insights con contexto de Reddit/earnings y ajusta scores."""
    # Obtener tickers únicos
    tickers = list({a["ticker"] for a in alerts})

    # Fetch contexto para cada ticker
    context_map = {}
    for ticker in tickers:
        try:
            context_map[ticker] = await get_ticker_context(ticker)
        except Exception:
            context_map[ticker] = {"penalty": 0, "penalty_reasons": [], "adjusted": False, "reddit": {"total_mentions": 0, "hype_level": "none"}, "earnings": {"has_upcoming_earnings": False}}

    # Aplicar penalización a cada alerta
    for a in alerts:
        ctx = context_map.get(a["ticker"], {})
        adj_score, raw_score = apply_context_penalty(a["score"], ctx)
        a["raw_score"] = raw_score
        a["score"] = adj_score
        a["context"] = {
            "penalty": ctx.get("penalty", 0),
            "reasons": ctx.get("penalty_reasons", []),
            "tags": ctx.get("tags", []),
            "reddit_mentions": ctx.get("reddit", {}).get("total_mentions", 0),
            "reddit_hype": ctx.get("reddit", {}).get("hype_level", "none"),
            "has_earnings": ctx.get("earnings", {}).get("has_upcoming_earnings", False),
            "earnings_date": ctx.get("earnings", {}).get("earnings_date"),
            "days_to_earnings": ctx.get("earnings", {}).get("days_to_earnings"),
            "reddit_top_posts": ctx.get("reddit", {}).get("top_posts", []),
        }

    # Recalcular insights con scores ajustados
    for ins in insights:
        ctx = context_map.get(ins["ticker"], {})
        ins["context"] = {
            "penalty": ctx.get("penalty", 0),
            "reasons": ctx.get("penalty_reasons", []),
            "tags": ctx.get("tags", []),
            "reddit_mentions": ctx.get("reddit", {}).get("total_mentions", 0),
            "reddit_hype": ctx.get("reddit", {}).get("hype_level", "none"),
            "reddit_subreddits": ctx.get("reddit", {}).get("subreddit_counts", {}),
            "reddit_top_posts": ctx.get("reddit", {}).get("top_posts", []),
            "has_earnings": ctx.get("earnings", {}).get("has_upcoming_earnings", False),
            "earnings_date": ctx.get("earnings", {}).get("earnings_date"),
            "days_to_earnings": ctx.get("earnings", {}).get("days_to_earnings"),
        }
        # Recalcular max_score del insight
        ticker_alerts = [a for a in alerts if a["ticker"] == ins["ticker"]]
        ins["max_score"] = max((a["score"] for a in ticker_alerts), default=0)
        ins["raw_max_score"] = max((a["raw_score"] for a in ticker_alerts), default=0)

    # Re-sort insights by adjusted score
    insights.sort(key=lambda x: x["max_score"], reverse=True)

    return context_map


@app.get("/api/context/{ticker}")
async def get_context(ticker: str):
    """Obtiene contexto público (Reddit, earnings) para un ticker."""
    ctx = await get_ticker_context(ticker.upper())
    return ctx


@app.get("/api/scan")
async def scan(
    list_name: str = Query(None, alias="list"),
    tickers: str = Query(None),
    index: str = Query(None),
    threshold: int = Query(50),
):
    """Escaneo completo. Para listas grandes usa /api/scan/stream."""
    ticker_list = _resolve_tickers(list_name, tickers, index)
    config.ALERT_THRESHOLD = threshold

    df = scan_tickers(ticker_list)

    alerts = df.to_dict(orient="records") if not df.empty else []

    # Agrupar por ticker para insights
    ticker_groups = {}
    for a in alerts:
        t = a["ticker"]
        if t not in ticker_groups:
            ticker_groups[t] = {"ticker": t, "company": a.get("company", t), "spot": a["spot"], "alerts": [], "max_score": 0, "total_notional": 0}
        ticker_groups[t]["alerts"].append(a)
        ticker_groups[t]["max_score"] = max(ticker_groups[t]["max_score"], a["score"])
        ticker_groups[t]["total_notional"] += a["notional"]

    insights = sorted(ticker_groups.values(), key=lambda x: x["max_score"], reverse=True)

    # Enriquecer con contexto Reddit/earnings
    await _enrich_with_context(alerts, insights)

    source = _source_label(list_name, tickers, index)
    result = {
        "scan_time": datetime.now().isoformat(),
        "source": source,
        "tickers_scanned": len(ticker_list),
        "tickers_with_alerts": len(ticker_groups),
        "threshold": threshold,
        "alerts": alerts,
        "insights": insights,
        "summary": {
            "total": len(alerts),
            "high": len([a for a in alerts if a["score"] >= 75]),
            "medium": len([a for a in alerts if 50 <= a["score"] < 75]),
        },
    }

    _save_scan(result, source)
    return result


@app.get("/api/scan/stream")
async def scan_stream(
    list_name: str = Query(None, alias="list"),
    tickers: str = Query(None),
    index: str = Query(None),
    threshold: int = Query(50),
):
    """Escaneo con Server-Sent Events para progreso en tiempo real."""
    ticker_list = _resolve_tickers(list_name, tickers, index)
    source = _source_label(list_name, tickers, index)
    config.ALERT_THRESHOLD = threshold

    async def generate():
        total = len(ticker_list)
        all_alerts = []

        yield f"data: {json.dumps({'type': 'start', 'total': total})}\n\n"

        for i, ticker in enumerate(ticker_list):
            yield f"data: {json.dumps({'type': 'progress', 'current': i+1, 'total': total, 'ticker': ticker})}\n\n"

            try:
                entries = scan_ticker(ticker)
                for e in entries:
                    if e["score"] >= threshold:
                        all_alerts.append(e)
                        yield f"data: {json.dumps({'type': 'alert', 'alert': e})}\n\n"
            except Exception:
                pass

            # Rate limiting
            if (i + 1) % config.BATCH_SIZE == 0:
                await asyncio.sleep(config.DELAY_BETWEEN_BATCHES)
            else:
                await asyncio.sleep(config.DELAY_BETWEEN_TICKERS)

        # Insights agrupados
        ticker_groups = {}
        for a in all_alerts:
            t = a["ticker"]
            if t not in ticker_groups:
                ticker_groups[t] = {"ticker": t, "company": a.get("company", t), "spot": a["spot"], "alerts": [], "max_score": 0, "total_notional": 0}
            ticker_groups[t]["alerts"].append(a)
            ticker_groups[t]["max_score"] = max(ticker_groups[t]["max_score"], a["score"])
            ticker_groups[t]["total_notional"] += a["notional"]

        insights = sorted(ticker_groups.values(), key=lambda x: x["max_score"], reverse=True)

        # Enriquecer con contexto Reddit/earnings
        yield f"data: {json.dumps({'type': 'progress', 'current': total, 'total': total, 'ticker': 'Analizando contexto Reddit/Earnings...'})}\n\n"
        await _enrich_with_context(all_alerts, insights)

        scan_time = datetime.now().isoformat()
        summary = {
            "type": "done",
            "scan_time": scan_time,
            "source": source,
            "tickers_scanned": total,
            "tickers_with_alerts": len(ticker_groups),
            "total_alerts": len(all_alerts),
            "high": len([a for a in all_alerts if a["score"] >= 75]),
            "medium": len([a for a in all_alerts if 50 <= a["score"] < 75]),
            "insights": insights,
            "alerts": all_alerts,
        }

        # Guardar resultado
        save_data = dict(summary)
        save_data.pop("type", None)
        save_data["threshold"] = threshold
        save_data["summary"] = {"total": len(all_alerts), "high": summary["high"], "medium": summary["medium"]}
        _save_scan(save_data, source)

        yield f"data: {json.dumps(summary, default=str)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/scan/full")
async def scan_full(
    threshold: int = Query(50),
    top: int = Query(30),
):
    """Full scan: todos los índices combinados, streaming con SSE."""
    # Unir todos los tickers sin duplicados
    all_tickers = []
    seen = set()
    for key in INDICES:
        for t in get_index_tickers(key):
            if t not in seen:
                seen.add(t)
                all_tickers.append(t)

    config.ALERT_THRESHOLD = threshold

    async def generate():
        total = len(all_tickers)
        all_alerts = []

        yield f"data: {json.dumps({'type': 'start', 'total': total})}\n\n"

        for i, ticker in enumerate(all_tickers):
            yield f"data: {json.dumps({'type': 'progress', 'current': i+1, 'total': total, 'ticker': ticker})}\n\n"

            try:
                entries = scan_ticker(ticker)
                for e in entries:
                    if e["score"] >= threshold:
                        all_alerts.append(e)
                        yield f"data: {json.dumps({'type': 'alert', 'alert': e})}\n\n"
            except Exception:
                pass

            if (i + 1) % config.BATCH_SIZE == 0:
                await asyncio.sleep(config.DELAY_BETWEEN_BATCHES)
            else:
                await asyncio.sleep(config.DELAY_BETWEEN_TICKERS)

        # Agrupar y ordenar
        ticker_groups = {}
        for a in all_alerts:
            t = a["ticker"]
            if t not in ticker_groups:
                ticker_groups[t] = {"ticker": t, "company": a.get("company", t), "spot": a["spot"], "alerts": [], "max_score": 0, "total_notional": 0}
            ticker_groups[t]["alerts"].append(a)
            ticker_groups[t]["max_score"] = max(ticker_groups[t]["max_score"], a["score"])
            ticker_groups[t]["total_notional"] += a["notional"]

        # Top N empresas por score
        insights = sorted(ticker_groups.values(), key=lambda x: x["max_score"], reverse=True)[:top]

        # Solo alertas del top N
        top_tickers = {ins["ticker"] for ins in insights}
        top_alerts = [a for a in all_alerts if a["ticker"] in top_tickers]
        top_alerts.sort(key=lambda x: x["score"], reverse=True)

        # Enriquecer con contexto Reddit/earnings
        yield f"data: {json.dumps({'type': 'progress', 'current': total, 'total': total, 'ticker': 'Analizando contexto Reddit/Earnings...'})}\n\n"
        await _enrich_with_context(top_alerts, insights)

        scan_time = datetime.now().isoformat()
        summary = {
            "type": "done",
            "scan_time": scan_time,
            "source": "full_scan",
            "tickers_scanned": total,
            "tickers_with_alerts": len(ticker_groups),
            "total_alerts": len(all_alerts),
            "top_shown": len(insights),
            "high": len([a for a in all_alerts if a["score"] >= 75]),
            "medium": len([a for a in all_alerts if 50 <= a["score"] < 75]),
            "insights": insights,
            "alerts": top_alerts,
        }

        # Guardar
        save_data = dict(summary)
        save_data.pop("type", None)
        save_data["threshold"] = threshold
        save_data["summary"] = {"total": len(all_alerts), "high": summary["high"], "medium": summary["medium"]}
        _save_scan(save_data, "full_scan")

        yield f"data: {json.dumps(summary, default=str)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/history")
async def get_history():
    """Lista escaneos guardados, del más reciente al más antiguo."""
    SCANS_DIR.mkdir(exist_ok=True)
    files = sorted(SCANS_DIR.glob("*.json"), reverse=True)
    result = []
    for f in files:
        try:
            with open(f) as fh:
                data = json.load(fh)
            result.append({
                "filename": f.name,
                "scan_time": data.get("scan_time", ""),
                "source": data.get("source", ""),
                "tickers_scanned": data.get("tickers_scanned", 0),
                "total_alerts": data.get("summary", {}).get("total", 0),
                "high": data.get("summary", {}).get("high", 0),
                "medium": data.get("summary", {}).get("medium", 0),
            })
        except Exception:
            continue
    return result


@app.get("/api/history/{filename}")
async def get_scan(filename: str):
    """Carga un escaneo guardado."""
    filepath = SCANS_DIR / filename
    if not filepath.exists() or not filepath.suffix == ".json":
        return {"error": "not found"}
    with open(filepath) as f:
        return json.load(f)


@app.delete("/api/history/{filename}")
async def delete_scan(filename: str):
    """Elimina un escaneo guardado."""
    filepath = SCANS_DIR / filename
    if filepath.exists() and filepath.suffix == ".json":
        filepath.unlink()
    return {"ok": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    STATIC_DIR.mkdir(exist_ok=True)
    print(f"Insider Trading Detector -> http://localhost:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
