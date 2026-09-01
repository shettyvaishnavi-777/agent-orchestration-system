import os
import sys
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )


# =========================================================
# PROJECT PATHS
# =========================================================

sys.path.insert(0, "1agent")
sys.path.insert(0, "1backend")
sys.path.insert(0, "1memory")


# =========================================================
# IMPORT AGENTS / MODULES
# =========================================================

from research_agent import research_agent
from data_agent import data_agent
from writer_agent import writer_agent
from reviewer_agent import reviewer_agent

from safety import requires_human_approval
from memory import save_memory


# =========================================================
# GROQ LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# SHARED STATE
# =========================================================

class State(TypedDict):
    user_task: str
    plan: str
    research: str
    analysis: str
    final_report: str
    review: str

    human_approved: bool
    status: str

    research_attempts: int
    data_attempts: int
    writer_attempts: int
    review_attempts: int

    trace: list[str]


# =========================================================
# SUPERVISOR AGENT
# =========================================================

def supervisor(state: State):

    task = state["user_task"]

    prompt = f"""
You are the Supervisor Agent in a multi-agent AI
orchestration system.

USER TASK:
{task}

Create a concise execution plan.

Available agents:

1. Research Agent
2. Data Analysis Agent
3. Writer Agent
4. Reviewer Agent

Explain what each agent should do.

Do not perform the task yourself.
Only create the execution plan.
"""

    response = llm.invoke(prompt)

    trace = state.get("trace", [])

    trace.append(
        "✅ Supervisor created execution plan"
    )

    print("\n========================================")
    print("             SUPERVISOR")
    print("========================================")

    print(response.content)

    return {
        "plan": response.content,
        "trace": trace
    }


# =========================================================
# SAFETY CHECK
# =========================================================

def safety_check(state: State):

    task = state["user_task"]

    trace = state.get("trace", [])

    print("\n========================================")
    print("             SAFETY CHECK")
    print("========================================")

    if requires_human_approval(task):

        print(
            "⚠️ Sensitive action detected."
        )

        trace.append(
            "⚠️ Sensitive action detected"
        )

        trace.append(
            "⏸️ Human approval required"
        )

        return {
            "human_approved": False,
            "status": "pending_approval",
            "trace": trace
        }

    print(
        "✅ No human approval required."
    )

    trace.append(
        "✅ Safety check passed"
    )

    return {
        "human_approved": True,
        "status": "approved",
        "trace": trace
    }


# =========================================================
# SAFETY ROUTER
# =========================================================

def safety_router(state: State):

    if state["status"] == "pending_approval":
        return "wait"

    if state["status"] == "approved":
        return "research"

    return "stop"


# =========================================================
# WAIT NODE
# =========================================================

def wait_node(state: State):

    trace = state.get("trace", [])

    trace.append(
        "⏸️ Workflow paused for human approval"
    )

    return {
        "status": "pending_approval",
        "trace": trace
    }


# =========================================================
# RESEARCH AGENT
# =========================================================

def research_node(state: State):

    trace = state.get("trace", [])

    attempts = (
        state.get("research_attempts", 0) + 1
    )

    trace.append(
        f"🔎 Research Agent attempt {attempts}"
    )

    print("\n========================================")
    print(
        f"       RESEARCH AGENT - ATTEMPT {attempts}"
    )
    print("========================================")

    try:

        result = research_agent(
            state["user_task"]
        )

        if not result or not result.strip():

            raise ValueError(
                "Research Agent returned empty result."
            )

        result = result[:3000]

        trace.append(
            "🌐 Web Search Tool used"
        )

        trace.append(
            "✅ Research Agent completed successfully"
        )

        print(result)

        return {
            "research": result,
            "research_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        print(
            f"❌ Research Agent failed: {error}"
        )

        trace.append(
            "❌ Research Agent failed: "
            f"{str(error)[:100]}"
        )

        if attempts < 2:

            trace.append(
                "🔄 Research Agent will retry"
            )

            return {
                "research_attempts": attempts,
                "trace": trace
            }

        trace.append(
            "🛑 Research Agent failed after retry"
        )

        return {
            "research": "",
            "research_attempts": attempts,
            "status": "failed",
            "trace": trace
        }


