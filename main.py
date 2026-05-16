from fastapi import FastAPI, HTTPException, Header
from google import genai
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

    # 2. ΡΥΘΜΙΣΗ ΝΕΟΥ GEMINI CLIENT
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {"error": "Missing GEMINI_API_KEY"}

    try:
        # Χρήση του νέου google.genai client (έκδοση 2026)
        client = genai.Client(api_key=gemini_key)
        
        # Εδώ λέμε στο Gemini να χρησιμοποιήσει τα Google Search εργαλεία του 
        # για να προσπαθήσει να αντλήσει τις πληροφορίες/κείμενο από το URL
        prompt = (
            f"Ανέλυσε το περιεχόμενο αυτού του συνδέσμου βίντεο: {video_url}. "
            f"Κάνε μια σύντομη περίληψη στα Ελληνικά. Αν δεν μπορείς να δεις το βίντεο, "
            f"χρησιμοποίησε τις πληροφορίες της σελίδας, τον τίτλο ή τα hashtags για να μου πεις "
            f"περί τίνος πρόκειται, χωρίς όμως να βγάλεις φανταστική ιστορία."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return {"summary": response.text}
    except Exception as e:
        return {"error": str(e)}
