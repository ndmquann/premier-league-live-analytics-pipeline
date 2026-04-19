from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

_pool = None
def get_pool():
    global _pool
    if _pool is None:
        print(f"Connecting to: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
        try:
            _pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT", 5432)
            )
            print(f"✅ Connected to DB at {os.getenv('DB_HOST')}")
        except Exception as e:
            print(f"❌ Pool creation failed: {e}")
            raise  # 👈 don't swallow it, re-raise
    return _pool
def get_connection():
    return get_pool().getconn()

def release_connection(connection):
    get_pool().putconn(connection)

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)

def save_teams(teams: list):
    with get_db() as conn:
        cursor = conn.cursor()
        for team in teams:
            cursor.execute("""
                INSERT INTO teams (id, name, short_name, crest)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    short_name = EXCLUDED.short_name,
                    crest = EXCLUDED.crest
            """, 
            (
                team["id"],
                team["name"],
                team["shortName"],
                team["crest"]
            ))

def save_standings(table: list):
    with get_db() as conn:
        cursor = conn.cursor()
        for team in table:
            cursor.execute("""
                INSERT INTO standings (position, team_id, played_games, won, draw, lost, points, goals_for, goals_against, goal_difference)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (position) DO UPDATE SET
                    team_id = EXCLUDED.team_id,
                    played_games = EXCLUDED.played_games,
                    won = EXCLUDED.won,
                    draw = EXCLUDED.draw,
                    lost = EXCLUDED.lost,
                    points = EXCLUDED.points,
                    goals_for = EXCLUDED.goals_for,
                    goals_against = EXCLUDED.goals_against,
                    goal_difference = EXCLUDED.goal_difference
            """,
            (
                team["position"],
                team["team"]["id"],
                team["playedGames"],
                team["won"],
                team["draw"],
                team["lost"],
                team["points"],
                team["goalsFor"],
                team["goalsAgainst"],
                team["goalDifference"]
            ))

def save_matches(matches: list):
    print(matches[0])
    with get_db() as conn:
        cursor = conn.cursor()
        for match in matches:
            cursor.execute("""
                INSERT INTO matches (id, home_team_id, away_team_id, home_score, away_score, utc_date, status, matchday, time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    home_team_id = EXCLUDED.home_team_id,
                    away_team_id = EXCLUDED.away_team_id,
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    utc_date = EXCLUDED.utc_date,
                    status = EXCLUDED.status,
                    matchday = EXCLUDED.matchday,
                    time = EXCLUDED.time
            """,
            (
                match["id"],
                match["homeTeam"]["id"],
                match["awayTeam"]["id"],
                match["score"]["fullTime"]["home"],
                match["score"]["fullTime"]["away"],
                match["utcDate"],
                match["status"],
                match["matchday"],
                match["time"]
            ))

def get_today_matches_and_scores():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                m.utc_date, 
                m.status, 
                m.time,
                m.matchday,
                ht.name as home_team_name,
                awt.name as away_team_name,
                m.home_score,
                m.away_score
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams awt ON m.away_team_id = awt.id
            WHERE m.utc_date = CURRENT_DATE
            ORDER BY m.utc_date;
        """)
        return cursor.fetchall()

def get_standings():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                s.position,
                t.name as team_name,
                s.played_games,
                s.won,
                s.draw,
                s.lost,
                s.points,
                s.goals_for,
                s.goals_against,
                s.goal_difference
            FROM standings s
            JOIN teams t ON s.team_id = t.id
            ORDER BY s.position;
        """)
        return cursor.fetchall()

def get_liverpool_points():
    with get_db() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                s.*,
                t.name as team_name
            FROM standings s
            JOIN teams t ON s.team_id = t.id
            WHERE t.id = 64;
        """)
        return cursor.fetchone()

def get_weekday_result(matchday):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                m.utc_date,
                m.status,
                m.time,
                ht.name as home_team_name,
                awt.name as away_team_name,
                m.home_score,
                m.away_score
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams awt ON m.away_team_id = awt.id
            WHERE m.matchday = %s
            ORDER BY m.utc_date;
        """, (int(matchday),))
        return cursor.fetchall()