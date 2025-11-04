# src/agents/compliance_agent.py

from src.utils import DOCUMENTS_DF, ACTIVITY_LOG_PATH, log_activity
from google import genai
import json
import os
from datetime import date

# --- Helper Function (No AI needed) ---

def check_document_status(doc_id):
    """
    Simulates checking a document's status in the central registry.
    This is typically done via a database query, but here we read the global DataFrame.
    """
    doc = DOCUMENTS_DF[DOCUMENTS_DF['doc_id'] == doc_id]
    if not doc.empty:
        return {
            'doc_id': doc.iloc[0]['doc_id'],
            'status': doc.iloc[0]['status'],
            'expiry_date': doc.iloc[0]['expiry_date']
        }
    return None

# --- Compliance/Update Functions (No AI needed) ---

def acknowledge_staff_read(doc_id, owner_info):
    """Logs the staff's simulated acknowledgment of a document."""
    owner_name = owner_info['name']
    
    # Simulate an official record creation
    log_activity("Compliance Agent", "Acknowledgment Logged", 
                 f"Official compliance record created for {owner_name} regarding '{doc_id}'.")
    
    # In a real system, this would update a training/acknowledgment matrix.
    return True

def update_document_review_date(doc_id, new_date):
    """Updates the document's review/expiry date in the global registry (DataFrame)."""
    global DOCUMENTS_DF
    
    # Find the document index
    idx = DOCUMENTS_DF[DOCUMENTS_DF['doc_id'] == doc_id].index
    
    if not idx.empty:
        # Update the review date
        DOCUMENTS_DF.loc[idx, 'review_date'] = str(new_date)
        
        # In a full system, you would also update the expiry_date based on a standard interval (e.g., +2 years)
        
        log_activity("Compliance Agent", "Document Update", f"Updating review date for {doc_id}.")
        log_activity("Compliance Agent", "Document Update Complete", f"{doc_id} review date updated to {new_date}.")
        
        return True
    return False

def finalize_document_status(doc_id, status):
    """Finalizes the status of a document (e.g., 'Active (Renewed)' or 'Retired')."""
    global DOCUMENTS_DF
    
    idx = DOCUMENTS_DF[DOCUMENTS_DF['doc_id'] == doc_id].index
    
    if not idx.empty:
        DOCUMENTS_DF.loc[idx, 'status'] = status
        log_activity("Compliance Agent", "Final Record Update", f"Document {doc_id} status set to '{status}'.")
        return True
    return False

def finalize_cp_privileges(applicant_name, specialty):
    """Simulates logging the final privileging status for a C&P applicant."""
    # In a real system, this would write to a credentialing database
    
    log_activity("Compliance Agent", "Final C&P Approval Granted", 
                 f"Privileging granted for {applicant_name}, specialty: {specialty}.")
    
    return True

# --- AI Reporting Function (New) ---

def generate_dashboard(metrics):
    """
    Generates the final compliance dashboard, including an AI-generated Executive Summary.
    """
    log_activity("Compliance Agent", "Dashboard Generation", "Starting metric aggregation and AI analysis...")

    # 1. Read the full Activity Log for context
    try:
        with open(ACTIVITY_LOG_PATH, 'r') as f:
            activity_log = f.read()
    except Exception as e:
        log_activity("Compliance Agent", "Log Read Error", f"Could not read activity log for AI analysis. Error: {e}")
        activity_log = "Error: Activity log file could not be read."
        
    # 2. Define the AI Analysis Prompt
    prompt = f"""
    You are an Executive Reporting Analyst AI. Your task is to analyze the following activity log and generate a 
    concise, professional Executive Summary for the Quality Management Representative (QMR).
    
    EXECUTIVE SUMMARY REQUIREMENTS:
    1. Must be three short paragraphs, max 10 lines total.
    2. Must summarize the total number of documents processed and renewed.
    3. Must summarize the outcome of the C&P application(s) handled.
    4. Must highlight any critical fallbacks (e.g., LLM routing fallback if present in the log).
    
    ACTIVITY LOG FOR ANALYSIS:
    {activity_log}
    """
    
    # 3. Call Gemini to generate the summary
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Use Pro for better summarization and reasoning
            contents=prompt
        )
        executive_summary = response.text
    except Exception as e:
        log_activity("Compliance Agent", "AI Summary Error", f"Failed to generate AI summary. Error: {e}")
        executive_summary = "AI Summary Failed. Review raw logs for details."


    # 4. Compile the Final Dashboard (Markdown file)
    dashboard_content = f"# Daily Workflow Summary ({date.today().strftime('%Y-%m-%d')})\n\n"
    
    # ADD THE AI GENERATED SUMMARY 
    dashboard_content += "## Executive Summary (AI Generated)\n"
    dashboard_content += executive_summary
    dashboard_content += "\n\n---\n\n## Key Metrics\n"
    dashboard_content += f"**Documents Renewed:** {metrics.get('docs_renewed', 0)}\n"
    dashboard_content += f"**C&P Privileges Granted:** {metrics.get('cp_granted', 0)}\n"
    
    # Save the final file
    output_path = os.path.join('outputs', 'compliance_dashboard.md')
    os.makedirs('outputs', exist_ok=True) # Ensure outputs directory exists
    with open(output_path, 'w') as f:
        f.write(dashboard_content)
        
    log_activity("Compliance Agent", "Dashboard Generation", f"Dashboard saved to {output_path}.")