import os
import json
from anthropic import Anthropic
from typing import Dict, Any

class ClaudeExtractor:
    """Uses Claude API to extract structured clinical data from patient transcripts"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please set it in environment or pass to constructor.")
        self.client = Anthropic(api_key=self.api_key)

    def extract_clinical_data(self, transcript: str) -> Dict[str, Any]:
        """
        Extract structured clinical data from patient transcript using Claude.

        Returns a structured dict with:
        - medications_taken: List of medications with times and dosages
        - symptoms: List of symptoms with severity and timing
        - side_effects: Potential adverse events
        - quality_of_life: Energy, functioning, etc.
        - adherence_status: Whether patient is compliant
        - clinical_summary: Human-readable summary
        """

        prompt = f"""You are a clinical data extraction AI. Extract structured medical information from this patient's voice report.

Patient transcript:
"{transcript}"

Extract and return a JSON object with the following structure (be precise and only include information explicitly mentioned):

{{
  "medications_taken": [
    {{"name": "medication name", "time": "HH:MM or descriptive time", "dose": "dosage if mentioned", "type": "trial_medication or concomitant"}}
  ],
  "symptoms": [
    {{"name": "symptom name", "severity": "mild/moderate/severe or number/10", "onset_time": "time if mentioned", "duration": "duration if mentioned", "resolved": true/false}}
  ],
  "side_effects": [
    {{"symptom": "symptom name", "relation_to_drug": "possible/probable/unlikely", "timing": "timing relative to medication"}}
  ],
  "quality_of_life": {{
    "energy_level": "good/normal/low/poor or description",
    "work_capacity": "normal/impaired/unable or description",
    "functioning": "description of daily activities"
  }},
  "adherence_status": "compliant/non-compliant/partial",
  "clinical_summary": "A brief clinical note summarizing the report in 1-2 sentences"
}}

Important rules:
- Only extract information that is EXPLICITLY stated in the transcript
- If a field is not mentioned, use null or omit it
- For severity, extract the exact scale used (e.g., "4/10" or "mild")
- For times, preserve the format mentioned (e.g., "8 AM", "around 10 o'clock")
- Side effects should only be listed if there's a temporal relationship to medication
- Be conservative - don't infer information not clearly stated

Return ONLY the JSON object, no other text."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from Claude's response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            # Parse JSON
            extracted_data = json.loads(response_text)

            # Validate structure
            required_keys = ["medications_taken", "symptoms", "side_effects", "quality_of_life", "adherence_status", "clinical_summary"]
            for key in required_keys:
                if key not in extracted_data:
                    extracted_data[key] = [] if key.endswith("s") or key == "medications_taken" else ("" if key == "clinical_summary" else {})

            return extracted_data

        except Exception as e:
            print(f"❌ Claude extraction error: {str(e)}")
            # Return empty structure on error
            return {
                "medications_taken": [],
                "symptoms": [],
                "side_effects": [],
                "quality_of_life": {},
                "adherence_status": "unknown",
                "clinical_summary": f"Error extracting data: {str(e)}"
            }

# Test function
if __name__ == "__main__":
    # Test with sample transcript
    test_transcript = """Good morning. I took my trial medication at 8 AM today.
    Around 10 o'clock, I started feeling some nausea - not terrible, maybe a 4 out of 10.
    Also had a mild headache that lasted about 30 minutes. Took some ibuprofen for that.
    Energy levels are pretty good though, been able to work normally."""

    extractor = ClaudeExtractor()
    result = extractor.extract_clinical_data(test_transcript)
    print(json.dumps(result, indent=2))
