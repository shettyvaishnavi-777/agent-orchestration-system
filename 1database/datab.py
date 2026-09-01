import psycopg


def get_connection():
    return psycopg.connect(
        dbname="agent_orchestration",
        user="postgres",
        password="vaishnavi@18",
        host="localhost",
        port=5432
    )