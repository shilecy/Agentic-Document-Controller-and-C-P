# src/agents/document_expiry_agent.py (Revised)

from src.utils import DOCUMENTS_DF, CURRENT_DATE, log_activity, get_owner_info
from datetime import timedelta
from google import genai
import json

# Define the structured output schema for the LLM's recommendation
recommendation_schema = {
    "type": "object",
    "properties": {
        "urgency_level": {"type": "string", "enum": ["Low", "Medium", "High"], "description": "The determined urgency for renewal."},
        "recommended_action": {"type": "string", "description": "The specific communication action to take (e.g., 'send_email', 'send_whatsapp')."}
    },
    "required": ["urgency_level", "recommended_action"]
}

def get_expiring_documents(check_days=60):
    """
    AI-Enhanced: Analyzes documents expiring soon and uses LLM to determine
    the best action based on document context.
    """
    log_activity("Document Expiry Agent", "Check Start", "Analyzing documents for upcoming expiries.")
    
    # Calculate the cutoff date (Fixed logic remains for filtering)
    cutoff_date = CURRENT_DATE + timedelta(days=check_days)
    
    expiring_list = []
    
    # Filter documents based on the expiration date and 'Active' status
    filtered_docs = DOCUMENTS_DF[
        (DOCUMENTS_DF['Expiry_Date_dt'] <= cutoff_date) & 
        (DOCUMENTS_DF['status'] == 'Active')
    ]

    for index, doc in filtered_docs.iterrows():
        doc_data = doc.to_dict()
        
        # 🚨 FETCH OWNER INFO HERE 🚨
        owner_info = get_owner_info(doc_data['owner_email'])
        owner_position = owner_info.get('position', 'Staff') # Use a safe default
        
        # 1. Define Context for LLM
        prompt = f"""
        Analyze the following document context to determine renewal urgency and recommended communication.
        
        DOCUMENT DETAILS:
        - Title: {doc_data['title']}
        - Type: {doc_data['type']}
        - Status: {doc_data['status']}
        - Days until expiry (simulated): {(doc_data['Expiry_Date_dt'] - CURRENT_DATE).days}
        - Owner Position: {owner_position} # 🚨 USE THE FETCHED VARIABLE
        
        POLICY GUIDANCE:
        - Policies are HIGH urgency.
        - Work Instructions (WI) are MEDIUM urgency.
        - Documents owned by the 'Chief of Medical Staff' are always HIGH urgency.
        - Documents already expired based on current date {CURRENT_DATE} must be HIGH urgency.
        
        Provide the output as a clean JSON object based on the required schema.
        """
        
        # 2. Call LLM for Contextual Decision
        try:
            client = genai.Client()
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": recommendation_schema
                }
            )
            recommendation = json.loads(response.text.strip())
            
        except Exception as e:
            log_activity("Document Expiry Agent", "AI Decision Error", f"LLM failed for {doc_data['doc_id']}. Defaulting to Medium urgency. Error: {e}")
            recommendation = {'urgency_level': 'Medium', 'recommended_action': 'send_email'} # Safe fallback
        
        # 3. Augment the document data with AI results
        doc_data.update(recommendation)
        expiring_list.append(doc_data)

    log_activity("Document Expiry Agent", "Found Documents", f"Found {len(expiring_list)} documents for action.")
    return expiring_list