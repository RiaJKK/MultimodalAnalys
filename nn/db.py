import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.extensions import connection as PgConnection

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/mavis"
)

def get_connection() -> PgConnection:
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init() -> None:
    """Создаёт расширение pgcrypto и все таблицы (идемпотентно)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat (
                    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
                    title       VARCHAR(255) NOT NULL,
                    created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
                    updated_at  TIMESTAMP    NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS video (
                    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
                    chat_id           UUID         NOT NULL
                                          REFERENCES chat(id) ON DELETE CASCADE,
                    file_path         TEXT         NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    duration_seconds  INTEGER,
                    status            VARCHAR(50)  NOT NULL DEFAULT 'pending',
                    uploaded_at       TIMESTAMP    NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS analysis_result (
                    id            UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
                    chat_id       UUID      NOT NULL
                                      REFERENCES chat(id) ON DELETE CASCADE,
                    combined_text TEXT,
                    llm_output    JSONB,
                    analyzed_at   TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_video_chat_id
                    ON video(chat_id);
                CREATE INDEX IF NOT EXISTS idx_analysis_chat_id
                    ON analysis_result(chat_id);
            """)
        conn.commit()


# ── CRUD: chat ────────────────────────────────────────────────────────────────

def chat_create(title: str) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO chat (title) VALUES (%s) RETURNING *;",
                (title,)
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def chat_get(chat_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM chat WHERE id = %s;", (chat_id,))
            row = cur.fetchone()
    return dict(row) if row else None


def chat_list() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM chat ORDER BY created_at DESC;")
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def chat_update_title(chat_id: str, title: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE chat SET title = %s, updated_at = NOW() WHERE id = %s;",
                (title, chat_id)
            )
        conn.commit()


# ── CRUD: video ───────────────────────────────────────────────────────────────

def video_create(chat_id: str, file_path: str,
                 original_filename: str, duration_seconds: int | None = None) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO video
                       (chat_id, file_path, original_filename, duration_seconds)
                   VALUES (%s, %s, %s, %s)
                   RETURNING *;""",
                (chat_id, file_path, original_filename, duration_seconds)
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def video_set_status(video_id: str, status: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE video SET status = %s WHERE id = %s;",
                (status, video_id)
            )
        conn.commit()


def video_list_by_chat(chat_id: str) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM video WHERE chat_id = %s ORDER BY uploaded_at;",
                (chat_id,)
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]


# ── CRUD: analysis_result ─────────────────────────────────────────────────────

def analysis_create(chat_id: str, combined_text: str, llm_output: dict) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO analysis_result (chat_id, combined_text, llm_output)
                   VALUES (%s, %s, %s)
                   RETURNING *;""",
                (chat_id, combined_text, Json(llm_output))
            )
            row = cur.fetchone()
        conn.commit()
    return dict(row)


def analysis_get_by_chat(chat_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM analysis_result WHERE chat_id = %s "
                "ORDER BY analyzed_at DESC LIMIT 1;",
                (chat_id,)
            )
            row = cur.fetchone()
    return dict(row) if row else None
