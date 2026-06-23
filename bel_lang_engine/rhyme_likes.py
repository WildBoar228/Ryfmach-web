import os
import sqlite3
import threading


LIKES_DB_PATH = "db/RhymeLikes.db"

likes_db_lock = threading.Lock()


def init_db():
    os.makedirs(os.path.dirname(LIKES_DB_PATH), exist_ok=True)
    with sqlite3.connect(LIKES_DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS rhyme_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_word TEXT NOT NULL,
                request_stress INTEGER NOT NULL,
                rhyme_word TEXT NOT NULL,
                rhyme_stress INTEGER NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(request_word, request_stress, rhyme_word, rhyme_stress)
            )
        """)


def update_score(request_word: str, request_stress: int, rhyme_word: str, rhyme_stress: int, delta: int):
    init_db()
    with likes_db_lock:
        with sqlite3.connect(LIKES_DB_PATH) as con:
            word_pair = [(request_word, request_stress), (rhyme_word, rhyme_stress)]
            word_pair.sort()
            (request_word, request_stress), (rhyme_word, rhyme_stress) = word_pair

            cur = con.execute("""
                INSERT INTO rhyme_likes (
                    request_word,
                    request_stress,
                    rhyme_word,
                    rhyme_stress,
                    score
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(request_word, request_stress, rhyme_word, rhyme_stress)
                DO UPDATE SET
                    score = score + excluded.score,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING score
            """, (request_word, request_stress, rhyme_word, rhyme_stress, delta))
            row = cur.fetchone()
            
            print(f"Update rhyme score: {word_pair}: {row[0] if row else None}")
            return row[0] if row else None
