# Setting Up Ngrok for Omi Integration

## What is ngrok?
Ngrok creates a secure tunnel from the internet to your local server, allowing your Omi device to send data to your local machine.

## Setup Steps

### 1. Install ngrok
```bash
# Option 1: Download from website
# Go to: https://ngrok.com/download

# Option 2: Using snap (Linux)
sudo snap install ngrok

# Option 3: Using brew (Mac)
brew install ngrok
```

### 2. Sign up for ngrok (Free)
1. Go to https://dashboard.ngrok.com/signup
2. Create a free account
3. Copy your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken

### 3. Authenticate ngrok
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### 4. Start ngrok tunnel
Make sure your server is running first, then in a NEW terminal:
```bash
ngrok http 8000
```

You'll see output like:
```
ngrok

Session Status                online
Account                      your-email@example.com
Version                      3.x.x
Region                       United States (us)
Latency                      -
Web Interface                http://127.0.0.1:4040
Forwarding                   https://abc123.ngrok.io -> http://localhost:8000
```

### 5. Copy your ngrok URL
Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok.io`)

### 6. Configure Omi App

#### Official Omi App Integration:
1. Open the Omi mobile app
2. Go to **Settings** or **Integrations**
3. Look for **Webhooks** or **Developer** options
4. Add a new webhook with URL:
   ```
   https://YOUR-NGROK-URL.ngrok.io/webhook/omi
   ```

#### Alternative: Omi Developer Portal
If the app doesn't have webhook settings:
1. Go to https://docs.omi.me or your Omi developer dashboard
2. Find the webhook/integration settings
3. Add webhook URL: `https://YOUR-NGROK-URL.ngrok.io/webhook/omi`

### 7. Test It!
1. Talk to your Omi device: "I took my aspirin and have a headache"
2. Check your terminal - you should see the webhook being hit
3. Visit http://localhost:8000 to see the data in the dashboard

## Troubleshooting

### Ngrok session expired
Free ngrok sessions expire after 2 hours. Just restart ngrok and update the URL in Omi.

### Webhook not receiving data
- Check that ngrok is still running
- Verify the URL in Omi app is correct (with /webhook/omi at the end)
- Look at ngrok web interface: http://127.0.0.1:4040 to see incoming requests

### No data showing on dashboard
- Check that the server (app.py) is still running
- Look at terminal logs for errors
- Try the test script: `./test_webhook.sh`

## Production Deployment (Later)
For a permanent URL without ngrok, deploy to:
- Railway: https://railway.app
- Render: https://render.com
- Fly.io: https://fly.io
- Heroku: https://heroku.com