# =========================================================
# RESEARCH ROUTER
# =========================================================

def research_router(state: State):

    if state.get("research"):
        return "data"

    if state.get("research_attempts", 0) < 2:
        return "research"

    return "stop"


# =========================================================
# DATA AGENT
# =========================================================

def data_node(state: State):

    trace = state.get("trace", [])

    attempts = (
        state.get("data_attempts", 0) + 1
    )

    trace.append(
        f"📊 Data Agent attempt {attempts}"
    )

    print("\n========================================")
    print(
        f"          DATA AGENT - ATTEMPT {attempts}"
    )
    print("========================================")

    try:

        research = state["research"][:2500]

        result = data_agent(
            f"""
Analyze the following research:

{research}

Provide:

1. Important data points
2. Comparisons
3. Key observations
4. Short conclusion

Keep the response concise.
Do not invent data.
Use only the supplied research.
"""
        )

        if not result or not result.strip():

            raise ValueError(
                "Data Agent returned empty result."
            )

        result = result[:2500]

        trace.append(
            "✅ Data Agent completed successfully"
        )

        print(result)

        return {
            "analysis": result,
            "data_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        print(
            f"❌ Data Agent failed: {error}"
        )

        trace.append(
            "❌ Data Agent failed: "
            f"{str(error)[:100]}"
        )

        if attempts < 2:

            trace.append(
                "🔄 Data Agent will retry"
            )

            return {
                "data_attempts": attempts,
                "trace": trace
            }

        trace.append(
            "🛑 Data Agent failed after retry"
        )

        return {
            "analysis": "",
            "data_attempts": attempts,
            "status": "failed",
            "trace": trace
        }


# =========================================================
# DATA ROUTER
# =========================================================

def data_router(state: State):

    if state.get("analysis"):
        return "writer"

    if state.get("data_attempts", 0) < 2:
        return "data"

    return "stop"


# =========================================================
# WRITER AGENT
# =========================================================

def writer_node(state: State):

    trace = state.get("trace", [])

    attempts = (
        state.get("writer_attempts", 0) + 1
    )

    trace.append(
        f"📝 Writer Agent attempt {attempts}"
    )

    print("\n========================================")
    print(
        f"         WRITER AGENT - ATTEMPT {attempts}"
    )
    print("========================================")

    try:

        task = state["user_task"][:1000]

        research = state["research"][:2000]

        analysis = state["analysis"][:2000]

        review = state.get(
            "review",
            ""
        )[:2000]

        result = writer_agent(
            f"""
Create a COMPLETE and professional final report.

USER TASK:
{task}

RESEARCH:
{research}

DATA ANALYSIS:
{analysis}

REVIEWER FEEDBACK:
{review}

IMPORTANT REQUIREMENTS:

1. Complete every required section.
2. Do not stop in the middle of a sentence.
3. Do not stop in the middle of a table.
4. Do not use unfinished text such as "...".
5. Include a clear conclusion.
6. Include a References section.
7. Do not invent sources, URLs, citations, or facts.
8. Use only the supplied information.
9. If reviewer feedback exists, fix every issue.
10. Make sure the report ends properly.

Required sections:

# Title

## 1. Introduction

## 2. Main Findings

## 3. Comparison

## 4. Advantages and Disadvantages

## 5. Conclusion

## 6. References

If references are not available, write:

"References were not provided in the available source material."

Return ONLY the final polished report.
"""
        )

        if not result or not result.strip():

            raise ValueError(
                "Writer Agent returned empty result."
            )

        result = result[:7000]

        trace.append(
            "✅ Writer Agent completed successfully"
        )

        print(result)

        return {
            "final_report": result,
            "writer_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        print(
            f"❌ Writer Agent failed: {error}"
        )

        trace.append(
            "❌ Writer Agent failed: "
            f"{str(error)[:100]}"
        )

        if attempts < 2:

            trace.append(
                "🔄 Writer Agent will retry"
            )

            return {
                "writer_attempts": attempts,
                "trace": trace
            }

        trace.append(
            "🛑 Writer Agent failed after retry"
        )

        return {
            "final_report": "",
            "writer_attempts": attempts,
            "status": "failed",
            "trace": trace
        }


