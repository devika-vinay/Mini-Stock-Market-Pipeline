"""
Mini Data Pipeline
- Pulls OHLCV data for one or more tickers from Yahoo Finance
- Computes returns
- Loads curated tables into SQLite
"""
import logging
import sqlite3
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path


DB_SCHEMA = {
    "prices": """
        CREATE TABLE IF NOT EXISTS prices (
            ticker TEXT NOT NULL,
            date   TEXT NOT NULL,
            open REAL, high REAL, low REAL, close REAL, adj_close REAL,
            volume INTEGER,
            daily_return REAL,
            ma_20 REAL,
            ma_50 REAL,
            vol_20 REAL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (ticker, date)
        );
    """,
}

def init_db(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for ddl in DB_SCHEMA.values():
        cur.execute(ddl)
    con.commit()
    return con

def seed_df_from_static(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Load a single ticker's CSV from src/data/{ticker}.csv and filter to [start, end]."""
    base_dir = Path(__file__).resolve().parent          # …/src
    path = base_dir / "data" / f"{ticker}.csv"          # …/src/data/{ticker}.csv

    if not path.exists():
        raise FileNotFoundError(f"No static CSV found at {path}")

    df = pd.read_csv(path, parse_dates=["Date"]).rename(columns={
        "Date":"date","Open":"open","High":"high","Low":"low",
        "Close":"close","Adj Close":"adj_close","Volume":"volume"
    })
    mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
    return df.loc[mask].sort_values("date").reset_index(drop=True)



def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Calculate daily returns as the percentage change of the adjusted close price
    df["daily_return"] = df["adj_close"].pct_change()

    # Calculate moving averages over periods of 20 and 50 days
    df["ma_20"] = df["adj_close"].rolling(20, min_periods=1).mean()
    df["ma_50"] = df["adj_close"].rolling(50, min_periods=1).mean()

    # Calculate rolling volatility (standard deviation of daily returns) over a 20-day window, annualized
    df["vol_20"] = df["daily_return"].rolling(20, min_periods=1).std() * np.sqrt(252)
    return df

def load_prices(con, ticker: str, df: pd.DataFrame):
    df = df.copy()
    df["ticker"] = ticker.upper()
    df["created_at"] = datetime.utcnow().isoformat()

    # Clear any existing rows for this ticker 
    cur = con.cursor()
    cur.execute("DELETE FROM prices WHERE ticker = ?", (ticker.upper(),))
    con.commit()

    # insert fresh rows
    df.to_sql(
        "prices", con,
        if_exists="append", index=False,
        method="multi", chunksize=1000
    )

def run_pipeline(tickers: str, start: str, end: str, db_path: str):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    tickers_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    con = init_db(db_path)

    # stateful behavior: keep only current selection in the DB
    if tickers_list:
        cur = con.cursor()
        placeholders = ",".join("?" * len(tickers_list))
        cur.execute(f"DELETE FROM prices WHERE ticker NOT IN ({placeholders})", tickers_list)
        con.commit()

    loaded_counts = []
    for t in tickers_list:
        logging.info("Loading static CSV for %s", t)
        df_raw = seed_df_from_static(t, start, end)
        df_feat = engineer_features(df_raw)
        load_prices(con, t, df_feat)
        loaded_counts.append((t, len(df_feat)))

    con.commit()
    con.close()

    # summary only for current selection
    con2 = sqlite3.connect(db_path)
    placeholders = ",".join("?" * len(tickers_list))
    sql = f"""
    WITH last AS (
      SELECT ticker, MAX(date) AS d
      FROM prices
      WHERE ticker IN ({placeholders})
      GROUP BY ticker
    )
    SELECT p.ticker, p.date, p.adj_close, p.ma_20, p.ma_50, p.vol_20
    FROM prices p JOIN last l ON p.ticker=l.ticker AND p.date=l.d
    ORDER BY p.vol_20 DESC;
    """
    summary = pd.read_sql_query(sql, con2, params=tickers_list)
    con2.close()
    return summary, loaded_counts
