# TECHNICAL README — Project startup (Windows / PowerShell)

This document describes, step-by-step, how to start the project locally from a Windows machine using PowerShell. It covers: XAMPP (MySQL), Docker (Zookeeper + Kafka), the Python environment, and how to launch the components (producer, consumer, dashboard).

Important: adapt paths if your repository is not located at `C:\Users\yassi\BIG-DATA-PROJECT`.

Prerequisites
- Docker Desktop installed and running
- XAMPP installed (MySQL available)
- Python 3.10+ installed
- Git (to clone the repository)

Detailed steps
--------------

1) Open PowerShell as Administrator

   - Right-click the PowerShell icon → "Run as administrator" (sometimes required for Docker/XAMPP operations).

2) Start XAMPP and enable MySQL

   - Open the XAMPP Control Panel and start **Apache** (if needed) and **MySQL**.
   - Verify MySQL is listening on the expected port (in this project we use `3307` by default): open phpMyAdmin or check `Config > my.ini` in XAMPP.

3) Start Docker Desktop

   - Make sure Docker Desktop is running and the Docker engine is healthy.

4) Clone the repository (if you haven't already)

```powershell
cd C:\Users\yassi
git clone <REPO_URL>
cd BIG-DATA-PROJECT
```

5) (Optional but recommended) Create and activate a Python virtual environment

```powershell
python -m venv venv
# PowerShell activate
venv\Scripts\Activate.ps1
```

6) Install Python dependencies

If a `requirements.txt` file exists (recommended):

```powershell
pip install -r requirements.txt
```

Otherwise install common dependencies manually:

```powershell
pip install streamlit pandas sqlalchemy pymysql kafka-python yfinance altair
```

7) Start Kafka & Zookeeper using Docker Compose

```powershell
cd docker
docker compose up -d

# Check running containers
docker ps
khask tl9ahm bzoj khdamin
# Stream logs (optional)
docker compose logs -f , wla dkhol ldocker wshof ereur"f7ala dyal ila kama khdm lik "
```

Notes:
- `docker/docker-compose.yml` uses Confluent images (`confluentinc/cp-zookeeper`, `confluentinc/cp-kafka`). The first pull may download several hundred MB.
- If you get a container name conflict (e.g. `/zookeeper` already exists), run `docker rm -f <container_id>` or `docker compose down` before `up`.

8) Verify MySQL connectivity

Check that MySQL is reachable (default port `3307` for this project):

```powershell
# Quick Python connectivity test (run from project root)
python - << 'PY'
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import os
u = os.getenv('MYSQL_USER','root')
p = os.getenv('MYSQL_PASSWORD','')
h = os.getenv('MYSQL_HOST','127.0.0.1')
pt = int(os.getenv('MYSQL_PORT','3307'))
db = os.getenv('MYSQL_DATABASE','bigdata_project')
engine = create_engine(URL.create('mysql+pymysql', username=u, password=p, host=h, port=pt, database=db))
print(engine.connect().execute('SELECT 1').scalar())
PY
```

9) Load / initialize sample data into MySQL (optional)

If you need to load sample JSON files present in `data/gold/`:

```powershell
# from the project root
python transformations\load_to_mysql.py
```

10) Run the Kafka producer (continuous message publishing)

```powershell
# activate venv first if used
venv\Scripts\Activate.ps1
python scraper\kafka_producer.py
```

The producer is built to be resilient and will retry if Kafka is not yet available.

11) Run the Kafka consumer (to observe messages)

```powershell
venv\Scripts\Activate.ps1
python scraper\kafka_consumer.py
```

12) Run the Streamlit dashboard

```powershell
venv\Scripts\Activate.ps1
streamlit run dashboards\app.py
```

13) Useful troubleshooting commands

```powershell
# List Docker containers
docker ps -a

# View Kafka logs
docker compose logs kafka

# Remove a problematic container
docker rm -f <container_id>

# Restart Docker Compose services
docker compose down
docker compose up -d
```

Important notes
- If MySQL does not use port 3307, export the environment variables before running scripts:

```powershell
$env:MYSQL_PORT = '3306'
$env:MYSQL_USER = 'root'
$env:MYSQL_PASSWORD = ''
$env:MYSQL_DATABASE = 'bigdata_project'
```

- To view the Streamlit UI open `http://localhost:8501` in your browser.

Quick checklist

1. XAMPP → MySQL running
2. Docker Desktop running
3. `docker compose up -d` in `docker/` → Kafka & Zookeeper up
4. Activate venv + `pip install -r requirements.txt`
5. (optional) `python transformations\load_to_mysql.py`
6. `python scraper\kafka_producer.py`
7. `python scraper\kafka_consumer.py` (observer)
8. `streamlit run dashboards\app.py` → open browser

