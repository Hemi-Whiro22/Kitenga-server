from fastapi import FastAPI, Request
app = FastAPI()
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests  # <-- Make sure this is included!


# 🔐 SUPABASE CONFIG
SUPABASE_URL = "https://pfyxslvdrcwcdsfldyvl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmeXhzbHZkcmN3Y2RzZmxkeXZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwNDQwMzksImV4cCI6MjA2MDYyMDAzOX0.3F6cFHFvFpyc1V0CnfRH-U6OBGKwagj0-N5UZ8jBFMo"  # paste full key here

@app.get("/")
async def root():
    return {"message": "Kitenga Den Hook Server is alive."}


app = FastAPI()

# Allow requests from localhost and anywhere else if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"] for stricter rules
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── KITENGA MODULES ─────────────────────────────────────────────

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
    table = data.get("table", "")
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
            return JSONResponse(content={"status": "Memory stored."})
        else:
            return JSONResponse(content={"status": "Failed to store memory."}, status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content={"status": "Error", "message": str(e)}, status_code=500)


@app.get("/kitenga/fetch")
async def kitenga_fetch(request: Request):
    table = request.query_params.get("table", "projects")
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
            return JSONResponse(content={"status": "Failed to fetch data."}, status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content={"status": "Error", "message": str(e)}, status_code=500)


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
