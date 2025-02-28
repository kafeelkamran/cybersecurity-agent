# cybersecurity_agent.py

import subprocess
from typing import Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from datetime import datetime
import shutil

# State Definition using TypedDict for LangGraph compatibility
class AgentState(TypedDict):
    task_list: List[dict]
    scope: Dict[str, List[str]]
    results: Dict
    logs: List[str]
    current_task: Optional[dict]
    retry_count: Dict[str, int]

# Scope Enforcement
class ScopeManager:
    def __init__(self, scope: Dict):
        self.domains = scope.get("domains", [])
        self.ip_ranges = scope.get("ip_ranges", [])
    
    def is_in_scope(self, target: str) -> bool:
        if "." in target:  # Domain check
            return any(domain in target for domain in self.domains)
        return True  # Simplified for example

# Security Tools Integration
@tool
def run_nmap(target: str, ports: str = "1-1000") -> dict:
    """Runs an nmap scan on the specified target with given port range.
    
    Args:
        target (str): The domain or IP to scan
        ports (str): Port range to scan (default: '1-1000')
    
    Returns:
        dict: Contains 'output' with scan results and 'error' if any
    """
    if not shutil.which("nmap"):
        return {"error": "nmap is not installed or not found in PATH"}
    cmd = f"nmap -p {ports} {target}"
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        output = result.stdout
        vulnerabilities = ["Open port detected" for line in output.split("\n") if "open" in line and "/tcp" in line]
        return {"output": output, "error": result.stderr, "vulnerabilities": vulnerabilities if vulnerabilities else []}
    except Exception as e:
        return {"error": str(e), "vulnerabilities": []}

@tool
def run_gobuster(target: str, wordlist: str = r"D:\cybersecurity agent\wordlists\common.txt") -> dict:
    """Runs a gobuster directory enumeration scan on the target.
    
    Args:
        target (str): The URL or domain to scan
        wordlist (str): Path to wordlist file (default: 'D:\\cybersecurity agent\\wordlists\\common.txt')
    
    Returns:
        dict: Contains 'output' with scan results and 'error' if any
    """
    if not shutil.which("gobuster"):
        return {"error": "gobuster is not installed or not found in PATH"}
    cmd = f"gobuster dir -u {target} -w \"{wordlist}\""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout
        vulnerabilities = ["Directory found" for line in output.split("\n") if "Status: 200" in line or "Status: 301" in line]
        return {"output": output, "error": result.stderr, "vulnerabilities": vulnerabilities if vulnerabilities else []}
    except Exception as e:
        return {"error": str(e), "vulnerabilities": []}

# Task Management
def task_planner(state: AgentState) -> Dict:
    instruction = state.get("current_task", {}).get("instruction", "")
    updates = {"task_list": state.get("task_list", [])}
    
    if "scan" in instruction.lower() and "ports" in instruction.lower():
        updates["task_list"].append({
            "id": "nmap_scan",
            "type": "nmap",
            "target": instruction.split(" ")[1] if len(instruction.split()) > 1 else "google.com",
            "params": {"ports": "1-1000"},
            "status": "pending"
        })
    
    if "discover directories" in instruction.lower():
        updates["task_list"].append({
            "id": "gobuster_scan",
            "type": "gobuster",
            "target": instruction.split(" ")[1] if len(instruction.split()) > 1 else "google.com",
            "params": {"wordlist": r"D:\cybersecurity agent\wordlists\common.txt"},
            "status": "pending"
        })
    
    updates["logs"] = state.get("logs", []) + [f"{datetime.now()} - Planned tasks from instruction: {instruction}"]
    return updates

