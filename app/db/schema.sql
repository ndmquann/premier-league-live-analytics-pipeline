CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT,
    crest TEXT
);

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    utc_date DATE NOT NULL,
    status TEXT NOT NULL,
    minute INTEGER,
    venue TEXT,
    matchday INTEGER,
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    home_score INTEGER,
    away_score INTEGER
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    scorer_id INTEGER REFERENCES players(id),
    assist_id INTEGER REFERENCES players(id),
    team_id INTEGER REFERENCES teams(id),
    match_id INTEGER REFERENCES matches(id),
    minute INTEGER,
    injury_time INTEGER,
    goal_type TEXT,
    UNIQUE (match_id, scorer_id, minute)
);

CREATE TABLE IF NOT EXISTS standings (
    position INTEGER PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id) UNIQUE,
    played_games INTEGER NOT NULL,
    won INTEGER NOT NULL,
    draw INTEGER NOT NULL,
    lost INTEGER NOT NULL,
    points INTEGER NOT NULL,
    goals_for INTEGER NOT NULL,
    goals_against INTEGER NOT NULL,
    goal_difference INTEGER NOT NULL
);