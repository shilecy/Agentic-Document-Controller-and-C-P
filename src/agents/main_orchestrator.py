# agents/main_orchestrator.py

import os
from datetime import datetime, date

# Import all necessary components
# 🚨 CORRECTION 1: Updated Communication and Compliance Agent Imports 🚨
from src.utils import log_activity, log_communication, CURRENT_DATE, DOCUMENTS_DF
from src.agents.document_expiry_agent import get_expiring_documents
from src.agents.ai_review_agent import generate_ai_summary
from src.agents.routing_role_agent import get_owner_info, determine_reviewers_and_approvers, determine_cp_approver
from src.agents.communication_agent import send_expiry_notification, send_review_request, send_whatsapp_acknowledgement, send_cp_approval_request # Added send_cp_approval_request
from src.agents.credential_verification_agent import verify_consultant_credentials
from src.agents.compliance_agent import generate_dashboard, finalize_cp_privileges, update_document_review_date, finalize_document_status, acknowledge_staff_read # Added finalize_document_status and acknowledge_staff_read

def run_process_a_document_control_lifecycle():
    """
    Orchestrator: Manages the proactive document renewal workflow.
    """
    log_activity("Orchestrator", "Start Process A", "Daily execution: Document Control Lifecycle.")
    
    expiring_docs = get_expiring_documents()
    
    # Initialize metrics for the dashboard
    metrics = {'docs_renewed': 0, 'cp_granted': 0}
    
    for doc in expiring_docs:
        doc_id = doc['doc_id']
        doc_title = doc['title']
        owner_email = doc['owner_email']
        expiry_date_str = doc['expiry_date']
        doc_type = doc['type']
        
        owner_info = get_owner_info(owner_email)
        if not owner_info:
            log_activity("Orchestrator", "Error", f"Skipping {doc_id}: Owner email not found in HR list.")
            continue
            
        owner_name = owner_info['name']
        owner_role = owner_info['position']
        
        # 1. AI Review Agent: Get content suggestion (AI Summary)
        # Note: We generate it but don't use it in the communication function as designed in the new AI comm agent
        ai_summary = generate_ai_summary(doc_id, doc_title)
        
        # 2. Communication Agent: Send expiry notice
# 2. Communication Agent: Send expiry notice
        # 🚨 CORRECTION 2: Updated arguments for send_expiry_notification 🚨
        send_expiry_notification(doc_id, doc_title, owner_email, expiry_date_str)
        
        # 🟢 N8N INTEGRATION: Print JSON output for the initial Email Node
        import json
        
        # --- Prepare Data for N8N Email Node ---
        n8n_email_data = {
            "doc_id": doc_id,
            "doc_title": doc_title,
            "owner_email": owner_email,
            "subject": f"URGENT: Action Required - {doc_title} Expiration",
            "body_intro": f"Dear {owner_name}, the {doc_title} ({doc_id}) is due for renewal before {expiry_date_str}. Please update and submit the new version.",
            # Include next step info for potential HITL link generation in n8n
            "next_reviewer_email": reviewer_info['email'] if 'reviewer_info' in locals() else 'unknown' 
        }
        
        # Print the JSON object to stdout for the n8n Execute Command node to capture
        print(json.dumps(n8n_email_data))
        # ----------------------------------------
        
        # 3. HITL Simulation: Owner Review and Submission
        log_activity("Orchestrator", "HITL Simulation", 
                     f"Awaiting updated document {doc_id} from {owner_name}. (Simulated: Submitted for Review)")
        
        
        # 4. Routing Agent: Determine Reviewer/Approver for the new version
        reviewer_info, approver_info = determine_reviewers_and_approvers(doc_title, owner_role)
        
        # 5. Communication Agent: Request Review
        # 🚨 CORRECTION 3: Updated arguments for send_review_request 🚨
        send_review_request(doc_title, owner_name, reviewer_info)
        
        # 6. HITL Simulation: Approval/Acknowledgment
        log_activity("Orchestrator", "HITL Simulation", 
                     f"Awaiting approval from {approver_info['name']} for {doc_id}. (Simulated: Approved)")
        
        # 7. Communication Agent: Trigger staff acknowledgment flow
        # 🚨 CORRECTION 4: Updated arguments for send_whatsapp_acknowledgement 🚨
        send_whatsapp_acknowledgement(owner_email, doc_title, "request_sent") 
        
        log_activity("Communication Agent", "HITL Input", f"Simulated acknowledgment received from {owner_name} for '{doc_title}'.")
        send_whatsapp_acknowledgement(owner_email, doc_title, "confirmation") # Confirmation message
        
        # 8. Compliance Agent: Log acknowledgment and Update the last_review date
        acknowledge_staff_read(doc_id, owner_info) # Log the acknowledgment
        update_document_review_date(doc_id, CURRENT_DATE) # Update date using the current simulation date
        
        # 9. Compliance Agent: Final status logging (The audit trail)
        # 🚨 CORRECTION 5: Use finalize_document_status instead of the removed log_final_approval 🚨
        finalize_document_status(doc_id, "Active (Renewed)")
        
        metrics['docs_renewed'] += 1

    log_activity("Orchestrator", "End Process A", "Document Control lifecycle complete for this run.")
    
    return metrics # Return metrics to the main block


