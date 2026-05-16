from fastapi import FastAPI, HTTPException, Header
import google.generativeai as genai
from typing import Optional
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Online"}

@app.get("/summarize")
async def summarize_video(video_url: str, x_api_key: Optional[str] = Header(None)):
    # 1. ΕΛΕΓΧΟΣ API KEY
    my_key = os.getenv("MY_PRIVATE_KEY", "super_secret_tiktok_123")
    if x_api_key != my_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # 2. ΡΥΘΜΙΣΗ GEMINI
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {"error": "Missing GEMINI_API_KEY"}

    try:
        genai.configure(api_key=gemini_key)
        
        # ΕΔΩ ΟΡΙΖΟΥΜΕ ΤΟ ΜΟΝΤΕΛΟ (Αν θες το Pro, άλλαξέ το σε 'gemini-2.5-pro')
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"Κάνε μια σύντομη περίληψη στα Ελληνικά για αυτό το TikTok βίντεο: {video_url}"
        response = model.generate_content(prompt)
        return {"summary": response.text}
    except Exception as e:
        return {"error": str(e)}
