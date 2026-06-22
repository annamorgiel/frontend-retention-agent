# src/gemini_client.py
import streamlit as st
from google import genai
from google.genai import types

def ask_gemini(prompt_text: str) -> str:
    """Sends a contextual customer profile to Gemini for strategic mitigation text."""
    try:
        # 💡 Pull the key safely right when the button is clicked, not at boot time
        api_key = st.secrets["GEMINI_API_KEY"]

        # Initialize client explicitly with the loaded key
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high")
            ),
        )
        return response.text
    except KeyError:
        return "❌ Configuration Error: 'GEMINI_API_KEY' not found in .streamlit/secrets.toml"
    except Exception as e:
        return f"❌ Error calling Gemini: {str(e)}"
