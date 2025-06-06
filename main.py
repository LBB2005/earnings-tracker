from typing import Optional
from fastapi import FastAPI, Query
from utils import (
    get_recent_earnings,
    get_company_news,
    summarize_news_sentiment,
)

app = FastAPI(title="Earnings Tracker")


@app.get("/earnings")
def read_earnings(
    filter: Optional[str] = Query(None, description="Filter by surprise type"),
    min_surprise: float = Query(0.0, description="Minimum absolute surprise %"),
):
    data = get_recent_earnings()
    if filter:
        data = [d for d in data if d["surprise_type"].lower() == filter.lower()]
    if min_surprise:
        data = [d for d in data if abs(d["earnings_surprise_pct"]) >= min_surprise]
    return data


@app.get("/sentiment/{ticker}")
def read_sentiment(ticker: str):
    news = get_company_news(ticker)
    overall, detailed = summarize_news_sentiment(news)
    return {"ticker": ticker.upper(), "overall_sentiment": overall, "headlines": detailed}
