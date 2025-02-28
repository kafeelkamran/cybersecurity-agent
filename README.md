```markdown
# Cybersecurity Agent with LangGraph and Streamlit

This project implements an agentic cybersecurity pipeline using LangGraph and LangChain, integrated with a Streamlit UI for real-time visualization. It autonomously performs security scans (e.g., nmap, gobuster), manages a dynamic task list, enforces scope constraints, and generates detailed reports with vulnerability highlights.

## Features
- **Dynamic Task Execution**: Breaks down high-level security instructions into executable steps, managing tasks with statuses (Pending, Running, Completed, Failed).
- **Scope Enforcement**: Restricts scans to user-defined domains and IP ranges, preventing out-of-scope actions.
- **Security Tools Integration**: Executes real nmap and gobuster scans, parsing outputs for vulnerabilities.
- **Real-Time Monitoring**: Streamlit UI displays ongoing scans, task list, logs, and results as they happen.
- **Audit Reporting**: Provides a final report with task summaries, scope violations, and highlighted vulnerabilities.
- **Visual Dashboard**: Bar chart showing task status distribution.

## Project Structure
- `cybersecurity_agent.py`: Core LangGraph-based workflow for task planning, execution, and scope enforcement.
- `app.py`: Streamlit UI for scope definition, instruction input, and real-time visualization.
- `wordlists/`: Directory containing wordlist files (e.g., `common.txt`) for gobuster.

## Prerequisites
- Python 3.10 or 3.12
- Virtual environment (recommended)
- System tools: `nmap`, `gobuster`

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv cyberagent.venv
source cyberagent.venv/bin/activate  # On Windows: cyberagent.venv\Scripts\activate
```

### 3. Install Python Dependencies
```bash
pip install langgraph langchain-core streamlit pandas
```

### 4. Install System Dependencies
- **nmap**:
  - Windows: Download from [nmap.org](https://nmap.org/download.html) and add to PATH.
  - Linux: `sudo apt-get install nmap`
  - macOS: `brew install nmap`
- **gobuster**:
  - Download from [GitHub Releases](https://github.com/OJ/gobuster/releases).
  - Extract to a directory (e.g., `C:\Program Files\gobuster`) and add to PATH.
  - Verify: `gobuster --version`

### 5. Prepare Wordlists
- Create a `wordlists` folder in the project directory.
- Add a wordlist file (e.g., `common.txt`) or download from [SecLists](https://github.com/danielmiessler/SecLists).
- Default path: `D:\cybersecurity agent\wordlists\common.txt` (adjust in `cybersecurity_agent.py` if needed).

## Running the Application

### 1. Start the Streamlit App
```bash
streamlit run app.py
```
- Opens at `http://localhost:8501` in your browser.

### 2. Usage
1. **Define Scope**:
   - Enter domains (e.g., `google.com`) and IP ranges (e.g., `192.168.1.0/24`) in the form.
   - Click "Set Scope".
2. **Enter Instructions**:
   - Input a security task (e.g., "Scan google.com for open ports and discover directories").
3. **Run Scan**:
   - Click "Run Scan" to start the workflow.
   - Watch the dashboard update in real-time with task list, logs, results, and summary.

## Configuration
- **Wordlist Path**: Edit `run_gobuster` in `cybersecurity_agent.py` to change the default wordlist path if not using `D:\cybersecurity agent\wordlists\common.txt`.
- **Scope**: Defined via the UI; no additional config file needed.

## Example Output
- **Task List**: Table with tasks (e.g., `nmap_scan`, `gobuster_scan`) and statuses.
- **Logs**: Timestamped entries like "Task nmap_scan completed".
- **Results**: Tool outputs and errors, with vulnerabilities (e.g., "Open port detected") highlighted.
- **Summary**: Bar chart of task statuses and scope violation warnings.

## Testing & Verification
- Ensure `nmap` and `gobuster` are in PATH and functional.
- Test with a local target (e.g., a test server) if public domains like `google.com` block scans.
- Expected UI: Real-time updates every second during scan execution.

## System Architecture
- **LangGraph Workflow**:
  - `task_planner`: Breaks instructions into tasks.
  - `task_executor`: Executes tasks, enforces scope, handles retries.
- **Streamlit UI**:
  - Real-time containers for task list, logs, results, and summary.
- **Scope Enforcement**: `ScopeManager` class validates targets.

## Deliverables
- **Pipeline**: LangGraph-based, dynamic cybersecurity scans.
- **Task Management**: Real-time monitoring with retries.
- **Scope**: Enforced via UI-defined domains/IP ranges.
- **Logs/Reports**: Detailed execution logs and visual summary.

## Bonus Features
- **Visual Deployment**: Fully implemented with Streamlit.
- **Unit Tests**: Not included (see Future Improvements).

## Future Improvements
- Add unit tests with Pytest for task execution and scope enforcement.
- Support more tools (e.g., ffuf, sqlmap).
- Enhance vulnerability detection with regex-based parsing.
- Implement a config file for wordlist paths and tool settings.

## Demo
- A 3-4 minute demo video could be recorded showing:
  1. Scope definition in the UI.
  2. Running a scan with real-time updates.
  3. Reviewing logs, results, and vulnerabilities.
  4. Final report with bar chart.

## License
Apache License - feel free to use, modify, and distribute.

## Contributing
Pull requests are welcome! Please open an issue first to discuss changes.

## Contact
For questions, reach out via GitHub issues or [kafeel17kamran@gmail.com].
```