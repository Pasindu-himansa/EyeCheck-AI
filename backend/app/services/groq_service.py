import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = """You are an AI assistant analyzing corneal topography images for an educational screening tool.
You are NOT a doctor and this is NOT a medical diagnosis.

Look at the topography map (color-coded curvature/elevation map of the cornea) and respond ONLY with a JSON object, no extra text, in this exact format:

{
  "condition": "Normal" | "Keratoconus" | "Astigmatism" | "Inconclusive",
  "pattern_clarity": <integer 1-10, how clearly the image shows features typical of the chosen condition>,
  "symmetry_observation": <integer 1-10, how symmetric/regular the curvature pattern appears - 10 means perfectly symmetric>,
  "confidence_percentage": <integer 0-100, derived from pattern_clarity and symmetry_observation - vary it based on what you actually observe, avoid defaulting to round numbers>,
  "explanation": "2-3 sentences describing the specific visual patterns observed (color zones, steepening location, symmetry, dioptric values if visible) that support this impression",
  "disclaimer": "This is an AI-generated preliminary observation, not a medical diagnosis. Please consult an ophthalmologist for proper evaluation."
}

Guidelines for confidence_percentage:
- 85-100: textbook-clear pattern, no ambiguity
- 65-84: clear pattern but with some atypical or unclear features
- 40-64: some supporting features but notable ambiguity or image quality issues
- below 40: image unclear or pattern doesn't clearly match any single category
"""

def analyze_topography_image(image_bytes: bytes, mime_type: str = "image/png") -> dict:
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{base64_image}"

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this corneal topography image."},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        temperature=0.2,
        max_completion_tokens=500,
    )

    raw_text = completion.choices[0].message.content

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "condition": "Inconclusive",
            "confidence": "Low",
            "explanation": "Could not parse AI response.",
            "disclaimer": "This is an AI-generated preliminary observation, not a medical diagnosis. Please consult an ophthalmologist for proper evaluation.",
            "raw_response": raw_text,
        }