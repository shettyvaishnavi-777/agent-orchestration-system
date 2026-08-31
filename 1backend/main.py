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
    raise ValueError("GROQ_API_KEY not found in .env file")


# =========================================================
# PROJECT PATHS
# =========================================================

sys.path.insert(0, "1agent")
sys.path.insert(0, "1backend")
sys.path.insert(0, "1memory")


# =========================================================
# IMPORT AGENTS
# =========================================================

from research_agent import research_agent
from data_agent import data_agent
from writer_agent import writer_agent
from reviewer_agent import reviewer_agent

from safety import requires_human_approval
from memory import save_memory


# =========================================================
# LLM
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
# SUPERVISOR
# =========================================================

def supervisor(state: State):

    task = state["user_task"]

    prompt = f"""
You are the Supervisor Agent.

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

    trace.append("✅ Supervisor created execution plan")

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

        trace.append("⚠️ Sensitive action detected")
        trace.append("⏸️ Human approval required")

        return {
            "human_approved": False,
            "status": "pending_approval",
            "trace": trace
        }

    trace.append("✅ Safety check passed")

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
# WAIT
# =========================================================

def wait_node(state: State):

    trace = state.get("trace", [])

    trace.append("⏸️ Workflow paused for human approval")

    return {
        "status": "pending_approval",
        "trace": trace
    }


# =========================================================
# RESEARCH
# =========================================================

def research_node(state: State):

    trace = state.get("trace", [])

    attempts = state.get("research_attempts", 0) + 1

    trace.append(
        f"🔎 Research Agent attempt {attempts}"
    )

    try:

        result = research_agent(
            state["user_task"]
        )

        if not result or not result.strip():
            raise ValueError(
                "Research Agent returned empty result."
            )

        result = result[:2500]

        trace.append(
            "✅ Research Agent completed successfully"
        )

        return {
            "research": result,
            "research_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        trace.append(
            f"❌ Research Agent failed: {str(error)[:100]}"
        )

        if attempts < 2:

            trace.append(
                "🔄 Research Agent will retry"
            )

            return {
                "research_attempts": attempts,
                "trace": trace
            }

        return {
            "status": "failed",
            "research_attempts": attempts,
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
# DATA
# =========================================================

def data_node(state: State):

    trace = state.get("trace", [])

    attempts = state.get("data_attempts", 0) + 1

    trace.append(
        f"📊 Data Agent attempt {attempts}"
    )

    try:

        research = state["research"][:1800]

        result = data_agent(
            f"""
Analyze this research:

{research}

Provide:
1. Important data points
2. Comparisons
3. Key observations
4. Short conclusion

Keep the response concise.
Do not invent data.
"""
        )

        if not result or not result.strip():
            raise ValueError(
                "Data Agent returned empty result."
            )

        result = result[:2000]

        trace.append(
            "✅ Data Agent completed successfully"
        )

        return {
            "analysis": result,
            "data_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        trace.append(
            f"❌ Data Agent failed: {str(error)[:100]}"
        )

        if attempts < 2:

            trace.append(
                "🔄 Data Agent will retry"
            )

            return {
                "data_attempts": attempts,
                "trace": trace
            }

        return {
            "status": "failed",
            "data_attempts": attempts,
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
# WRITER
# =========================================================

def writer_node(state: State):

    trace = state.get("trace", [])

    attempts = state.get("writer_attempts", 0) + 1

    trace.append(
        f"📝 Writer Agent attempt {attempts}"
    )

    try:

        task = state["user_task"][:500]
        research = state["research"][:1000]
        analysis = state["analysis"][:1000]

        # Include reviewer feedback when rewriting
        review = state.get("review", "")[:1000]

        result = writer_agent(
            f"""
Create a professional final report.

USER TASK:
{task}

RESEARCH:
{research}

DATA ANALYSIS:
{analysis}

PREVIOUS REVIEW FEEDBACK:
{review}

Include:
1. Title
2. Introduction
3. Main Findings
4. Comparison
5. Conclusion

Use only the supplied information.
Do not invent facts.
Keep the report concise.

