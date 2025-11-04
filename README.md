## AI Agent Workflow Orchestrator (Local Simulation Mode)

This repository contains the core logic for an AI-powered agent system designed to automate compliance workflows in a hospital setting. The primary file, src/agents/main_orchestrator.py, is configured to run in a Local Batch Simulation Mode, executing a full end-to-end daily check without requiring a separate server or external Human-In-The-Loop (HITL) integration platform.

## Prerequisites & Setup

The agents rely on the Google Gemini API for their decision-making, summarization, and routing logic.

## 1. Environment Setup

It is highly recommended to use a Python virtual environment:

### 1. Create a virtual environment
    python -m venv venv

### 2. Activate the virtual environment
# Windows:
    .\venv\Scripts\activate


## 2. Install Dependencies

Install all required Python libraries from the requirements.txt file:

    pip install -r requirements.txt


## 3. Configure API Key (Crucial)

For the AI agents to function (i.e., generate summaries, determine urgency, and route correctly), you must set your Gemini API Key as an environment variable.

Note: If your daily quota is exceeded, the agents will use robust fallback logic, but the AI-driven features will fail, as seen in the command line output.

## Windows (Command Prompt):
    set GEMINI_API_KEY="YOUR_API_KEY_HERE"


## How to Run the Local Simulation

Once the setup is complete and your environment is activated, execute the entire agentic workflow with a single command:

    python -m src.agents.main_orchestrator


The script will clean previous logs, initialize the workflow, and execute both the Document Control and Credentialing & Privileging processes sequentially, logging all actions and communications.

## The Simulated Documents Workflow (Process A Detail)

This workflow manages the mandatory review and renewal of hospital documents (like Policies and Work Instructions). All steps marked "HITL Simulation" are automatically completed by the script in batch mode for demonstration purposes.

