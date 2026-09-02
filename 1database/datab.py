import os
import time

import psycopg
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# DATABASE SETTINGS
# =========================================================

DB_NAME = os.getenv(
    "DB_NAME",
    "agent_orchestration"
)

DB_USER = os.getenv(
    "DB_USER",
    "postgres"
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD",
    "postgres"
)

DB_HOST = os.getenv(
    "DB_HOST",
    "localhost"
)

DB_PORT = int(
    os.getenv(
        "DB_PORT",
        "5432"
    )
)


# =========================================================
# GET CONNECTION
# =========================================================

def get_connection():

    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database(
    retries=10,
    delay=2
):
    """
    Create required database tables automatically.

    Retries are useful when PostgreSQL is starting inside
    Docker and is not ready immediately.
    """

    for attempt in range(1, retries + 1):

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        task TEXT NOT NULL,
                        research TEXT,
                        analysis TEXT,
                        final_report TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )

            connection.commit()
            connection.close()

            print(
                "✅ PostgreSQL database initialized successfully."
            )

            return True

        except Exception as error:

            print(
                f"⚠️ PostgreSQL initialization attempt "
                f"{attempt}/{retries} failed: {error}"
            )

            if attempt < retries:

                time.sleep(delay)

            else:

                print(
                    "❌ PostgreSQL could not be initialized."
                )

                return False


# =========================================================
# TEST CONNECTION
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("       POSTGRESQL DATABASE TEST")
    print("========================================")

    if initialize_database():

        print(
            f"✅ PostgreSQL ready "
            f"({DB_HOST}:{DB_PORT})"
        )

    print("\n========================================")
    print("      DATABASE TEST COMPLETE")
    print("========================================")