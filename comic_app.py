import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load API key from .env or Streamlit secrets
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

st.set_page_config(page_title="ComicStor", page_icon="📖", layout="wide")

st.title("📖 ComicStor")
st.write("Create your own AI comic story!")
st.caption("✨ Turn your imagination into a 5-panel comic story with AI.")

with st.sidebar:
    st.header("📖 About ComicStor")
    st.write(
        "ComicStor uses Gemini AI to turn your idea into a story "
        "with five comic panels."
    )
    st.divider()
    st.subheader("✨ Features")
    st.write("📖 AI Story Generation")
    st.write("🎭 Character Consistency")
    st.write("💬 Character Dialogues")
    st.write("📥 Story Download")
    st.caption("Image generation is disabled to avoid image-generation errors.")

st.divider()

story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    placeholder="Example: A village girl discovers a magical book...",
    height=130,
)

st.info("🎭 The story prompt asks the AI to keep characters consistent across all five panels.")

col1, col2 = st.columns(2)
with col1:
    generate_clicked = st.button("🚀 Generate My Comic", type="primary", use_container_width=True)
with col2:
    clear_clicked = st.button("🗑️ Clear", use_container_width=True)

if clear_clicked:
    st.session_state["comic_story"] = ""
    st.session_state["comic_idea"] = ""
    st.rerun()

if generate_clicked:
    if not story_idea.strip():
        st.warning("💡 Please enter a story idea to create your comic!")
    elif not api_key:
        st.error(
            "GEMINI_API_KEY was not found. Add it to your .env file "
            "or Streamlit Secrets, then restart the app."
        )
    else:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
Create a short comic story based on this idea:
{story_idea.strip()}

Write exactly 5 comic panels, using these exact headings:
Panel 1
Panel 2
Panel 3
Panel 4
Panel 5

For each panel, provide:
1. Scene
2. Character action
3. Dialogue

Keep the same characters consistent across all 5 panels. Maintain the same
character names, ages, appearance, hairstyle, clothing, and personality.
Do not include image prompts or instructions to generate images.
Make the story clear, creative, and suitable for a general audience.
"""
            with st.spinner("Creating your comic story..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

            story = (response.text or "").strip()
            if not story:
