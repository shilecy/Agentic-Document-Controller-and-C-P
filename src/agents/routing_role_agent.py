# src/agents/routing_role_agent.py (TOP OF FILE)

# --- NEW IMPORTS ---
from src.utils import get_owner_info, HR_IPSG_LIST, log_activity 
from google import genai
import json # To handle Gemini's JSON output
# -------------------

def get_staff_names():
    """Helper to get a list of staff names and roles for the LLM to use."""
    staff_list = []
    for email, info in HR_IPSG_LIST.items():
        # Use 'name' and 'position' keys
        staff_list.append(f"{info['name']} ({info['position']}), Email: {email}") 
    return "\n".join(staff_list)

def determine_reviewers_and_approvers(doc_title, owner_role):
    """
    Routing Agent: Uses Gemini to dynamically determine the best Reviewer and Approver 
    based on the document and owner's role, adhering to a defined policy.
    """
    log_activity("Routing & Role Agent", "AI Routing Start", f"Using LLM for route determination for: {doc_title}")
    
    # 1. Prepare Staff and Rules Context
    staff_context = get_staff_names()
    
    # Define the policy rules for the LLM
    policy_rules = """
    Routing Policy Rules:
    1. GENERAL RULE: The Approver is always the 'Chief of Medical Staff' (Mr. Lee).
    2. WI/Form Reviewer: If the document is a Work Instruction (WI) or Form (implied by title, e.g., 'Blood Transfusion WI'), the Reviewer defaults to the document Owner (Ms. Lim/Nurse).
    3. POLICY Reviewer: If the document is a Policy, the Reviewer must be the 'QMR' (Dr. Chan).
    """

    # 1. Define the Schema (Add this to the top of the function or file)
    # Define the expected JSON structure
    routing_schema = {
        "type": "object",
        "properties": {
            "reviewer_email": {"type": "string", "description": "The email of the determined reviewer."},
            "approver_email": {"type": "string", "description": "The email of the determined final approver."}
        },
        "required": ["reviewer_email", "approver_email"]
    }

    # 2. Define the LLM Prompt
    prompt = f"""
    You are a professional Document Control Routing AI. Your task is to select the most appropriate Reviewer and Approver 
    from the STAFF LIST based on the DOCUMENT DETAILS and the ROUTING POLICY RULES.

    DOCUMENT DETAILS:
    - Document Title: {doc_title}
    - Document Owner Role: {owner_role}

    ROUTING POLICY RULES:
    {policy_rules}

    STAFF LIST:
    {staff_context}

    OUTPUT FORMAT: You must only output a single JSON object with the following structure:
    {{
        "reviewer_email": "reviewer@email.com",
        "approver_email": "approver@email.com"
    }}
    """
    
    # 3. Call Gemini (Update this section)
    try:
        client = genai.Client()
    
        # Use the structured output feature
        response = client.models.generate_content(
            model='gemini-2.5-pro', # Or gemini-2.5-pro for better fidelity
            contents=prompt,
            config={
                "response_mime_type": "application/json", # Enforce JSON output
               "response_schema": routing_schema        # Enforce the specific structure
            }
        )
        
        # 4. Parse JSON Output
        route_data = json.loads(response.text.strip())
        
        reviewer_email = route_data.get('reviewer_email', 'qmr@phmk.my') # Default fallback
        approver_email = route_data.get('approver_email', 'qmr@phmk.my') # Default fallback

        # Use the imported get_owner_info from utils.py
        reviewer_info = get_owner_info(reviewer_email)
        approver_info = get_owner_info(approver_email)
        
        log_activity("Routing & Role Agent", "AI Routing Complete", f"AI Route: Reviewer set to {reviewer_info['name']} | Approver set to {approver_info['name']}")
        
        return reviewer_info, approver_info

    except Exception as e:
        log_activity("Routing & Role Agent", "AI Routing ERROR", f"LLM routing failed. Falling back to default QMR route. Error: {e}")
        # Fallback to a safe, default route (QMR for both)
        qmr_info = get_owner_info('qmr@phmk.my')
        return qmr_info, qmr_info

def determine_cp_approver():
    """Determines the final C&P Approver (Chief Medical Officer/QMR equivalent)."""
    
    approver_role = 'Approver' 
    
    for email, info in HR_IPSG_LIST.items():
        if info.get('approval_role') == approver_role: # Use 'approval_role'
             log_activity("Routing & Role Agent", "C&P Approver Found", 
                         f"Approver set to {info['name']}") # Use 'name'
             return {
                 'name': info['name'],
                 'email': email,
                 'role': info['approval_role'] # Use 'approval_role'
             }
    
    log_activity("Routing & Role Agent", "C&P Approver Error", "No C&P Approver found in HR list.")
    return None