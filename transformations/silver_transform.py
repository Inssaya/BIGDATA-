import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_and_clean_stocks(input_path="data/bronze/aapl_stock.json", 
                              output_path="data/silver/aapl_cleaned.json"):
    """
    Transform Bronze → Silver: Clean and validate stock data
    """
    try:
        logger.info(f"Loading data from {input_path}")
        df = pd.read_json(input_path)
        
        # KEEP only important columns
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        
        # CONVERT Date column
        df["Date"] = pd.to_datetime(df["Date"])
        
        # REMOVE missing values
        df = df.dropna()
        
        # SAVE cleaned data into Silver layer
        df.to_json(
            output_path,
            orient="records",
            indent=4,
            date_format="iso"
        )
        
        logger.info(f"Cleaned {len(df)} records to {output_path}")
        return df
        
    except Exception as e:
        logger.error(f"Error cleaning stock data: {e}")
        return None


# Backward compatibility - old script format
if __name__ == "__main__":
    df = pd.read_json("data/bronze/aapl_stock.json")
    
    print("Original Data:")
    print(df)
    
    df = extract_and_clean_stocks()
    print("\nCleaned data saved to Silver layer!")