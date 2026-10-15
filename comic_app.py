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
                st.error("Gemini returned an empty response. Please try again.")
            else:
                st.session_state["comic_story"] = story
                st.session_state["comic_idea"] = story_idea.strip()
                st.success("🎉 Your ComicStor story is ready!")

        except Exception as e:
            message = str(e)
            lower_message = message.lower()
            if "429" in message or "quota" in lower_message or "resource_exhausted" in lower_message:
                st.error("⚠️ Gemini API quota/rate limit reached. Please wait and try again.")
            elif "503" in message or "unavailable" in lower_message:
                st.error("⚠️ Gemini is temporarily unavailable. Please try again shortly.")
            elif "404" in message or "not found" in lower_message:
                st.error("⚠️ The selected Gemini model is unavailable for this API key. Check the model name and API access.")
            elif "api key" in lower_message or "permission" in lower_message or "401" in message or "403" in message:
                st.error("⚠️ The Gemini API key is invalid or does not have permission. Check GEMINI_API_KEY.")
            else:
                st.error("⚠️ Could not generate the story. Check your API key, internet connection, and installed Google Gen AI SDK.")
                st.code(message)

if st.session_state.get("comic_story"):
    story = st.session_state["comic_story"]
    st.divider()
    st.header("📖 Your Comic Story")

    # Split the response at each Panel heading and show each panel separately.
    import re
    parts = re.split(r"(?=^\s*Panel\s+[1-5]\s*$)", story, flags=re.IGNORECASE | re.MULTILINE)
    panels = [part.strip() for part in parts if part.strip()]

    for index, panel in enumerate(panels, start=1):
        st.markdown("---")
        lines = panel.splitlines()
        heading = lines[0].strip() if lines else f"Panel {index}"
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else panel

        st.subheader(f"🎬 {heading}")
        if content:
            # Format the common section labels without requiring a fixed response format.
            content = re.sub(r"(?im)^\s*1\.\s*Scene\s*:?", "🎬 **Scene:**", content)
            content = re.sub(r"(?im)^\s*2\.\s*Character action\s*:?", "🎭 **Character Action:**", content)
            content = re.sub(r"(?im)^\s*3\.\s*Dialogue\s*:?", "💬 **Dialogue:**", content)
            content = re.sub(r"(?im)^\s*Scene\s*:", "🎬 **Scene:**", content)
            content = re.sub(r"(?im)^\s*Character action\s*:", "🎭 **Character Action:**", content)
            content = re.sub(r"(?im)^\s*Dialogue\s*:", "💬 **Dialogue:**", content)
            st.markdown(content)

    st.download_button(
        "📥 Download Your Comic Story",
        data=story,
        file_name="ComicStor_Story.txt",
        mime="text/plain",
        use_container_width=True,
    )
