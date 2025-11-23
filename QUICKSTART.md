# 🚀 Quick Start - Clinical Trial Companion

Your end-to-end Omi clinical trial system is **ready to go**! Here's how to get started in the next hour.

## ✅ What's Already Working

The server is currently running at `http://localhost:8000` with 4 test entries in the database!

**Try it now**: Open http://localhost:8000 in your browser to see the dashboard.

## 📋 Next Steps to Connect Your Omi Device

### Step 1: Install ngrok (5 minutes)

Pick one method:

```bash
# Option A: Download directly
# Go to: https://ngrok.com/download

# Option B: Using snap (Linux)
sudo snap install ngrok

# Option C: Using brew (Mac)
brew install ngrok
```

Then sign up and authenticate:
```bash
# 1. Get authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
# 2. Run:
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 2: Start ngrok (1 minute)

Open a **NEW terminal** and run:
```bash
ngrok http 8000
```

You'll see something like:
```
Forwarding    https://abc123-45-67-89.ngrok.io -> http://localhost:8000
```

**Copy that URL!** (the one that starts with `https://`)

### Step 3: Configure Omi App (3 minutes)

According to Omi docs, you need to create a custom app/plugin:

1. Open **Omi mobile app**
2. Go to: **App Store** → **Create Custom App**
3. Fill in:
   - **Name**: Clinical Trial Companion
   - **Webhook URL**: `https://YOUR-NGROK-URL/webhook/omi`
   - **Trigger**: Memory Created (when conversation ends)
4. **Install** the app
5. **Enable** it in your installed apps

### Step 4: Test with Real Device (2 minutes)

1. Talk to your Omi device naturally:
   > "I took my aspirin this morning and I'm feeling a mild headache. The medication seems to be working okay though."

2. Wait for Omi to finish recording (usually a few seconds after you stop talking)

3. Check your terminal running `python3 app.py` - you should see:
   ```
   ==================================================
   📥 RECEIVED OMI WEBHOOK
   ==================================================
   ```

4. Refresh the dashboard at http://localhost:8000

## 🎯 Testing Without Omi Device

Use the test script:
```bash
./test_webhook.sh
```

Or manually:
```bash
curl -X POST http://localhost:8000/webhook/omi \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I have a headache and took ibuprofen"
  }'
```

## 📊 What It Extracts

The system automatically identifies:
- **Symptoms**: headache, nausea, fatigue, fever, pain, dizziness, etc.
- **Medications**: aspirin, ibuprofen, tylenol, etc.
- **Side Effects**: when patients mention "side effect", "reaction", etc.

## 🔧 Troubleshooting

### Server not running?
```bash
./start.sh
```

### Dashboard shows old data?
The page auto-refreshes every 5 seconds, or click "Refresh Now"

### Webhook not receiving data from Omi?
1. Check ngrok is still running (free sessions expire after 2 hours)
2. Verify URL in Omi app is correct
3. Check ngrok web interface: http://127.0.0.1:4040 to see requests

### Need to see what Omi is sending?
Check your terminal where `app.py` is running - it prints full payloads

## 📁 Project Structure

```
clinical-trial-companion/
├── app.py              # FastAPI server & webhook endpoint
├── database.py         # SQLite database models
├── templates/
│   └── dashboard.html  # Web dashboard UI
├── requirements.txt    # Python dependencies
├── start.sh           # Quick start script
├── test_webhook.sh    # Test without Omi device
└── setup_ngrok.md     # Detailed ngrok guide
```

## 🚀 What's Next?

Want to enhance it? Here are some ideas:
1. Add more medical keywords to extract
2. Export data to CSV for clinical trial submissions
3. Add patient authentication
4. Deploy to Railway/Render for permanent URL
5. Integrate NLP models (spaCy medical NER) for better extraction
6. Add data visualization charts
7. Generate FDA-compliant reports

## ⏱️ Time Check

You've completed the build phase! Now you just need:
- 5-10 min: Set up ngrok
- 2 min: Configure Omi app
- 1 min: Test with device

**Total remaining time: ~15 minutes**

Good luck! 🏥
