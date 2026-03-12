"""
Escanea opciones call buscando actividad REALMENTE inusual.

Estrategia:
1. Pre-filtra tickers sin opciones líquidas (ahorra tiempo)
2. Compara volumen de hoy vs baseline del ticker (OI como proxy)
3. Detecta clustering: múltiples strikes inusuales = señal fuerte
4. Genera insights claros con fechas y razones concretas
"""

import time
from datetime import datetime
from collections import defaultdict

import pandas as pd
import yfinance as yf

import config


def _estimate_baseline(calls_df: pd.DataFrame) -> float:
    """Estima el volumen diario 'normal' de calls usando OI como proxy.
    Regla: vol normal ~ 8-12% del OI total."""
    total_oi = calls_df["openInterest"].fillna(0).sum()
    return total_oi * 0.10 if total_oi > 0 else 0


def _get_company_name(stock: yf.Ticker, ticker: str) -> str:
    """Obtiene el nombre completo de la empresa."""
    try:
        name = getattr(stock, "info", {}).get("shortName") or getattr(stock, "info", {}).get("longName")
        if name:
            return name
    except Exception:
        pass
    return ticker


# Cache de nombres para no repetir llamadas
_name_cache: dict[str, str] = {}


def scan_ticker(ticker: str) -> list[dict]:
    """Escanea un ticker y devuelve contratos con actividad inusual."""
    stock = yf.Ticker(ticker)

    # Obtener nombre de la empresa
    if ticker not in _name_cache:
        _name_cache[ticker] = _get_company_name(stock, ticker)
    company_name = _name_cache[ticker]

    # Obtener precio spot
    spot_price = None
    try:
        spot_price = getattr(stock.fast_info, "last_price", None)
    except Exception:
        pass
    if spot_price is None:
        try:
            hist = stock.history(period="2d")
            if not hist.empty:
                spot_price = hist["Close"].iloc[-1]
        except Exception:
            pass
    if not spot_price or spot_price <= 0:
        return []

    try:
        expirations = stock.options
    except Exception:
        return []
    if not expirations:
        return []

    now = datetime.now()
    all_calls = []
    entries = []

    for exp_str in expirations:
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
        dte = (exp_date - now).days
        if dte < config.MIN_DTE or dte > config.MAX_DTE:
            continue

        try:
            chain = stock.option_chain(exp_str)
        except Exception:
            continue

        calls = chain.calls
        if calls.empty:
            continue

        all_calls.append(calls)

        for _, row in calls.iterrows():
            strike = row.get("strike", 0)
            volume = row.get("volume", 0) or 0
            open_interest = row.get("openInterest", 0) or 0
            implied_vol = row.get("impliedVolatility", 0) or 0
            last_price = row.get("lastPrice", 0) or 0
            bid = row.get("bid", 0) or 0
            ask = row.get("ask", 0) or 0

            # Filtros básicos
            if volume < config.MIN_VOLUME:
                continue
            if strike < spot_price * 0.97:  # Solo ATM y OTM
                continue
            otm_pct = (strike - spot_price) / spot_price
            if otm_pct > config.MAX_OTM_PCT:
                continue

            vol_oi_ratio = volume / open_interest if open_interest > 0 else float(volume)
            notional = volume * last_price * 100

            entries.append({
                "ticker": ticker,
                "company": company_name,
                "scanned_at": now.isoformat(),
                "data_timestamp": now.strftime("%Y-%m-%d %H:%M"),
                "expiration": exp_str,
                "dte": dte,
                "strike": round(strike, 2),
                "spot": round(spot_price, 2),
                "otm_pct": round(otm_pct * 100, 2),
                "volume": int(volume),
                "open_interest": int(open_interest),
                "vol_oi_ratio": round(vol_oi_ratio, 2),
                "implied_vol": round(implied_vol * 100, 2),
                "last_price": round(last_price, 2),
                "bid": round(bid, 2),
                "ask": round(ask, 2),
                "notional": round(notional, 0),
            })

    if not entries:
        return []

    # Calcular baseline del ticker
    if all_calls:
        combined = pd.concat(all_calls, ignore_index=True)
        baseline = _estimate_baseline(combined)
    else:
        baseline = 0

    # Enriquecer cada entrada con contexto
    cluster_count = len(entries)
    for e in entries:
        e["baseline"] = round(baseline, 0)
        e["vol_vs_baseline"] = round(e["volume"] / baseline, 1) if baseline > 0 else 0
        e["cluster_count"] = cluster_count
        e["score"] = _score(e, cluster_count)
        e["reason"] = _build_reason(e, cluster_count)

    return entries


