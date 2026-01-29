from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
import httpx
import json

# -- API KEYS ---
GEMINI_API_KEY = "AIzaSyA3bry0LbroMGbl3GjIGQKvNUAZ01OBdK4"#API MAKE TO LINO
PERPLEXITY_API_KEY = "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"

genai.configure(api_key = GEMINI_API_KEY)
app = FastAPI(title = "ABC Company AI Enrichment Service")

# --- Pydantic Schemas ---
class LeadInput(BaseModel):
    company_name: str
    website: str = ""

class EnrichmentOutput(BaseModel):
    summary: str
    fit_assessment: str
    lead_score: int
    next_action: str

# --- Step 1: Search via Perplexity ---
async def search_company_details(company_name: str, website: str):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    query = f"Find the official website and a summary of business activities for {company_name}..."
    if website:
        query += f"Verify if {website} is their official website."
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "Return the company website and detailed business description."},
            {"role": "user", "content": query}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json = payload, headers = headers, timeout = 20.0)
        return response.json()['choices'][0]['message']['content']

# --- Step 2: Scoring via Gemini ---
def get_ai_assessment(company_context: str):
    model = genai.GenerativeModel("gemini-2.5-flash") 
    
    prompt = f"""
    Analyze this company for ABC Company (AI Support for e-commerce).
    Context: {company_context}
    
    Respond ONLY with a valid JSON object:
    {{
      "summary": "short summary",
      "fit_assessment": "fit explanation",
      "lead_score": 85,
      "next_action": "suggested action"
    }}
    """

    response = model.generate_content(prompt)
    
    # DEBUG: See exactly what Gemini responded
    print(f"--- Gemini Response Raw: {response.text} ---")

    # Clean potential markdown blocks that break json.loads
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(clean_text)
    except Exception as e:
        print(f"Failed to parse JSON: {clean_text}")
        raise e

# -- Endpoint --

@app.post("/enrich", response_model=EnrichmentOutput)
async def enrich_lead(lead: LeadInput):
    print(f">>> [1/4] Request received for: {lead.company_name}")
    
    try:
        # Step 1: Enrichment
        print(">>> [2/4] Consulting Perplexity (this may take a while)...")
        raw_context = await search_company_details(lead.company_name, lead.website)
        
        # Step 2: Evaluation
        print(">>> [3/4] Sending context to Gemini...")
        assessment = get_ai_assessment(raw_context)
        
        print(">>> [4/4] Process completed! Sending response to n8n...")
        return assessment
        
    except Exception as e:
        print(f"!!! ERROR DETECTED: {str(e)}")
        # If something fails, we return an error JSON so the connection doesn't reset
        return {
            "summary": "Error", 
            "lead_score": 0, 
            "fit_assessment": f"Internal Error: {str(e)}",
            "next_action": "Check server logs"
        }

@app.get("/")
async def root():
    print(">>> Tunnel verified! Someone entered the root URL.")
    return {"message": "Server active"}

if __name__ == "__main__":
    import uvicorn
    # Listening on 0.0.0.0 is essential for the tunnel to work
    uvicorn.run(app, host = "0.0.0.0", port=8000)