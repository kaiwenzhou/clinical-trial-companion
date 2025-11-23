#!/bin/bash

echo "🧪 Testing webhook with sample clinical data..."
echo ""

# Test 1: Symptoms and medication
echo "Test 1: Sending transcript with symptoms and medication..."
curl -X POST http://localhost:8000/webhook/omi \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I took my aspirin this morning and I am having a really bad headache. The pain is in my forehead and it hurts when I move."
  }'

echo -e "\n\n"

# Test 2: Side effects
echo "Test 2: Sending transcript with side effects..."
curl -X POST http://localhost:8000/webhook/omi \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "The new medication is causing some nausea and dizziness. I also feel very tired all the time."
  }'

echo -e "\n\n"

# Test 3: Multiple medications
echo "Test 3: Sending transcript with multiple medications..."
curl -X POST http://localhost:8000/webhook/omi \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "I took ibuprofen for my fever this morning. Also took my prescription tablet at lunch. The pain has gone down."
  }'

echo -e "\n\n"
echo "✅ Tests complete! Check the dashboard at http://localhost:8000"
