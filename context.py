"""
Contexto público para descartar falsos positivos de insider trading.

Cruza tickers con:
1. Reddit (WSB, stocks, options) — si está trending, no es insider
2. Earnings próximos — actividad pre-earnings es esperada
3. Noticias recientes — si hay catalizador público, no es insider

El resultado es un "descuento" al score de sospecha.
"""

import httpx
import yfinance as yf
from datetime import datetime, timedelta
from collections import defaultdict

# Cache para no repetir llamadas
_reddit_cache: dict[str, dict] = {}
_earnings_cache: dict[str, dict] = {}

SUBREDDITS = ["wallstreetbets", "stocks", "options", "investing", "stockmarket"]
REDDIT_HEADERS = {"User-Agent": "InsiderDetector/1.0", "Accept-Language": "en-US,en;q=0.9"}


def _filter_relevant_posts(posts: list, ticker: str, seen_ids: set) -> list:
    """Filtra posts que realmente mencionan el ticker."""
    relevant = []
    for p in posts:
        pd = p.get("data", {})
        post_id = pd.get("id", "")
        if post_id in seen_ids:
            continue

        title = (pd.get("title") or "").upper()
        selftext = (pd.get("selftext") or "").upper()

        # Buscar el ticker como palabra completa o con $
        if (f" {ticker} " in f" {title} "
            or f" {ticker} " in f" {selftext} "
            or f"${ticker}" in title
            or f"${ticker}" in selftext
            or title.startswith(f"{ticker} ")
            or title.endswith(f" {ticker}")
            or f"({ticker})" in title):
            seen_ids.add(post_id)
            relevant.append(pd)

    return relevant


def _format_post(pd: dict, subreddit: str) -> dict:
    """Formatea un post de Reddit para el output."""
    created_utc = pd.get("created_utc", 0)
    return {
        "subreddit": subreddit,
        "title": pd.get("title", "")[:140],
        "score": pd.get("score", 0),
        "num_comments": pd.get("num_comments", 0),
        "created": datetime.fromtimestamp(created_utc).isoformat() if created_utc else "",
        "created_ago": _time_ago(created_utc),
        "url": f"https://reddit.com{pd.get('permalink', '')}",
    }


def _time_ago(utc_timestamp: float) -> str:
    """Convierte timestamp a 'hace X horas/dias'."""
    if not utc_timestamp:
        return ""
    diff = datetime.now() - datetime.fromtimestamp(utc_timestamp)
    hours = diff.total_seconds() / 3600
    if hours < 1:
        return f"hace {int(diff.total_seconds()/60)}m"
    if hours < 24:
        return f"hace {int(hours)}h"
    days = int(hours / 24)
    return f"hace {days}d"


async def check_reddit(ticker: str) -> dict:
    """Busca menciones recientes del ticker en subreddits financieros."""
    if ticker in _reddit_cache:
        return _reddit_cache[ticker]

    total_mentions = 0
    top_posts = []
    subreddit_counts = {}
    seen_ids = set()

    async with httpx.AsyncClient(timeout=10, headers=REDDIT_HEADERS, follow_redirects=True) as client:
        # 1. Búsqueda por subreddit
        for sub in SUBREDDITS:
            try:
                url = f"https://www.reddit.com/r/{sub}/search.json"
                resp = await client.get(url, params={
                    "q": f"{ticker} OR ${ticker}",
                    "sort": "relevance",
                    "t": "week",
                    "limit": 25,
                    "restrict_sr": "true",
                })
                if resp.status_code != 200:
                    continue

                data = resp.json()
                posts = data.get("data", {}).get("children", [])

                relevant = _filter_relevant_posts(posts, ticker, seen_ids)
                count = len(relevant)
                subreddit_counts[sub] = count
                total_mentions += count

                for pd in relevant:
                    top_posts.append(_format_post(pd, sub))
            except Exception:
                continue

        # 2. Búsqueda global (no restringida a subreddit) para capturar posts en otros subs
        try:
            resp = await client.get("https://www.reddit.com/search.json", params={
                "q": f"${ticker} stock OR {ticker} calls OR {ticker} options",
                "sort": "relevance",
                "t": "week",
                "limit": 25,
                "type": "link",
            })
            if resp.status_code == 200:
                data = resp.json()
                posts = data.get("data", {}).get("children", [])
                relevant = _filter_relevant_posts(posts, ticker, seen_ids)
                for pd in relevant:
                    sub = pd.get("subreddit", "?")
                    subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
                    total_mentions += 1
                    top_posts.append(_format_post(pd, sub))
        except Exception:
            pass

    # Ordenar posts por engagement
    top_posts.sort(key=lambda x: x.get("score", 0) + x.get("num_comments", 0), reverse=True)

    result = {
        "total_mentions": total_mentions,
        "subreddit_counts": subreddit_counts,
        "top_posts": top_posts[:5],
        "is_trending": total_mentions >= 5,
        "hype_level": _classify_hype(total_mentions, top_posts),
    }

    _reddit_cache[ticker] = result
    return result


