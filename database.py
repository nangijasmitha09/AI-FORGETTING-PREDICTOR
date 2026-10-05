import sqlite3

DATABASE = "forgetting_predictor.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            topic TEXT NOT NULL,
            subject TEXT NOT NULL,

            difficulty INTEGER NOT NULL,
            quiz_score INTEGER NOT NULL,

            days_since_study INTEGER NOT NULL,
            revisions INTEGER NOT NULL,

            risk INTEGER NOT NULL,
            risk_level TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


def create_user(name, email, password):

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name, email, password)
        )

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


def get_user_by_email(email):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()

    connection.close()

    return user


def add_topic(
    user_id,
    topic,
    subject,
    difficulty,
    quiz_score,
    days_since_study,
    revisions,
    risk,
    risk_level
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO topics
        (
            user_id,
            topic,
            subject,
            difficulty,
            quiz_score,
            days_since_study,
            revisions,
            risk,
            risk_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            topic,
            subject,
            difficulty,
            quiz_score,
            days_since_study,
            revisions,
            risk,
            risk_level
        )
    )

    connection.commit()
    connection.close()


def get_topics(user_id):

    connection = get_connection()

    topics = connection.execute(
        """
        SELECT *
        FROM topics
        WHERE user_id = ?
        ORDER BY risk DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    return topics


def get_statistics(user_id):

    connection = get_connection()

    total = connection.execute(
        """
        SELECT COUNT(*)
        FROM topics
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    high_risk = connection.execute(
        """
        SELECT COUNT(*)
        FROM topics
        WHERE user_id = ?
        AND risk >= 50
        """,
        (user_id,)
    ).fetchone()[0]

    average = connection.execute(
        """
        SELECT AVG(risk)
        FROM topics
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()[0]

    connection.close()

    return {
        "total": total,
        "high_risk": high_risk,
        "average": round(average or 0)
    }