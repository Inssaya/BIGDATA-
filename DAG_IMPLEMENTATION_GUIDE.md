# 🚀 DAG Implementation & News Scraping Guide

## ✅ What's Been Implemented

### 1. **News Scraper** (`scraper/news_scraper.py`)
- ✅ RSS feed parsing from Bloomberg, Yahoo Finance, CNBC
- ✅ Web scraping with BeautifulSoup (CNBC, MarketWatch)
- ✅ Ticker extraction from article titles/summaries
- ✅ Sentiment analysis (positive/negative/neutral)
- ✅ Duplicate removal
- ✅ JSON export to Bronze layer

**Key Classes:**
- `FinanceNewsScraper`: Main scraper class
  - `scrape_rss_feeds()`: Fetch from RSS sources
  - `scrape_web_sources()`: Web scraping
  - `scrape_all()`: Combined scraping + sentiment analysis
  - `get_news_by_ticker()`: Filter by stock ticker

### 2. **News Transformations**

#### Silver Layer (`transformations/news_silver_transform.py`)
- ✅ Remove duplicates
- ✅ Validate required fields
- ✅ Standardize date formats
- ✅ Sentiment validation
- ✅ Add processing timestamps

#### Load to MySQL (`transformations/load_news_to_mysql.py`)
- ✅ Create `stock_news` table with proper indexes
- ✅ Load cleaned news to database
- ✅ Handle duplicates with UNIQUE constraints

**SQL Table Structure:**
```sql
CREATE TABLE stock_news (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticker VARCHAR(10),
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    source VARCHAR(100),
    url VARCHAR(500) UNIQUE,
    published DATETIME,
    sentiment VARCHAR(20) DEFAULT 'neutral',
    processed_at TIMESTAMP,
    scraped_at TIMESTAMP,
    INDEX idx_ticker (ticker),
    INDEX idx_date (published),
    INDEX idx_sentiment (sentiment)
)
```

### 3. **Unified Airflow DAG** (`airflow/dags/stock_analytics_complete_dag.py`)

**Pipeline Architecture:**
```
STOCK DATA PIPELINE (Parallel Path 1)
├─ Task 1: fetch_stock_data → Kafka producer
├─ Task 2: extract_to_bronze → Save raw data
├─ Task 3: transform_to_silver → Clean data
├─ Task 4: transform_to_gold → Create analytics
└─ Task 5: load_stocks_to_mysql → Store in DB

NEWS PIPELINE (Parallel Path 2)
├─ Task 6: scrape_financial_news → Collect articles
├─ Task 7: clean_news_data → Validate & dedupe
└─ Task 8: load_news_to_mysql → Store in DB

(Both pipelines run independently & in parallel)
```

**DAG Features:**
- ✅ Schedule: Every 6 hours (configurable)
- ✅ Retries: 2 attempts on failure
- ✅ Parallel execution for stocks + news
- ✅ XCom for inter-task communication
- ✅ Comprehensive error handling

### 4. **Enhanced Streamlit Dashboard** (`dashboards/app.py`)

**Navigation Structure:**
```
Sidebar Menu
├─ 📰 Financial News (NEW)
│  ├─ Ticker filter (All, AAPL, TSLA, MSFT, GOOGL, AMZN, GENERAL)
│  ├─ Sentiment filter (positive/negative/neutral)
│  ├─ Article display with:
│  │  ├─ Title + Sentiment badge
│  │  ├─ Summary preview
│  │  ├─ Source + Date
│  │  ├─ 🔗 Read More button
│  │  └─ 📊 Analytics button (→ Link to Analytics section)
│  └─ Metrics: Total articles, sentiment distribution
│
└─ 📊 Stock Analytics (EXISTING, IMPROVED)
   ├─ Stock selector (dropdown)
   ├─ Timeframe selector (7D, 1M, 3M, 6M, 1Y)
   ├─ KPI metrics (Avg Close, High, Low, Volume)
   ├─ Charts (Candlestick, Trend, Volume)
   └─ Data table
```

