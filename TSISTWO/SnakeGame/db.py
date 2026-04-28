"""PostgreSQL client for leaderboard and session persistence.

Implements table creation, saving game sessions, retrieving top scores
and personal best. Uses psycopg2 (binary) when available.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import datetime
from urllib.parse import quote_plus

try:
    import psycopg2  # type: ignore[import-not-found]
    from psycopg2.extras import RealDictCursor  # type: ignore[import-not-found]
    from psycopg2.pool import SimpleConnectionPool  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - runtime dependency
    psycopg2 = None  # type: ignore


class DatabaseError(Exception):
    pass


class DatabaseClient:
    """Simple PostgreSQL client.

    Usage:
        db = DatabaseClient(dsn="postgresql://user:pass@host:5432/dbname")
        db.ensure_tables()
        db.save_session("alice", 123, 2)

    The client uses a small connection pool. If psycopg2 is not installed
    the client will raise DatabaseError on connect attempts.
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        minconn: int = 1,
        maxconn: int = 5,
    ) -> None:
        self.dsn = dsn or os.getenv("DATABASE_URL") or self._build_dsn_from_settings(settings)
        self.pool: Optional[SimpleConnectionPool] = None
        self.minconn = minconn
        self.maxconn = maxconn

    @staticmethod
    def _build_dsn_from_settings(settings: Optional[Dict[str, Any]]) -> Optional[str]:
        if not settings:
            return None

        host = str(settings.get("db_host", "localhost"))
        port = int(settings.get("db_port", 5432))
        db_name = str(settings.get("db_name", "snake_db"))
        user = str(settings.get("db_user", "snake_user"))
        password = str(settings.get("db_password", "your_password"))
        sslmode = str(settings.get("db_sslmode", "prefer"))

        user_q = quote_plus(user)
        pass_q = quote_plus(password)
        db_q = quote_plus(db_name)
        return f"postgresql://{user_q}:{pass_q}@{host}:{port}/{db_q}?sslmode={sslmode}"

    @classmethod
    def from_settings(cls, settings: Dict[str, Any], minconn: int = 1, maxconn: int = 5) -> "DatabaseClient":
        return cls(settings=settings, minconn=minconn, maxconn=maxconn)

    def connect(self) -> None:
        if psycopg2 is None:
            raise DatabaseError("psycopg2 is not installed in this environment")
        if not self.dsn:
            raise DatabaseError("No DSN provided (set DATABASE_URL or pass dsn)")
        if self.pool is None:
            try:
                self.pool = SimpleConnectionPool(self.minconn, self.maxconn, self.dsn)
            except Exception as e:
                raise DatabaseError(f"Failed to create connection pool: {e}")

    def close(self) -> None:
        if self.pool:
            try:
                self.pool.closeall()
            finally:
                self.pool = None

    def _get_conn(self):
        if self.pool is None:
            self.connect()
        assert self.pool is not None
        try:
            return self.pool.getconn()
        except Exception as e:
            raise DatabaseError(f"Failed to get connection: {e}")

    def _put_conn(self, conn) -> None:
        if self.pool and conn is not None:
            try:
                self.pool.putconn(conn)
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass

    def ensure_tables(self) -> None:
        sql_players = """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL
        );
        """

        sql_sessions = """
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            level INTEGER NOT NULL,
            played_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS idx_game_sessions_score ON game_sessions(score DESC);
        """

        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute(sql_players)
            cur.execute(sql_sessions)
            conn.commit()
            cur.close()
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise DatabaseError(f"Failed to create tables: {e}")
        finally:
            if conn:
                self._put_conn(conn)

    def save_session(self, username: str, score: int, level: int, played_at: Optional[datetime.datetime] = None) -> None:
        """Save a finished game session.

        Creates the player row if necessary.
        """
        if played_at is None:
            played_at = datetime.datetime.now(datetime.UTC)

        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username RETURNING id;",
                (username,),
            )
            player_id = cur.fetchone()[0]

            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level, played_at) VALUES (%s, %s, %s, %s);",
                (player_id, int(score), int(level), played_at),
            )
            conn.commit()
            cur.close()
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise DatabaseError(f"Failed to save session: {e}")
        finally:
            if conn:
                self._put_conn(conn)

    def get_top(self, limit: int = 10) -> List[Dict[str, Any]]:
        sql = """
        SELECT p.username, gs.score, gs.level, gs.played_at
        FROM game_sessions gs
        JOIN players p ON gs.player_id = p.id
        ORDER BY gs.score DESC, gs.played_at ASC
        LIMIT %s;
        """
        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
            cur.close()
            return [dict(r) for r in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get top scores: {e}")
        finally:
            if conn:
                self._put_conn(conn)

    def get_personal_best(self, username: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT gs.score, gs.level, gs.played_at
        FROM game_sessions gs
        JOIN players p ON gs.player_id = p.id
        WHERE p.username = %s
        ORDER BY gs.score DESC, gs.played_at ASC
        LIMIT 1;
        """
        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(sql, (username,))
            row = cur.fetchone()
            cur.close()
            return dict(row) if row else None
        except Exception as e:
            raise DatabaseError(f"Failed to get personal best: {e}")
        finally:
            if conn:
                self._put_conn(conn)

