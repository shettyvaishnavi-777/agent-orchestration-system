import streamlit as st
import sys

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Agent Orchestration System",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# PROJECT PATHS
# =========================================================

sys.path.insert(0, "1backend")
sys.path.insert(0, "1agent")
sys.path.insert(0, "1memory")

# =========================================================
# IMPORTS
# =========================================================

from main import run_task
from memory import load_memory, clear_memory


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🤖 Agent System")

page = st.sidebar.radio(
    "Navigation",
    [
        "🚀 Run Task",
        "🧠 Memory & History"
    ]
)


# =========================================================
# RUN TASK PAGE
# =========================================================

if page == "🚀 Run Task":

    st.title("🤖 AI Agent Orchestration System")

    st.write(
        "A multi-agent AI platform that decomposes complex tasks, "
        "coordinates specialist agents, uses tools, provides "
        "human oversight, maintains memory, reviews results, "
        "and generates a final answer."
    )

    st.divider()

    # =====================================================
    # TASK INPUT
    # =====================================================

    st.subheader("📝 Enter Your Task")

    user_task = st.text_area(
        "Task",
        height=150,
        placeholder=(
            "Example: Research electric vehicles and create "
            "a comparison report."
        )
    )

    # =====================================================
    # START TASK
    # =====================================================

    if st.button(
        "🚀 Start Task",
        use_container_width=True
    ):

        if not user_task.strip():

            st.warning(
                "⚠️ Please enter a task first."
            )

        else:

            with st.spinner(
                "🤖 Agents are working on your task..."
            ):

                try:

                    result = run_task(user_task)

                    st.session_state["result"] = result
                    st.session_state["user_task"] = user_task

                    # Clear old approval decision
                    st.session_state.pop(
                        "approval_decision",
                        None
                    )

                except Exception as error:

                    st.error(
                        f"❌ Error: {error}"
                    )


    # =====================================================
    # SHOW RESULT
    # =====================================================

    if "result" in st.session_state:

        result = st.session_state["result"]


        # =================================================
        # HUMAN APPROVAL
        # =================================================

        if result["status"] == "pending_approval":

            st.warning(
                "⚠️ HUMAN APPROVAL REQUIRED"
            )

            st.write(
                "The system detected a sensitive operation:"
            )

            st.code(
                st.session_state["user_task"]
            )

            st.write(
                "Choose what should happen next:"
            )

            col1, col2 = st.columns(2)


            # APPROVE
            with col1:

                if st.button(
                    "✅ APPROVE",
                    use_container_width=True
                ):

                    st.session_state[
                        "approval_decision"
                    ] = "approved"

                    st.success(
                        "✅ Human approved the requested action."
                    )

                    st.info(
                        "This project demonstrates the approval "
                        "gate without performing a real destructive "
                        "operation."
                    )


            # REJECT
            with col2:

                if st.button(
                    "❌ REJECT",
                    use_container_width=True
                ):

                    st.session_state[
                        "approval_decision"
                    ] = "rejected"

                    st.error(
                        "❌ Human rejected the requested action."
                    )

                    st.info(
                        "The workflow has been stopped."
                    )


            # SHOW DECISION
            decision = st.session_state.get(
                "approval_decision"
            )

            if decision == "approved":

                st.success(
                    "🟢 Approval Status: APPROVED"
                )

            elif decision == "rejected":

                st.error(
                    "🔴 Approval Status: REJECTED"
                )


        # =================================================
        # COMPLETED TASK
        # =================================================

        elif result["status"] == "completed":

            st.success(
                "✅ Task completed successfully!"
            )

            st.divider()


            # =================================================
            # STATUS
            # =================================================

            st.subheader("📊 Execution Status")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.success("✅ Supervisor")

            with col2:
                st.success("✅ Research")

            with col3:
                st.success("✅ Data")

            with col4:
                st.success("✅ Writer")

            with col5:
                st.success("✅ Reviewer")


            # =================================================
            # EXECUTION TRACE
            # =================================================

            st.subheader("🔍 Execution Trace")

            trace = result.get(
                "trace",
                []
            )

            if trace:

                for item in trace:

                    st.write(item)

            else:

                st.info(
                    "No execution trace available."
                )


            # =================================================
            # SUPERVISOR PLAN
            # =================================================

            st.subheader("🧠 Supervisor Plan")

            with st.expander(
                "View Supervisor Execution Plan",
                expanded=True
            ):

                st.markdown(
                    result.get(
                        "plan",
                        "No plan available."
                    )
                )


            # =================================================
            # RESEARCH
            # =================================================

            st.subheader(
                "🔎 Research Agent Result"
            )

            with st.expander(
                "View Research Results"
            ):

                research = result.get(
                    "research",
                    ""
                )

                if research:

                    st.markdown(research)

                else:

                    st.info(
                        "No research result available."
                    )


            # =================================================
            # DATA
            # =================================================

            st.subheader(
                "📈 Data Analysis Agent Result"
            )

            with st.expander(
                "View Data Analysis"
            ):

                analysis = result.get(
                    "analysis",
                    ""
                )

                if analysis:

                    st.markdown(analysis)

                else:

                    st.info(
                        "No data analysis available."
                    )


            # =================================================
            # WRITER
            # =================================================

            st.subheader(
                "📝 Writer Agent Result"
            )

            with st.expander(
                "View Generated Report"
            ):

                st.markdown(
                    result.get(
                        "final_report",
                        "No report available."
                    )
                )


            # =================================================
            # REVIEWER
            # =================================================

            st.subheader(
                "🔍 Reviewer Agent"
            )

            review = result.get(
                "review",
                ""
            )

            if review:

                # Show reviewer result
                st.info(review)

                # Detect status
                review_lower = review.lower()

                if "approved" in review_lower:

                    st.success(
                        "✅ Reviewer Status: APPROVED"
                    )

                elif "rejected" in review_lower:

                    st.warning(
                        "⚠️ Reviewer Status: REJECTED"
                    )

            else:

                st.info(
                    "No reviewer result available."
                )


            # =================================================
            # FINAL REPORT
            # =================================================

            st.subheader(
                "📄 Final Report"
            )

            final_report = result.get(
                "final_report",
                ""
            )

            if final_report:

                st.markdown(final_report)

            else:

                st.info(
                    "No final report available."
                )


        # =================================================
        # FAILED TASK
        # =================================================

        elif result["status"] == "failed":

            st.error(
                "❌ The task could not be completed."
            )

            st.subheader(
                "🔍 Execution Trace"
            )

            trace = result.get(
                "trace",
                []
            )

            for item in trace:

                st.write(item)


