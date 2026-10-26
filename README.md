# Autonomous AI Engineer Loop

An autonomous, self-correcting multi-agent system built with LangGraph and Llama 3. It takes a product requirement, writes code, executes it in a local sandbox, catches errors, and rewrites the code until it runs successfully.

## The Problem
AI Engineers spend 80% of their time writing code, running it, reading the stack trace, and fixing bugs. This is a slow, manual loop.

## The Solution
This project implements a "Write-Test-Fix" state machine.
1. **Coder Agent:** Writes the Python script.
2. **Executor Agent:** Runs the script in a local subprocess.
3. **Router:** If the code fails, it captures the exact stack trace and routes back to the Coder Agent.
4. **Loop:** It repeats until the code executes perfectly.

## Tech Stack
* Python
* LangGraph (State Machine)
* LangChain (Agent Orchestration)
* Groq (Llama 3 API)

## How to Run
1. Clone the repo.
2. Install dependencies: `pip install langgraph langchain-groq python-dotenv`
3. Create a `.env` file and add: `GROQ_API_KEY=your_api_key_here`
4. Run `python auto_engineer.py`
