import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_stock_analytics(input_path="data/silver/aapl_cleaned.json",
                           output_path="data/gold/aapl_analytics.json"):
    """
    Transform Silver → Gold: Create analytics from cleaned stock data
    """
    try:
        logger.info(f"Loading cleaned data from {input_path}")
        df = pd.read_json(input_path)
        
        # CREATE analytics
        analytics = {
            "average_close": df["Close"].mean(),
            "highest_price": df["High"].max(),
            "lowest_price": df["Low"].min(),
            "total_volume": int(df["Volume"].sum())
        }
        
        # CONVERT to DataFrame
        analytics_df = pd.DataFrame([analytics])
        
        # SAVE into Gold layer
        analytics_df.to_json(
            output_path,
            orient="records",
            indent=4
        )
        
        logger.info("Gold analytics created successfully!")
        return analytics_df
        
    except Exception as e:
        logger.error(f"Error creating analytics: {e}")
        return None


# Backward compatibility - old script format
if __name__ == "__main__":
    df = pd.read_json("data/silver/aapl_cleaned.json")
    
    create_stock_analytics()
    print("Gold analytics saved successfully!")