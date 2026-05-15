from fastapi import FastAPI, HTTPException, Header
import google.generativeai as genai
from typing import Optional
import os

app = FastAPI()

# Το δικό σου κλειδί για το Make.com
MY_PRIVATE_KEY = "super_secret_tiktok_123"

@app.get("/")
def home():
    return {"status": "Gemini API is Online"}

@app.get("/summarize")
def summarize_video(video_url: str, x_api_key: Optional[str] = Header(None)):
    # 1. Έλεγχος ασφαλείας
    if x_api_key != MY_PRIVATE_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # 2. Ρύθμιση Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {"error": "Gemini Key missing in Railway Variables"}

    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro') # Το γρήγορο μοντέλο
        
        # 3. Ερώτηση στο Gemini
        prompt = f"Ανάλυσε αυτό το βίντεο από το TikTok και κάνε μου μια σύντομη περίληψη στα Ελληνικά: {video_url}"
        response = model.generate_content(prompt)
        
        return {
            "summary": response.text,
            "url": video_url
        }

    except Exception as e:
        return {"error": str(e)}
