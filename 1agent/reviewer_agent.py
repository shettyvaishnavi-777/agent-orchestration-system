import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY not found in .env file")


# =========================================================
# CREATE LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# REVIEWER AGENT
# =========================================================

def reviewer_agent(
    user_task: str,
    research: str,
    analysis: str,
    final_report: str
):

    prompt = f"""
You are the Reviewer Agent in a multi-agent AI system.

Your job is to review the final report produced by
the Writer Agent.

USER TASK:
{user_task}

RESEARCH:
{research}

DATA ANALYSIS:
{analysis}

FINAL REPORT:
{final_report}

Evaluate the report using these criteria:

1. Accuracy
2. Completeness
3. Relevance
4. Clarity
5. Whether the report answers the user's task

Give:

SCORE: a number from 1 to 10

STATUS:
APPROVED or REJECTED

FEEDBACK:
Give a short explanation.

If the score is 7 or higher, approve the report.

If the score is below 7, reject it and explain what
the Writer Agent should improve.
"""

    response = llm.invoke(prompt)

    return response.content


# =========================================================
# TEST REVIEWER
# =========================================================

if __name__ == "__main__":

    result = reviewer_agent(
        user_task="Create an EV comparison report.",

        research=(
            "Electric vehicles use battery-powered "
            "electric motors."
        ),

        analysis=(
            "EVs can have lower operating costs "
            "than conventional vehicles."
        ),

        final_report=(
            "Electric vehicles are increasingly used "
            "because of their efficiency and potential "
            "environmental benefits."
        )
    )

    print("\n========================================")
    print("          REVIEWER AGENT")
    print("========================================")

    print(result)

    print("\n========================================")
    print("        REVIEW COMPLETED")
    print("========================================")
