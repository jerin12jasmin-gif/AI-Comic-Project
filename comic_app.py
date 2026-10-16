
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Streamlit Secrets fallback
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Comic Story",
    page_icon="📖",
    layout="wide"
)

# --------------------------------------------------
# Application Title
# --------------------------------------------------

st.title("📖 Comic Story")

st.write("Create your own AI comic story!")

st.caption(
    "✨ Turn your imagination into a five-panel "
    "comic story with AI — text only, no image generation."
)

st.divider()

# --------------------------------------------------
# About Section
# --------------------------------------------------

with st.sidebar:
    st.header("📖 About Comic Story")

    st.write(
        "Comic Story uses Gemini AI to transform "
        "your story idea into a five-panel comic story."
    )

    st.divider()

    st.subheader("✨ Features")

    st.write("📖 AI Story Generation")
    st.write("💬 Character Dialogues")
    st.write("🎭 Character Consistency")
    st.write("📥 Story Download")

# --------------------------------------------------
# Gemini Client
# --------------------------------------------------

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# --------------------------------------------------
# Story Input
# --------------------------------------------------

story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    placeholder=(
        "Example: A village girl discovers "
        "a magical book..."
    ),
    height=150
)

st.info(
    "🎭 The AI will try to keep the same characters "
    "consistent across all five panels."
)

# --------------------------------------------------
# Buttons
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    generate_button = st.button(
        "🚀 Generate My Comic",
        use_container_width=True
    )

with col2:
    clear_button = st.button(
        "🗑️ Clear",
        use_container_width=True
    )

if clear_button:
    st.rerun()

# --------------------------------------------------
# Generate Comic Story
# --------------------------------------------------

if generate_button:

    if not story_idea.strip():
        st.warning(
            "💡 Please enter a story idea first!"
        )
        st.stop()

    if not client:
        st.error(
            "⚠️ Gemini API key is missing. "
            "Add GEMINI_API_KEY to your .env file "
            "or Streamlit Secrets."
        )
        st.stop()

    prompt = f"""
Create an interesting comic story based on this idea:

{story_idea}

Write exactly FIVE panels.

Use these headings exactly:

Panel 1
Panel 2
Panel 3
Panel 4
Panel 5

For every panel, include:

1. Scene:
Describe what happens in the scene.

2. Character Action:
Explain what the characters are doing.

3. Dialogue:
Write short, natural dialogue for the characters.

IMPORTANT RULES:

- Keep the same main characters throughout all five panels.
- Keep their names, ages, appearance, hairstyles,
  clothing, and personalities consistent.
- Give the story a clear beginning, middle, and ending.
- Make the story creative, simple, and interesting.
- Do not generate images.
- Do not include image prompts.
- Return text only.
"""

    # --------------------------------------------------
    # Call Gemini
    # --------------------------------------------------

    with st.spinner("✨ Creating your comic story..."):

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            story_text = response.text

            if not story_text or not story_text.strip():
                st.error(
                    "⚠️ Gemini returned an empty story. "
                    "Please try again."
                )
                st.stop()

        except Exception as e:

            error_message = str(e)
            error_lower = error_message.lower()

            if (
                "429" in error_message
                or "quota" in error_lower
                or "rate limit" in error_lower
            ):
                st.error(
                    "⚠️ Gemini API quota or rate limit "
                    "reached. Please wait and try again, "
                    "or check your Gemini API quota."
                )

            elif (
                "503" in error_message
                or "unavailable" in error_lower
            ):
                st.error(
                    "⚠️ Gemini is temporarily unavailable. "
                    "Please try again later."
                )

            elif (
                "401" in error_message
                or "403" in error_message
                or "api key" in error_lower
                or "permission" in error_lower
            ):
                st.error(
                    "⚠️ Check your Gemini API key "
                    "and its permissions."
                )

            elif "404" in error_message:
                st.error(
                    "⚠️ The selected Gemini model was "
                    "not found or is unavailable."
                )

            else:
                st.error(
                    "⚠️ Unable to generate the story."
                )
                st.code(error_message)

            st.stop()

    # --------------------------------------------------
    # Display Story
    # --------------------------------------------------

    st.success("🎉 Your comic story is ready!")

    st.markdown("## 📖 Your Comic Story")

    # Split the generated text into five panels
    import re

    panels = re.split(
        r"(?im)^\s*Panel\s+([1-5])\s*:?\s*$",
        story_text
    )

    panel_content = {}

    for index in range(1, len(panels), 2):
        if index + 1 < len(panels):
            panel_number = panels[index].strip()
            content = panels[index + 1].strip()
            panel_content[panel_number] = content

    # Show panels in order
    for number in range(1, 6):

        st.divider()

        st.subheader(f"📖 Panel {number}")

        content = panel_content.get(str(number))

        if content:
            st.markdown(content)
        else:
            st.write(
                "Panel content could not be separated "
                "automatically. See the complete story below."
            )

    # --------------------------------------------------
    # Download Story
    # --------------------------------------------------

    st.divider()

    st.download_button(
        label="📥 Download Your Comic Story",
        data=story_text,
        file_name="Comic_Story.txt",
        mime="text/plain",
        use_container_width=True
    )

    with st.expander("📄 View Complete Story"):
        st.text(story_text)
