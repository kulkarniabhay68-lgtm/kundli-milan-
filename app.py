from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Any
import requests

from backend.engine import calculate_match
from backend.report import generate_report

app = FastAPI(title="Kundli Milan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    boy: dict[str, Any]
    girl: dict[str, Any]


@app.get("/")
def home():
    return {
        "message": "Kundli Milan API is running",
        "status": "success"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "Kundli Milan API is running"
    }


@app.get("/api/geocode")
def geocode(q: str = ""):
    if len(q.strip()) < 3:
        return []

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": q,
                "format": "jsonv2",
                "limit": 5
            },
            headers={"User-Agent": "KundliMilanApp/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()

        return [
            {
                "name": item.get("name")
                or item.get("display_name", ""),
                "display_name": item.get("display_name", ""),
                "secondary": item.get("display_name", ""),
                "latitude": float(item["lat"]),
                "longitude": float(item["lon"]),
            }
            for item in results
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="जन्मस्थळ शोधता आले नाही."
        ) from exc


@app.post("/api/calculate")
def calculate(request: MatchRequest):
    try:
        return calculate_match(request.boy, request.girl)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"गणना करता आली नाही: {exc}"
        ) from exc


@app.post("/api/report")
def report(request: MatchRequest):
    try:
        result = calculate_match(request.boy, request.girl)
        pdf = generate_report(result)

        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                'inline; filename="kundli-milan-report.pdf"'
            },
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"रिपोर्ट तयार करता आला नाही: {exc}"
        ) from exc
