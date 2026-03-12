"""
Finance tools combining Yahoo Finance and Finnhub stock analysis capabilities
Enhanced with accessibility features and improved formatting
"""

import yfinance as yf
import finnhub
import pandas as pd
import numpy as np
import aiohttp
import asyncio
from transformers import pipeline
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Union, Callable, Awaitable
from functools import lru_cache
from datetime import datetime, timedelta

# Helper functions for sentiment analysis
@lru_cache(maxsize=128)
def _get_sentiment_model():
    return pipeline("sentiment-analysis", model="ProsusAI/finbert")

async def _async_sentiment_analysis(content: str, model) -> Dict[str, Union[str, float]]:
    result = model(content)[0]
    return {"sentiment": result["label"], "confidence": result["score"]}

# Yahoo Finance functions
def _get_asset_info(ticker: str) -> Dict[str, Any]:
    asset = yf.Ticker(ticker)
    info = asset.info

    if info.get("quoteType") == "CRYPTOCURRENCY":
        return {
            "name": info.get("name", "N/A"),
            "symbol": info.get("symbol", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "circulating_supply": info.get("circulatingSupply", 0),
            "max_supply": info.get("maxSupply", 0),
            "24h_volume": info.get("volume24Hr", 0),
            "7d_change": info.get("sevenDayAvgChangePercent", 0),
            "is_crypto": True,
        }
    else:
        return {
            "name": info.get("longName", "N/A"),
            "symbol": info.get("symbol", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0),
            "is_crypto": False,
        }

def _get_current_price(ticker: str) -> Dict[str, float]:
    asset = yf.Ticker(ticker)
    data = asset.history(period="1d")
    return {
        "current_price": data["Close"].iloc[-1],
        "open": data["Open"].iloc[-1],
        "high": data["High"].iloc[-1],
        "low": data["Low"].iloc[-1],
        "volume": data["Volume"].iloc[-1],
    }

def _get_asset_news(ticker: str) -> List[Dict[str, Any]]:
    asset = yf.Ticker(ticker)
    news = asset.news[:10]  # Get the first 10 news items
    return [{
        "title": item["title"],
        "publisher": item["publisher"],
        "link": item["link"],
        "published_time": item["providerPublishTime"],
        "summary": item.get("summary", "No summary available.")
    } for item in news]

def _get_historical_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    asset = yf.Ticker(ticker)
    return asset.history(period=period)

def _analyze_historical_data(df: pd.DataFrame) -> Dict[str, Any]:
    analysis = {}
    
    # Calculate simple moving averages
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["SMA200"] = df["Close"].rolling(window=200).mean()
    
    # Calculate price change and volatility
    df["Daily_Return"] = df["Close"].pct_change()
    analysis["price_change"] = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    analysis["volatility"] = df["Daily_Return"].std() * np.sqrt(252) * 100  # Annualized volatility
    
    # Trend analysis
    current_price = df["Close"].iloc[-1]
    analysis["trend_sma50"] = "Bullish" if current_price > df["SMA50"].iloc[-1] else "Bearish"
    analysis["trend_sma200"] = "Bullish" if current_price > df["SMA200"].iloc[-1] else "Bearish"
    
    # Highest and lowest prices
    analysis["highest_price"] = df["High"].max()
    analysis["lowest_price"] = df["Low"].min()
    analysis["avg_volume"] = df["Volume"].mean()
    
    return analysis

def _get_rsi_macd(symbol: str, period: str = "1mo", interval: str = "1d") -> str:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period, interval=interval)
    close_prices = data["Close"]
    
    # Calculate RSI
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Calculate MACD
    ema_12 = close_prices.ewm(span=12, adjust=False).mean()
    ema_26 = close_prices.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    
    # Format output
    output = f"Results for {symbol} over period {period} with interval {interval}:\n\n"
    output += f"Latest RSI: {rsi.iloc[-1]:.2f}\n"
    output += f"Latest MACD: {macd_line.iloc[-1]:.2f}\n"
    output += f"Latest MACD Signal: {signal_line.iloc[-1]:.2f}\n"
    output += f"Latest MACD Histogram: {macd_hist.iloc[-1]:.2f}\n\n"
    
    output += "RSI Evolution:\n"
    output += f"{rsi.tail(10).to_string(header=False)}\n\n"
    
    output += "MACD Evolution:\n"
    output_df = pd.DataFrame({
        "MACD": macd_line,
        "Signal": signal_line,
        "Histogram": macd_hist
    }, index=macd_line.index)
    output += f"{output_df.tail(10).to_string(index=True)}"
    
    return output

async def _async_gather_asset_data(ticker: str) -> Dict[str, Any]:
    asset_info = _get_asset_info(ticker)
    current_price = _get_current_price(ticker)
    news_items = _get_asset_news(ticker)
    historical_data = _get_historical_data(ticker)
    historical_analysis = _analyze_historical_data(historical_data)
    
    model = _get_sentiment_model()
    sentiment_tasks = [_async_sentiment_analysis(item["title"], model) for item in news_items]
    sentiments = await asyncio.gather(*sentiment_tasks)
    
    sentiment_results = [{
        "title": news_items[i]["title"],
        "publisher": news_items[i]["publisher"],
        "link": news_items[i]["link"],
        "published_time": news_items[i]["published_time"],
        "sentiment": sentiment["sentiment"],
        "confidence": sentiment["confidence"]
    } for i, sentiment in enumerate(sentiments)]
    
    return {
        "asset_info": asset_info,
        "current_price": current_price,
        "sentiments": sentiment_results,
        "historical_analysis": historical_analysis
    }

