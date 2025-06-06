# Earnings Tracker

This project provides a small FastAPI service that lists recent earnings releases for companies in the S&P 500 index and optionally analyzes sentiment of recent news headlines.

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Run the API with Uvicorn:

```bash
uvicorn main:app --reload
```

## Endpoints

- **GET /earnings** – Returns companies that reported earnings in the last 7 days.
  - Optional query params:
    - `filter` – `positive`, `negative`, or `neutral` to filter by surprise type.
    - `min_surprise` – minimum absolute surprise percentage to include.

- **GET /sentiment/{ticker}** – Summarizes bullish/bearish/neutral sentiment from recent news headlines for a company.

Both endpoints return JSON responses documented in the automatically generated Swagger UI at `/docs` once the server is running.