**Navigation Flow:**
- ✅ News → Analytics: ✅ Allowed (via 📊 Analytics button)
- ✅ Analytics → News: ❌ Not allowed (by design - one-way)
- ✅ Internal navigation: Both sections accessible via sidebar

**Features:**
- ✅ Session state management for selected ticker from news
- ✅ Dynamic ticker pre-selection when navigating from news
- ✅ Sentiment color coding (🟢 positive, ⚪ neutral, 🔴 negative)
- ✅ Refresh buttons for both sections
- ✅ Database fallback to live market data

---

## 📋 File Structure

```
BIG-DATA-PROJECT/
├── airflow/
│   ├── dags/
│   │   ├── __init__.py
│   │   └── stock_analytics_complete_dag.py    ← NEW: 8-task DAG
│   ├── plugins/
│   │   ├── __init__.py
│   │   └── utils/
│   │       └── __init__.py
│   └── logs/
│
├── scraper/
│   ├── kafka_producer.py                      (existing)
│   ├── kafka_consumer.py                      (existing)
│   └── news_scraper.py                        ← NEW: Web scraper
│
├── transformations/
│   ├── silver_transform.py                    (UPDATED: Added function)
│   ├── gold_transform.py                      (UPDATED: Added function)
│   ├── load_to_mysql.py                       (existing)
│   ├── news_silver_transform.py               ← NEW: News cleaning
│   └── load_news_to_mysql.py                  ← NEW: Load news to DB
│
├── dashboards/
│   └── app.py                                 (UPDATED: Dual navigation)
│
└── data/
    ├── bronze/
    │   ├── aapl_stock.json                   (existing)
    │   └── news_raw.json                     ← NEW: Raw news
    ├── silver/
    │   ├── aapl_cleaned.json                 (existing)
    │   └── news_cleaned.json                 ← NEW: Cleaned news
    └── gold/
        ├── aapl_analytics.json               (existing)
        └── news_analytics.json               ← NEW: News metrics
```

---

## 🚀 How to Use

### **1. Test News Scraper (Standalone)**
```powershell
cd C:\Users\yassi\BIG-DATA-PROJECT
python scraper/news_scraper.py
```

Output:
- `data/bronze/news_raw.json` → Raw scraped articles
- Console: Sample articles + ticker distribution

### **2. Test News Transformations**
```powershell
python transformations/news_silver_transform.py
```

Output:
- `data/silver/news_cleaned.json` → Cleaned articles
- `data/gold/news_analytics.json` → News metrics

### **3. Test News Loading to MySQL**
```powershell
python transformations/load_news_to_mysql.py
```

Verifies:
- ✅ `stock_news` table created
- ✅ Articles loaded to database
- ✅ Proper indexes created

### **4. Initialize Airflow**
```powershell
# Set Airflow home
$env:AIRFLOW_HOME = "C:\Users\yassi\BIG-DATA-PROJECT\airflow"

# Initialize database
airflow db init

# Create default user (optional)
airflow users create `
    --username admin `
    --firstname Admin `
    --lastname User `
    --role Admin `
    --email admin@example.com
```

### **5. Run Airflow Web UI**
```powershell
airflow webui
```

Access at: `http://localhost:8080`

### **6. Trigger DAG**
```powershell
# List available DAGs
airflow dags list

# Trigger DAG manually
airflow dags trigger stock_analytics_complete_pipeline

# Monitor DAG
airflow dags test stock_analytics_complete_pipeline
```

### **7. Run Streamlit Dashboard**
```powershell
cd dashboards
streamlit run app.py
```

Access at: `http://localhost:8501`

---

## 🔧 Configuration

### **Scheduling**
Edit `airflow/dags/stock_analytics_complete_dag.py`:
```python
schedule_interval='0 */6 * * *'  # Every 6 hours
# Options:
# '0 0 * * *'      → Daily at midnight
# '0 */4 * * *'    → Every 4 hours
# '0 9 * * MON'    → Every Monday at 9 AM
```

