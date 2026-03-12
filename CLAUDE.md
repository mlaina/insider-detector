# Insider Trading Detector — Agent Guide

## What is this

A web app that scans US stock options (calls) looking for unusual activity patterns that may indicate insider trading. It scores each anomaly 0-100 and cross-references with Reddit hype and earnings calendars to distinguish genuine signals from public noise.

**Stack**: Python 3.11+, FastAPI, yfinance, httpx, Tailwind CSS (CDN). No database — scans are saved as JSON files.

**Run**: `python app.py` → http://localhost:8000

## Architecture

```
app.py          → FastAPI server, routes, SSE streaming, scan persistence
scanner.py      → Core detection: fetches options chains, scores anomalies
context.py      → Reddit + earnings cross-referencing (async, httpx)
config.py       → All thresholds, weights, rate limits (single source of truth)
tickers.py      → Index definitions (NASDAQ-100, S&P 500, sectors, etc.)
main.py         → CLI alternative (rich tables, --watch mode)
watchlist.json  → User-defined custom watchlists
static/
  index.html    → SPA frontend (vanilla JS, Tailwind)
  how-it-works.html → Documentation page
scans/          → Saved scan results as JSON (gitignored)
```

## Data flow

1. User picks source (index, watchlist, custom tickers) → frontend calls `/api/scan/stream` or `/api/scan/full`
2. Backend iterates tickers, calls `scan_ticker()` for each → yfinance options chain
3. Each call option contract is filtered (min volume, DTE range, OTM range) then scored on 6 signals
4. Results streamed via SSE (`type: progress`, `type: alert`, `type: done`)
5. After scanning, `_enrich_with_context()` fetches Reddit mentions + earnings dates for tickers with alerts
6. Final results (alerts + insights + context) sent in the `done` event and saved to `scans/`

## Scoring (0-100)

Eight weighted signals (weights sum to 1.0):

| Signal | Weight | What it measures |
|--------|--------|-----------------|
| Vol vs baseline | 0.20 | Today's volume vs estimated daily normal (OI × 10%) |
| Vol/OI ratio | 0.15 | New positions — high ratio = fresh money entering |
| Notional ($) | 0.15 | Size of bet in dollars (vol × price × 100) |
| Directional flow | 0.12 | Call/put volume ratio — extreme one-directional flow = conviction |
| Near expiry | 0.12 | DTE — shorter = more leveraged = more suspicious |
| OI concentration | 0.10 | Abnormal OI concentrated in a single contract |
| OTM depth | 0.08 | How far out of the money — deep OTM + volume = directional bet |
| Clustering | 0.08 | Multiple unusual contracts on same ticker |

Each signal normalized to 0-100, multiplied by weight, summed. See `scanner.py:_score()`.

### Directional flow
Scanner fetches both calls AND puts for each expiration. Calculates the percentage of volume in the dominant direction. 85%+ calls = extreme bullish flow, 85%+ puts = extreme bearish flow. This signal is what other tools call "EXTREME DIRECTIONAL FLOW".

### OI concentration
Detects when a single contract holds 20%+ of the ticker's total OI with at least 1,000 contracts. This indicates deliberate accumulation in a specific strike/expiration.

## Context system (context.py)

- **Reddit**: Searches r/wallstreetbets, r/stocks, r/options, r/investing, r/stockmarket + global search. Uses `Accept-Language: en-US` for English results. Classifies hype as none/low/moderate/high/viral.
- **Earnings**: Checks yfinance calendar for upcoming earnings dates within 30 days.
- **Penalties are minimal**: Reddit viral = -10 pts, trending = -5 pts. Earnings = 0 penalty (informational only — pre-earnings activity can be genuine insider trading).
- All context data (posts, dates, links) is saved in scan JSONs for posterior analysis.

## Key design decisions

- **Reddit does NOT discard opportunities** — it's informational context. A ticker trending on Reddit can still be a valid opportunity.
- **Earnings do NOT penalize** — pre-earnings unusual activity is exactly the insider trading pattern we're looking for.
- **SSE streaming** is required for index scans (500+ tickers). Uses `await asyncio.sleep()` for rate limiting — never `time.sleep()` in async context.
- **All data is persisted** in scan JSONs including Reddit posts, earnings dates, raw scores, adjusted scores.
- **Modal shows all Reddit articles** with links, subreddit, upvotes, comments, and relative publication time.

## API routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main SPA |
| GET | `/how-it-works` | Documentation page |
| GET | `/api/indices` | Available indices + ticker counts |
| GET | `/api/watchlist` | Custom watchlists |
| POST | `/api/watchlist/{name}` | Create/update watchlist |
| DELETE | `/api/watchlist/{name}` | Delete watchlist |
| GET | `/api/scan` | Scan (blocking, for small lists) |
| GET | `/api/scan/stream` | Scan with SSE streaming |
| GET | `/api/scan/full` | Full scan: all indices combined, SSE |
| GET | `/api/context/{ticker}` | Reddit + earnings context for one ticker |
| GET | `/api/history` | List saved scans |
| GET | `/api/history/{filename}` | Load a saved scan |
| DELETE | `/api/history/{filename}` | Delete a saved scan |

## Common scan parameters

- `threshold` (int, default 50): minimum score to generate alert
- `list` (str): watchlist name
- `index` (str): index key from tickers.py (nasdaq100, sp500, dow, etc.)
- `tickers` (str): comma-separated ticker symbols
- `top` (int, default 30): for full scan, how many top companies to return

## Modifying thresholds

All detection parameters are in `config.py`. Change weights, minimums, rate limits there. The scoring formula is in `scanner.py:_score()`.

## Rate limiting

Yahoo Finance is rate-sensitive. Config defaults: 0.3s between tickers, 2.0s every 10 tickers. Adjust in `config.py` if getting throttled.

## Frontend

Single HTML file (`static/index.html`) with inline JS. No build step. Uses Tailwind CDN. Key globals:
- `allAlerts`: current scan's alert array
- `scanData`: full scan summary (used for modal context fallback)
- SSE `done` event includes enriched `alerts` array — frontend replaces accumulated alerts with it

Modal opens on click of insight card or table row, closes on Escape or click outside.
