# Clinical Trial Companion - Complete Setup Guide

## Overview

This project demonstrates a voice-based clinical trial companion that uses the Omi wearable device and Claude AI to automatically extract structured clinical data from patient conversations.

## What We Built

✅ **Claude API Integration** - Uses Claude Sonnet 4 for intelligent medical NER
✅ **Enhanced Dashboard** - Shows patient info, latest reports, timeline, and statistics
✅ **Sample Data** - 15 realistic patient entries pre-loaded for demo
✅ **PDF Export** - One-click export of FDA-ready patient reports
✅ **Real-time Updates** - Dashboard auto-refreshes every 5 seconds

---

## Quick Setup (3 steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `anthropic` - Claude API client
- `sqlalchemy` - Database ORM
- `aiosqlite` - Async SQLite
- `jinja2` - Template engine

### Step 2: Set Your API Key

You **MUST** set your Anthropic API key for Claude extraction to work.

**Option A: Environment Variable**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option B: Create .env file** (recommended)
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

To verify it's set:
```bash
echo $ANTHROPIC_API_KEY
```

### Step 3: Load Sample Data & Start Server

```bash
# Populate database with sample data (15 patient entries)
python3 populate_db.py

# Start the server
python3 app.py
```

Then open: **http://localhost:8000**

---

## Project Structure

```
clinical-trial-companion/
│
├── app.py                      # Main FastAPI application with all endpoints
├── database.py                 # SQLAlchemy models and database operations
├── claude_extractor.py         # Claude API integration for medical NER
├── populate_db.py             # Script to populate DB with sample data
├── sample_data.json           # 15 realistic patient session entries
├── requirements.txt           # Python package dependencies
│
├── templates/
│   ├── dashboard.html         # Main dashboard UI (enhanced)
│   └── report.html            # PDF export template
│
└── docs/
    ├── DEMO_GUIDE.md          # Complete demo presentation guide
    ├── SETUP.md               # This file
    ├── README.md              # Project overview
    └── QUICKSTART.md          # Omi integration guide
```

---

## Features Explained

### 1. Claude API Medical Extraction

The system uses Claude Sonnet 4 to extract structured medical data:

**Input (Natural Speech):**
> "I took my trial medication at 8 AM today. Around 10 o'clock, I started feeling some nausea - not terrible, maybe a 4 out of 10."

**Output (Structured Data):**
```json
{
  "medications_taken": [
    {"name": "trial medication", "time": "08:00", "type": "trial_medication"}
  ],
  "symptoms": [
    {"name": "nausea", "severity": "4/10", "onset_time": "10:00"}
  ],
  "side_effects": [
    {"symptom": "nausea", "relation_to_drug": "possible", "timing": "2 hours post-dose"}
  ],
  "quality_of_life": {
    "energy_level": "good",
    "work_capacity": "normal"
  },
  "adherence_status": "compliant",
  "clinical_summary": "Patient reports moderate nausea..."
}
```

### 2. Enhanced Dashboard

The new dashboard shows:

- **🔴 LIVE indicator** - Shows real-time status
- **Patient stats** - Active patients, total reports, adherence rate, compliance
- **Latest entry card** - Prominently displays most recent report with full extraction
- **Timeline view** - Chronological list of all patient reports
- **Export button** - One-click PDF generation

### 3. Sample Data

The `sample_data.json` includes 15 entries spanning 7 days:
- Morning and evening medication doses
- Various symptoms (nausea, headaches, dizziness, fatigue)
- Different severity levels (mild, moderate, rated 1-10)
- Side effects and quality of life indicators
- Perfect for demonstrating the system

### 4. PDF Export

Clicking "📄 Export Report" generates a professional clinical trial report with:
- Patient information
- Trial details
- Summary statistics (adherence, symptoms, etc.)
- Detailed timeline of all entries
- Clinical notes for each report
- Print-friendly format

---

## API Endpoints

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard (HTML) |
| `/webhook/omi` | POST | Receives data from Omi device |
| `/api/entries` | GET | Get all entries as JSON |
| `/export/pdf/{patient_id}` | GET | Export patient report |
| `/api/test` | POST | Test endpoint for webhook |

### Testing the Webhook

Without Omi device, you can test with curl:

```bash
curl -X POST http://localhost:8000/webhook/omi \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I took my medication at 9 AM. Feeling some mild nausea, maybe a 3 out of 10."
  }'
```

