## AI Agent Workflow Orchestrator (Local Simulation Mode)

This repository contains the core logic for an AI-powered agent system designed to automate compliance workflows in a hospital setting. The primary file, src/agents/main_orchestrator.py, is configured to run in a Local Batch Simulation Mode, executing a full end-to-end daily check without requiring a separate server or external Human-In-The-Loop (HITL) integration platform.

## Prerequisites & Setup

The agents rely on the Google Gemini API for their decision-making, summarization, and routing logic.

## 1. Environment Setup

It is highly recommended to use a Python virtual environment:

### 1. Create a virtual environment
    python -m venv venv

### 2. Activate the virtual environment
### Windows:
    .\venv\Scripts\activate


## 2. Install Dependencies

Install all required Python libraries from the requirements.txt file:

    pip install -r requirements.txt


## 3. Configure API Key (Crucial)

For the AI agents to function (i.e., generate summaries, determine urgency, and route correctly), you must set your Gemini API Key as an environment variable.

Note: If your daily quota is exceeded, the agents will use robust fallback logic, but the AI-driven features will fail, as seen in the command line output.

### Windows (Command Prompt):
    set GEMINI_API_KEY="YOUR_API_KEY_HERE"


### How to Run the Local Simulation

Once the setup is complete and your environment is activated, execute the entire agentic workflow with a single command:

    python -m src.agents.main_orchestrator


The script will clean previous logs, initialize the workflow, and execute both the Document Control and Credentialing & Privileging processes sequentially, logging all actions and communications.

## The Simulated Documents Workflow 

This workflow manages the mandatory review and renewal of hospital documents (like Policies and Work Instructions). All steps marked "HITL Simulation" are automatically completed by the script in batch mode for demonstration purposes.

Process A — Document Control Lifecycle 

This workflow runs daily to identify expiring documents, route them for review, and log compliance decisions.

Workflow Steps

| Step | Agent                     | Core Action                             | 
| ---- | ------------------------- | --------------------------------------- | 
| 1    | **Orchestrator**          | Starts daily document check             | 
| 2    | **Document Expiry Agent** | Identifies expiring docs & urgency      | 
| 3    | **AI Review Agent**       | Creates document summary                | 
| 4    | **Routing & Role Agent**  | Assigns reviewer (fallback QMR)         | 
| 5    | **Communication Agent**   | Sends “Action Required” email           | 
| 6    | **HITL Upload Action**    | Owner submits revised documents         | 
| 7    | **Communication Agent**   | Sends final approval request email      | 
| 8    | **Compliance Agent**      | Logs compliance & sets ACTIVE (Renewed) | 

Process B — Credentialing & Privileging (C&P)

Used to verify consultant credentials and grant practice privileges.

| Step | Agent                             | Action                                                    | Outcome                        |
| ---- | --------------------------------- | --------------------------------------------------------- | ------------------------------ |
| 1    | **Orchestrator**                  | Start new C&P case                                        | —                              | 
| 2    | **Credential Verification Agent** | Verify compliance                                         | Pass/Fail                      | 
| 3    | **Routing & Role Agent**          | Determine approver                                        | Approver selected              | 
| 4    | **Communication Agent**           | Send incomplete docs notice **OR** final approval request | Email sent                     | 
| 5    | **HITL Simulation**               | Reviewer approves                                         | Human approval                 | 
| 6    | **Compliance Agent**              | Log privileges granted                                    | Status = `ACTIVE (Privileged)` |

Final Consolidation

| Step | Agent                | Core Action                                 |
| ---- | -------------------- | ------------------------------------------- |
| 1    | **Compliance Agent** | Aggregates metrics & generates AI dashboard |
| 2    | **Orchestrator**     | Final logging & shutdown                    |
