from __future__ import annotations

import io
import json
import os
import urllib.parse
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .engine import calculate_match
from .report import build_pdf

BASE = os.path.dirname(os.path.dirname(__file__))
STATIC = os.path.join(BASE, "static")

app = FastAPI(title="कुंडली मिलन Calculation Engine", version="1.0")

class Person(BaseModel):
    name: str
    date: str
    time: str
    place: str
    place_display: str | None = None
    latitude: float
    longitude: float
    timezone: str = "Asia/Kolkata"

class MatchRequest(BaseModel):
    boy: Person
    girl: Person

@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))

@app.get("/api/geocode")
def geocode(q: str):
    if len(q.strip()) < 3:
        return []
    params = urllib.parse.urlencode({
        "format":"jsonv2","addressdetails":"1","limit":"8",
        "countrycodes":"in","accept-language":"mr,en","q":q.strip()
    })
    req = urllib.request.Request(
        "https://nominatim.openstreetmap.org/search?"+params,
        headers={"User-Agent":"KundliMilan/1.0 contact@example.com"}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            raw = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service unavailable: {e}")
    out=[]
    for x in raw:
        a=x.get("address",{})
        parts=[a.get("village") or a.get("town") or a.get("city") or a.get("municipality"),
               a.get("subdistrict") or a.get("county"),
               a.get("state"), a.get("country")]
        parts=[p for p in parts if p]
        name=a.get("village") or a.get("town") or a.get("city") or x.get("display_name","").split(",")[0]
        out.append({
            "name":name,
            "secondary":", ".join(parts[1:]) if len(parts)>1 else x.get("display_name",""),
            "display_name":x.get("display_name",""),
            "latitude":float(x["lat"]),
            "longitude":float(x["lon"]),
            "address":a
        })
    return out

@app.post("/api/calculate")
def calculate(req: MatchRequest):
    try:
        return calculate_match({"boy":req.boy.model_dump(),"girl":req.girl.model_dump()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/report")
def report(req: MatchRequest):
    try:
        result=calculate_match({"boy":req.boy.model_dump(),"girl":req.girl.model_dump()})
        pdf=build_pdf(result)
        return StreamingResponse(
            io.BytesIO(pdf),
            media_type="application/pdf",
            headers={"Content-Disposition":"inline; filename=kundli-milan-report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

app.mount("/static", StaticFiles(directory=STATIC), name="static")
