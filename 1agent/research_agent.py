import os
import sys

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# -----------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------------

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY not found in .env file")


# -----------------------------------------
# IMPORT WEB SEARCH TOOL
# -----------------------------------------

sys.path.insert(0, "1tools")

from web_search import web_search


# -----------------------------------------
# CREATE LLM
# -----------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------------------
# RESEARCH AGENT
# -----------------------------------------

def research_agent(task: str):

    print("\n[Research Agent] Analyzing task...")

    # Keep task small
    task = task[:1000]

    # -----------------------------------------
    # STEP 1: ASK AI FOR SEARCH QUERY
    # -----------------------------------------

    query_prompt = f"""
You are a Research Agent.

User task:
{task}

Create ONE short and useful web search query
that will help answer this task.

Return ONLY the search query.
Do not explain anything.
"""

    query_response = llm.invoke(query_prompt)

    query = query_response.content.strip()

    print("\n[Research Agent] Search query:")
    print(query)


    # -----------------------------------------
    # STEP 2: USE REAL WEB SEARCH TOOL
    # -----------------------------------------

    print("\n[Research Agent] Calling Web Search Tool...")

    results = web_search(
        query=query,
        max_results=5
    )

    if not results:
        return "No web search results were found."


    print("[Research Agent] Web search completed.")


    # -----------------------------------------
    # STEP 3: PREPARE SEARCH RESULTS
    # -----------------------------------------

    search_text = ""

    for i, result in enumerate(results, start=1):

        search_text += f"""
Result {i}
Title: {result.get("title", "")}
URL: {result.get("url", "")}
Description: {result.get("snippet", "")}
"""


    # Keep result size small
    search_text = search_text[:5000]


    # -----------------------------------------
    # STEP 4: ASK AI TO SUMMARIZE
    # -----------------------------------------

    summary_prompt = f"""
You are a Research Specialist Agent.

User task:
{task}

Web search results:

{search_text}

Based only on these search results, provide:

1. Important facts
2. Key findings
3. Useful comparison points
4. Short summary

Do not invent facts.
Keep the answer concise.
"""

    print("\n[Research Agent] Analyzing search results...")

    summary_response = llm.invoke(summary_prompt)

    return summary_response.content


# -----------------------------------------
# TEST RESEARCH AGENT
# -----------------------------------------

if __name__ == "__main__":

    task = """
    Research the major advantages and disadvantages
    of electric vehicles.
    """

    print("\n========================================")
    print("          RESEARCH AGENT")
    print("========================================")

    result = research_agent(task)

    print("\n========================================")
    print("          RESEARCH RESULT")
    print("========================================")

    print(result)

    print("\n========================================")
    print("       RESEARCH COMPLETED")
    print("========================================")
