from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import requests
import shlex
import os

app = FastAPI(title="CyberAI Cloud")

# إعداد CORS للسماح بالوصول من أي مكان
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # في الإنتاج يفضل تحديد الدومين
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 مفتاح سري بسيط للحماية
API_SECRET_KEY = "cyber-admin-123" 

OLLAMA_API = "http://ollama:11434/api/generate"

class ScanRequest(BaseModel):
    target: str
    scan_type: str
    ai_model: str

def verify_token(x_token: str = Header(...)):
    if x_token != API_SECRET_KEY:
        raise HTTPException(status_code=400, detail="Invalid Auth Token")

@app.get("/")
def read_root():
    return {"status": "CyberAI Cloud Platform Ready"}

@app.post("/api/scan")
async def run_scan(request: ScanRequest, token: str = Depends(verify_token)):
    # حماية من الحقن
    if any(char in request.target for char in [";", "|", "&", "`"]):
        raise HTTPException(status_code=400, detail="Invalid characters in target")
    
    target = shlex.quote(request.target)
    cmd = []
    
    if request.scan_type == "quick_scan":
        cmd = ["nmap", "-sV", "--top-ports", "50", target]
    elif request.scan_type == "vuln_scan":
        cmd = ["nuclei", "-u", target, "-silent"]
    
    try:
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = process.stdout if process.stdout else "No output returned."
        
        # تحليل الذكاء الاصطناعي
        ai_resp = requests.post(OLLAMA_API, json={
            "model": request.ai_model,
            "prompt": f"Analyze this security scan output concisely:\n{output}",
            "stream": False
        })
        ai_text = ai_resp.json().get("response", "AI Error")
        
        return {"tool_output": output, "ai_analysis": ai_text}
        
    except Exception as e:
        return {"error": str(e)}