# =========================================================
# REVIEWER AGENT
# =========================================================

def review_node(state: State):

    trace = state.get("trace", [])

    attempts = (
        state.get("review_attempts", 0) + 1
    )

    trace.append(
        f"🔍 Reviewer Agent attempt {attempts}"
    )

    print("\n========================================")
    print(
        f"        REVIEWER AGENT - ATTEMPT {attempts}"
    )
    print("========================================")

    try:

        review = reviewer_agent(
            user_task=state["user_task"][:1000],

            research=state["research"][:2000],

            analysis=state["analysis"][:2000],

            final_report=state["final_report"][:6000]
        )

        if not review or not review.strip():

            raise ValueError(
                "Reviewer returned empty result."
            )

        review = review[:3000]

        trace.append(
            "✅ Reviewer Agent completed"
        )

        print(review)

        return {
            "review": review,
            "review_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        print(
            f"❌ Reviewer Agent failed: {error}"
        )

        trace.append(
            "❌ Reviewer Agent failed: "
            f"{str(error)[:100]}"
        )

        return {
            "review": "",
            "review_attempts": attempts,
            "status": "failed",
            "trace": trace
        }


# =========================================================
# REVIEW ROUTER
# =========================================================

def review_router(state: State):

    review = state.get(
        "review",
        ""
    )

    trace = state.get(
        "trace",
        []
    )

    # Remove Markdown characters and normalize case.
    # This handles:
    # STATUS: APPROVED
    # **STATUS:** APPROVED
    # **STATUS: APPROVED**
    clean_review = (
        review
        .replace("*", "")
        .replace("#", "")
        .strip()
        .lower()
    )

    # =====================================================
    # APPROVED
    # =====================================================

    if "status: approved" in clean_review:

        trace.append(
            "✅ Reviewer approved the report"
        )

        return "finish"


    # =====================================================
    # REJECTED
    # =====================================================

    if "status: rejected" in clean_review:

        trace.append(
            "⚠️ Reviewer rejected the report"
        )

        # Give Writer one revision.
        if state.get(
            "writer_attempts",
            0
        ) < 2:

            trace.append(
                "🔄 Reviewer feedback sent back to Writer"
            )

            return "rewrite"


        # Maximum revision reached.
        trace.append(
            "❌ Report rejected after maximum "
            "revision attempts"
        )

        return "stop"


    # =====================================================
    # UNCLEAR REVIEW
    # =====================================================

    trace.append(
        "⚠️ Reviewer status was unclear"
    )

    trace.append(
        "🛑 Workflow stopped because review "
        "was unclear"
    )

    return "stop"


# =========================================================
# STOP NODE
# =========================================================

def stop_node(state: State):

    trace = state.get(
        "trace",
        []
    )

    trace.append(
        "🛑 Workflow stopped"
    )

    return {
        "status": "failed",
        "trace": trace
    }


# =========================================================
# FINISH NODE
# =========================================================

def finish_node(state: State):

    trace = state.get(
        "trace",
        []
    )

    trace.append(
        "✅ Workflow completed successfully"
    )

    return {
        "status": "completed",
        "trace": trace
    }


# =========================================================
# BUILD LANGGRAPH
# =========================================================

graph = StateGraph(State)


# =========================================================
# ADD NODES
# =========================================================

graph.add_node(
    "supervisor",
    supervisor
)

graph.add_node(
    "safety_check",
    safety_check
)

graph.add_node(
    "wait",
    wait_node
)

graph.add_node(
    "research",
    research_node
)