# =========================================================
# MEMORY & HISTORY
# =========================================================

elif page == "🧠 Memory & History":

    st.title(
        "🧠 Memory & Task History"
    )

    st.write(
        "Previously completed tasks stored by the "
        "AI Agent Orchestration System."
    )

    st.divider()


    # =====================================================
    # LOAD MEMORY
    # =====================================================

    memories = load_memory()


    # =====================================================
    # MEMORY OVERVIEW
    # =====================================================

    st.subheader(
        "📊 Memory Overview"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Stored Tasks",
            len(memories)
        )

    with col2:

        if memories:

            st.metric(
                "Memory Status",
                "Active"
            )

        else:

            st.metric(
                "Memory Status",
                "Empty"
            )


    st.divider()


    # =====================================================
    # PREVIOUS TASKS
    # =====================================================

    st.subheader(
        "📋 Previous Tasks"
    )


    if not memories:

        st.info(
            "No task history is available yet."
        )

    else:

        for index, memory in enumerate(
            reversed(memories),
            start=1
        ):

            task_name = memory.get(
                "user_task",
                "Unknown task"
            )

            with st.expander(
                f"Task {index}: {task_name[:100]}"
            ):

                st.write(
                    "**Saved at:** "
                    + memory.get(
                        "timestamp",
                        "Unknown"
                    )
                )

                st.markdown(
                    "### 🔎 Research"
                )

                st.markdown(
                    memory.get(
                        "research",
                        "No research available."
                    )
                )

                st.markdown(
                    "### 📈 Analysis"
                )

                st.markdown(
                    memory.get(
                        "analysis",
                        "No analysis available."
                    )
                )

                st.markdown(
                    "### 📝 Final Report"
                )

                st.markdown(
                    memory.get(
                        "final_report",
                        "No final report available."
                    )
                )


    # =====================================================
    # DELETE MEMORY
    # =====================================================

    st.divider()

    st.subheader(
        "🗑️ Memory Management"
    )

    if memories:

        st.warning(
            "Deleting memory permanently removes all "
            "stored task history."
        )

    else:

        st.info(
            "There is currently no saved memory."
        )


    if st.button(
        "🗑️ Delete All Memory",
        use_container_width=True
    ):

        clear_memory()

        st.success(
            "✅ All memory has been deleted."
        )

        st.rerun()