import requests
from bs4 import BeautifulSoup
import feedparser
import pandas as pd
from datetime import datetime
import json
import time
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinanceNewsScraper:
    """
    Scrape financial news from multiple sources and extract relevant stock information
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.tickers = [
            'AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
            'ORCL', 'IBM', 'CRM', 'QCOM', 'ADBE', 'UBER', 'SNOW', 'PLTR', 'PYPL', 'SHOP',
            'SPY', 'QQQ', 'DIA', 'IWM', 'XLF', 'XLK', 'SMH'
        ]
        self.company_keywords = {
            'APPLE': 'AAPL',
            'TESLA': 'TSLA',
            'MICROSOFT': 'MSFT',
            'GOOGLE': 'GOOGL',
            'ALPHABET': 'GOOGL',
            'AMAZON': 'AMZN',
            'META': 'META',
            'FACEBOOK': 'META',
            'NVIDIA': 'NVDA',
            'NETFLIX': 'NFLX',
            'ADVANCED MICRO DEVICES': 'AMD',
            'AMD': 'AMD',
            'INTEL': 'INTC',
            'ORACLE': 'ORCL',
            'IBM': 'IBM',
            'SALESFORCE': 'CRM',
            'QUALCOMM': 'QCOM',
            'ADOBE': 'ADBE',
            'UBER': 'UBER',
            'SNOWFLAKE': 'SNOW',
            'PALANTIR': 'PLTR',
            'PAYPAL': 'PYPL',
            'SHOPIFY': 'SHOP',
        }
        self.market_keywords = {
            'STOCK FUTURES': 'SPY',
            'EQUITY FUTURES': 'SPY',
            'MARKET FUTURES': 'SPY',
            'S&P 500': 'SPY',
            'NASDAQ': 'QQQ',
            'TECH SHARES': 'QQQ',
            'TECH STOCKS': 'QQQ',
            'DOW': 'DIA',
            'SMALL CAP': 'IWM',
            'FINANCIALS': 'XLF',
            'BANKS': 'XLF',
            'SEMICONDUCTORS': 'SMH',
            'CHIPS': 'SMH',
            'TECH': 'XLK',
            'MARKET': 'SPY',
            'SHARES': 'SPY',
            'STOCKS': 'SPY',
        }
        
        # RSS feeds and web sources
        self.rss_feeds = [
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://feeds.cnbc.com/cnbcnews/',
            'https://www.reuters.com/rssFeed/topNews',
            'https://www.reuters.com/rssFeed/businessNews',
            'https://www.theguardian.com/business/rss',
            'https://seekingalpha.com/feed.xml',
            'https://www.ft.com/?format=rss',
        ]
        
        self.web_sources = [
            {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com/technology/',
                'selector': '.LatestNews-item'
            },
            {
                'name': 'MarketWatch',
                'url': 'https://www.marketwatch.com/investing/',
                'selector': '.element--article'
            },
        ]

    def scrape_rss_feeds(self):
        """Scrape news from RSS feeds"""
        articles = []
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Scraping RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:  # Get top entries (up to 20)
                    article = {
                        'title': entry.get('title', 'N/A'),
                        'summary': entry.get('summary', '')[:500],
                        'link': entry.get('link', ''),
                        'published': entry.get('published', datetime.now().isoformat()),
                        'source': feed.feed.get('title', 'RSS Feed'),
                        'ticker': self._extract_ticker(entry.get('title', '') + ' ' + entry.get('summary', '')),
                        'sentiment': 'neutral',  # Will be updated with sentiment analysis
                    }
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Error scraping RSS feed {feed_url}: {e}")
                continue
        
        return articles

    def scrape_web_sources(self):
        """Scrape news from web sources using BeautifulSoup"""
        articles = []
        
        for source in self.web_sources:
            try:
                logger.info(f"Scraping {source['name']}")
                response = requests.get(source['url'], headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                items = soup.select(source['selector'])
                
                for item in items[:5]:  # Get top 5 from each source
                    title_elem = item.find(['h2', 'h3', 'a'])
                    title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                    
                    link_elem = item.find('a')
                    link = urljoin(source['url'], link_elem['href']) if link_elem and link_elem.get('href') else ''
                    
                    summary_elem = item.find(['p', 'span'])
                    summary = summary_elem.get_text(strip=True)[:500] if summary_elem else ''
                    
                    article = {
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'published': datetime.now().isoformat(),
                        'source': source['name'],
                        'ticker': self._extract_ticker(title + ' ' + summary),
                        'sentiment': 'neutral',
                    }
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
                continue
        
        return articles

    def _extract_ticker(self, text):
        """
        Extract stock ticker from text.
        Returns the first matching ticker found in text, or 'GENERAL' if none found.
        """
        text_upper = text.upper()
        for ticker in self.tickers:
            if ticker in text_upper:
                return ticker

        for keyword, ticker in self.company_keywords.items():
            if keyword in text_upper:
                return ticker

        for keyword, ticker in self.market_keywords.items():
            if keyword in text_upper:
                return ticker

        return 'GENERAL'

    def _is_stock_related(self, article):
        """Keep only articles tied to stocks or listed companies."""
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        ticker = self._extract_ticker(text)
        return ticker != 'GENERAL'

    def _analyze_sentiment(self, text):
        """
        Simple sentiment analysis (can be enhanced with TextBlob or transformers)
        """
        positive_words = ['bullish', 'gains', 'surge', 'rally', 'profit', 'growth', 'boost']
        negative_words = ['bearish', 'loss', 'crash', 'plunge', 'decline', 'fall', 'drops']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def scrape_all(self):
        """Scrape from all sources and combine results"""
        logger.info("Starting comprehensive news scraping...")
        
        # Scrape RSS feeds
        articles = self.scrape_rss_feeds()
        
        # Scrape web sources
        articles.extend(self.scrape_web_sources())
        
        # Analyze sentiment for each article
        for article in articles:
            text = article['title'] + ' ' + article['summary']
            article['sentiment'] = self._analyze_sentiment(text)
        
        # Remove duplicates based on title
        unique_articles = []
        seen_titles = set()
        for article in articles:
            if article['title'] not in seen_titles and self._is_stock_related(article):
                unique_articles.append(article)
                seen_titles.add(article['title'])
        
        logger.info(f"Scraped {len(unique_articles)} unique articles")
        return pd.DataFrame(unique_articles)

    def save_to_json(self, df, filepath='data/bronze/news_raw.json'):
        """Save scraped news to JSON file"""
        df.to_json(filepath, orient='records', indent=4, date_format='iso')
        logger.info(f"News saved to {filepath}")

    def get_news_by_ticker(self, ticker, df=None):
        """Filter news by specific ticker"""
        if df is None:
            df = self.scrape_all()
        return df[df['ticker'] == ticker]


def main():
    """Main execution function"""
    scraper = FinanceNewsScraper()
    
    # Scrape all news
    news_df = scraper.scrape_all()
    
    # Display sample
    print("\n=== SAMPLE SCRAPED NEWS ===")
    print(news_df.head(5).to_string())
    
    # Save to file
    scraper.save_to_json(news_df)
    
    # Show stats by ticker
    print("\n=== NEWS BY TICKER ===")
    print(news_df['ticker'].value_counts())


if __name__ == "__main__":
    main()