graph.add_node(
    "data",
    data_node
)

graph.add_node(
    "writer",
    writer_node
)

graph.add_node(
    "reviewer",
    review_node
)

graph.add_node(
    "finish",
    finish_node
)

graph.add_node(
    "stop",
    stop_node
)


# =========================================================
# START
# =========================================================

graph.add_edge(
    START,
    "supervisor"
)


# =========================================================
# SUPERVISOR → SAFETY
# =========================================================

graph.add_edge(
    "supervisor",
    "safety_check"
)


# =========================================================
# SAFETY ROUTING
# =========================================================

graph.add_conditional_edges(
    "safety_check",
    safety_router,
    {
        "wait": "wait",
        "research": "research",
        "stop": "stop"
    }
)


# =========================================================
# HUMAN APPROVAL WAIT
# =========================================================

graph.add_edge(
    "wait",
    END
)


# =========================================================
# RESEARCH ROUTING
# =========================================================

graph.add_conditional_edges(
    "research",
    research_router,
    {
        "research": "research",
        "data": "data",
        "stop": "stop"
    }
)


# =========================================================
# DATA ROUTING
# =========================================================

graph.add_conditional_edges(
    "data",
    data_router,
    {
        "data": "data",
        "writer": "writer",
        "stop": "stop"
    }
)


# =========================================================
# WRITER → REVIEWER
# =========================================================

graph.add_edge(
    "writer",
    "reviewer"
)


# =========================================================
# REVIEWER ROUTING
# =========================================================

graph.add_conditional_edges(
    "reviewer",
    review_router,
    {
        "finish": "finish",
        "rewrite": "writer",
        "stop": "stop"
    }
)


# =========================================================
# FINISH / STOP
# =========================================================

graph.add_edge(
    "finish",
    END
)

graph.add_edge(
    "stop",
    END
)


# =========================================================
# COMPILE
# =========================================================

app = graph.compile()


# =========================================================
# RUN TASK
# =========================================================

def run_task(user_task: str):

    result = app.invoke({

        "user_task": user_task,

        "plan": "",

        "research": "",

        "analysis": "",

        "final_report": "",

        "review": "",

        "human_approved": False,

        "status": "started",

        "research_attempts": 0,

        "data_attempts": 0,

        "writer_attempts": 0,

        "review_attempts": 0,

        "trace": []
    })


    # =====================================================
    # SAVE ONLY COMPLETED / APPROVED TASKS
    # =====================================================

    if result["status"] == "completed":

        save_memory(
            user_task=user_task,

            research=result.get(
                "research",
                ""
            ),

            analysis=result.get(
                "analysis",
                ""
            ),

            final_report=result.get(
                "final_report",
                ""
            )
        )

        result["trace"].append(
            "💾 Task saved to PostgreSQL"
        )

        result["trace"].append(
            "🧠 Semantic memory saved to ChromaDB"
        )


    return result


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    user_task = """
    Research electric vehicles and create a comparison
    report covering advantages, disadvantages,
    performance, charging and environmental benefits.
    """

    result = run_task(
        user_task
    )


    if result["status"] == "completed":

        print("\n========================================")
        print("             FINAL REPORT")
        print("========================================")

        print(
            result.get(
                "final_report",
                ""
            )
        )

        print("\n========================================")
        print("              REVIEW")
        print("========================================")

        print(
            result.get(
                "review",
                "No review available."
            )
        )


    elif result["status"] == "pending_approval":

        print("\n========================================")
        print("       HUMAN APPROVAL REQUIRED")
        print("========================================")

        print(user_task)


    else:

        print("\n========================================")
        print("             TASK FAILED")
        print("========================================")

        print(
            result.get(
                "review",
                ""
            )
        )


    print("\n========================================")
    print("          EXECUTION TRACE")
    print("========================================")

    for item in result.get(
        "trace",
        []
    ):

        print(item)


    print("\n========================================")
    print("       ORCHESTRATION FINISHED")
    print("========================================")