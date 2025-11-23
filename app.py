from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional
import json
import re
from database import Database, ClinicalEntry

app = FastAPI(title="Clinical Trial Companion")
templates = Jinja2Templates(directory="templates")
db = Database()

# Medical keywords for extraction
SYMPTOMS = ['pain', 'headache', 'nausea', 'fatigue', 'dizziness', 'fever', 'cough',
            'tired', 'sick', 'hurt', 'ache', 'sore', 'weak', 'vomit', 'rash']
MEDICATIONS = ['aspirin', 'ibuprofen', 'tylenol', 'medication', 'pill', 'tablet',
               'medicine', 'drug', 'dose', 'prescription']
SIDE_EFFECTS = ['side effect', 'reaction', 'allergy', 'adverse']

def extract_clinical_data(transcript: str) -> dict:
    """Extract medical entities from transcript"""
    transcript_lower = transcript.lower()

    found_symptoms = [s for s in SYMPTOMS if s in transcript_lower]
    found_medications = [m for m in MEDICATIONS if m in transcript_lower]
    found_side_effects = [se for se in SIDE_EFFECTS if se in transcript_lower]

    return {
        "symptoms": found_symptoms,
        "medications": found_medications,
        "side_effects": found_side_effects,
        "raw_transcript": transcript
    }

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

        # Extract clinical data
        clinical_data = extract_clinical_data(transcript)

        print(f"\n🔍 EXTRACTED DATA:")
        print(f"   Symptoms: {clinical_data['symptoms']}")
        print(f"   Medications: {clinical_data['medications']}")
        print(f"   Side Effects: {clinical_data['side_effects']}")

        # Store in database
        entry = await db.add_entry(
            transcript=transcript,
            symptoms=clinical_data['symptoms'],
            medications=clinical_data['medications'],
            side_effects=clinical_data['side_effects'],
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