def _classify_hype(mentions: int, posts: list) -> str:
    """Clasifica el nivel de hype en Reddit."""
    if mentions == 0:
        return "none"

    max_engagement = max((p.get("score", 0) + p.get("num_comments", 0) for p in posts), default=0)

    if mentions >= 15 or max_engagement >= 500:
        return "viral"
    if mentions >= 8 or max_engagement >= 100:
        return "high"
    if mentions >= 3 or max_engagement >= 20:
        return "moderate"
    return "low"


def check_earnings(ticker: str) -> dict:
    """Verifica si hay earnings próximos para el ticker."""
    if ticker in _earnings_cache:
        return _earnings_cache[ticker]

    result = {
        "has_upcoming_earnings": False,
        "earnings_date": None,
        "days_to_earnings": None,
    }

    try:
        stock = yf.Ticker(ticker)
        cal = stock.calendar
        if cal is not None:
            # yfinance devuelve calendario con earnings dates
            earnings_date = None
            if isinstance(cal, dict):
                ed = cal.get("Earnings Date")
                if ed:
                    if isinstance(ed, list) and len(ed) > 0:
                        earnings_date = ed[0]
                    elif hasattr(ed, "date"):
                        earnings_date = ed
            elif hasattr(cal, "iloc"):
                # DataFrame format
                try:
                    ed = cal.loc["Earnings Date"]
                    if hasattr(ed, "iloc"):
                        earnings_date = ed.iloc[0]
                    else:
                        earnings_date = ed
                except Exception:
                    pass

            if earnings_date:
                if hasattr(earnings_date, "date"):
                    ed_date = earnings_date.date() if callable(getattr(earnings_date, "date")) else earnings_date
                else:
                    ed_date = earnings_date

                now = datetime.now()
                if hasattr(ed_date, "year"):
                    days_to = (datetime(ed_date.year, ed_date.month, ed_date.day) - now).days
                    if -2 <= days_to <= 30:  # Earnings en los próximos 30 días o hace 2 días
                        result["has_upcoming_earnings"] = True
                        result["earnings_date"] = str(ed_date)
                        result["days_to_earnings"] = days_to
    except Exception:
        pass

    _earnings_cache[ticker] = result
    return result


async def get_ticker_context(ticker: str) -> dict:
    """Obtiene el contexto completo para un ticker."""
    reddit = await check_reddit(ticker)
    earnings = check_earnings(ticker)

    # Calcular penalización al score
    # NOTA: La penalización es suave. Reddit hype NO descarta la oportunidad,
    # solo indica que hay contexto público. Earnings sí penaliza más porque
    # la actividad pre-earnings es esperada y no es insider.
    penalty = 0
    reasons = []
    tags = []  # Tags informativos para el frontend

    # Reddit context (informativo, penalización mínima)
    hype = reddit["hype_level"]
    if hype == "viral":
        penalty += 10
        reasons.append(f"Viral en Reddit ({reddit['total_mentions']} posts esta semana)")
        tags.append("reddit_viral")
    elif hype == "high":
        penalty += 5
        reasons.append(f"Trending en Reddit ({reddit['total_mentions']} posts)")
        tags.append("reddit_trending")
    elif hype == "moderate":
        reasons.append(f"Mencionado en Reddit ({reddit['total_mentions']} posts)")
        tags.append("reddit_mentioned")
    elif hype == "low":
        reasons.append(f"Algunas menciones en Reddit ({reddit['total_mentions']})")

    # Earnings: solo informativo, sin penalización
    # Actividad inusual antes de earnings PUEDE ser insider trading genuino
    if earnings["has_upcoming_earnings"]:
        days = earnings["days_to_earnings"]
        if days is not None:
            if days <= 3:
                tags.append("earnings_imminent")
            elif days <= 7:
                tags.append("earnings_soon")
            elif days <= 14:
                tags.append("earnings_upcoming")

    return {
        "reddit": reddit,
        "earnings": earnings,
        "penalty": min(penalty, 45),  # Cap: no reducir más del 45%
        "penalty_reasons": reasons,
        "tags": tags,
        "adjusted": len(reasons) > 0,
    }


def apply_context_penalty(score: float, context: dict) -> tuple[float, float]:
    """Aplica la penalización del contexto al score.

    Returns: (adjusted_score, original_score)
    """
    penalty = context.get("penalty", 0)
    adjusted = max(0, score - penalty)
    return round(adjusted, 1), round(score, 1)
