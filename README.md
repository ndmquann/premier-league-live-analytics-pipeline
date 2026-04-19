# Premier League Data Pipeline

A data pipeline that crawls Premier League match data — scores, scorers, standings, and fixtures — and displays them on a live dashboard. Built with Python, Airflow, PostgreSQL, and Streamlit, fully containerised with Docker.

---

## Features

- Fetches today's Premier League fixtures every morning and evening (8AM + 6PM Vietnam time)
- Polls live scores and goal events every 15 minutes during active matches
- Tracks standings in a PostgreSQL database
- Highlights Liverpool FC stats on the dashboard
- Smart scheduling — only polls when matches are actually live (`IN_PLAY`, `PAUSED`, `EXTRA_TIME`, `PENALTY_SHOOTOUT`)

---

## Architecture

```
football-data.org API
        ↓
Python fetchers (requests + pydantic)
        ↓
Airflow DAGs (scheduling + orchestration)
        ↓
PostgreSQL (matches, standings, teams)
        ↓
Streamlit dashboard (read-only)
```

---

## Project Structure

```
pl-pipeline/
├── app/
│   ├── fetchers/
│   │   ├── base.py             # shared API config
│   │   ├── fixtures.py         # today's scheduled matches
│   │   ├── scores.py           # live scores events
│   │   ├── standings.py        # Premier League table
│   │   └── liverpool.py        # Liverpool fixtures + results
│   ├── models/
│   │   └── match.py            # pydantic data models
│   ├── db/
│   │   ├── database.py         # connection pool + save functions
│   │   └── schema.sql          # table definitions
│   └── dashboard.py            # Streamlit UI
├── airflow/
│   └── dags/
│       ├── morning_evening_dag.py   # 8AM + 6PM job
│       └── match_poller_dag.py      # every 15 min during live matches
├── docker/
│   ├── airflow.Dockerfile
│   └── streamlit.Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                        # secrets — never commit this
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Database Schema

| Table | Description |
|-------|-------------|
| `teams` | Club names, short names, crest URLs |
| `matches` | Fixtures, scores, status, matchday |
| `standings` | Live league table — one row per team, upserted each matchday |

---

## Airflow DAGs

### `morning_evening_dag`
Runs at **8:00 AM** and **6:00 PM** Vietnam time (UTC+7).

```
fetch_fixtures → fetch_standings → fetch_liverpool
```

### `match_poller_dag`
Runs every **15 minutes**, all day.

```
check_live (ShortCircuit) → fetch_scores
```

Skips entirely if no match status is `IN_PLAY`, `PAUSED`, `EXTRA_TIME`, or `PENALTY_SHOOTOUT`.

---

## Prerequisites

- Docker + Docker Compose
- A free API key from [football-data.org](https://www.football-data.org/client/register)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ndmquann/premier-league-live-analytics-pipeline.git
cd pl-pipeline
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
API_KEY=your_football_data_api_key
BASE_URL=https://api.football-data.org/v4
LIVERPOOL_ID=64

DB_HOST=postgres
DB_NAME=pl_pipeline
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_PORT=5432
```

### 3. Build and run

```bash
docker-compose up --build
```

### 4. Access the services

| Service | URL |
|---------|-----|
| Streamlit dashboard | http://localhost:8501 |
| Airflow UI | http://localhost:8080 |
| PostgreSQL | localhost:5432 |

### 5. Initialise the database

On first run, execute the schema:

```bash
docker-compose exec postgres psql -U postgres -d pl_pipeline -f /app/app/db/schema.sql
```

---

## Dashboard

The Streamlit dashboard shows:

- **Liverpool FC** — position, points, played, won, lost as live metrics
- **Today's matches** — kick-off times (Vietnam time), live scores, match status
- **Full standings** — Premier League table with all stats

---

## Local Development (without Docker)

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

Set `DB_HOST=localhost` in `.env`, then:

```bash
streamlit run app/dashboard.py
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | football-data.org API key |
| `BASE_URL` | API base URL |
| `LIVERPOOL_ID` | Liverpool FC team ID (64) |
| `DB_HOST` | PostgreSQL host (`postgres` in Docker, `localhost` locally) |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_PORT` | Database port (default 5432) |

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| requests | API calls |
| pydantic | Data validation |
| psycopg2 | PostgreSQL driver |
| Apache Airflow | Scheduling + orchestration |
| PostgreSQL 15 | Data storage |
| Streamlit | Dashboard |
| Docker Compose | Container orchestration |

---

## Notes

- The free tier of football-data.org allows 10 requests/minute — well within our polling schedule
- All match times are stored in UTC and converted to Vietnam time (UTC+7) in the dashboard
- The `standings` table uses `UPSERT` — always 20 rows, refreshed each matchday
- `.env` is listed in `.dockerignore` and `.gitignore` — never commit it
