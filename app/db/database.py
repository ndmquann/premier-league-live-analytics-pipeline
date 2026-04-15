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
                INSERT INTO standings (position, team_id, played_games, won, draw, lost, goals_for, goals_against, goal_difference)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (team_id) DO UPDATE SET
                    position = EXCLUDED.position,
                    team_id = EXCLUDED.team_id,
                    played_games = EXCLUDED.played_games,
                    won = EXCLUDED.won,
                    draw = EXCLUDED.draw,
                    lost = EXCLUDED.lost,
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
                team["goalsFor"],
                team["goalsAgainst"],
                team["goalDifference"]
            ))

def save_matches(matches: list):
    with get_db() as conn:
        cursor = conn.cursor()
        for match in matches:
            cursor.execute("""
                INSERT INTO matches (id, home_team_id, away_team_id, home_team_score, away_team_score, utc_date, status, minute, venue, matchday)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    home_team_id = EXCLUDED.home_team_id,
                    away_team_id = EXCLUDED.away_team_id,
                    home_team_score = EXCLUDED.home_team_score,
                    away_team_score = EXCLUDED.away_team_score,
                    utc_date = EXCLUDED.utc_date,
                    status = EXCLUDED.status,
                    minute = EXCLUDED.minute,
                    venue = EXCLUDED.venue,
                    matchday = EXCLUDED.matchday
            """,
            (
                match["id"],
                match["homeTeam"]["id"],
                match["awayTeam"]["id"],
                match["score"]["fullTime"]["home"],
                match["score"]["fullTime"]["away"],
                match["utcDate"],
                match["status"],
                match["minute"],
                match["venue"],
                match["matchday"]
            ))

def save_goals(goals: list, match_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        for goal in goals:
            cursor.execute("""
                INSERT INTO players (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
            """,
            (
                goal["scorer"]["id"],
                goal["scorer"]["name"]
            ))
            cursor.execute("""
                INSERT INTO goals (scorer_id, team_id, match_id, minute, injury_time, goal_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id, scorer_id, minute) DO UPDATE SET
                    scorer_id = EXCLUDED.scorer_id,
                    team_id = EXCLUDED.team_id,
                    match_id = EXCLUDED.match_id,
                    minute = EXCLUDED.minute,
                    injury_time = EXCLUDED.injury_time,
                    goal_type = EXCLUDED.goal_type
            """,
            (
                goal["scorer"]["id"],
                goal["team"]["id"],
                match_id,
                goal["minute"],
                goal["injuryTime"],
                goal["type"]
            ))

def get_today_matches_and_scores():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                m.utc_date, 
                m.status, 
                m.minute,
                m.venue,
                m.matchday,
                ht.name as home_team_name,
                awt.name as away_team_name,
                m.home_score,
                m.away_score
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams awt ON m.away_team_id = awt.id
            WHERE m.utc_date = CURRENT_DATE
        """)
        return cursor.fetchall()

def get_standings():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM standings;
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
            WHERE t.id = 64 
        """)
        return cursor.fetchone()
    
def get_today_goals():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                g.minute,
                s.name as scorer_name,
                a.name as assist_name,
                t.name as team_name,
                g.goal_type
            FROM goals g
            JOIN players s ON g.scorer_id = s.id
            LEFT JOIN players a ON g.assist_id = a.id
            JOIN teams t ON g.team_id = t.id
            JOIN matches m ON g.match_id = m.id
            WHERE m.utc_date = CURRENT_DATE    
        """)
        return cursor.fetchall()
