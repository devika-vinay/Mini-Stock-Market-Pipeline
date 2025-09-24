import sqlite3
from datetime import date, timedelta

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from pipeline import run_pipeline

st.set_page_config(page_title="Mini Pipeline", page_icon="📈", layout="wide")
st.title("Mini Data Pipeline & Analytics Demo")

with st.sidebar:
    st.header("Run Pipeline")
    tickers = st.text_input("Tickers (comma-separated)", value="RY.TO,TD.TO")
    default_start = (date.today() - timedelta(days=90))
    start = st.date_input("Start date", value=default_start)
    end = st.date_input("End date", value=date.today())
    db_path = st.text_input("SQLite DB path", value="mini_pipeline.db")
    run_btn = st.button("Run")

if run_btn:
    with st.spinner("Running pipeline"):
        summary, counts = run_pipeline(
            tickers=tickers,
            start=start.isoformat(),
            end=end.isoformat(),
            db_path=db_path,
        )
    st.success("Loaded: " + ", ".join([f"{t}:{n}" for t, n in counts]))
    st.session_state["db_path"] = db_path
    st.session_state["last_summary"] = summary


# Show summary if available
summary = st.session_state.get("last_summary")
db_path = st.session_state.get("db_path", "mini_pipeline.db")

st.subheader("Latest Metrics by Ticker")
if isinstance(summary, pd.DataFrame) and not summary.empty:
    st.dataframe(summary, use_container_width=True)
else:
    st.info("Run the pipeline from the left sidebar to populate data.")

# Simple chart: pick a ticker and plot price vs MAs
st.subheader("Chart: Price & Moving Averages")
sel_ticker = st.text_input("Ticker to chart", value="RY.TO")
if st.button("Show Chart"):
    try:
        con = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT date, adj_close, ma_20, ma_50 FROM prices WHERE ticker=? ORDER BY date;",
            con, params=[sel_ticker]
        )
        con.close()
        if df.empty:
            st.warning("No data for that ticker. Try running the pipeline or another ticker.")
        else:
            df["date"] = pd.to_datetime(df["date"])
            fig = plt.figure()
            plt.plot(df["date"], df["adj_close"], label="Adj Close")
            plt.plot(df["date"], df["ma_20"], label="MA20")
            plt.plot(df["date"], df["ma_50"], label="MA50")
            plt.legend(); plt.title(f"{sel_ticker} — Price & MAs")
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Chart error: {e}")

# Optional: export summary
if summary is not None and not summary.empty:
    st.download_button(
        label="Download summary CSV",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="latest_metrics.csv",
        mime="text/csv"
    )
