# Insider Trading Detector

Real-time scanner that detects unusual call options activity across US stock indices. Analyzes options flow from Yahoo Finance, scores anomalies 0-100 using 6 signals, and cross-references with Reddit and earnings data to distinguish potential insider trading from public hype.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Scan 600+ tickers** across NASDAQ-100, S&P 500, Dow Jones, sector indices, and custom watchlists
- **Suspicion scoring (0-100)** based on 6 weighted signals: volume anomaly, new positions (Vol/OI), bet size (notional), expiration urgency, OTM depth, and clustering
- **Reddit cross-referencing** — searches r/wallstreetbets, r/stocks, r/options and more to identify public hype vs genuine insider signals
- **Earnings calendar** — shows upcoming earnings dates as context (pre-earnings unusual activity can indicate insider trading)
- **SSE streaming** — real-time progress for large scans
- **Scan history** — all results saved as JSON for posterior analysis
- **Full Scan mode** — scans all indices combined, returns top 30 most suspicious companies
- **Detail modal** — score breakdown, all Reddit articles with links, earnings info

## Quick start

```bash
# Clone
git clone https://github.com/mlaina/insider-detector.git
cd insider-detector

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
python app.py
# → http://localhost:8000
```

## Usage

### Web interface (recommended)

Open http://localhost:8000. Choose a source:

- **Index** — NASDAQ-100, S&P 500, Dow Jones, Semiconductors, Biotech, Energy, Financials, Mega Cap Tech, Meme stocks, Russell 2000
- **Watchlist** — custom ticker lists (manage in the UI)
- **Custom** — type specific tickers (e.g. `AAPL, TSLA, NVDA`)
- **Full Scan** — scans all indices combined (~600 unique tickers)

Set a threshold (default 40) and click Scan. Results stream in real-time.

### CLI

```bash
python main.py                          # Scan all watchlists
python main.py --list tech              # Scan one watchlist
python main.py --tickers AAPL TSLA NVDA # Specific tickers
python main.py --watch --interval 15    # Continuous monitoring
python main.py --threshold 60           # Higher threshold
```

## How scoring works

Each call option contract passing filters (min volume 100, DTE 1-45, OTM ≤ 30%) is scored on 8 signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| Volume vs baseline | 20% | Today's volume vs estimated daily normal (OI × 10%) |
| Vol/OI ratio | 15% | New positions entering — high ratio = fresh money |
| Notional | 15% | Size of bet in $ (volume × premium × 100) |
| Directional flow | 12% | Call vs put volume ratio — extreme one-directional = conviction |
| Near expiry | 12% | Shorter DTE = more leverage = more suspicious |
| OI concentration | 10% | Abnormal OI concentrated in a single contract |
| OTM depth | 8% | Deep out-of-the-money + high volume = directional conviction |
| Clustering | 8% | Multiple unusual contracts on same ticker = coordinated bet |

**Score ≥ 75** = High suspicion (red) · **Score ≥ 50** = Medium suspicion (yellow)

### Context filtering

After scoring, each ticker with alerts is cross-referenced with:

- **Reddit** (5 subreddits + global search) — classifies hype level. Viral = -10 pts, Trending = -5 pts. Mostly informational — Reddit hype does NOT discard opportunities.
- **Earnings** — shows date and days remaining. No penalty — pre-earnings unusual activity is exactly the insider trading pattern we look for.

See [How it works](http://localhost:8000/how-it-works) for a detailed explanation with examples.

## Project structure

```
app.py              FastAPI server, API routes, SSE streaming
scanner.py          Core detection logic: options chain analysis + scoring
context.py          Reddit + earnings cross-referencing (async)
config.py           All thresholds, weights, rate limits
tickers.py          Index definitions (11 indices, 600+ tickers)
main.py             CLI interface with rich tables
watchlist.json      Custom watchlists
static/
  index.html        SPA frontend (vanilla JS + Tailwind CSS)
  how-it-works.html Documentation page
scans/              Saved scan results as JSON (gitignored)
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/scan/stream?index=nasdaq100` | Scan with SSE streaming |
| `GET` | `/api/scan/full?top=30` | Full scan all indices |
| `GET` | `/api/scan?tickers=AAPL,TSLA` | Blocking scan (small lists) |
| `GET` | `/api/context/{ticker}` | Reddit + earnings for a ticker |
| `GET` | `/api/indices` | Available indices |
| `GET` | `/api/history` | Saved scans list |
| `GET` | `/api/history/{filename}` | Load saved scan |

All scan endpoints accept `threshold` (int, default 50).

## Configuration

Edit `config.py` to tune detection:

```python
MIN_VOLUME = 100              # Min contracts to consider
VOL_ANOMALY_MULTIPLIER = 3.0  # Volume must be 3x normal
MIN_VOL_OI_RATIO = 1.5        # New positions threshold
MIN_NOTIONAL = 50_000         # Min bet size ($)
ALERT_THRESHOLD = 50          # Min score to alert
BATCH_SIZE = 10               # Tickers per batch
DELAY_BETWEEN_BATCHES = 2.0   # Rate limiting (seconds)
```

## Data sources

- **Options data**: [Yahoo Finance](https://finance.yahoo.com) via [yfinance](https://github.com/ranaroussi/yfinance) (free, ~15 min delay)
- **Reddit**: Public JSON API (no auth required)
- **Earnings dates**: yfinance calendar

## Limitations

- **Estimated baseline** — Uses OI as proxy for average daily volume (no historical options volume without paid providers like CBOE/Unusual Whales)
- **No sweep detection** — Can't detect multi-exchange simultaneous hits (requires Level 2 data)
- **No buy/sell distinction** — Yahoo Finance doesn't indicate if volume is buying (bullish) or selling (bearish)
- **~15 min data delay** — Real-time detection requires direct market feeds
- **Rate limiting** — Yahoo Finance throttles aggressive requests; adjust delays in config if needed

## Deployment

Works on any platform that runs Python. Options:

- **Railway** / **Render** — push to deploy, free tier available
- **Fly.io** — add a `Dockerfile`
- **VPS** — `python app.py --host 0.0.0.0 --port 8000`

## License

MIT
