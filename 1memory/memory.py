import sys

# =========================================================
# PROJECT PATHS
# =========================================================

sys.path.insert(0, "1database")
sys.path.insert(0, "1memory")


# =========================================================
# IMPORT DATABASE CONNECTION
# =========================================================

from datab import get_connection


# =========================================================
# IMPORT CHROMADB FUNCTIONS
# =========================================================

from semantic_memory import (
    save_semantic_memory,
    search_semantic_memory,
    clear_semantic_memory
)


# =========================================================
# LOAD MEMORY FROM POSTGRESQL
# =========================================================

def load_memory():
    """
    Load all memories from PostgreSQL.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                id,
                task,
                research,
                analysis,
                final_report,
                created_at
            FROM tasks
            ORDER BY id ASC
        """)

        rows = cursor.fetchall()

        memories = []

        for row in rows:

            memories.append({
                "id": row[0],
                "user_task": row[1],
                "research": row[2] or "",
                "analysis": row[3] or "",
                "final_report": row[4] or "",
                "timestamp": (
                    row[5].isoformat()
                    if row[5]
                    else None
                )
            })

        return memories

    finally:

        cursor.close()
        conn.close()


# =========================================================
# SAVE MEMORY
# =========================================================

def save_memory(
    user_task: str,
    research: str,
    analysis: str,
    final_report: str
):
    """
    Save completed task to PostgreSQL
    and ChromaDB.
    """

    # -----------------------------------------------------
    # SAVE TO POSTGRESQL
    # -----------------------------------------------------

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO tasks
            (
                task,
                research,
                analysis,
                final_report
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_task,
                research[:2000],
                analysis[:2000],
                final_report[:3000]
            )
        )

        conn.commit()

        print(
            "✅ Memory saved to PostgreSQL!"
        )

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


    # -----------------------------------------------------
    # SAVE TO CHROMADB
    # -----------------------------------------------------

    try:

        save_semantic_memory(
            user_task=user_task,
            research=research,
            analysis=analysis,
            final_report=final_report
        )

        print(
            "✅ Semantic memory saved to ChromaDB!"
        )

    except Exception as error:

        print(
            f"⚠️ ChromaDB save failed: {error}"
        )


# =========================================================
# GET RECENT MEMORIES
# =========================================================

def get_recent_memories(limit: int = 3):
    """
    Return the most recent memories from PostgreSQL.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id,
                task,
                research,
                analysis,
                final_report,
                created_at
            FROM tasks
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        memories = []

        for row in rows:

            memories.append({
                "id": row[0],
                "user_task": row[1],
                "research": row[2] or "",
                "analysis": row[3] or "",
                "final_report": row[4] or "",
                "timestamp": (
                    row[5].isoformat()
                    if row[5]
                    else None
                )
            })

        # Same behavior as the old JSON version
        memories.reverse()

        return memories

    finally:

        cursor.close()
        conn.close()


# =========================================================
# SEARCH SEMANTIC MEMORY
# =========================================================

def search_memory(
    query: str,
    limit: int = 3
):
    """
    Search previous tasks by meaning using ChromaDB.
    """

    return search_semantic_memory(
        query=query,
        limit=limit
    )


# =========================================================
# CLEAR ALL MEMORY
# =========================================================

def clear_memory():
    """
    Clear both PostgreSQL and ChromaDB memory.
    """

    # -----------------------------------------------------
    # CLEAR POSTGRESQL
    # -----------------------------------------------------

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "DELETE FROM tasks"
        )

        conn.commit()

        print(
            "✅ All PostgreSQL memory deleted!"
        )

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()


    # -----------------------------------------------------
    # CLEAR CHROMADB
    # -----------------------------------------------------

    try:

        clear_semantic_memory()

    except Exception as error:

        print(
            f"⚠️ ChromaDB clear failed: {error}"
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("     POSTGRESQL + CHROMADB MEMORY TEST")
    print("========================================")


    # Save a test task
    save_memory(
        user_task="Test combined semantic memory",

        research=(
            "Electric vehicles use batteries "
            "and electric motors."
        ),

        analysis=(
            "Electric vehicles can reduce "
            "tailpipe emissions."
        ),

        final_report=(
            "This is a combined PostgreSQL "
            "and ChromaDB memory test."
        )
    )


    # Read PostgreSQL memories
    memories = get_recent_memories()

    print("\nRecent PostgreSQL memories:")

    for memory in memories:

        print(
            memory["id"],
            memory["user_task"],
            memory["timestamp"]
        )


    # Search ChromaDB
    print("\nSemantic search:")

    results = search_memory(
        "Tell me about electric cars",
        limit=3
    )

    for result in results:

        print("\n------------------------------")

        print(
            result.get(
                "document",
                ""
            )
        )

        print(
            "Distance:",
            result.get(
                "distance"
            )
        )


    print("\n========================================")
    print("     COMBINED MEMORY TEST COMPLETE")
    print("========================================")