from fastapi import FastAPI, HTTPException, Header
import openai
from typing import Optional
import os

app = FastAPI()

# Εδώ ορίζουμε το δικό σου μυστικό κλειδί για το API
# Θα το βάζεις στο Header του Make.com ως: X-API-KEY
MY_PRIVATE_KEY = "super_secret_tiktok_123"

@app.get("/")
def home():
    return {"status": "API is Online", "task": "TikTok Summarizer"}

@app.get("/summarize")
def summarize_video(video_url: str, x_api_key: Optional[str] = Header(None)):
    # 1. Έλεγχος αν ο χρήστης (το Make) έστειλε το σωστό κλειδί
    if x_api_key != MY_PRIVATE_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

    # 2. Εδώ παίρνουμε το OpenAI Key από το Railway (θα το ρυθμίσουμε μετά)
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        return {"error": "OpenAI Key not configured in Railway settings"}

    try:
        client = openai.OpenAI(api_key=openai_key)
        
        # 3. Στέλνουμε το link στο GPT για να κάνει την περίληψη
        # (Σημείωση: Το GPT-4o μπορεί να διαβάσει περιεχόμενο από Links)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Είσαι ειδικός στα social media. Θα σου δίνω ένα TikTok link και θα μου γράφεις μια σύντομη περίληψη 3 σημείων στα Ελληνικά."},
                {"role": "user", "content": f"Κάνε περίληψη αυτού του βίντεο: {video_url}"}
            ]
        )
        
        summary = response.choices[0].message.content
        return {"summary": summary, "url": video_url}

    except Exception as e:
        return {"error": str(e)}