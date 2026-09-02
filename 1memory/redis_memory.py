import os
import redis
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# REDIS CONNECTION
# =========================================================

# When running inside Docker Compose:
#   REDIS_HOST=redis
#   REDIS_PORT=6379
#
# When running directly on Windows:
#   localhost:6380

redis_host = os.getenv(
    "REDIS_HOST",
    "localhost"
)

redis_port = int(
    os.getenv(
        "REDIS_PORT",
        "6380"
    )
)


redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    decode_responses=True
)


# =========================================================
# TEST CONNECTION
# =========================================================

def test_redis():

    try:

        response = redis_client.ping()

        if response:

            print(
                f"✅ Redis connection successful "
                f"({redis_host}:{redis_port})"
            )

            return True

    except Exception as error:

        print(
            f"❌ Redis connection failed: {error}"
        )

        return False

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

    return redis_client.hgetall(
        f"task:{task_id}"
    )


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