If reviewer feedback is provided,
improve the report based on it.
"""
        )

        if not result or not result.strip():
            raise ValueError(
                "Writer Agent returned empty result."
            )

        result = result[:5000]

        trace.append(
            "✅ Writer Agent completed successfully"
        )

        return {
            "final_report": result,
            "writer_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        trace.append(
            f"❌ Writer Agent failed: {str(error)[:100]}"
        )

        if attempts < 2:

            trace.append(
                "🔄 Writer Agent will retry"
            )

            return {
                "writer_attempts": attempts,
                "trace": trace
            }

        return {
            "status": "failed",
            "writer_attempts": attempts,
            "trace": trace
        }


# =========================================================
# REVIEWER
# =========================================================

def review_node(state: State):

    trace = state.get("trace", [])

    attempts = state.get("review_attempts", 0) + 1

    trace.append(
        f"🔍 Reviewer Agent attempt {attempts}"
    )

    try:

        review = reviewer_agent(
            user_task=state["user_task"][:500],
            research=state["research"][:1000],
            analysis=state["analysis"][:1000],
            final_report=state["final_report"][:3000]
        )

        if not review or not review.strip():
            raise ValueError(
                "Reviewer returned empty result."
            )

        review = review[:2000]

        trace.append(
            "✅ Reviewer Agent completed"
        )

        return {
            "review": review,
            "review_attempts": attempts,
            "trace": trace
        }

    except Exception as error:

        trace.append(
            f"❌ Reviewer Agent failed: {str(error)[:100]}"
        )

        return {
            "status": "failed",
            "review_attempts": attempts,
            "trace": trace
        }


# =========================================================
# REVIEW ROUTER
# =========================================================

def review_router(state: State):

    review = state.get("review", "").lower()

    # Simple approval detection
    if "approved" in review:

        return "finish"

    # Reject / improvement
    if "rejected" in review:

        if state.get("writer_attempts", 0) < 2:
            return "rewrite"

        return "finish"

    # If reviewer did not clearly say approved/rejected,
    # accept the report after review.
    return "finish"


# =========================================================
# STOP
# =========================================================

def stop_node(state: State):

    trace = state.get("trace", [])

    trace.append(
        "🛑 Workflow stopped"
    )

    return {
        "status": "failed",
        "trace": trace
    }


# =========================================================
# FINISH
# =========================================================

def finish_node(state: State):

    trace = state.get("trace", [])

    trace.append(
        "✅ Workflow completed successfully"
    )

    return {
        "status": "completed",
        "trace": trace
    }


# =========================================================
# CREATE LANGGRAPH
# =========================================================

graph = StateGraph(State)

graph.add_node("supervisor", supervisor)
graph.add_node("safety_check", safety_check)
graph.add_node("wait", wait_node)

graph.add_node("research", research_node)
graph.add_node("data", data_node)
graph.add_node("writer", writer_node)
graph.add_node("reviewer", review_node)

graph.add_node("finish", finish_node)
graph.add_node("stop", stop_node)


# =========================================================
# EDGES
# =========================================================

graph.add_edge(
    START,
    "supervisor"
)

graph.add_edge(
    "supervisor",
    "safety_check"
)

graph.add_conditional_edges(
    "safety_check",
    safety_router,
    {
        "wait": "wait",
        "research": "research",
        "stop": "stop"
    }
)

# Pending approval ends temporarily
graph.add_edge(
    "wait",
    END
)

# Research
graph.add_conditional_edges(
    "research",
    research_router,
    {
        "research": "research",
        "data": "data",
        "stop": "stop"
    }
)

# Data
graph.add_conditional_edges(
    "data",
    data_router,
    {
        "data": "data",
        "writer": "writer",
        "stop": "stop"
    }
)

# Writer → Reviewer
graph.add_edge(
    "writer",
    "reviewer"
)

# Reviewer → Finish or Writer
graph.add_conditional_edges(
    "reviewer",
    review_router,
    {
        "finish": "finish",
        "rewrite": "writer"
    }
)

graph.add_edge(
    "finish",
    END
)

graph.add_edge(
    "stop",
    END
)


# Compile
app = graph.compile()


# =========================================================
# RUN FUNCTION
# =========================================================

def run_task(user_task: str):

    return app.invoke({

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


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    user_task = """
    Research electric vehicles and create a comparison
    report covering advantages, disadvantages,
    performance, charging and environmental benefits.
    """

    result = run_task(user_task)

    if result["status"] == "completed":

        print("\n========================================")
        print("             FINAL REPORT")
        print("========================================")

        print(result["final_report"])

        print("\n========================================")
        print("              REVIEW")
        print("========================================")

        print(result["review"])

        save_memory(
            user_task=user_task,
            research=result["research"],
            analysis=result["analysis"],
            final_report=result["final_report"]
        )

        print("\n✅ Task saved to memory.")

    elif result["status"] == "pending_approval":

        print("\n========================================")
        print("       HUMAN APPROVAL REQUIRED")
        print("========================================")

        print(user_task)

    else:

        print("\n========================================")
        print("             TASK FAILED")
        print("========================================")

    print("\n========================================")
    print("          EXECUTION TRACE")
    print("========================================")

    for item in result["trace"]:
        print(item)

    print("\n========================================")
    print("       ORCHESTRATION FINISHED")
    print("========================================")