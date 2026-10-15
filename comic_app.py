import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load API key from environment variables or Streamlit Secrets
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
    st.write("ComicStor turns your idea into a story with five comic panels.")
    st.divider()
    st.subheader("✨ Features")
    st.write("📖 AI Story Generation")
    st.write("🎭 Character Consistency")
    st.write("💬 Character Dialogues")
    st.write("📥 Story Download")
    st.caption("AI image generation is disabled.")

st.divider()

if "comic_story" not in st.session_state:
    st.session_state["comic_story"] = ""

story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    placeholder="Example: A village girl discovers a magical book...",
    height=130,
)

st.info("🎭 The AI prompt asks for consistent characters across all five panels.")

left, right = st.columns(2)
with left:
    generate_clicked = st.button(
        "🚀 Generate My Comic", type="primary", use_container_width=True
    )
with right:
    clear_clicked = st.button("🗑️ Clear", use_container_width=True)

if clear_clicked:
    st.session_state["comic_story"] = ""
    st.rerun()


def get_text_model(client):
    """Return a text-generation model that this API key reports as available."""
    available = []
    for model_info in client.models.list():
        name = getattr(model_info, "name", "") or ""
        actions = getattr(model_info, "supported_actions", None) or []
        if name and any("generatecontent" == str(action).lower() for action in actions):
            # API model names may be returned as "models/model-name".
            model_id = name.removeprefix("models/")
            available.append(model_id)

    if not available:
        raise RuntimeError(
            "No model supporting generateContent was returned for this API key. "
            "Check the key and its Gemini API access."
        )

    # Prefer current Flash aliases, then other Flash models, then any text model.
    preferred = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash"]
    for candidate in preferred:
        if candidate in available:
            return candidate

    flash_models = [name for name in available if "flash" in name.lower() and "image" not in name.lower()]
    if flash_models:
        return flash_models[0]

    text_models = [name for name in available if "image" not in name.lower()]
    if text_models:
        return text_models[0]

    return available[0]


if generate_clicked:
    if not story_idea.strip():
        st.warning("💡 Please enter a story idea to create your comic!")
    elif not api_key:
        st.error(
            "GEMINI_API_KEY was not found. Add it to your .env file locally "
            "or to Streamlit Secrets when deployed."
        )
    else:
        try:
            client = genai.Client(api_key=api_key)

            with st.spinner("Checking available Gemini models..."):
                model_name = get_text_model(client)

            prompt = f"""
Create a short comic story based on this idea:
{story_idea.strip()}

Write exactly five panels with these headings:
Panel 1
Panel 2
Panel 3
Panel 4
Panel 5

For every panel include:
1. Scene
2. Character action
3. Dialogue

Keep all characters consistent across the five panels. Preserve each character's
name, age, appearance, hairstyle, clothing, and personality.
Do not include image prompts and do not generate images.
Make the story creative, clear, and suitable for a general audience.
"""
            with st.spinner("Creating your comic story..."):
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

            story = (response.text or "").strip()
            if not story:
                st.error("Gemini returned an empty response. Please try again.")
            else:
                st.session_state["comic_story"] = story
                st.success(f"🎉 Your ComicStor story is ready! (Model: {model_name})")

        except Exception as error:
            message = str(error)
            lower = message.lower()

            if "429" in message or "quota" in lower or "resource_exhausted" in lower:
                st.error("⚠️ Gemini API quota/rate limit reached. Please wait and try again.")
            elif "503" in message or "unavailable" in lower:
                st.error("⚠️ Gemini is temporarily unavailable. Please try again shortly.")
            elif "api key" in lower or "permission" in lower or "401" in message or "403" in message:
                st.error("⚠️ The API key is invalid or does not have permission. Check your Gemini API key and API access.")
            elif "404" in message or "not found" in lower:
                st.error("⚠️ The API did not accept the selected model. Check which models your API key can access.")
            else:
                st.error("⚠️ Story generation failed. Check the API key, model access, and package versions.")
                st.code(message)

if st.session_state["comic_story"]:
    story = st.session_state["comic_story"]
    st.divider()
    st.header("📖 Your Comic Story")

    parts = re.split(
        r"(?=^\s*Panel\s+[1-5]\s*$)",
        story,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    panels = [part.strip() for part in parts if part.strip()]

    for index, panel in enumerate(panels, start=1):
        st.markdown("---")
        lines = panel.splitlines()
        heading = lines[0].strip() if lines else f"Panel {index}"
        content = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        st.subheader(f"🎬 {heading}")
        if content:
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
