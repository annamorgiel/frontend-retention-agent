# src/gemini_client.py
from google import genai
from google.genai import types

# Initialize the client. It will automatically detect
# the environment variable / streamlit secret.
client = genai.Client()

def ask_gemini(prompt_text: str) -> str:
    """Sends a contextual customer profile to Gemini for strategic mitigation text."""
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high")
            ),
        )
        return response.text
    except Exception as e:
        return f"❌ Error calling Gemini: {str(e)}"
