# db.py
import os
import sqlite3
from datetime import datetime
from config import DB_PATH, DB_DIR

def _connect():
    os.makedirs(DB_DIR, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = _connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS solves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        level INTEGER NOT NULL,
        solved_at TEXT NOT NULL,
        UNIQUE(team_id, level),
        FOREIGN KEY(team_id) REFERENCES teams(id)
    )
    """)

    con.commit()
    con.close()

def create_team(name: str) -> bool:
    con = _connect()
    try:
        con.execute(
            "INSERT INTO teams(name, created_at) VALUES(?, ?)",
            (name, datetime.utcnow().isoformat())
        )
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

def team_exists(name: str) -> bool:
    con = _connect()
    row = con.execute("SELECT 1 FROM teams WHERE name = ?", (name,)).fetchone()
    con.close()
    return row is not None

def get_team_id(name: str):
    con = _connect()
    row = con.execute("SELECT id FROM teams WHERE name = ?", (name,)).fetchone()
    con.close()
    return row["id"] if row else None

def record_solve(team_id: int, level: int) -> bool:
    con = _connect()
    try:
        con.execute(
            "INSERT INTO solves(team_id, level, solved_at) VALUES(?, ?, ?)",
            (team_id, level, datetime.utcnow().isoformat())
        )
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

def get_solved_levels(team_id: int) -> set[int]:
    con = _connect()
    rows = con.execute("SELECT level FROM solves WHERE team_id = ?", (team_id,)).fetchall()
    con.close()
    return {r["level"] for r in rows}

def get_next_unlocked_level(team_id: int, total_levels: int) -> int:
    solved = get_solved_levels(team_id)
    if not solved:
        return 1
    nl = max(solved) + 1
    return min(nl, total_levels)

def scoreboard():
    con = _connect()
    rows = con.execute("""
        SELECT t.name as team, COUNT(s.id) as score
        FROM teams t
        LEFT JOIN solves s ON s.team_id = t.id
        GROUP BY t.id
        ORDER BY score DESC, t.name ASC
    """).fetchall()
    con.close()
    return [{"team": r["team"], "score": r["score"]} for r in rows]

def reset_all():
    con = _connect()
    con.execute("DELETE FROM solves")
    con.execute("DELETE FROM teams")
    con.commit()
    con.close()