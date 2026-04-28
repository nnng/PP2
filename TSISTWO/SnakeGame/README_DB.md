PostgreSQL setup and SQL statements for SnakeGame

1. Create database and role (example):

-- create role and db
CREATE ROLE snake_user WITH LOGIN PASSWORD 'your_password';
CREATE DATABASE snake_db OWNER snake_user;

-- connect to database
\c snake_db

2. SQL schema (run inside snake_db):

CREATE TABLE IF NOT EXISTS players (
id SERIAL PRIMARY KEY,
username TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
id SERIAL PRIMARY KEY,
player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
score INTEGER NOT NULL,
level INTEGER NOT NULL,
played_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_game_sessions_score ON game_sessions(score DESC);

3. Optional functions / procedures (not required):

-- returns top N
CREATE OR REPLACE FUNCTION get_top(n INTEGER)
RETURNS TABLE(username TEXT, score INTEGER, level INTEGER, played_at TIMESTAMPTZ) AS $$
BEGIN
  RETURN QUERY
  SELECT p.username, gs.score, gs.level, gs.played_at
  FROM game_sessions gs JOIN players p ON gs.player_id = p.id
  ORDER BY gs.score DESC, gs.played_at ASC
  LIMIT n;
END; $$ LANGUAGE plpgsql;

4. How to run these statements using psql:

psql -h <host> -p <port> -U postgres
-- then paste SQL, or from shell:
psql "postgresql://postgres:postgrespass@localhost:5432" -f schema.sql

5. Environment variable for the Python client:

Set DATABASE_URL to: postgresql://snake_user:your_password@localhost:5432/snake_db

6. Testing save from Python CLI:

# install dependencies (in the environment that will run the game)

python -m pip install -r requirements.txt

# save a sample score

python save_score.py --dsn "postgresql://snake_user:your_password@localhost:5432/snake_db" --username alice --score 10 --level 1

# get top 10 using psql

psql "postgresql://snake_user:your_password@localhost:5432/snake_db" -c "SELECT p.username, gs.score, gs.level, gs.played_at FROM game_sessions gs JOIN players p ON gs.player_id = p.id ORDER BY gs.score DESC LIMIT 10;"