Then refresh the dashboard to see the new entry.

---

## Connecting to Omi Device

If you have an Omi device:

1. **Start ngrok** to expose your local server:
   ```bash
   ngrok http 8000
   ```

2. **Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`)

3. **Configure Omi app:**
   - Open Omi mobile app
   - Go to Settings → Integrations → Developer
   - Create Integration
   - Set webhook URL: `https://your-ngrok-url.ngrok.io/webhook/omi`
   - Enable integration

4. **Talk to your Omi:**
   - Put on the device
   - Speak naturally about symptoms/medications
   - Dashboard will auto-update within seconds

---

## Database Schema

The enhanced schema supports rich clinical data:

```python
class ClinicalEntry:
    id: int                      # Entry ID
    timestamp: datetime          # When the report was created
    patient_id: str              # Patient identifier (default: "7482")
    transcript: str              # Full voice transcript

    # Extracted data (JSON fields):
    medications_taken: list      # [{"name": "...", "time": "...", "dose": "..."}]
    symptoms: list               # [{"name": "...", "severity": "...", "onset_time": "..."}]
    side_effects: list           # [{"symptom": "...", "relation_to_drug": "..."}]
    quality_of_life: dict        # {"energy_level": "...", "work_capacity": "..."}
    adherence_status: str        # "compliant" / "non-compliant"
    clinical_summary: str        # AI-generated summary

    raw_data: dict               # Original Omi payload
```

---

## Troubleshooting

### "Claude extraction not working"

**Symptom:** Dashboard shows entries but no extracted data (medications, symptoms, etc.)

**Solution:**
1. Check if API key is set: `echo $ANTHROPIC_API_KEY`
2. Verify key is valid (starts with `sk-ant-`)
3. Restart the server after setting the key
4. Check server logs for errors

### "No entries showing on dashboard"

**Symptom:** Dashboard is empty

**Solution:**
1. Run `python3 populate_db.py` to load sample data
2. Check if database file exists: `ls -la *.db`
3. Verify server is running without errors

### "Export PDF button doesn't work"

**Symptom:** Clicking export shows error

**Solution:**
1. Make sure you have at least one entry in the database
2. Check the patient_id in the URL matches an existing patient
3. Check server logs for template errors

### "Omi webhook not receiving data"

**Symptom:** Speaking to Omi doesn't create entries

**Solution:**
1. Verify ngrok is running: `ngrok http 8000`
2. Check Omi app webhook configuration
3. Test webhook with curl (see above)
4. Check server logs for incoming requests

---

## Performance Notes

- **Auto-refresh:** Dashboard refreshes every 5 seconds
- **Claude API:** Each extraction call takes ~2-3 seconds
- **Database:** SQLite is sufficient for demo; use PostgreSQL for production
- **Concurrent users:** FastAPI handles multiple patients simultaneously

---

## Next Steps for Production

1. **Authentication:** Add patient/researcher login
2. **Multi-patient:** Support multiple patients per trial
3. **Alerts:** Real-time notifications for severe adverse events
4. **EHR Integration:** Connect to Epic, Cerner, etc.
5. **FDA Compliance:** Digital signatures, 21 CFR Part 11
6. **Analytics:** Advanced visualizations and insights
7. **Mobile App:** Dedicated researcher mobile app

---

## Security Considerations

⚠️ **This is a demo/hackathon project. For production use:**

- Encrypt patient data at rest and in transit
- Implement proper authentication and authorization
- Use HTTPS for all connections
- Comply with HIPAA regulations
- Add audit logging
- Implement data retention policies
- Use secure API key management (not environment variables)

---

## Support

For questions or issues:

1. Check `DEMO_GUIDE.md` for presentation tips
2. Check `README.md` for project overview
3. Check `QUICKSTART.md` for Omi integration

---

## Tech Stack

- **Hardware:** Omi wearable device
- **Backend:** FastAPI (Python 3.10+)
- **AI:** Claude Sonnet 4 API (Anthropic)
- **Database:** SQLite (async with aiosqlite)
- **Frontend:** HTML/CSS/JavaScript (Jinja2 templates)
- **Deployment:** Uvicorn ASGI server

---

## License

Built for hackathon/educational purposes.

---

**🎉 You're all set! Run `python3 app.py` and visit http://localhost:8000**
