# 🤖 Agent Orchestration System

A multi-agent AI orchestration platform that coordinates specialized AI agents to solve complex multi-step tasks.

## Features

- Supervisor Agent
- Research Agent
- Data Analysis Agent
- Writer Agent
- Reviewer Agent
- Web Search Tool
- Calculator Tool
- Human-in-the-Loop approval
- Safety checks
- Persistent memory
- Task history
- Execution tracing
- Retry handling
- Streamlit dashboard

## Technologies

- Python
- LangGraph
- LangChain
- Groq
- Streamlit
- DuckDuckGo Search

## Architecture

```text
User
 ↓
Streamlit
 ↓
Supervisor
 ↓
Safety Check
 ↓
Research Agent
 ↓
Web Search Tool
 ↓
Data Agent
 ↓
Writer Agent
 ↓
Reviewer Agent
 ↓
Final Report
 ↓
Memory