def task_executor(state: AgentState) -> Dict:
    scope_manager = ScopeManager(state.get("scope", {}))
    task_list = state.get("task_list", [])
    current_task = next((t for t in task_list if t["status"] == "pending"), None)
    updates = {
        "logs": state.get("logs", []),
        "results": state.get("results", {}),
        "retry_count": state.get("retry_count", {}),
        "task_list": task_list
    }
    
    if not current_task:
        updates["logs"].append(f"{datetime.now()} - No pending tasks")
        return updates
    
    if not scope_manager.is_in_scope(current_task["target"]):
        updates["logs"].append(f"{datetime.now()} - Scope violation for {current_task['target']}")
        current_task["status"] = "failed"
        updates["results"][current_task["id"]] = {"error": "Target out of scope"}
        return updates
    
    updates["current_task"] = current_task
    current_task["status"] = "running"  # Mark task as running
    updates["logs"].append(f"{datetime.now()} - Task {current_task['id']} started")
    task_type = current_task["type"]
    
    try:
        if task_type == "nmap":
            result = run_nmap.invoke({"target": current_task["target"], 
                                   "ports": current_task["params"]["ports"]})
        elif task_type == "gobuster":
            wordlist = current_task["params"].get("wordlist", r"D:\cybersecurity agent\wordlists\common.txt")
            result = run_gobuster.invoke({"target": current_task["target"], "wordlist": wordlist})
        
        updates["results"][current_task["id"]] = result
        current_task["status"] = "completed"
        updates["logs"].append(f"{datetime.now()} - Task {current_task['id']} completed")
        
        if task_type == "nmap" and "80" in result.get("output", ""):
            updates["task_list"].append({
                "id": f"gobuster_{len(task_list)}",
                "type": "gobuster",
                "target": current_task["target"],
                "params": {"wordlist": r"D:\cybersecurity agent\wordlists\common.txt"},
                "status": "pending"
            })
            updates["logs"].append(f"{datetime.now()} - Added gobuster task due to port 80 detection")
    
    except Exception as e:
        retry_count = updates["retry_count"].get(current_task["id"], 0)
        if retry_count < 3:
            updates["retry_count"][current_task["id"]] = retry_count + 1
            updates["logs"].append(f"{datetime.now()} - Task {current_task['id']} failed, retry {retry_count + 1}")
            if task_type == "nmap":
                result = run_nmap.invoke({"target": current_task["target"], 
                                        "ports": current_task["params"]["ports"]})
            elif task_type == "gobuster":
                wordlist = current_task["params"].get("wordlist", r"D:\cybersecurity agent\wordlists\common.txt")
                result = run_gobuster.invoke({"target": current_task["target"], "wordlist": wordlist})
            updates["results"][current_task["id"]] = result
        else:
            current_task["status"] = "failed"
            updates["logs"].append(f"{datetime.now()} - Task {current_task['id']} failed permanently")
            if task_type == "nmap":
                result = run_nmap.invoke({"target": current_task["target"], 
                                        "ports": current_task["params"]["ports"]})
            elif task_type == "gobuster":
                wordlist = current_task["params"].get("wordlist", r"D:\cybersecurity agent\wordlists\common.txt")
                result = run_gobuster.invoke({"target": current_task["target"], "wordlist": wordlist})
            updates["results"][current_task["id"]] = result
    
    return updates

# Workflow Definition
def build_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("planner", task_planner)
    workflow.add_node("executor", task_executor)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "executor")
    
    def should_continue(state: AgentState):
        return "continue" if any(t["status"] in ["pending", "running"] for t in state.get("task_list", [])) else "end"
    
    workflow.add_conditional_edges("executor", should_continue, {
        "continue": "executor",
        "end": END
    })
    
    return workflow.compile()

def run_workflow_step_by_step(initial_state):
    """Generator to run the workflow step-by-step for real-time updates."""
    app = build_workflow()
    state = initial_state
    while True:
        state = app.invoke(state, config={"step": True})
        yield state
        if not any(t["status"] in ["pending", "running"] for t in state.get("task_list", [])):
            break

if __name__ == "__main__":
    initial_state = {
        "task_list": [],
        "scope": {"domains": ["google.com"], "ip_ranges": []},
        "results": {},
        "logs": [],
        "current_task": {"instruction": "Scan google.com for open ports and discover directories"},
        "retry_count": {}
    }
    for state in run_workflow_step_by_step(initial_state):
        print("Step State:", state)