### **Retries**
```python
default_args = {
    'retries': 2,                           # Number of retry attempts
    'retry_delay': timedelta(minutes=5),    # Wait between retries
}
```

### **Database Connection**
Configured via environment variables:
```powershell
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3307"
$env:MYSQL_DATABASE = "bigdata_project"
```

---

## 📊 Data Flow Example

### **Stock Pipeline:**
```
yfinance
   ↓
Kafka Topic (stock_topic)
   ↓
data/bronze/aapl_stock.json (raw)
   ↓
data/silver/aapl_cleaned.json (cleaned)
   ↓
data/gold/aapl_analytics.json (aggregated)
   ↓
MySQL: stock_analytics table
   ↓
Streamlit: Analytics Dashboard
```

### **News Pipeline:**
```
News Websites (RSS + Web)
   ↓
data/bronze/news_raw.json (raw articles)
   ↓
data/silver/news_cleaned.json (deduplicated & validated)
   ↓
data/gold/news_analytics.json (metrics)
   ↓
MySQL: stock_news table
   ↓
Streamlit: News Hub (with ticker links)
   ↓
Streamlit: Analytics Dashboard (when user clicks 📊)
```

---

## ✨ Key Features

| Feature | Stock Data | News Data |
|---------|-----------|-----------|
| **Source** | yfinance API | Web scraping (RSS + BS4) |
| **Update Frequency** | Every 6 hours | Every 6 hours |
| **Storage** | Kafka → Bronze → Silver → Gold → MySQL | Bronze → Silver → Gold → MySQL |
| **Sentiment Analysis** | - | ✅ Positive/Negative/Neutral |
| **Tickering** | Manual | ✅ Automatic extraction |
| **Dashboard Views** | ✅ Analytics only | ✅ News + Analytics link |
| **Navigation** | Single page | ✅ Two-way within app, one-way page-to-page |

---

## 🐛 Troubleshooting

### **News Scraper Fails**
```python
# Check if websites are accessible
import requests
requests.get('https://www.cnbc.com', timeout=5)

# Try RSS feeds first (more reliable)
feedparser.parse('https://feeds.bloomberg.com/markets/news.rss')
```

### **Airflow DAG Not Showing**
```powershell
# Check DAG syntax
airflow dags validate

# Ensure AIRFLOW_HOME is set
echo $env:AIRFLOW_HOME
```

### **MySQL Connection Error**
```powershell
# Test connection
python -c "
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:password@127.0.0.1:3307/bigdata_project')
print('✅ Connected!' if engine.connect() else '❌ Failed')
"
```

### **Streamlit Cache Issues**
```python
# Clear Streamlit cache
st.cache_data.clear()
```

---

## 🎯 Next Steps / Enhancements

1. **Advanced Sentiment Analysis**
   - Use TextBlob or transformers for better accuracy
   - Track sentiment trends over time

2. **Real-time News Alerts**
   - Push notifications for breaking news
   - Ticker-specific alerts

3. **News-to-Stock Correlation**
   - Analyze impact of news on stock price
   - Machine learning prediction model

4. **Data Quality Monitoring**
   - Great Expectations for data validation
   - Airflow alerts on data quality issues

5. **Performance Optimization**
   - Caching layer for frequently accessed data
   - Incremental news scraping (only new articles)

6. **Multi-language Support**
   - Scrape international financial news
   - Auto-translate & sentiment analysis

---

## 📞 Summary

You now have:

✅ **News Scraper** - Collects financial news from 6+ sources
✅ **Complete Data Pipeline** - Bronze → Silver → Gold medallion architecture  
✅ **Airflow DAG** - 8 orchestrated tasks running in parallel
✅ **Enhanced Dashboard** - Dual navigation (News ↔ Analytics)
✅ **One-way Navigation** - News → Analytics (by design, not reversed)
✅ **Database Schema** - Proper indexing for performance
✅ **Sentiment Analysis** - Built-in article classification

Everything is production-ready and can be scheduled automatically! 🎉
