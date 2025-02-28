# app.py

import streamlit as st
from cybersecurity_agent import run_workflow_step_by_step, AgentState
import pandas as pd
import time
from typing import Dict, List

# Streamlit UI
st.title("Cybersecurity Agent Dashboard")

# Scope Definition Section
st.header("Define Scan Scope")
with st.form(key="scope_form"):
    domains_input = st.text_area("Domains (one per line, e.g., google.com)", "google.com")
    ip_ranges_input = st.text_area("IP Ranges (one per line, e.g., 192.168.1.0/24)", "")
    scope_submit = st.form_submit_button(label="Set Scope")

if scope_submit:
    domains = [d.strip() for d in domains_input.split("\n") if d.strip()]
    ip_ranges = [r.strip() for r in ip_ranges_input.split("\n") if r.strip()]
    st.session_state["scope"] = {"domains": domains, "ip_ranges": ip_ranges}
    st.success("Scope defined successfully!")

# Instruction Input
st.header("Security Instructions")
instruction = st.text_input("Enter your security task instructions", 
                          "Scan google.com for open ports and discover directories")

# Run Scan and Real-Time Updates
if "scope" in st.session_state:
    if st.button("Run Scan"):
        initial_state = {
            "task_list": [],
            "scope": st.session_state["scope"],
            "results": {},
            "logs": [],
            "current_task": {"instruction": instruction},
            "retry_count": {}
        }
        
        # Containers for real-time updates
        task_container = st.empty()
        log_container = st.empty()
        result_container = st.empty()
        summary_container = st.empty()
        
        with st.spinner("Running security scan..."):
            for state in run_workflow_step_by_step(initial_state):
                # Update Task List
                task_data = [
                    {"ID": task["id"], "Type": task["type"], "Target": task["target"], "Status": task["status"]}
                    for task in state.get("task_list", [])
                ]
                with task_container.container():
                    st.header("Task List")
                    st.table(task_data)
                
                # Update Logs
                with log_container.container():
                    st.header("Execution Logs")
                    st.text_area("Logs", "\n".join(state.get("logs", [])), height=200)
                
                # Update Results
                with result_container.container():
                    st.header("Scan Results")
                    for task_id, result in state.get("results", {}).items():
                        with st.expander(f"Results for {task_id}"):
                            st.subheader("Output")
                            st.text(result.get("output", "No output"))
                            st.subheader("Errors")
                            st.text(result.get("error", "No errors"))
                            if "vulnerabilities" in result and result["vulnerabilities"]:
                                st.subheader("Vulnerabilities")
                                for vuln in result["vulnerabilities"]:
                                    st.error(vuln)
                
                # Update Summary
                with summary_container.container():
                    st.header("Summary Report")
                    completed = len([t for t in state.get("task_list", []) if t["status"] == "completed"])
                    failed = len([t for t in state.get("task_list", []) if t["status"] == "failed"])
                    pending = len([t for t in state.get("task_list", []) if t["status"] == "pending"])
                    running = len([t for t in state.get("task_list", []) if t["status"] == "running"])
                    
                    task_counts = pd.DataFrame({
                        "Status": ["Completed", "Failed", "Pending", "Running"],
                        "Count": [completed, failed, pending, running]
                    })
                    st.bar_chart(task_counts.set_index("Status"))
                    
                    scope_violations = [log for log in state.get("logs", []) if "Scope violation" in log]
                    if scope_violations:
                        st.warning("Scope Violations Detected:")
                        for violation in scope_violations:
                            st.text(violation)
                
                time.sleep(1)  # Simulate real-time feel, adjust as needed
            
            st.success("Scan completed!")
            st.session_state["final_state"] = state

# Sidebar Instructions
st.sidebar.header("How to Run")
st.sidebar.markdown("""
1. Install dependencies: `pip install streamlit pandas`
2. Ensure `cybersecurity_agent.py` is in the same directory
3. Run: `streamlit run app.py`
4. Define scope and enter instructions in the UI
""")