def run_process_b_credentialing_privileging():
    """
    Orchestrator: Manages the consultant credentialing workflow.
    """
    log_activity("Orchestrator", "Start Process B", "New C&P application received (Dr. Alice Tan).")
    
    # 1. Credential Verification Agent: Check documents
    verification_result = verify_consultant_credentials()
    applicant = verification_result['applicant']
    
    if verification_result['is_compliant']:
        # 2. Routing Agent: Find final approver
        approver_info = determine_cp_approver()
        
        # 3. Communication Agent: Request final C&P approval
        # 🚨 CORRECTION 6: Use the new AI-powered send_cp_approval_request 🚨
        send_cp_approval_request(applicant, verification_result['specialty'], approver_info['email'])
        
        # 4. HITL Simulation: Final Approval
        log_activity("Orchestrator", "HITL Simulation", 
                     f"Awaiting final C&P approval from {approver_info['name']} for {applicant}.")
        
        # 5. Compliance Agent: Finalize privileges and update metrics
        finalize_cp_privileges(applicant, verification_result['specialty'])
        
        return {'cp_granted': 1}

    else:
        # Non-compliant: Request missing documents
        subject = f"C&P Application Incomplete: {applicant}"
        body = (f"Dear {applicant}, your C&P application is missing the following documents: "
                 f"{', '.join(verification_result['missing_docs'])}. Please resubmit.")
        log_communication(verification_result['email'], "Email", subject, body)
        log_activity("Orchestrator", "State Update", f"Application PENDING DOCS for {applicant}.")
        
        return {'cp_granted': 0}


# --- Main Execution Block ---
if __name__ == "__main__":
    
    # 1. Clear previous logs for a clean run
    if os.path.exists(os.path.join('logs', 'activity_log.txt')):
        os.remove(os.path.join('logs', 'activity_log.txt'))
    if os.path.exists(os.path.join('logs', 'communications_log.txt')):
        os.remove(os.path.join('logs', 'communications_log.txt'))

    # Re-initialize logs via a utility call to ensure headers are written
    from src.utils import log_activity as init_log
    init_log("Orchestrator", "System Init", f"Starting Agentic Workflow on {CURRENT_DATE}.")

    # --- Execute Workflows ---
    metrics_a = run_process_a_document_control_lifecycle()
    metrics_b = run_process_b_credentialing_privileging()
    
    # Aggregate Metrics
    final_metrics = {
        'docs_renewed': metrics_a.get('docs_renewed', 0),
        'cp_granted': metrics_b.get('cp_granted', 0)
    }
    
    # --- Final Output ---
    # 🚨 CORRECTION 7: Pass the final metrics to the dashboard generator 🚨
    generate_dashboard(final_metrics) 
    
    log_activity("Orchestrator", "System Shutdown", "All workflows executed and dashboard generated. Review logs and outputs folder.")