from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import requests  # <-- Make sure this is included!

# 🔐 SUPABASE CONFIG
SUPABASE_URL = "https://pfyxslvdrcwcdsfldyvl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmeXhzbHZkcmN3Y2RzZmxkeXZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwNDQwMzksImV4cCI6MjA2MDYyMDAzOX0.3F6cFHFvFpyc1V0CnfRH-U6OBGKwagj0-N5UZ8jBFMo"  # paste full key here

@app.get("/")
async def root():
    return {"message": "Kitenga Den Hook Server is alive."}
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from localhost and anywhere else if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"] for stricter rules
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── KITENGA ────────────────────────────────────────
@app.post("/kitenga/log")
async def kitenga_log(request: Request):
    data = await request.json()
    print("[KITENGA LOG]", data)
    return JSONResponse(content={"status": "kitenga_log_received", "data": data})

@app.post("/kitenga/speak")
async def kitenga_speak(request: Request):
    data = await request.json()
    print("[KITENGA SPEAK]", data)
    return {"reply": f"Kitenga says: '{data.get('message', '')}'"}

@app.get("/kitenga/fetch")
async def fetch_from_supabase(table: str = "projects"):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    r = requests.get(url, headers=headers)
    return r.json()

@app.post("/kitenga/remember")
async def remember_in_supabase(request: Request):
    data = await request.json()
    table = data.get("table", "projects")
    payload = data.get("entry")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=headers, json=payload)
    return r.json()

# ─── RONGOHIA (OCR) ─────────────────────────────────
@app.post("/rongohia/ocr")
async def rongohia_ocr(request: Request):
    data = await request.json()
    print("[RONGOHIA OCR]", data)
    return {"status": "OCR triggered", "input": data}

# ─── TAWERA (SAVE TO SUPABASE) ─────────────────────
@app.post("/tawera/save")
async def tawera_save(request: Request):
    data = await request.json()
    print("[TAWERA SAVE]", data)
    return {"status": "Saved to Supabase (mock)", "input": data}

# ─── WAIRUA (KŌRERO ROUTING) ───────────────────────
@app.post("/wairua/route")
async def wairua_route(request: Request):
    data = await request.json()
    print("[WAIRUA ROUTE]", data)
    return {"status": "Routed kōrero", "input": data}

if __name__ == "__main__":
    uvicorn.run("den_hook_server:app", host="0.0.0.0", port=10000, reload=True)
