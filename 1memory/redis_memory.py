import redis


# =========================================================
# REDIS CONNECTION
# =========================================================

redis_client = redis.Redis(
    host="localhost",
    port=6380,
    decode_responses=True
)


# =========================================================
# TEST CONNECTION
# =========================================================

def test_redis():

    try:

        response = redis_client.ping()

        if response:

            print("✅ Redis connection successful!")
            return True

    except Exception as error:

        print(f"❌ Redis connection failed: {error}")
        return False


# =========================================================
# SAVE WORKING MEMORY
# =========================================================

def save_working_memory(
    task_id: str,
    data: dict
):

    redis_client.hset(
        f"task:{task_id}",
        mapping=data
    )

    print(
        f"✅ Working memory saved to Redis: {task_id}"
    )


# =========================================================
# GET WORKING MEMORY
# =========================================================

def get_working_memory(
    task_id: str
):

    data = redis_client.hgetall(
        f"task:{task_id}"
    )

    return data


# =========================================================
# DELETE WORKING MEMORY
# =========================================================

def delete_working_memory(
    task_id: str
):

    redis_client.delete(
        f"task:{task_id}"
    )

    print(
        f"✅ Working memory deleted: {task_id}"
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("          REDIS MEMORY TEST")
    print("========================================")

    if test_redis():

        save_working_memory(
            task_id="test_1",
            data={
                "status": "running",
                "agent": "research",
                "message": "Research task in progress"
            }
        )

        result = get_working_memory(
            "test_1"
        )

        print("\nStored working memory:")
        print(result)

        delete_working_memory(
            "test_1"
        )

    print("\n========================================")
    print("        REDIS MEMORY TEST COMPLETE")
    print("========================================")