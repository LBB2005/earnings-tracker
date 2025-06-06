from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple
import yfinance as yf


def get_sp500_tickers() -> List[str]:
    """Return a list of S&P 500 tickers."""
    try:
        return yf.tickers_sp500()
    except Exception:
        return []


def get_recent_earnings(days: int = 7) -> List[Dict]:
    """Fetch earnings from the last `days` days for S&P 500 companies."""
    tickers = get_sp500_tickers()
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    results = []

    for ticker in tickers:
        try:
            tkr = yf.Ticker(ticker)
            history = tkr.get_earnings_history() or []
        except Exception:
            continue

        for record in history:
            date_str = record.get("startdatetime") or record.get("startDate")
            if not date_str:
                continue
            date_str = date_str.replace("Z", "+00:00")
            try:
                rep_date = datetime.fromisoformat(date_str)
            except Exception:
                continue
            if not (start_date <= rep_date <= end_date):
                continue

            actual = record.get("epsactual")
            estimate = record.get("epsestimate")
            if actual is None or estimate is None:
                continue
            try:
                surprise = ((actual - estimate) / abs(estimate)) * 100
            except ZeroDivisionError:
                surprise = 0.0
            if surprise > 5:
                surprise_type = "Positive"
            elif surprise < -5:
                surprise_type = "Negative"
            else:
                surprise_type = "Neutral"
            results.append(
                {
                    "ticker": ticker,
                    "report_date": rep_date.date().isoformat(),
                    "estimated_eps": estimate,
                    "actual_eps": actual,
                    "earnings_surprise_pct": round(surprise, 2),
                    "surprise_type": surprise_type,
                }
            )

    results.sort(key=lambda r: abs(r["earnings_surprise_pct"]), reverse=True)
    return results


def get_company_news(ticker: str, limit: int = 10) -> List[Dict]:
    """Return recent news items for a ticker using yfinance."""
    try:
        news = yf.Ticker(ticker).news or []
    except Exception:
        news = []
    return news[:limit]


POSITIVE_WORDS = [
    "beat",
    "beats",
    "surge",
    "rise",
    "soar",
    "record",
    "gain",
]
NEGATIVE_WORDS = [
    "miss",
    "fall",
    "plunge",
    "drop",
    "decline",
    "warning",
]


def analyze_headline_sentiment(headline: str) -> str:
    """Very naive sentiment analysis for a single headline."""
    text = headline.lower()
    score = 0
    for w in POSITIVE_WORDS:
        if w in text:
            score += 1
    for w in NEGATIVE_WORDS:
        if w in text:
            score -= 1
    if score > 0:
        return "Bullish"
    if score < 0:
        return "Bearish"
    return "Neutral"


def summarize_news_sentiment(news: List[Dict]) -> Tuple[str, List[Dict]]:
    """Analyze sentiment for a list of news items."""
    counts = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
    for item in news:
        sentiment = analyze_headline_sentiment(item.get("title", ""))
        item["sentiment"] = sentiment
        counts[sentiment] += 1
    if counts["Bullish"] > max(counts["Bearish"], counts["Neutral"]):
        overall = "Bullish"
    elif counts["Bearish"] > max(counts["Bullish"], counts["Neutral"]):
        overall = "Bearish"
    else:
        overall = "Neutral"
    return overall, news
