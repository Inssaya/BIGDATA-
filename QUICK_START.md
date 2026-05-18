# 🚀 Quick Start Guide - Testing the Implementation

## ⚡ 5-Minute Setup

### Step 1: Verify Dependencies
```powershell
cd C:\Users\yassi\BIG-DATA-PROJECT

# Activate venv
.venv\Scripts\Activate.ps1

# Verify packages installed
python -c "import beautifulsoup4, feedparser, requests; print('✅ News scraping packages OK')"
```

### Step 2: Test News Scraper
```powershell
python scraper/news_scraper.py
```

Expected output:
```
Starting comprehensive news scraping...
Scraping RSS feed: https://feeds.bloomberg.com/markets/news.rss
...
Scraped 15 unique articles
News saved to data/bronze/news_raw.json

=== NEWS BY TICKER ===
AAPL    5
TSLA    3
MSFT    2
...
```

### Step 3: Test News Transformations
```powershell
# Clean news data
python transformations/news_silver_transform.py

# Load to MySQL
python transformations/load_news_to_mysql.py
```

Expected output:
```
Cleaned 15 unique articles
Load news from data/silver/news_cleaned.json
stock_news table created/verified successfully
Successfully loaded 15 news articles to MySQL
```

### Step 4: Start Streamlit Dashboard
```powershell
cd dashboards
streamlit run app.py
```

Then:
1. Open http://localhost:8501
2. Try **📰 Financial News** tab → Select ticker, read articles
3. Click **📊 Analytics** button on any article → Should navigate to Analytics dashboard with that ticker pre-selected
4. Try **📊 Stock Analytics** tab → View charts and metrics

---

## 📝 File Checklist

✅ **Scrapers:**
- [x] `scraper/news_scraper.py` - News web scraper

✅ **Transformations:**
- [x] `transformations/news_silver_transform.py` - Clean news
- [x] `transformations/load_news_to_mysql.py` - Load news to DB
- [x] `transformations/silver_transform.py` - Updated with function
- [x] `transformations/gold_transform.py` - Updated with function

✅ **Orchestration:**
- [x] `airflow/dags/stock_analytics_complete_dag.py` - 8-task DAG

✅ **Dashboard:**
- [x] `dashboards/app.py` - Dual navigation (News + Analytics)

✅ **Documentation:**
- [x] `DAG_IMPLEMENTATION_GUIDE.md` - Comprehensive guide

---

## 🎯 What Each Component Does

### News Scraper (`news_scraper.py`)
```python
scraper = FinanceNewsScraper()
news_df = scraper.scrape_all()  # Scrapes RSS + web sources
scraper.save_to_json(news_df)   # Saves to data/bronze/
```

**Sources:**
- 📰 Bloomberg RSS
- 📰 Yahoo Finance RSS
- 📰 CNBC RSS
- 📰 CNBC website (BeautifulSoup)
- 📰 MarketWatch website (BeautifulSoup)

### News Transformations
```
Bronze (raw)
    ↓ clean_news_data()
Silver (cleaned)
    ↓ load_news_to_mysql()
MySQL (stock_news table)
```

### Airflow DAG
```
Task 1-5: Stock Pipeline (parallel)
Task 6-8: News Pipeline (parallel)
→ Both run independently every 6 hours
```

### Dashboard
```
Sidebar Navigation
├─ 📰 News Hub (NEW)
│  └─ 📊 Analytics (via button)
│
└─ 📊 Analytics (EXISTING)
   └─ ❌ Cannot go back to News
```

---

## 🔗 Navigation Demo

1. **Start at News Tab**
   ```
   📰 Financial News
   ↓ (see articles about AAPL)
   ↓ (click 📊 Analytics button)
   ↓
   📊 Stock Analytics (AAPL auto-selected)
   ↓ (view AAPL charts)
   ↓ (want to read more news? Use sidebar)
   ↓
   📰 Financial News (must use sidebar)
   ```

2. **Start at Analytics Tab**
   ```
   📊 Stock Analytics
   ↓ (view AAPL charts)
   ↓ (NO button to go to news)
   ↓ (want news? Use sidebar)
   ↓
   📰 Financial News
   ```

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: beautifulsoup4` | `pip install beautifulsoup4 feedparser requests` |
| News scraper hangs | Check internet connection; RSS feeds timeout after 10s |
| MySQL connection error | Verify XAMPP is running; check credentials |
| Streamlit not loading news | Ensure `stock_news` table exists and has data |
| DAG validation fails | Check `airflow/dags/stock_analytics_complete_dag.py` syntax |

---

## 📊 Expected Data

### `data/bronze/news_raw.json`
```json
[
  {
    "title": "Apple Stock Rallies on New iPhone Sales",
    "summary": "AAPL surges 5% on strong Q1 earnings...",
    "link": "https://...",
    "published": "2026-05-13T10:30:00",
    "source": "Bloomberg",
    "ticker": "AAPL",
    "sentiment": "positive"
  },
  ...
]
```

### MySQL `stock_news` Table
```
id  | ticker | title                    | sentiment | published
----|--------|--------------------------|-----------|----------
1   | AAPL   | Apple Stock Rallies...   | positive  | 2026-05-13
2   | TSLA   | Tesla Crypto Bet...      | neutral   | 2026-05-13
...
```

### Streamlit Dashboard
**News Tab Features:**
- Filter by ticker dropdown
- Filter by sentiment (positive/negative/neutral)
- Article cards with sentiment emoji
- "Read More" button (external link)
- "Analytics" button (navigates to Analytics with ticker pre-selected)

**Analytics Tab Features:**
- Stock selector (7 popular stocks)
- Timeframe selector (7D to 1Y)
- 4 KPI metrics (Avg, High, Low, Volume)
- Candlestick chart
- Trend & Volume charts
- Data table

---

## ✅ Success Checklist

- [ ] News scraper runs successfully
- [ ] News data saved to `data/bronze/news_raw.json`
- [ ] News loaded to MySQL `stock_news` table
- [ ] Streamlit dashboard starts without errors
- [ ] 📰 News tab displays articles
- [ ] 📊 Analytics tab displays charts
- [ ] Can navigate News → Analytics via button
- [ ] Cannot navigate Analytics → News (by design)
- [ ] Sidebar navigation works between sections
- [ ] Ticker filtering works in News tab
- [ ] Sentiment filtering works in News tab

---

## 🎯 Next: Run the DAG

Once everything is working:

```powershell
# Initialize Airflow
$env:AIRFLOW_HOME = "C:\Users\yassi\BIG-DATA-PROJECT\airflow"
airflow db init

# Start Airflow UI
airflow webui
# Visit http://localhost:8080

# Trigger DAG
airflow dags trigger stock_analytics_complete_pipeline

# Monitor execution
airflow dags test stock_analytics_complete_pipeline
```

See `DAG_IMPLEMENTATION_GUIDE.md` for detailed Airflow setup instructions.

---

Good luck! 🚀 Let me know if you hit any issues!
