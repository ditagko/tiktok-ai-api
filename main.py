from fastapi import FastAPI, HTTPException, Header, UploadFile, File
import google.generativeai as genai
from typing import Optional
import os
import shutil

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Online"}

@app.post("/summarize")
async def summarize_video(
    file: UploadFile = File(...), 
    x_api_key: Optional[str] = Header(None)
):
    # 1. ΕΛΕΓΧΟΣ API KEY
    my_key = os.getenv("MY_PRIVATE_KEY", "super_secret_tiktok_123")
    if x_api_key != my_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # 2. ΡΥΘΜΙΣΗ GEMINI
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return {"error": "Missing GEMINI_API_KEY"}

    # Αποθήκευση του αρχείου τοπικά στο Railway προσωρινά
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        genai.configure(api_key=gemini_key)
        
        # Ανέβασμα του βίντεο στο Gemini File API
        print("Uploading file to Gemini...")
        video_file = genai.upload_file(path=temp_file_path)
        
        # Χρήση του gemini-2.5-flash (οικονομικό και multimodal)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = "Κάνε μια σύντομη περίληψη στα Ελληνικά για αυτό το βίντεο. Άκουσε τον ήχο και δες τους υπότιτλους αν υπάρχουν."
        response = model.generate_content([video_file, prompt])
        
        # Διαγραφή του αρχείου από το Gemini μετά την επεξεργασία
        genai.delete_file(video_file.name)
        
        return {"summary": response.text}
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Διαγραφή του τοπικού προσωρινού αρχείου από το Railway
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
