from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import openai
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

firebase_key_json = os.getenv("FIREBASE_KEY_JSON")
db = None  # Default to None

if firebase_key_json and not firebase_admin._apps:
    try:
        cred = credentials.Certificate(json.loads(firebase_key_json))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print("[FIREBASE INIT ERROR]", e)


app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load config from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Optional Tables
DEFAULT_TABLE = os.getenv("SUPABASE_TABLE", "korero")

# Stream cache
latest_awa_stream = {}

@app.get("/")
async def root():
    return {"message": "Kitenga + Rongohia are alive and synced."}

@app.post("/kitenga/log")
async def kitenga_log(request: Request):
    data = await request.json()
    print("[KITENGA LOG]", data)
    return JSONResponse(content={"status": "kitenga_log_received", "data": data})

@app.post("/kitenga/speak")
async def kitenga_speak(request: Request):
    data = await request.json()
    print("[KITENGA SPEAK]", data)
    return JSONResponse(content={"reply": f"Kitenga says: '{data.get('message', '')}'"})

@app.post("/kitenga/remember")
async def kitenga_remember(request: Request):
    data = await request.json()
    table = data.get("table", DEFAULT_TABLE)
    entry = data.get("entry", {})

    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY,
                "Prefer": "return=representation"
            },
            json=entry
        )
        if response.status_code in [200, 201]:
            db.collection("supabase_sync").add(entry)
            return JSONResponse(content={"status": "Memory stored and mirrored."})
        else:
            return JSONResponse(
                content={"status": "Failed to store memory.", "detail": response.text},
                status_code=response.status_code
            )
    except Exception as e:
        return JSONResponse(content={"status": "Error", "message": str(e)}, status_code=500)

@app.get("/kitenga/fetch")
async def kitenga_fetch(request: Request):
    table = request.query_params.get("table", DEFAULT_TABLE)
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "apikey": SUPABASE_KEY
            }
        )
        if response.status_code == 200:
            return JSONResponse(content=response.json())
        else:
            return JSONResponse(
                content={"status": "Failed to fetch data.", "detail": response.text},
                status_code=response.status_code
            )
    except Exception as e:
        return JSONResponse(content={"status": "Error", "message": str(e)}, status_code=500)

@app.post("/rongohia/ocr")
async def rongohia_ocr(request: Request):
    data = await request.json()
    image_url = data.get("image_url", "")
    if not image_url:
        return JSONResponse(content={"error": "Missing image_url"}, status_code=400)

    try:
        response = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-vision-preview"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all visible text from this image clearly."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content
        db.collection("ocr_results").add({"image_url": image_url, "text": result})
        return JSONResponse(content={"status": "success", "text": result})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/awa/stream")
async def awa_stream(request: Request):
    global latest_awa_stream
    data = await request.json()
    latest_awa_stream = {
        "message": data.get("message", ""),
        "from": data.get("from", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }
    print("[AWA STREAM]", latest_awa_stream)

    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{DEFAULT_TABLE}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY,
                "Prefer": "return=representation"
            },
            json=latest_awa_stream
        )
        db.collection("awa_stream").add(latest_awa_stream)
    except Exception as e:
        print("[SUPABASE ERROR]", e)

    return JSONResponse(content={"status": "flow_received", "echo": latest_awa_stream})

@app.get("/awa/latest")
async def awa_latest():
    return JSONResponse(content=latest_awa_stream)

@app.post("/glyph/mirror")
async def glyph_mirror(request: Request):
    data = await request.json()
    print("[GLYPH MIRROR]", data)
    try:
        doc_ref = db.collection("glyph_mirror").document()
        doc_ref.set(data)
        return JSONResponse(content={"status": "mirrored", "id": doc_ref.id})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.get("/glyph/query")
async def query_glyphs():
    try:
        docs = db.collection("glyph_mirror").stream()
        data = [doc.to_dict() for doc in docs]
        return JSONResponse(content={"glyphs": data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("den_hook_server:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)), reload=True)
