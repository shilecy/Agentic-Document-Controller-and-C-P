# src/agents/communication_agent.py

from src.utils import log_communication, get_owner_info, log_activity, HR_IPSG_LIST
from google import genai
import json

# --- LLM Helper for Dynamic Email Generation ---

def generate_llm_email_content(recipient_name, doc_title, due_date, context):
    """Uses Gemini to generate a personalized email subject and body, with a structured JSON output."""
    
    # 1. Define the Prompt
    prompt = f"""
    You are a professional corporate communication AI drafting an urgent email.
    
    TASK: Generate a concise email subject and a professional, yet firm, email body.
    
    DETAILS:
    - Recipient Name: {recipient_name}
    - Document Title: {doc_title}
    - Expiration Date: {due_date}
    - Context/Action Required: {context} 
    
    The email must clearly state the document/request details and the required action.
    """
    
    # 2. Define the JSON Schema for Structured Output
    email_schema = {
        "type": "object",
        "properties": {
            "subject": {"type": "string", "description": "The generated email subject line."},
            "body": {"type": "string", "description": "The generated email body, using newline characters where necessary."}
        },
        "required": ["subject", "body"]
    }
    
    # 3. Call Gemini with Structured Config
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": email_schema
            }
        )
        
        # Parse the guaranteed JSON output
        email_content = json.loads(response.text.strip())
        return email_content['subject'], email_content['body']
        
    except Exception as e:
        log_activity("Communication Agent", "LLM Gen Error", f"Failed to generate email content. Using fallback template. Error: {e}")
        
        # 4. FALLBACK: Simple hardcoded template if LLM fails
        if "expiry" in context.lower():
            subject = f"ACTION REQUIRED: Document '{doc_title}' expires on {due_date}"
            body = (
                f"Dear {recipient_name},\n\nThis is an urgent reminder that your document, "
                f"'{doc_title}', is due to expire on {due_date}. Please submit the updated version "
                f"for review immediately as the system requires your action to renew it.\n\n"
                f"Thank you,\nAI Document Control System"
            )
        else: # Generic fallback for review/approval requests
            subject = f"ACTION: Review/Approval Request for '{doc_title}'"
            body = (
                f"Dear {recipient_name},\n\nA new submission for '{doc_title}' requires your action. "
                f"Please log into the system to complete your review/approval. Thank you."
            )
        return subject, body


# --- Agent Functions ---

def send_expiry_notification(doc_id, doc_title, owner_email, expiry_date):
    """Sends a personalized email notification about an upcoming document expiry."""
    owner_info = get_owner_info(owner_email)
    owner_name = owner_info['name']
    
    # LLM-powered content generation
    subject, body = generate_llm_email_content(
        recipient_name=owner_name,
        doc_title=doc_title,
        due_date=expiry_date,
        context=f"Document expiry notification for {doc_title}. Requires submission of updated document for review."
    )
    
    log_communication(owner_email, "Email", subject, body)


def send_review_request(doc_title, owner_name, reviewer_info):
    """Sends a personalized email notification to the designated reviewer."""
    
    # LLM-powered content generation
    subject, body = generate_llm_email_content(
        recipient_name=reviewer_info['name'],
        doc_title=doc_title,
        due_date='N/A', # Not applicable for review requests
        context=f"A new document submission ({doc_title}) by {owner_name} requires your review."
    )
    
    log_communication(reviewer_info['email'], "Email", subject, body)


def send_cp_approval_request(applicant_name, specialty, approver_email):
    """Sends a personalized C&P final approval request to the designated approver."""
    approver_info = get_owner_info(approver_email)

    # LLM-powered content generation
    subject, body = generate_llm_email_content(
        recipient_name=approver_info['name'],
        doc_title=f"C&P Application for Dr. {applicant_name}",
        due_date='ASAP',
        context=f"Final Credentialing and Privileging (C&P) request for Dr. {applicant_name} ({specialty}). Application is fully compliant and awaits final sign-off."
    )
    
    log_communication(approver_email, "Email (C&P)", subject, body)


# --- Simulation/Simple Functions (No LLM required for these) ---

def send_whatsapp_acknowledgement(owner_email, doc_title, status):
    """Simulates sending a WhatsApp notification (no LLM required for this simple ping)."""
    owner_info = get_owner_info(owner_email)
    
    if status == "request_sent":
        subject = f"Request sent for '{doc_title}'"
        body = f"Hi {owner_info['name']}, your request for '{doc_title}' has been successfully sent for review/approval."
    else: # Acknowledgment confirmation
        subject = f"Acknowledgment confirmation for '{doc_title}'"
        body = f"Thank you, {owner_info['name']}. Your acknowledgment of '{doc_title}' has been logged in the system."
        
    log_communication(owner_email, "WhatsApp", subject, body)