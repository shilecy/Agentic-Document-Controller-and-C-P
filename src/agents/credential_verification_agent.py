# src/agents/credential_verification_agent.py (Revised)

from src.utils import CONSULTANT_APP, POLICY_RULES, log_activity
from google import genai
import json

# Define the structured output schema for the LLM's verification
verification_schema = {
    "type": "object",
    "properties": {
        "is_compliant": {"type": "boolean", "description": "True if the application meets all policy rules, False otherwise."},
        "missing_docs": {"type": "array", "items": {"type": "string"}, "description": "A list of specific policy requirements or documents that were NOT met."},
        "policy_justification": {"type": "string", "description": "A brief explanation of the compliance status based on the policy rules."}
    },
    "required": ["is_compliant", "missing_docs", "policy_justification"]
}

def verify_consultant_credentials():
    """
    AI-Enhanced: Uses LLM to interpret complex policy rules against the
    consultant application data to determine compliance.
    """
    log_activity("Credential Verification Agent", "Check Start", f"Verifying C&P application for {CONSULTANT_APP['name']}.")

    # Policy rules are loaded from utils.py (POLICY_RULES)
    policy_text = json.dumps(POLICY_RULES, indent=2)
    application_data = json.dumps(CONSULTANT_APP, indent=2)
    
    prompt = f"""
    You are a Credentialing and Privileging (C&P) Policy Compliance AI.
    
    TASK: Determine if the CONSULTANT APPLICATION DATA meets all requirements specified in the C&P POLICY RULES.
    
    C&P POLICY RULES:
    {policy_text}
    
    CONSULTANT APPLICATION DATA:
    {application_data}
    
    CRITICAL INSTRUCTION: Adhere strictly to the OUTPUT FORMAT. The 'is_compliant' field is the final judgment.
    """
    
    # 1. Call LLM for Policy Interpretation
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-pro', # Use Pro for better reasoning on policy text
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": verification_schema
            }
        )
        verification = json.loads(response.text.strip())
        
    except Exception as e:
        log_activity("Credential Verification Agent", "AI Policy Error", f"LLM verification failed. Defaulting to NON-COMPLIANT. Error: {e}")
        # Default fallback to non-compliant for safety
        verification = {'is_compliant': False, 'missing_docs': ['AI Policy Check Failed'], 'policy_justification': 'System error in policy interpretation.'}
    
    
    # 2. Return the structured results
    log_status = "COMPLIANT" if verification['is_compliant'] else "NON-COMPLIANT"
    log_activity("Credential Verification Agent", "Check Complete", 
                 f"Application for {CONSULTANT_APP['name']} is {log_status}.") # Use 'name'
                 
    return {
        'applicant': CONSULTANT_APP['name'],      # Use 'name' for the applicant's name
        'email': CONSULTANT_APP['email'],         # Use 'email' for the applicant's email
        'specialty': CONSULTANT_APP['specialty'], # This key seems correct
        'is_compliant': verification['is_compliant'],
        'missing_docs': verification['missing_docs'],
        'ai_justification': verification['policy_justification']
    }