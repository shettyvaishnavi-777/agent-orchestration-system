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


def writer_agent(task: str):

    # Limit the amount of information sent to the model
    # to avoid Groq TPM/request-size errors.
    task = task[:2000]

    prompt = f"""
You are the Writing Specialist Agent.

Your job is to create a professional final report
using the information provided to you.

Information:

{task}

Create a well-structured report containing:

1. Title
2. Introduction
3. Main findings
4. Comparison
5. Advantages and disadvantages
6. Conclusion

Use clear and professional language.

Do not invent facts.
Use only the information provided above.
"""

    response = llm.invoke(prompt)

    return response.content


# Test Writer Agent
if __name__ == "__main__":

    result = writer_agent(
        """
        Create a professional report comparing electric vehicles.
        Discuss their advantages, disadvantages, performance,
        charging and environmental benefits.
        """
    )

    print("\n====================================")
    print("          WRITER AGENT")
    print("====================================\n")

    print(result)

    print("\n====================================")
    print("         WRITING COMPLETED")
    print("====================================")