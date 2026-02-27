# SwingTraderAI
Smart technical analysis for MOEX and crypto traders Receive instant reports and signals on stocks (Moscow Exchange) and cryptocurrencies: • Trend, key levels, overbought/oversold levels • Automatic notifications for your watchlist • Easy setup and extension via code

## Features

- Periodically fetches fresh market data  
  • MOEX (via yfinance — tickers like SBER.ME, GAZP.ME, IMOEX.ME, etc.)  
  • Crypto exchanges (via ccxt — Binance, Bybit, OKX, etc.)
- Calculates a wide range of technical indicators (pandas_ta)
- Runs an AI agent (LangGraph + strong LLM) to interpret market context
- Detects signals based on predefined rules and/or model reasoning
- Stores full history of analyses and signals in PostgreSQL
- Sends Telegram notifications when interesting setups appear
- Exposes HTTP API for manual analysis requests and signal retrieval

## Current capabilities

- Automatic scanning of watchlist every N minutes
- Support for multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d, etc.)
- Classic indicators + SuperTrend, basic Volume Profile, ATR, Ichimoku, etc.
- Simple rule-based signals (RSI extremes, MACD cross, Bollinger squeeze/breakout, etc.)
- Extensible to complex multi-step LLM reasoning
- Separate Telegram bot for viewing recent signals and triggering manual analysis

## Architecture

```
moex-crypto-ta-backend/
├── app/                  # core FastAPI backend
│   ├── core/             # config, database, dependencies, scheduler
│   ├── models/           # SQLAlchemy models (Signal, Analysis, Ticker…)
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # data_fetcher, indicators, llm_agent, signal_detector
│   ├── tasks/            # background jobs (market_scanner)
│   └── api/              # HTTP endpoints
├── bots/                 # client implementations
│   └── telegram/         # aiogram bot
├── alembic/              # database migrations
└── scripts/              # CLI utilities for debugging
```

## Tech stack

- Python 3.14
- FastAPI + Uvicorn
- SQLAlchemy 2.0 + Alembic + PostgreSQL
- LangGraph (stateful AI workflows)
- pandas + pandas_ta
- ccxt (crypto exchanges)
- yfinance (MOEX)
- aiogram 3.x (Telegram bot)
- APScheduler (background tasks)
- pydantic-settings (configuration)
- LiteLLM or direct LLM clients (Claude, Grok, Gemini, etc.)

## Quick start

1. Clone the repository

```bash
git clone https://github.com/David2261/SwingTraderAI.git
cd SwingTraderAI
```

2. Create virtual environment and install dependencies

```bash
poetry install
source .venv/bin/activate
```

3. Create `.env` file and fill in the required values

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ta_db
# To run in Docker, use postgres instead of localhost.

# Telegram
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_TG_ID

# LLM API keys (choose one or more)
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...

# Scanning settings
SCAN_INTERVAL_MINUTES=30
```

4. Start PostgreSQL (easiest way — Docker)

```bash
docker run -d --name ta-postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ta_db \
  -p 5432:5432 \
  postgres:16
```

5. Apply database migrations

```bash
alembic upgrade head
```

6. Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

7. (in a separate terminal) Run the Telegram bot

```bash
python -m bots.telegram.bot
```

Now you can interact with the bot:

```
/start
/ta SBER.ME
/signals last 10
```

## License

Apache License 2.0
