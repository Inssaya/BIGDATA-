import pandas as pd
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_news_data(input_path='data/bronze/news_raw.json', output_path='data/silver/news_cleaned.json'):
    """
    Clean and validate news data from bronze layer
    
    Operations:
    - Remove duplicates
    - Validate required fields
    - Standardize date format
    - Remove empty/null records
    """
    try:
        logger.info(f"Loading news from {input_path}")
        df = pd.read_json(input_path)
        
        # Remove rows with missing critical fields
        required_fields = ['title', 'source', 'ticker']
        df = df.dropna(subset=required_fields)
        
        # Remove duplicates based on title
        df = df.drop_duplicates(subset=['title'], keep='first')
        
        # Standardize date format
        if 'published' in df.columns:
            df['published'] = pd.to_datetime(df['published'], errors='coerce')
        
        # Ensure sentiment is valid
        valid_sentiments = ['positive', 'negative', 'neutral']
        df.loc[~df['sentiment'].isin(valid_sentiments), 'sentiment'] = 'neutral'
        
        # Add processing timestamp
        df['processed_at'] = datetime.now().isoformat()
        
        logger.info(f"Cleaned {len(df)} news records")
        
        # Save to silver layer
        df.to_json(output_path, orient='records', indent=4, date_format='iso')
        logger.info(f"Cleaned news saved to {output_path}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error cleaning news data: {e}")
        return None


def create_news_analytics(input_path='data/silver/news_cleaned.json', 
                          output_path='data/gold/news_analytics.json'):
    """
    Create analytics/aggregations from cleaned news data
    
    Metrics:
    - Total news count per ticker
    - Sentiment distribution
    - News sources distribution
    - Latest news timestamp
    """
    try:
        logger.info(f"Creating news analytics from {input_path}")
        df = pd.read_json(input_path)
        
        analytics = {
            'total_articles': len(df),
            'unique_tickers': df['ticker'].nunique(),
            'news_by_ticker': df['ticker'].value_counts().to_dict(),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
            'top_sources': df['source'].value_counts().head(5).to_dict(),
            'latest_news_date': df['published'].max() if 'published' in df.columns else datetime.now().isoformat(),
            'generated_at': datetime.now().isoformat(),
        }
        
        analytics_df = pd.DataFrame([analytics])
        
        # Save to gold layer
        analytics_df.to_json(output_path, orient='records', indent=4, date_format='iso')
        logger.info(f"News analytics saved to {output_path}")
        
        print("\n=== NEWS ANALYTICS ===")
        print(f"Total Articles: {analytics['total_articles']}")
        print(f"Unique Tickers: {analytics['unique_tickers']}")
        print(f"\nNews by Ticker: {analytics['news_by_ticker']}")
        print(f"\nSentiment: {analytics['sentiment_distribution']}")
        
        return analytics_df
        
    except Exception as e:
        logger.error(f"Error creating news analytics: {e}")
        return None


def main():
    """Test transformation functions"""
    print("=== SILVER TRANSFORMATION ===")
    clean_news_data()
    
    print("\n=== GOLD TRANSFORMATION ===")
    create_news_analytics()


if __name__ == "__main__":
    main()
