import os
import chromadb


# =========================================================
# CHROMA DATABASE LOCATION
# =========================================================

MEMORY_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

CHROMA_FOLDER = os.path.join(
    MEMORY_FOLDER,
    "chroma_db"
)


# =========================================================
# CREATE CHROMA CLIENT
# =========================================================

client = chromadb.PersistentClient(
    path=CHROMA_FOLDER
)


# =========================================================
# CREATE COLLECTION
# =========================================================

collection = client.get_or_create_collection(
    name="agent_memory"
)


# =========================================================
# SAVE SEMANTIC MEMORY
# =========================================================

def save_semantic_memory(
    user_task: str,
    research: str,
    analysis: str,
    final_report: str
):
    """
    Save a completed task into ChromaDB.

    ChromaDB will create an embedding for the text
    and store it for semantic search.
    """

    document = f"""
USER TASK:
{user_task}

RESEARCH:
{research[:1500]}

ANALYSIS:
{analysis[:1500]}

FINAL REPORT:
{final_report[:2000]}
"""

    memory_id = (
        f"task_{collection.count() + 1}"
    )

    collection.add(
        ids=[memory_id],
        documents=[document],
        metadatas=[
            {
                "user_task": user_task
            }
        ]
    )

    print(
        f"✅ Semantic memory saved: {memory_id}"
    )


# =========================================================
# SEARCH SEMANTIC MEMORY
# =========================================================

def search_semantic_memory(
    query: str,
    limit: int = 3
):
    """
    Find previous tasks that are semantically
    similar to the new query.
    """

    if collection.count() == 0:

        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(
            limit,
            collection.count()
        )
    )

    memories = []

    documents = results.get(
        "documents",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    for i, document in enumerate(documents):

        distance = (
            distances[i]
            if i < len(distances)
            else None
        )

        memories.append(
            {
                "document": document,
                "distance": distance
            }
        )

    return memories


# =========================================================
# CLEAR SEMANTIC MEMORY
# =========================================================

def clear_semantic_memory():
    """
    Remove all semantic memories.
    """

    global collection

    client.delete_collection(
        name="agent_memory"
    )

    collection = client.get_or_create_collection(
        name="agent_memory"
    )

    print(
        "✅ ChromaDB semantic memory cleared."
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("       CHROMADB MEMORY TEST")
    print("========================================")

    save_semantic_memory(
        user_task="Research electric vehicles",

        research=(
            "Electric vehicles use batteries "
            "and electric motors."
        ),

        analysis=(
            "EVs can provide lower operating "
            "costs and reduced tailpipe emissions."
        ),

        final_report=(
            "Electric vehicles are an important "
            "transportation technology."
        )
    )

    print("\nSearching for similar tasks...")

    results = search_semantic_memory(
        "Tell me about electric cars"
    )

    for result in results:

        print("\n----------------------------------------")
        print(result["document"])

        print(
            "Distance:",
            result["distance"]
        )

    print("\n========================================")
    print("      CHROMADB TEST COMPLETED")
    print("========================================")