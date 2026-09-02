# 🤖 Agent Orchestration System

A multi-agent AI orchestration platform that coordinates specialized AI agents to solve complex multi-step tasks.

The system uses a Supervisor Agent to plan tasks, delegates work to specialized agents, performs safety checks, supports human approval, reviews generated results, and stores task information using PostgreSQL, ChromaDB, and Redis.

---

## 🚀 Features

- Supervisor Agent
- Research Agent
- Data Analysis Agent
- Writer Agent
- Reviewer Agent
- Reviewer feedback and revision loop
- Web Search Tool
- Calculator Tool
- Human-in-the-Loop approval
- Safety checks
- Retry handling
- PostgreSQL persistent task memory
- ChromaDB semantic memory
- Semantic Memory Search
- Redis working memory
- Task history
- Execution tracing
- Streamlit dashboard
- Docker support
- Docker Compose support

---

## 🧠 System Architecture

```text
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │  Streamlit  │
                    │     UI      │
                    └──────┬──────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Supervisor    │
                  │      Agent      │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Safety Check   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Research Agent  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Web Search Tool │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Data Agent    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Writer Agent   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Reviewer Agent  │
                  └────────┬────────┘
                           │
                    ┌──────┴───────┐
                    │              │
                 APPROVED       REJECTED
                    │              │
                    ▼              │
              Final Report         │
                                   │
                                   └──────► Writer
                                            Revision

                           │
                 ┌─────────┴──────────┐
                 ▼                    ▼
          PostgreSQL               ChromaDB
       Persistent Memory      Semantic Long-Term Memory

                           │
                           ▼
                         Redis
                  Working / Task State