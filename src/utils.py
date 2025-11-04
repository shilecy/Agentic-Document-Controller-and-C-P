# src/utils.py (Revised)

import pandas as pd
import json
from datetime import datetime, date
import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Global Configuration ---
LOGS_DIR = 'logs'
COMMUNICATIONS_LOG_PATH = os.path.join(LOGS_DIR, 'communications_log.txt')
ACTIVITY_LOG_PATH = os.path.join(LOGS_DIR, 'activity_log.txt')
os.makedirs('data', exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Set the current date for simulation (e.g., today: 2025-10-30)
# NOTE: The expiration date check will be based on this. 
# Documents D001 (03-15) and D002 (12-10) are ALREADY expired based on this date.
CURRENT_DATE = date(2025, 10, 30) 


# --- Logging Helper (Kept simple and clean) ---
def log_activity(agent_name, action, detail):
    """Logs internal agent actions to the Activity Log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{agent_name}] {action}: {detail}\n"
    # Ensure logs directory exists before writing
    os.makedirs(LOGS_DIR, exist_ok=True) 
    with open(ACTIVITY_LOG_PATH, 'a') as f:
        f.write(log_entry)
    print(f"[{agent_name}] {action}: {detail}")
    return log_entry

try:
    # 1. Load HR/IPSG List: Use column names directly for consistency
    HR_IPSG_DF = pd.read_csv('data/hr_ipsg_list.csv')

    # NEW LINE HERE: Convert the DataFrame to the LIST/Dictionary format
    # The dictionary key will be the email, and the value will be the staff info.
    HR_IPSG_LIST = HR_IPSG_DF.set_index('email').to_dict('index')
    
    # 2. Load Documents: Pay attention to date formats
    DOCUMENTS_DF = pd.read_csv('data/documents.csv')
    # Use your exact date format (e.g., 2025-03-15)
    DOCUMENTS_DF['Expiry_Date_dt'] = pd.to_datetime(
        DOCUMENTS_DF['expiry_date'], format='%Y-%m-%d', errors='coerce'
    ).dt.date
    
    # 3. Load JSON files
    with open('data/consultant_application.json', 'r') as f:
        CONSULTANT_APP = json.load(f)
    with open('data/email_templates.json', 'r') as f:
        EMAIL_TEMPLATES = json.load(f)
    with open('data/policy_rules.json', 'r') as f:
        POLICY_RULES = json.load(f)
    
    # Log the successful setup (this will be the very first log entry)
    log_activity("Orchestrator", "Setup", "All data loaded and logging initialized.")

except Exception as e:
    print(f"!!! CRITICAL ERROR: Could not load required data files. Check 'data/' folder. Error: {e}")
    # Initialize empty structures to prevent immediate crash
    DOCUMENTS_DF, HR_IPSG_DF = pd.DataFrame(), pd.DataFrame()
    POLICY_RULES, EMAIL_TEMPLATES, CONSULTANT_APP = {}, {}, {}

def get_owner_info(email):
    """Retrieves staff info from the HR_IPSG_LIST based on email using default CSV headers."""
    info = HR_IPSG_LIST.get(email)
    
    if info:
        info['email'] = email
        # The returned dictionary uses keys: 'name', 'position', 'department', 'approval_role'
        return info
    else:
        log_activity("Utility", "Error", f"Staff email {email} not found in HR list. Defaulting to QMR.")
        
        qmr_email = 'qmr@phmk.my' 
        # Ensure the fallback uses the correct keys: 'name', 'position', etc.
        qmr_info = HR_IPSG_LIST.get(qmr_email, {'name': 'Default QMR', 'position': 'QMR', 'approval_role': 'Approver'})
        qmr_info['email'] = qmr_email
        return qmr_info

# --- Initialize Communication Log (Moved here for dependency) ---
def log_communication(recipient, comm_type, subject, body):
    """Writes a log entry for a simulated communication."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] [{comm_type}] TO: {recipient} | "
        f"SUBJECT: {subject}\n"
        f"---BODY---\n{body}\n----------\n"
    )
    with open(COMMUNICATIONS_LOG_PATH, 'a') as f:
        f.write(log_entry)
        
    log_activity("Communication Agent", f"{comm_type} Sent", f"'{subject}' to {recipient}")


# Re-initialize the log files with headers (since they might have failed on previous runs)
with open(ACTIVITY_LOG_PATH, 'w') as f:
    f.write(f"--- Agentic Workflow Execution Log Start: {CURRENT_DATE} ---\n")
with open(COMMUNICATIONS_LOG_PATH, 'w') as f:
    f.write(f"--- Simulated Communications Log Start: {CURRENT_DATE} ---\n")