def _compile_report(data: Dict[str, Any], price_history: pd.DataFrame, tech_data: str) -> str:
    info = data["asset_info"]
    price = data["current_price"]
    historical = data["historical_analysis"]
    
    if info["is_crypto"]:
        report = """
        Cryptocurrency Analysis Report for {name} ({symbol})

        Basic Information:
        Market Cap: ${market_cap:,.0f}
        Circulating Supply: {circulating_supply:,.0f}

        Current Trading Information:
        Current Price: ${current_price:.2f}
        24h Range: ${low:.2f} - ${high:.2f}
        24h Volume: {volume:,.0f}

        Historical Analysis:
        Price Change (1 year): {price_change:.2f}%
        Annualized Volatility: {volatility:.2f}%
        50-day SMA Trend: {trend_sma50}
        200-day SMA Trend: {trend_sma200}
        Highest Price (1 year): ${highest_price:.2f}
        Lowest Price (1 year): ${lowest_price:.2f}
        Average Daily Volume: {avg_volume:,.0f}
        Price history: {price_history}
        Technical data: {tech_data}
        """.format(
            name=info["name"],
            symbol=info["symbol"],
            market_cap=info["market_cap"],
            circulating_supply=info["circulating_supply"],
            current_price=price["current_price"],
            low=price["low"],
            high=price["high"],
            volume=price["volume"],
            price_change=historical["price_change"],
            volatility=historical["volatility"],
            trend_sma50=historical["trend_sma50"],
            trend_sma200=historical["trend_sma200"],
            highest_price=historical["highest_price"],
            lowest_price=historical["lowest_price"],
            avg_volume=historical["avg_volume"],
            price_history=price_history.to_string(),
            tech_data=tech_data
        )
    else:
        report = """
        Stock Analysis Report for {name} ({symbol})

        Basic Information:
        Sector: {sector}
        Industry: {industry}
        Market Cap: ${market_cap:,.0f}

        Current Trading Information:
        Current Price: ${current_price:.2f}
        Day's Range: ${low:.2f} - ${high:.2f}
        Volume: {volume:,.0f}

        Key Financial Metrics:
        P/E Ratio: {pe_ratio}
        Dividend Yield: {dividend_yield:.2%}
        Beta: {beta}
        52 Week Range: ${week_low:.2f} - ${week_high:.2f}

        Historical Analysis:
        Price Change (1 year): {price_change:.2f}%
        Annualized Volatility: {volatility:.2f}%
        50-day SMA Trend: {trend_sma50}
        200-day SMA Trend: {trend_sma200}
        Highest Price (1 year): ${highest_price:.2f}
        Lowest Price (1 year): ${lowest_price:.2f}
        Average Daily Volume: {avg_volume:,.0f}
        """.format(
            name=info["name"],
            symbol=info["symbol"],
            sector=info["sector"],
            industry=info["industry"],
            market_cap=info["market_cap"],
            current_price=price["current_price"],
            low=price["low"],
            high=price["high"],
            volume=price["volume"],
            pe_ratio=info["pe_ratio"],
            dividend_yield=info["dividend_yield"],
            beta=info["beta"],
            week_low=info["52_week_low"],
            week_high=info["52_week_high"],
            price_change=historical["price_change"],
            volatility=historical["volatility"],
            trend_sma50=historical["trend_sma50"],
            trend_sma200=historical["trend_sma200"],
            highest_price=historical["highest_price"],
            lowest_price=historical["lowest_price"],
            avg_volume=historical["avg_volume"]
        )

    report += "\nRecent News and Sentiment Analysis:\n"
    for item in data["sentiments"]:
        report += """
        Title: {title}
        Publisher: {publisher}
        Link: {url}
        Published Time: {published_time}
        Sentiment: {sentiment} (Confidence: {confidence:.2f})

        """.format(
            title=item["title"],
            publisher=item["publisher"],
            url=item["link"],
            published_time=item["published_time"],
            sentiment=item["sentiment"],
            confidence=item["confidence"]
        )
    return report

class Tools:
    """Finance tools combining Yahoo Finance and Finnhub capabilities"""
    
    class UserValves(BaseModel):
        FINNHUB_API_KEY: str = Field(default="", description="API key for Finnhub")

    def __init__(self):
        pass

    async def analyze_asset(
        self,
        ticker: str,
        __user__: dict = {},
        __event_emitter__: Callable[[Any], Awaitable[None]] = None,
    ) -> str:
        """
        Perform a comprehensive analysis and compile a detailed report for a given stock or cryptocurrency ticker.
        
        :param ticker: The asset ticker symbol (e.g., "AAPL" for Apple Inc. or "BTC-USD" for Bitcoin)
        :return: A comprehensive analysis report of the asset as a formatted string
        """
        await __event_emitter__({"type": "status", "data": {"description": "Initializing analysis", "done": False}})
        
        await __event_emitter__({"type": "status", "data": {"description": "Retrieving asset data", "done": False}})
        price_history = _get_historical_data(ticker)
        tech_data = _get_rsi_macd(ticker)
        
        data = await _async_gather_asset_data(ticker)
        
        await __event_emitter__({"type": "status", "data": {"description": "Compiling asset report", "done": False}})
        report = _compile_report(data, price_history, tech_data)
        
        last_price = data["current_price"]["current_price"]
        asset_type = "cryptocurrency" if data["asset_info"]["is_crypto"] else "stock"
        await __event_emitter__({
            "type": "status",
            "data": {
                "description": f"Finished creating report for {asset_type} - latest price: ${last_price:.4f}",
                "done": True
            }
        })
        return report 