#!/bin/bash

echo "🏥 Starting Clinical Trial Companion..."
echo ""
echo "Dashboard will be available at: http://localhost:8000"
echo "Webhook endpoint: http://localhost:8000/webhook/omi"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
