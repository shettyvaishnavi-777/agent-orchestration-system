import json
import os
from datetime import datetime


# =========================================================
# MEMORY FILE LOCATION
# =========================================================

# Get the folder where this memory.py file is located
MEMORY_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Store memory_data.json inside the same folder
MEMORY_FILE = os.path.join(
    MEMORY_FOLDER,
    "memory_data.json"
)


# =========================================================
# LOAD MEMORY
# =========================================================

def load_memory():
    """
    Load all previously saved memories.
    """

    if not os.path.exists(MEMORY_FILE):
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            # Make sure the JSON contains a list
            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


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
    Save a completed task into long-term memory.
    """

    memories = load_memory()

    memory = {
        "timestamp": datetime.now().isoformat(),

        "user_task": user_task,

        "research": research[:2000],

        "analysis": analysis[:2000],

        "final_report": final_report[:3000]
    }

    memories.append(memory)

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memories,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"✅ Memory saved to: {MEMORY_FILE}"
        )

    except OSError as error:

        print(
            f"❌ Could not save memory: {error}"
        )


# =========================================================
# GET RECENT MEMORIES
# =========================================================

def get_recent_memories(limit: int = 3):
    """
    Return the most recent memories.
    """

    memories = load_memory()

    return memories[-limit:]


# =========================================================
# CLEAR MEMORY
# =========================================================

def clear_memory():
    """
    Delete all stored memories.
    """

    if os.path.exists(MEMORY_FILE):

        try:

            os.remove(MEMORY_FILE)

            print("✅ All memory deleted.")

        except OSError as error:

            print(
                f"❌ Could not delete memory: {error}"
            )

    else:

        print("ℹ️ No memory file exists.")


# =========================================================
# TEST MEMORY
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("           MEMORY SYSTEM TEST")
    print("========================================")

    save_memory(
        user_task="Research electric vehicles",

        research=(
            "Electric vehicles use electric motors "
            "and rechargeable batteries."
        ),

        analysis=(
            "EVs can reduce tailpipe emissions "
            "and operating costs."
        ),

        final_report=(
            "Electric vehicles are an important "
            "transportation technology."
        )
    )

    memories = get_recent_memories()

    print("\nStored memories:")

    for memory in memories:

        print("\nTask:")
        print(memory["user_task"])

        print("Time:")
        print(memory["timestamp"])

    print("\nMemory file:")
    print(MEMORY_FILE)

    print("\n========================================")
    print("        MEMORY TEST COMPLETED")
    print("========================================")