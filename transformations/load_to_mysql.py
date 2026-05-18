import os
import pandas as pd
from sqlalchemy import create_engine


def load_stocks_to_mysql(input_path: str = "data/gold/aapl_analytics.json") -> bool:
    """
    Load Gold analytics JSON into MySQL table `stock_analytics`.

    Returns True on success, False on failure.
    """
    try:
        df = pd.read_json(input_path)

        # MYSQL connection
        username = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", os.getenv("MYSQL_ROOT_PASSWORD", ""))
        host = os.getenv("MYSQL_HOST", "127.0.0.1")
        port = os.getenv("MYSQL_PORT", "3307")
        database = os.getenv("MYSQL_DATABASE", "bigdata_project")

        # CREATE connection engine
        connection_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_url)

        # SEND data to MySQL
        df.to_sql(name="stock_analytics", con=engine, if_exists="replace", index=False)

        engine.dispose()
        print("Data loaded into MySQL successfully!")
        return True

    except Exception as e:
        print(f"Error loading stocks to MySQL: {e}")
        return False


if __name__ == "__main__":
    # Allow quick local execution for debugging
    success = load_stocks_to_mysql()
    raise SystemExit(0 if success else 1)