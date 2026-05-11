import streamlit as st
import os

import altair as alt
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")

# MySQL connection
username = os.getenv("MYSQL_USER", "root")
password = os.getenv("MYSQL_PASSWORD", os.getenv("MYSQL_ROOT_PASSWORD", ""))
host = os.getenv("MYSQL_HOST", "127.0.0.1")
port = os.getenv("MYSQL_PORT", "3307")
database = os.getenv("MYSQL_DATABASE", "bigdata_project")

connection_url = URL.create(
    "mysql+pymysql",
    username=username,
    password=password,
    host=host,
    port=int(port),
    database=database,
)
engine = create_engine(connection_url)


@st.cache_data(show_spinner=False)
def load_data(_refresh_token=0):
    return pd.read_sql("SELECT * FROM stock_analytics", engine)


def find_symbol_column(frame):
    symbol_candidates = ["ticker", "symbol", "stock_symbol", "stock", "stock_ticker"]
    lower_map = {column.lower(): column for column in frame.columns}
    for candidate in symbol_candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    return None


def find_column(frame, candidates):
    lower_map = {column.lower(): column for column in frame.columns}
    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    return None


@st.cache_data(show_spinner=False, ttl=120)
def load_market_timeseries(symbol, period):
    history = yf.Ticker(symbol).history(period=period, interval="1d")
    if history.empty:
        return pd.DataFrame()

    market_df = history.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    market_df["Date"] = pd.to_datetime(market_df["Date"], errors="coerce").dt.tz_localize(None)
    market_df = market_df.dropna(subset=["Date", "Open", "High", "Low", "Close", "Volume"])
    return market_df


if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0


st.title("Stock Analytics Dashboard")
st.caption("Real-time stock analytics from the stock_analytics table")

if st.button("Refresh Data"):
    st.session_state.refresh_count += 1

df = load_data(st.session_state.refresh_count)

if df.empty:
    st.warning("No data found in stock_analytics.")
    st.stop()

stock_options = ["AAPL", "TSLA", "MSFT", "AMZN", "GOOG", "META", "NFLX", "NVDA", "IBM", "ORCL"]

st.subheader("Stock Selector Section")
selector_col_1, selector_col_2 = st.columns([2, 1])
with selector_col_1:
    selected_stock = st.selectbox("Select Stock", stock_options, index=0)
with selector_col_2:
    timeframe_label = st.selectbox("Timeframe", ["7D", "1M", "3M", "6M", "1Y"], index=1)

timeframe_map = {"7D": "7d", "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y"}

symbol_column = find_symbol_column(df)
data_source_label = "MySQL (stock_analytics)"
if symbol_column:
    filtered_df = df[df[symbol_column].astype(str).str.upper() == selected_stock].copy()
else:
    filtered_df = pd.DataFrame()

market_df = load_market_timeseries(selected_stock, timeframe_map[timeframe_label])
has_db_stock_rows = not filtered_df.empty

if has_db_stock_rows:
    latest_row = filtered_df.iloc[-1]
    avg_close_value = float(latest_row.get("average_close", 0))
    highest_price_value = float(latest_row.get("highest_price", 0))
    lowest_price_value = float(latest_row.get("lowest_price", 0))
    total_volume_value = float(latest_row.get("total_volume", 0))
    table_df = filtered_df
else:
    data_source_label = "Live market feed (fallback)"

    if market_df.empty:
        st.warning(f"No database rows or live market data found for {selected_stock}.")
        st.stop()

    avg_close_value = float(market_df["Close"].mean())
    highest_price_value = float(market_df["High"].max())
    lowest_price_value = float(market_df["Low"].min())
    total_volume_value = float(market_df["Volume"].sum())
    latest_row = pd.Series(
        {
            "average_close": avg_close_value,
            "highest_price": highest_price_value,
            "lowest_price": lowest_price_value,
            "total_volume": total_volume_value,
        }
    )
    table_df = market_df.copy()

st.caption(f"Data Source: {data_source_label}")

st.subheader("KPI Section")
metric_columns = st.columns(4)
metric_columns[0].metric("Average Close", round(avg_close_value, 2))
metric_columns[1].metric("Highest Price", round(highest_price_value, 2))
metric_columns[2].metric("Lowest Price", round(lowest_price_value, 2))
metric_columns[3].metric("Total Volume", int(total_volume_value))

st.subheader("Charts Section")
if not market_df.empty:
    market_df["candle_color"] = market_df.apply(
        lambda row: "Bull" if row["Close"] >= row["Open"] else "Bear", axis=1
    )

    st.markdown("**Price Action (Crypto-Style Candlestick)**")

    base_chart = alt.Chart(market_df).encode(
        x=alt.X("Date:T", title="Date"),
        color=alt.Color(
            "candle_color:N",
            scale=alt.Scale(domain=["Bull", "Bear"], range=["#14b8a6", "#ef4444"]),
            legend=None,
        ),
    )
    wick_chart = base_chart.mark_rule().encode(y=alt.Y("Low:Q", title="Price"), y2="High:Q")
    body_chart = base_chart.mark_bar(size=8).encode(y="Open:Q", y2="Close:Q")
    st.altair_chart((wick_chart + body_chart).interactive(), use_container_width=True)

    trend_col, volume_col = st.columns(2)
    with trend_col:
        st.markdown("**Close Trend**")
        st.line_chart(market_df.set_index("Date")[["Close"]], use_container_width=True)

    with volume_col:
        st.markdown("**Volume**")
        volume_chart = (
            alt.Chart(market_df)
            .mark_bar()
            .encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Volume:Q", title="Volume"),
                color=alt.Color(
                    "candle_color:N",
                    scale=alt.Scale(domain=["Bull", "Bear"], range=["#14b8a6", "#ef4444"]),
                    legend=None,
                ),
            )
            .interactive()
        )
        st.altair_chart(volume_chart, use_container_width=True)
else:
    st.info("Market time-series is unavailable for this symbol right now. Showing fallback analytics chart.")
    fallback_bar = pd.DataFrame(
        {
            "metric": ["average_close", "highest_price", "lowest_price"],
            "value": [
                float(latest_row.get("average_close", 0)),
                float(latest_row.get("highest_price", 0)),
                float(latest_row.get("lowest_price", 0)),
            ],
        }
    ).set_index("metric")
    st.bar_chart(fallback_bar, use_container_width=True)

st.subheader("Table Section")
st.dataframe(table_df, use_container_width=True)