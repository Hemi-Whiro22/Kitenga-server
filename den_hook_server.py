
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Kitenga Den Hook Server is alive."}

@app.post("/tawera/log")
async def log_data(request: Request):
    data = await request.json()
    print("Received data:", data)
    return JSONResponse(content={"status": "success", "data_received": data})

if __name__ == "__main__":
    uvicorn.run("den_hook_server:app", host="0.0.0.0", port=10000, reload=True)
