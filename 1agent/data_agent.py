import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Create LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


def data_agent(task: str):

    prompt = f"""
You are the Data Analysis Specialist Agent.

Your job is to analyze information provided by the Supervisor.

Task:
{task}

Perform useful analysis.

Provide:
1. Important data points
2. Comparisons
3. Calculations if required
4. Key observations
5. A clear conclusion

Show calculations clearly when you perform them.
Do not invent data.
"""

    response = llm.invoke(prompt)

    return response.content


# Test Data Agent
if __name__ == "__main__":

    result = data_agent(
        "Compare electric vehicles based on range, charging time and price"
    )

    print("\n====================================")
    print("           DATA AGENT")
    print("====================================\n")

    print(result)

    print("\n====================================")
    print("         DATA COMPLETED")
    print("====================================")