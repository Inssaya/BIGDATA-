"""
Stock Analytics Hub - Dual Navigation Dashboard

Features:
- 📰 Financial News Section: Browse scraped news with ticker filtering
- 📊 Stock Analytics Section: Traditional analytics dashboard
- One-way navigation: News → Analytics (button to view analytics for selected stock)
- Sentiment analysis for news articles
"""

import streamlit as st
import os
import pandas as pd
import yfinance as yf
import altair as alt
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

# ============= PAGE CONFIG =============
st.set_page_config(
    page_title="Stock Analytics Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= DATABASE CONNECTION =============
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

try:
    engine = create_engine(connection_url)
    db_available = True
except Exception as e:
    db_available = False
    st.warning(f"Database connection failed: {e}")


# ============= CACHE FUNCTIONS =============

@st.cache_data(show_spinner=False, ttl=300)
def load_stock_analytics():
    """Load stock analytics from MySQL"""
    try:
        return pd.read_sql("SELECT * FROM stock_analytics", engine)
    except Exception as e:
        st.warning(f"Could not load stock analytics: {e}")
        return pd.DataFrame()


def ensure_news_table_exists():
    """Create the news table if it is missing so dashboard reads never fail."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_news (
        id INT PRIMARY KEY AUTO_INCREMENT,
        ticker VARCHAR(10),
        title VARCHAR(500) NOT NULL,
        summary TEXT,
        source VARCHAR(100),
        url VARCHAR(500) UNIQUE,
        published DATETIME,
        sentiment VARCHAR(20) DEFAULT 'neutral',
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_ticker (ticker),
        INDEX idx_date (published),
        INDEX idx_sentiment (sentiment)
    )
    """

    try:
        with engine.begin() as connection:
            connection.execute(text(create_table_sql))
    except Exception as error:
        st.warning(f"Could not ensure stock_news table exists: {error}")


@st.cache_data(show_spinner=False, ttl=300)
def load_news_data(ticker_filter=None, _refresh_token=0, limit=15):
    """Load news from MySQL, optionally filtered by ticker. Returns up to `limit` rows."""
    try:
        ensure_news_table_exists()

        if ticker_filter and ticker_filter != "All":
            query = f"SELECT * FROM stock_news WHERE ticker = '{ticker_filter}' ORDER BY published DESC LIMIT {int(limit)}"
        else:
            query = f"SELECT * FROM stock_news ORDER BY published DESC LIMIT {int(limit)}"
        
        return pd.read_sql(query, engine)
    except SQLAlchemyError as error:
        st.warning(f"Could not load news data: {error}")
        return pd.DataFrame()
    except Exception as error:
        st.warning(f"Could not load news data: {error}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False, ttl=120)
def load_market_timeseries(symbol, period):
    """Load historical price data from yfinance"""
    try:
        history = yf.Ticker(symbol).history(period=period, interval="1d")
        if history.empty:
            return pd.DataFrame()

        market_df = history.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
        market_df["Date"] = pd.to_datetime(market_df["Date"], errors="coerce").dt.tz_localize(None)
        market_df = market_df.dropna(subset=["Date", "Open", "High", "Low", "Close", "Volume"])
        return market_df
    except Exception as e:
        st.warning(f"Could not load market data: {e}")
        return pd.DataFrame()


# ============= UTILITY FUNCTIONS =============

def get_sentiment_color(sentiment):
    """Return color for sentiment badge"""
    if sentiment == 'positive':
        return '🟢'
    elif sentiment == 'negative':
        return '🔴'
    else:
        return '⚪'


def format_date(date_obj):
    """Format date for display"""
    if pd.isna(date_obj):
        return "N/A"
    try:
        dt = pd.to_datetime(date_obj)
        return dt.strftime("%b %d, %Y %H:%M")
    except:
        return str(date_obj)


STOCK_UNIVERSE = [
    {"ticker": "AAPL", "name": "Apple"},
    {"ticker": "MSFT", "name": "Microsoft"},
    {"ticker": "AMZN", "name": "Amazon"},
    {"ticker": "GOOGL", "name": "Alphabet"},
    {"ticker": "META", "name": "Meta Platforms"},
    {"ticker": "NVDA", "name": "NVIDIA"},
    {"ticker": "TSLA", "name": "Tesla"},
    {"ticker": "SPY", "name": "S&P 500 ETF"},
    {"ticker": "QQQ", "name": "Nasdaq 100 ETF"},
    {"ticker": "DIA", "name": "Dow Jones ETF"},
    {"ticker": "IWM", "name": "Russell 2000 ETF"},
    {"ticker": "XLF", "name": "Financial Select Sector ETF"},
    {"ticker": "XLK", "name": "Technology Select Sector ETF"},
    {"ticker": "SMH", "name": "Semiconductor ETF"},
    {"ticker": "NFLX", "name": "Netflix"},
    {"ticker": "AMD", "name": "Advanced Micro Devices"},
    {"ticker": "INTC", "name": "Intel"},
    {"ticker": "ORCL", "name": "Oracle"},
    {"ticker": "IBM", "name": "IBM"},
    {"ticker": "CRM", "name": "Salesforce"},
    {"ticker": "QCOM", "name": "Qualcomm"},
    {"ticker": "ADBE", "name": "Adobe"},
    {"ticker": "UBER", "name": "Uber"},
    {"ticker": "SNOW", "name": "Snowflake"},
    {"ticker": "PLTR", "name": "Palantir"},
    {"ticker": "PYPL", "name": "PayPal"},
    {"ticker": "SHOP", "name": "Shopify"},
    {"ticker": "BAC", "name": "Bank of America"},
    {"ticker": "JPM", "name": "JPMorgan Chase"},
    {"ticker": "WMT", "name": "Walmart"},
    {"ticker": "DIS", "name": "Disney"},
    {"ticker": "KO", "name": "Coca-Cola"},
    {"ticker": "PEP", "name": "PepsiCo"},
    {"ticker": "XOM", "name": "Exxon Mobil"},
    {"ticker": "CVX", "name": "Chevron"},
    {"ticker": "NKE", "name": "Nike"},
    {"ticker": "COST", "name": "Costco"},
    {"ticker": "MCD", "name": "McDonald's"},
    {"ticker": "BA", "name": "Boeing"},
    {"ticker": "CAT", "name": "Caterpillar"},
    {"ticker": "GE", "name": "GE Aerospace"},
    {"ticker": "GS", "name": "Goldman Sachs"},
    {"ticker": "MS", "name": "Morgan Stanley"},
    {"ticker": "V", "name": "Visa"},
    {"ticker": "MA", "name": "Mastercard"},
    {"ticker": "LLY", "name": "Eli Lilly"},
    {"ticker": "JNJ", "name": "Johnson & Johnson"},
    {"ticker": "PFE", "name": "Pfizer"},
    {"ticker": "MRK", "name": "Merck"},
    {"ticker": "UNH", "name": "UnitedHealth"},
    {"ticker": "TMO", "name": "Thermo Fisher"},
    {"ticker": "ABT", "name": "Abbott"},
    {"ticker": "AVGO", "name": "Broadcom"},
    {"ticker": "CSCO", "name": "Cisco"},
    {"ticker": "TXN", "name": "Texas Instruments"},
    {"ticker": "SBUX", "name": "Starbucks"},
    {"ticker": "ADP", "name": "ADP"},
    {"ticker": "AMAT", "name": "Applied Materials"},
    {"ticker": "LRCX", "name": "Lam Research"},
    {"ticker": "MU", "name": "Micron"},
    {"ticker": "NOW", "name": "ServiceNow"},
    {"ticker": "PANW", "name": "Palo Alto Networks"},
    {"ticker": "CRWD", "name": "CrowdStrike"},
    {"ticker": "OKTA", "name": "Okta"},
    {"ticker": "NET", "name": "Cloudflare"},
    {"ticker": "F", "name": "Ford"},
    {"ticker": "GM", "name": "General Motors"},
    {"ticker": "NIO", "name": "NIO"},
    {"ticker": "RIVN", "name": "Rivian"},
    {"ticker": "LCID", "name": "Lucid"},
    {"ticker": "SQ", "name": "Block"},
    {"ticker": "ROKU", "name": "Roku"},
    {"ticker": "SPOT", "name": "Spotify"},
    {"ticker": "BIDU", "name": "Baidu"},
    {"ticker": "BABA", "name": "Alibaba"},
    {"ticker": "JD", "name": "JD.com"},
    {"ticker": "T", "name": "AT&T"},
    {"ticker": "VZ", "name": "Verizon"},
    {"ticker": "TMUS", "name": "T-Mobile"},
    {"ticker": "AMGN", "name": "Amgen"},
    {"ticker": "GILD", "name": "Gilead"},
    {"ticker": "VRTX", "name": "Vertex"},
    {"ticker": "REGN", "name": "Regeneron"},
    {"ticker": "ISRG", "name": "Intuitive Surgical"},
    {"ticker": "DHR", "name": "Danaher"},
    {"ticker": "MDT", "name": "Medtronic"},
    {"ticker": "CVS", "name": "CVS Health"},
    {"ticker": "HD", "name": "Home Depot"},
    {"ticker": "LOW", "name": "Lowe's"},
    {"ticker": "TGT", "name": "Target"},
    {"ticker": "AXP", "name": "American Express"},
    {"ticker": "BLK", "name": "BlackRock"},
    {"ticker": "SCHW", "name": "Charles Schwab"},
    {"ticker": "C", "name": "Citigroup"},
    {"ticker": "WFC", "name": "Wells Fargo"},
    {"ticker": "USB", "name": "U.S. Bancorp"},
    {"ticker": "PNC", "name": "PNC Financial"},
]

STOCK_LOOKUP = {item["ticker"]: item for item in STOCK_UNIVERSE}


def search_stock_universe(query_text, limit=3):
    """Return up to `limit` matching stocks by ticker or company name."""
    cleaned_query = (query_text or "").strip().lower()
    if not cleaned_query:
        return STOCK_UNIVERSE[:10]

    matches = []
    for item in STOCK_UNIVERSE:
        ticker = item["ticker"].lower()
        name = item["name"].lower()
        if ticker.startswith(cleaned_query) or cleaned_query in ticker or cleaned_query in name:
            matches.append(item)

    return matches[:limit]


# ============= INITIALIZE SESSION STATE =============

if "current_page" not in st.session_state:
    st.session_state.current_page = "📰 Financial News"

if "selected_ticker_from_news" not in st.session_state:
    st.session_state.selected_ticker_from_news = None

if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

if "news_refresh_count" not in st.session_state:
    st.session_state.news_refresh_count = 0

# Top navigation bar (replaces sidebar)
# Inject CSS for a transparent fixed top navigation bar and spacing
st.markdown(
    """
    <style>
    .topnav { position: fixed; top: 0; left: 0; right: 0; height: 64px; display:flex; align-items:center; gap:6px; padding:8px 16px; background: rgba(255,255,255,0.85); backdrop-filter: blur(6px); box-shadow: 0 2px 12px rgba(0,0,0,0.08); z-index:9999; border-bottom:1px solid rgba(0,0,0,0.06); }
    .topnav .brand { font-weight:700; font-size:18px; margin-right:8px; white-space: nowrap; }
    .topnav .navbutton { background: transparent; border: none; padding: 8px 10px; font-size:14px; cursor: pointer; color: #111827; }
    .topnav .navbutton:hover { background: rgba(0,0,0,0.04); border-radius:6px; }
    .reportview-container .main > .block-container { padding-top: 92px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# If Streamlit supports query params API, use anchors + query param; otherwise
# fall back to Streamlit buttons (more compatible).
has_qs = hasattr(st, "experimental_get_query_params")
if has_qs:
    try:
        params = st.experimental_get_query_params()
        requested = params.get("page", [None])[0]
    except Exception:
        requested = None

    if requested == "analytics":
        st.session_state.current_page = "📊 Stock Analytics"
    elif requested == "news":
        st.session_state.current_page = "📰 Financial News"

    # Render a single HTML top navigation bar using anchor links that set ?page=...
    topnav_html = '''
    <div class="topnav">
      <div class="brand">Stock Analytics Hub</div>
            <div style="display:flex; gap:4px; align-items:center">
        <a class="navlink" href="?page=news">News</a>
        <a class="navlink" href="?page=analytics">Analytics</a>
      </div>
    </div>
    '''

    st.markdown(
        """
        <style>
        .topnav { justify-content: flex-start; }
        .navlink { display:inline-block; padding:8px 12px; border-radius:8px; background: rgba(255,255,255,0.03); color: #f8fafc; text-decoration:none; font-weight:600; border:1px solid rgba(255,255,255,0.06); line-height: 1; }
        .navlink:hover { background: rgba(255,255,255,0.06); }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(topnav_html, unsafe_allow_html=True)
else:
    # Compatible fallback: center two buttons using a middle column
    left, mid, right = st.columns([0.5, 2, 0.5], gap="small")
    with mid:
        c1, c2 = st.columns([1, 1], gap="small")
        with c1:
            if st.button("News", key="top_btn_news", use_container_width=True):
                st.session_state["current_page"] = "📰 Financial News"
                st.rerun()
        with c2:
            if st.button("Analytics", key="top_btn_analytics", use_container_width=True):
                st.session_state["current_page"] = "📊 Stock Analytics"
                st.rerun()


# ============= NEWS SECTION =============

def show_news_section():
    st.title("📰 Financial News Hub")
    st.markdown("Browse latest financial news with sentiment analysis")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        ticker_filter = st.selectbox(
            "Filter by Ticker",
            ["All", "AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "GENERAL"],
            index=0,
            key="news_ticker_filter"
        )
    
    with col2:
        sentiment_filter = st.selectbox(
            "Filter by Sentiment",
            ["All", "positive", "negative", "neutral"],
            index=0,
            key="news_sentiment_filter"
        )
    
    with col3:
        if st.button("🔄 Refresh News", key="refresh_news_btn"):
            st.session_state.news_refresh_count += 1
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Load news
    news_df = load_news_data(
        ticker_filter if ticker_filter != "All" else None,
        st.session_state.news_refresh_count,
        limit=15,
    )

    if not news_df.empty and "ticker" in news_df.columns:
        news_df = news_df[news_df["ticker"].astype(str).str.upper() != "GENERAL"].copy()
    
    if news_df.empty:
        st.info("📭 No stock-related news articles found yet. Try refreshing or scrape more company-specific sources.")
        return
    
    # Apply sentiment filter
    if sentiment_filter != "All":
        news_df = news_df[news_df['sentiment'] == sentiment_filter]
    
    if news_df.empty:
        st.info(f"📭 No {sentiment_filter} articles found.")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📰 Total Articles", len(news_df))
    col2.metric("🟢 Positive", len(news_df[news_df['sentiment'] == 'positive']))
    col3.metric("⚪ Neutral", len(news_df[news_df['sentiment'] == 'neutral']))
    col4.metric("🔴 Negative", len(news_df[news_df['sentiment'] == 'negative']))
    
    st.markdown("---")
    
    # Display articles
    st.subheader("Latest Articles")
    
    for idx, row in news_df.iterrows():
        with st.container(border=True):
            # Header with ticker and sentiment
            header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
            
            with header_col1:
                st.markdown(f"**{row['title']}**")
            
            with header_col2:
                ticker_badge = f"`{row['ticker']}`"
                st.markdown(ticker_badge)
            
            with header_col3:
                sentiment_emoji = get_sentiment_color(row['sentiment'])
                st.markdown(f"{sentiment_emoji} {row['sentiment'].upper()}")
            
            # Body
            st.write(row['summary'][:300] + "..." if len(str(row['summary'])) > 300 else row['summary'])
            
            # Footer
            footer_col1, footer_col2, footer_col3, footer_col4 = st.columns([2, 2, 1, 1])
            
            with footer_col1:
                st.caption(f"📰 {row['source']}")
            
            with footer_col2:
                st.caption(f"📅 {format_date(row['published'])}")
            
            with footer_col3:
                if st.button("🔗 Read More", key=f"read_{idx}", use_container_width=True):
                    if pd.notna(row['url']):
                        st.markdown(f"[Open Article]({row['url']})")
            
            with footer_col4:
                if st.button("📊 Analytics", key=f"analytics_{idx}", use_container_width=True):
                    st.session_state.selected_ticker_from_news = row['ticker']
                    st.session_state.current_page = "📊 Stock Analytics"
                    st.rerun()


# ============= ANALYTICS SECTION =============

def show_analytics_section():
    st.title("📊 Stock Analytics Dashboard")
    st.caption("Real-time stock analytics from market data and database")
    
    # Navigation info
    if st.session_state.selected_ticker_from_news:
        st.info(f"📰 Viewing analytics for ticker from news: **{st.session_state.selected_ticker_from_news}**")
    
    # Refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Data", key="refresh_analytics_btn"):
            st.session_state.refresh_count += 1
            st.rerun()
    
    st.markdown("---")
    
    # Stock selector
    st.subheader("📈 Stock Selector")
    selector_col_1, selector_col_2 = st.columns([2, 1])

    search_query = st.text_input(
        "Search stocks",
        value="",
        placeholder="Type a ticker or company name",
        key="stock_search_query",
    )

    search_matches = search_stock_universe(search_query, limit=3)
    stock_options = [f"{item['ticker']} - {item['name']}" for item in (search_matches if search_query.strip() else STOCK_UNIVERSE[:10])]
    if not stock_options:
        stock_options = [f"{item['ticker']} - {item['name']}" for item in STOCK_UNIVERSE[:10]]
    
    with selector_col_1:
        default_index = 0
        if st.session_state.selected_ticker_from_news:
            try:
                ticker = st.session_state.selected_ticker_from_news
                preferred_label = f"{ticker} - {STOCK_LOOKUP.get(ticker, {}).get('name', '')}".strip(" -")
                if preferred_label in stock_options:
                    default_index = stock_options.index(preferred_label)
                st.session_state.selected_ticker_from_news = None  # Reset
            except ValueError:
                default_index = 0
        
        selected_stock = st.selectbox(
            "Select Stock",
            stock_options,
            index=default_index,
            key="stock_selector"
        )

    selected_stock_ticker = selected_stock.split(" - ")[0].strip()
    
    with selector_col_2:
        timeframe_label = st.selectbox(
            "Timeframe",
            ["7D", "1M", "3M", "6M", "1Y"],
            index=1,
            key="timeframe_selector"
        )
    
    timeframe_map = {"7D": "7d", "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y"}
    
    # Load data
    df = load_stock_analytics()
    market_df = load_market_timeseries(selected_stock_ticker, timeframe_map[timeframe_label])
    
    # Determine data source and metrics
    data_source_label = "Live market feed"
    
    if not df.empty:
        filtered_df = df[df.get('ticker', '').astype(str).str.upper() == selected_stock_ticker].copy() if 'ticker' in df.columns else pd.DataFrame()
        if not filtered_df.empty:
            latest_row = filtered_df.iloc[-1]
            avg_close_value = float(latest_row.get("average_close", 0))
            highest_price_value = float(latest_row.get("highest_price", 0))
            lowest_price_value = float(latest_row.get("lowest_price", 0))
            total_volume_value = float(latest_row.get("total_volume", 0))
            data_source_label = "MySQL Database"
        else:
            if market_df.empty:
                st.warning(f"No data found for {selected_stock}")
                return
            
            avg_close_value = float(market_df["Close"].mean())
            highest_price_value = float(market_df["High"].max())
            lowest_price_value = float(market_df["Low"].min())
            total_volume_value = float(market_df["Volume"].sum())
    else:
        if market_df.empty:
            st.warning(f"No data found for {selected_stock_ticker}")
            return
        
        avg_close_value = float(market_df["Close"].mean())
        highest_price_value = float(market_df["High"].max())
        lowest_price_value = float(market_df["Low"].min())
        total_volume_value = float(market_df["Volume"].sum())
    
    st.caption(f"Data Source: {data_source_label}")
    if search_query.strip() and len(search_matches) == 3:
        st.caption("Showing 3 matching suggestions. Refine the search to see different results.")
    
    # KPIs
    st.subheader("📌 Key Performance Indicators")
    metric_columns = st.columns(4)
    metric_columns[0].metric("💰 Avg Close", f"${avg_close_value:.2f}")
    metric_columns[1].metric("📈 High Price", f"${highest_price_value:.2f}")
    metric_columns[2].metric("📉 Low Price", f"${lowest_price_value:.2f}")
    metric_columns[3].metric("📊 Total Volume", f"{int(total_volume_value):,}")
    
    # Charts
    st.subheader("📈 Price Charts")
    
    if not market_df.empty:
        market_df["candle_color"] = market_df.apply(
            lambda row: "Bull" if row["Close"] >= row["Open"] else "Bear", axis=1
        )
        
        # Candlestick chart
        st.markdown("**Candlestick Chart**")
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
        
        # Trend and Volume
        trend_col, volume_col = st.columns(2)
        
        with trend_col:
            st.markdown("**Close Price Trend**")
            st.line_chart(market_df.set_index("Date")[["Close"]], use_container_width=True)
        
        with volume_col:
            st.markdown("**Trading Volume**")
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
    
    # Data table
    st.subheader("📋 Data Table")
    if not market_df.empty:
        st.dataframe(market_df, use_container_width=True)


# ============= MAIN ROUTING =============

if st.session_state.current_page == "📰 Financial News":
    show_news_section()
else:
    show_analytics_section()


# ============= FOOTER =============
st.markdown("---")
st.caption("🔐 All data is securely fetched from MySQL and live market sources | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))