# Clinical Trial Companion 🏥

Real-time patient-reported outcomes from Omi device using AI-powered clinical data extraction.

## Quick Start

### 1. Start the Server
```bash
./start.sh
# or
python3 app.py
```

Server will run at: `http://localhost:8000`

### 2. Set Up ngrok (to expose local server to Omi)
```bash
# Install ngrok (if not installed)
# Download from: https://ngrok.com/download

# Start ngrok
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

### 3. Configure Omi App

1. Open Omi mobile app
2. Go to: **Settings → Integrations → Developer**
3. Click "Create Integration"
4. Set webhook URL to: `https://YOUR-NGROK-URL.ngrok.io/webhook/omi`
5. Save and enable the integration

### 4. Test It!

Talk to your Omi device:
- "I took my aspirin this morning and I'm feeling some mild headache"
- "The medication is working but I'm experiencing some nausea"
- "I have a fever and took ibuprofen an hour ago"

Then check the dashboard at: `http://localhost:8000`

## How It Works

```
Omi Device
  → Records conversation
  → Sends transcript to webhook
  → FastAPI extracts clinical data (symptoms, meds, side effects)
  → SQLite stores data
  → Dashboard displays real-time entries
```

## Endpoints

- `GET /` - Dashboard UI
- `POST /webhook/omi` - Webhook for Omi device
- `GET /api/entries` - JSON API for all entries
- `POST /api/test` - Test endpoint

## Test Locally

```bash
# Test the webhook with sample data
curl -X POST http://localhost:8000/webhook/omi \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I took my aspirin this morning and have a headache"
  }'

# Or use the test script
./test_webhook.sh
```

## Tech Stack

- **Backend**: FastAPI (async Python web framework)
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML/CSS/JS (auto-refreshing dashboard)
- **Medical NER**: Keyword-based extraction (upgradeable to spaCy/transformers)

## Next Steps

- Add more medical keywords
- Integrate NLP models (spaCy medical NER)
- Export to CSV for clinical trials
- Patient authentication
- Multi-patient support
- FDA compliance reporting