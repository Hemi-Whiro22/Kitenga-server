
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import openai
import os

app = FastAPI()

SUPABASE_URL = "https://pfyxslvdrcwcdsfldyvl.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            return JSONResponse(
                content={"status": "Failed to store memory.", "detail": response.text},
                status_code=response.status_code
            )
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
            model="gpt-4-vision-preview",
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
        return JSONResponse(content={"status": "success", "text": result})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/tawera/save")
async def tawera_save(request: Request):
    data = await request.json()
    print("[TAWERA SAVE]", data)
    return {"status": "Saved to Supabase (mock)", "input": data}

@app.post("/wairua/route")
async def wairua_route(request: Request):
    data = await request.json()
    print("[WAIRUA ROUTE]", data)
    return {"status": "Routed kōrero", "input": data}

if __name__ == "__main__":
    uvicorn.run("den_hook_server:app", host="0.0.0.0", port=10000, reload=True)
