import os

import pandas as pd
from sqlalchemy import create_engine

# LOAD Gold analytics data
df = pd.read_json("data/gold/aapl_analytics.json")

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
df.to_sql(
    name="stock_analytics",
    con=engine,
    if_exists="replace",
    index=False
)

print("Data loaded into MySQL successfully!")