def _score(e: dict, cluster_count: int) -> float:
    """Score de sospecha 0-100."""
    s = 0.0

    # Volumen vs baseline (25%)
    vb = e["vol_vs_baseline"]
    if vb >= config.VOL_ANOMALY_MULTIPLIER:
        s += min(100, (vb / 10) * 100) * config.WEIGHT_VOL_ANOMALY
    elif vb > 0:
        s += 0

    # Vol/OI — posiciones nuevas (20%)
    voi = e["vol_oi_ratio"]
    if voi >= config.MIN_VOL_OI_RATIO:
        s += min(100, (voi / 15) * 100) * config.WEIGHT_VOL_OI

    # Notional (20%)
    n = e["notional"]
    if n >= config.MIN_NOTIONAL:
        s += min(100, (n / 2_000_000) * 100) * config.WEIGHT_NOTIONAL

    # Near-term (15%)
    dte = e["dte"]
    dte_s = 100 if dte <= 5 else 80 if dte <= 10 else 50 if dte <= 21 else 25 if dte <= 30 else 10
    s += dte_s * config.WEIGHT_NEAR_EXPIRY

    # OTM depth (10%)
    otm = e["otm_pct"]
    otm_s = 100 if otm >= 15 else 70 if otm >= 8 else 40 if otm >= 3 else 10
    s += otm_s * config.WEIGHT_OTM_DEPTH

    # Clustering (10%)
    cl_s = 100 if cluster_count >= 5 else 70 if cluster_count >= 3 else 40 if cluster_count >= 2 else 0
    s += cl_s * config.WEIGHT_CLUSTERING

    return round(s, 1)


def _build_reason(e: dict, cluster_count: int) -> str:
    """Genera insight legible."""
    r = []

    vb = e["vol_vs_baseline"]
    if vb >= 5:
        r.append(f"Volumen {vb:.0f}x sobre lo normal")
    elif vb >= 3:
        r.append(f"Volumen {vb:.1f}x sobre lo normal")

    if e["vol_oi_ratio"] >= 5:
        r.append(f"V/OI {e['vol_oi_ratio']:.0f}x — posiciones mayoritariamente nuevas")
    elif e["vol_oi_ratio"] >= 2:
        r.append(f"V/OI {e['vol_oi_ratio']:.1f}x — flujo de posiciones nuevas")

    if e["notional"] >= 1_000_000:
        r.append(f"Apuesta de ${e['notional']/1e6:.1f}M")
    elif e["notional"] >= 100_000:
        r.append(f"Apuesta de ${e['notional']/1e3:.0f}K")

    if e["dte"] <= 7:
        r.append(f"Expira en {e['dte']} dias — maximo apalancamiento")
    elif e["dte"] <= 14:
        r.append(f"Expira en {e['dte']} dias — near-term")

    if e["otm_pct"] >= 10:
        r.append(f"{e['otm_pct']:.0f}% fuera del dinero — apuesta muy agresiva")
    elif e["otm_pct"] >= 5:
        r.append(f"{e['otm_pct']:.0f}% fuera del dinero")

    if cluster_count >= 3:
        r.append(f"{cluster_count} contratos inusuales en {e['ticker']}")

    return " | ".join(r) if r else "Actividad por encima de umbrales"


def scan_tickers(tickers: list[str], progress_cb=None) -> pd.DataFrame:
    """Escanea lista de tickers con rate limiting."""
    all_alerts = []
    scanned = 0
    errors = []

    for i, ticker in enumerate(tickers):
        if progress_cb:
            progress_cb(i + 1, len(tickers), ticker)

        try:
            entries = scan_ticker(ticker)
            for e in entries:
                if e["score"] >= config.ALERT_THRESHOLD:
                    all_alerts.append(e)
            scanned += 1
        except Exception as ex:
            errors.append({"ticker": ticker, "error": str(ex)})

        # Rate limiting
        if (i + 1) % config.BATCH_SIZE == 0:
            time.sleep(config.DELAY_BETWEEN_BATCHES)
        else:
            time.sleep(config.DELAY_BETWEEN_TICKERS)

    if not all_alerts:
        return pd.DataFrame()

    df = pd.DataFrame(all_alerts)
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    return df
