from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional
import json
import re
from database import Database, ClinicalEntry
from claude_extractor import ClaudeExtractor
import os

app = FastAPI(title="Clinical Trial Companion")
templates = Jinja2Templates(directory="templates")
db = Database()

# Initialize Claude extractor
try:
    claude_extractor = ClaudeExtractor()
    print("✅ Claude API initialized")
except Exception as e:
    print(f"⚠️  Claude API not initialized: {e}")
    print("   Set ANTHROPIC_API_KEY environment variable to enable AI extraction")
    claude_extractor = None

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard showing all clinical entries"""
    entries = await db.get_all_entries()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "entries": entries,
        "total": len(entries)
    })

@app.post("/webhook/omi")
async def omi_webhook(request: Request):
    """Receives data from Omi device"""
    try:
        # Get the JSON payload from Omi
        payload = await request.json()

        print("=" * 50)
        print("📥 RECEIVED OMI WEBHOOK")
        print("=" * 50)
        print(json.dumps(payload, indent=2))
        print("=" * 50)

        # Extract transcript - Omi sends it in different formats
        transcript = ""
        if isinstance(payload, dict):
            # Try different possible fields
            print(f"DEBUG: payload.get('transcript') = {repr(payload.get('transcript'))}")
            print(f"DEBUG: payload.get('text') = {repr(payload.get('text'))}")

            transcript = (
                payload.get('transcript') or
                payload.get('text') or
                (payload.get('segments', [{}])[0].get('text', '') if payload.get('segments') else '')
            )

            print(f"DEBUG: Final transcript = {repr(transcript)}")

        # Fallback: check if payload itself is a string
        if not transcript and isinstance(payload, str):
            transcript = payload

        if not transcript:
            print("⚠️  No transcript found in payload")
            return {"status": "ok", "message": "No transcript found"}

        # Extract clinical data using Claude
        if claude_extractor:
            print("\n🤖 Using Claude API for extraction...")
            clinical_data = claude_extractor.extract_clinical_data(transcript)
            print(f"\n🔍 EXTRACTED DATA:")
            print(json.dumps(clinical_data, indent=2))
        else:
            print("\n⚠️  Claude not available, skipping extraction")
            clinical_data = {
                "medications_taken": [],
                "symptoms": [],
                "side_effects": [],
                "quality_of_life": {},
                "adherence_status": "unknown",
                "clinical_summary": "Claude API not configured"
            }

        # Store in database
        entry = await db.add_entry(
            transcript=transcript,
            medications_taken=clinical_data.get("medications_taken", []),
            symptoms=clinical_data.get("symptoms", []),
            side_effects=clinical_data.get("side_effects", []),
            quality_of_life=clinical_data.get("quality_of_life", {}),
            adherence_status=clinical_data.get("adherence_status", "unknown"),
            clinical_summary=clinical_data.get("clinical_summary", ""),
            raw_data=payload
        )

        print(f"\n✅ Saved to database (ID: {entry.id})")
        print("=" * 50)

        return {
            "status": "success",
            "message": "Clinical data processed",
            "extracted": clinical_data,
            "entry_id": entry.id
        }

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/entries")
async def get_entries():
    """API endpoint to get all entries"""
    entries = await db.get_all_entries()
    return {
        "total": len(entries),
        "entries": [e.to_dict() for e in entries]
    }

@app.post("/api/test")
async def test_webhook(request: Request):
    """Test endpoint to simulate Omi webhook"""
    payload = await request.json()
    return await omi_webhook(request)

@app.get("/export/pdf/{patient_id}")
async def export_pdf(request: Request, patient_id: str):
    """Export patient data as a formatted PDF report"""
    entries = await db.get_all_entries()

    # Filter entries for this patient
    patient_entries = [e for e in entries if e.patient_id == patient_id]

    if not patient_entries:
        return HTMLResponse("<h1>No data found for this patient</h1>", status_code=404)

    # Calculate statistics
    total_entries = len(patient_entries)
    medications_count = sum(1 for e in patient_entries if e.medications_taken)
    symptoms_reported = sum(len(e.symptoms) for e in patient_entries if e.symptoms)

    # Get date range
    from datetime import datetime
    dates = [e.timestamp for e in patient_entries if e.timestamp]
    if dates:
        start_date = min(dates)
        end_date = max(dates)
        days_enrolled = (end_date - start_date).days + 1
    else:
        start_date = datetime.now()
        end_date = datetime.now()
        days_enrolled = 1

    return templates.TemplateResponse("report.html", {
        "request": request,
        "patient_id": patient_id,
        "patient_name": "Jane D.",
        "trial_name": "Migraine Prevention Study",
        "trial_id": "2024-447",
        "site": "Stanford Medical Center",
        "start_date": start_date,
        "end_date": end_date,
        "days_enrolled": days_enrolled,
        "total_entries": total_entries,
        "medications_count": medications_count,
        "symptoms_reported": symptoms_reported,
        "adherence_rate": 100,
        "entries": patient_entries
    })

@app.on_event("startup")
async def startup():
    await db.init_db()
    print("\n" + "=" * 50)
    print("🏥 CLINICAL TRIAL COMPANION STARTED")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:8000")
    print("🔗 Webhook: http://localhost:8000/webhook/omi")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
