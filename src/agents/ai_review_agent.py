# src/agents/ai_review_agent.py

from src.utils import log_activity, os # os is needed to access the key
from google import genai

def generate_ai_summary(doc_id, doc_title):
    """
    AI Review Agent: Uses Gemini to generate content analysis and suggested amendments.
    """
    log_activity("AI Review Agent", "Start Analysis", f"Generating LLM summary for {doc_id}: {doc_title}")
    
    # Initialize the client using the environment variable
    try:
        client = genai.Client()
    except Exception as e:
        log_activity("AI Review Agent", "Client Error", f"Failed to initialize Gemini Client: {e}")
        # FALLBACK: Use a generic message if API client fails
        return "LLM failure: Please conduct a full manual review."

    prompt = f"""
    You are a Quality Assurance AI Agent specializing in hospital document control. 
    Analyze the document titled "{doc_title}" which is approaching its renewal date.
    
    Task: Write a concise, professional summary (maximum 3 sentences) of **suggested amendments** to bring the policy in line with current best practices. Focus on common healthcare quality updates.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        ai_summary = response.text
        log_activity("AI Review Agent", "Analysis Complete", f"Generated LLM summary for {doc_id}.")
        return ai_summary
        
    except Exception as e:
        log_activity("AI Review Agent", "API Error", f"Gemini API call failed for {doc_id}. Error: {e}")
        # FALLBACK: Provide a useful message if the API call fails during execution
        return "System error: Failed to retrieve AI summary. Manual review required."