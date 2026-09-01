import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )


# =========================================================
# CREATE LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# WRITER AGENT
# =========================================================

def writer_agent(task: str):

    # Keep input small enough for Groq
    task = task[:5000]

    prompt = f"""
You are the Writing Specialist Agent in a multi-agent
AI orchestration system.

Your responsibility is to create a COMPLETE final report.

INPUT INFORMATION:
{task}

IMPORTANT RULES:

1. Write a complete report.
2. Do NOT stop in the middle of a table, sentence, or section.
3. Do NOT use placeholders such as "..." or "continue".
4. Make sure every requested section is completed.
5. Include a clear conclusion.
6. Include a References section when source names,
   URLs, or citations are provided in the input.
7. Do not invent citations, sources, statistics, or URLs.
8. Use only the information provided in the input.
9. Keep the report concise enough to finish completely.
10. Use Markdown headings and tables when useful.
11. If reviewer feedback is present, correct every issue
    mentioned by the reviewer.
12. Before finishing, mentally check that the report has
    no incomplete sentence, incomplete table, or missing
    required section.

The report should contain:

# Title

## 1. Introduction

## 2. Main Findings

## 3. Comparison

## 4. Advantages and Disadvantages

## 5. Conclusion

## 6. References

If references are not available in the supplied information,
write:

"References were not provided in the available source material."

Do not invent references.

REVIEWER FEEDBACK, IF ANY:
Use it to improve the report before producing the final version.

Now produce ONLY the final polished report.
"""


    response = llm.invoke(prompt)

    result = response.content.strip()

    return result


# =========================================================
# TEST WRITER AGENT
# =========================================================

if __name__ == "__main__":

    test_input = """
    Create a professional report comparing electric vehicles.

    Research:
    Electric vehicles use battery-powered electric motors.
    They can have lower operating costs and zero tailpipe
    emissions.

    Analysis:
    EVs can provide strong acceleration and may reduce
    operating costs compared with conventional vehicles.

    Reviewer feedback:
    Make sure every section is complete and include a
    conclusion. Do not cut off tables or sentences.
    """

    result = writer_agent(test_input)

    print("\n========================================")
    print("            WRITER AGENT")
    print("========================================\n")

    print(result)

    print("\n========================================")
    print("          WRITING COMPLETED")
    print("========================================")