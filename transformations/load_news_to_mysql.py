import os
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_news_table(connection_url):
    """
    Create stock_news table if it doesn't exist
    """
    engine = create_engine(connection_url)
    
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
        with engine.connect() as connection:
            connection.execute(text(create_table_sql))
            connection.commit()
            logger.info("stock_news table created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
    finally:
        engine.dispose()


def load_news_to_mysql(input_path='data/silver/news_cleaned.json'):
    """
    Load cleaned news data into MySQL database
    """
    
    # MySQL connection details
    username = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", os.getenv("MYSQL_ROOT_PASSWORD", ""))
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3307")
    database = os.getenv("MYSQL_DATABASE", "bigdata_project")
    
    connection_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    
    try:
        logger.info(f"Loading news from {input_path}")
        
        # Create table first
        create_news_table(connection_url)
        
        # Read cleaned news
        df = pd.read_json(input_path)
        
        # Rename columns to match database schema
        df = df.rename(columns={
            'link': 'url',
            'published': 'published',
        })
        
        # Ensure required columns exist
        for col in ['ticker', 'title', 'summary', 'source', 'url', 'sentiment']:
            if col not in df.columns:
                df[col] = None
        
        # Select only relevant columns
        df = df[['ticker', 'title', 'summary', 'source', 'url', 'published', 'sentiment']]
        
        # Create engine and load
        engine = create_engine(connection_url)

        # Normalize datetimes and replace NaN/NaT with None for DB compatibility
        if 'published' in df.columns:
            df['published'] = pd.to_datetime(df['published'], errors='coerce')

        # Replace pandas NA/NaT/NaN with Python None so pymysql can handle inserts
        df = df.where(pd.notnull(df), None)

        if df.empty:
            logger.info("No cleaned news rows found in the silver file.")
            engine.dispose()
            return

        upsert_sql = text(
            """
            INSERT INTO stock_news (ticker, title, summary, source, url, published, sentiment)
            VALUES (:ticker, :title, :summary, :source, :url, :published, :sentiment)
            ON DUPLICATE KEY UPDATE
                ticker = VALUES(ticker),
                title = VALUES(title),
                summary = VALUES(summary),
                source = VALUES(source),
                published = VALUES(published),
                sentiment = VALUES(sentiment)
            """
        )

        with engine.begin() as connection:
            for _, row in df.iterrows():
                connection.execute(upsert_sql, row.to_dict())

        logger.info(f"Successfully upserted {len(df)} news articles to MySQL")
        
        # Show summary
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) as count FROM stock_news"))
            count = result.fetchone()[0]
            logger.info(f"Total articles in database: {count}")
        
        engine.dispose()
        
    except Exception as e:
        logger.error(f"Error loading news to MySQL: {e}")
        raise


def main():
    """Main execution"""
    logger.info("Starting news loading to MySQL...")
    load_news_to_mysql()
    logger.info("News loading completed!")


if __name__ == "__main__":
    main()
