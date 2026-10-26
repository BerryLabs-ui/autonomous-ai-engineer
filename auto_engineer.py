import os
import subprocess
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()

# Initialize the LLM using Groq (Free API)
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# --- 1. DEFINE THE STATE ---
class EngineerState(TypedDict):
    prompt: str
    code: str
    error: str
    iterations: int
    is_success: bool

# --- 2. DEFINE THE AGENTS ---

def coder_agent(state: EngineerState):
    print(f"\n--- [Iteration {state['iterations'] + 1}] CODER AGENT ---")
    if state['iterations'] == 0:
        system_prompt = "You are an AI Engineer. Write a complete, working Python script based on the user prompt. Output ONLY the code, no markdown formatting, no explanations."
        prompt = state['prompt']
    else:
        system_prompt = f"You are an AI Engineer. Your previous code failed with this error:\n{state['error']}\n\nFix the code. Output ONLY the corrected Python code, no markdown formatting."
        prompt = f"Original goal: {state['prompt']}\n\nPrevious code:\n{state['code']}"
        
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    
    clean_code = response.content.replace("```python", "").replace("```", "").strip()
    return {"code": clean_code, "iterations": state["iterations"] + 1}

def executor_agent(state: EngineerState):
    print("--- EXECUTOR AGENT ---")
    filepath = "generated_app.py"
    with open(filepath, "w") as f:
        f.write(state["code"])
    
    print("Running generated code...")
    result = subprocess.run(["python", filepath], capture_output=True, text=True, timeout=15)
    
    if result.returncode == 0:
        print("✅ Code executed successfully.")
        print("\n--- STDOUT ---")
        print(result.stdout)
        return {"error": "", "is_success": True}
    else:
        print("❌ Execution failed. Capturing error.")
        error_msg = result.stderr.strip().split('\n')[-1]
        print(f"Error: {error_msg}")
        return {"error": error_msg, "is_success": False}

def router(state: EngineerState):
    if state["is_success"] or state["iterations"] >= 4:
        return "end"
    return "fix"

# --- 3. BUILD THE GRAPH ---
workflow = StateGraph(EngineerState)

workflow.add_node("coder", coder_agent)
workflow.add_node("executor", executor_agent)

workflow.set_entry_point("coder")
workflow.add_edge("coder", "executor")

workflow.add_conditional_edges(
    "executor",
    router,
    {
        "fix": "coder",
        "end": END
    }
)

auto_engineer = workflow.compile()

# --- 4. EXECUTE ---
if __name__ == "__main__":
    # The prompt that forces the AI to write and test code
    user_prompt = "Write a Python script that generates 5 random numbers using the 'numpy' library, calculates their mean, and prints the result. You must import numpy as np."
    
    print(f"User Prompt: {user_prompt}")
    
    initial_state = {
        "prompt": user_prompt,
        "code": "",
        "error": "",
        "iterations": 0,
        "is_success": False
    }
    
    final_state = auto_engineer.invoke(initial_state)
    
    print("\n--- FINAL EXECUTABLE CODE ---")
    print(final_state["code"])