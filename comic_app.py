
import os
import re
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==========================================
# 1. LOAD GEMINI API KEY
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None


# ==========================================
# 2. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Comic Story",
    page_icon="📖",
    layout="wide"
)

st.title("📖 Comic Story")
st.write("Create your own AI comic story!")
st.caption(
    "✨ Turn your imagination into a 5-panel comic story with AI."
)


# ==========================================
# 3. SIDEBAR
# ==========================================

with st.sidebar:
    st.header("📖 About Comic Story")

    st.write(
        "Comic Story turns your idea into a story "
        "with five comic panels."
    )

    st.divider()

    st.subheader("✨ Features")
    st.write("📖 AI Story Generation")
    st.write("🎭 Character Consistency")
    st.write("💬 Character Dialogues")
    st.write("📥 Story Download")

    st.caption("AI image generation is disabled.")


st.divider()


# ==========================================
# 4. SESSION STATE
# ==========================================

if "comic_story" not in st.session_state:
    st.session_state["comic_story"] = ""


# ==========================================
# 5. STORY IDEA INPUT
# ==========================================

story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    placeholder=(
        "Example: A village girl discovers a magical book "
        "that makes her wishes come true..."
    ),
    height=130,
)

st.info(
    "🎭 The AI prompt asks for consistent characters "
    "across all five panels."
)


left, right = st.columns(2)

with left:
    generate_clicked = st.button(
        "🚀 Generate My Comic",
        type="primary",
        use_container_width=True
    )

with right:
    clear_clicked = st.button(
        "🗑️ Clear",
        use_container_width=True
    )


if clear_clicked:
    st.session_state["comic_story"] = ""
    st.rerun()


# ==========================================
# 6. FIND AN AVAILABLE TEXT MODEL
# ==========================================

def get_text_model(client):
    """Find a text-generation model available to this API key."""

    available = []

    for model_info in client.models.list():
        name = getattr(model_info, "name", "") or ""
        actions = getattr(
            model_info,
            "supported_actions",
            None
        ) or []

        if name and any(
            "generatecontent" == str(action).lower()
            for action in actions
        ):
            model_id = name.removeprefix("models/")
            available.append(model_id)

    if not available:
        raise RuntimeError(
            "No text-generation model is available for this API key. "
            "Check your Gemini API access."
        )

    # Prefer these models when available.
    preferred = [
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash"
    ]

    for candidate in preferred:
        if candidate in available:
            return candidate

    # Otherwise, choose an available Flash text model.
    flash_models = [
        name for name in available
        if "flash" in name.lower()
        and "image" not in name.lower()
    ]

    if flash_models:
        return flash_models[0]

    # Otherwise, choose any available text model.
    text_models = [
        name for name in available
        if "image" not in name.lower()
    ]

    if text_models:
        return text_models[0]

    return available[0]


# ==========================================
# 7. GENERATE STORY WITH AUTOMATIC RETRIES
# ==========================================

def generate_story_with_retry(client, model_name, prompt):
    """
    Retry temporary server errors up to three times.
    Wait 2 seconds, then 4 seconds between attempts.
    """

    last_error = None

    for attempt in range(3):
        try:
            with st.spinner(
                f"✨ Creating your story... "
                f"Attempt {attempt + 1} of 3"
            ):
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

            return response

        except Exception as error:
            last_error = error
            message = str(error).lower()

            temporary_errors = [
                "503",
                "502",
                "500",
                "504",
                "unavailable",
                "overloaded",
                "internal server error",
                "deadline exceeded"
            ]

            is_temporary = any(
                item in message for item in temporary_errors
            )

            # Do not retry authentication, quota or other errors here.
            if not is_temporary:
                raise

            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

    raise RuntimeError(
        "Gemini is still unavailable after three attempts. "
        "Please try again later. "
        f"Details: {last_error}"
    )


# ==========================================
# 8. HANDLE GENERATE BUTTON
# ==========================================

if generate_clicked:

    if not story_idea.strip():
        st.warning(
            "💡 Please enter a story idea to create your comic!"
        )

    elif not api_key:
        st.error(
            "GEMINI_API_KEY was not found. Add it to your "
            ".env file locally or to Streamlit Secrets "
            "when deployed."
        )

    else:
        try:
            client = genai.Client(api_key=api_key)

            with st.spinner("🔍 Checking available Gemini models..."):
                model_name = get_text_model(client)

            # Build the story prompt.
            prompt = f"""
Create a creative five-panel comic story based on this idea:

{story_idea.strip()}

Write exactly five panels with these headings:

Panel 1
Panel 2
Panel 3
Panel 4
Panel 5

For every panel include:

1. Scene:
Describe where the scene takes place.

2. Character action:
Explain what the characters do.

3. Dialogue:
Write natural dialogue spoken by the characters.

IMPORTANT RULES:

- Create exactly five panels.
- Keep character names consistent.
- Preserve character appearance, hairstyle, clothing,
  age and personality across all panels.
- Make the story interesting and easy to understand.
- Include a clear beginning, middle and ending.
- Make the story suitable for a general audience.
- Do not include image prompts.
- Do not generate images.
- Return story text only.
"""

            # Generate the story with retries.
            response = generate_story_with_retry(
                client,
                model_name,
                prompt
            )

            story = (response.text or "").strip()

            if not story:
                st.error(
                    "Gemini returned an empty response. "
                    "Please try again."
                )

            else:
                st.session_state["comic_story"] = story

                st.success(
                    f"🎉 Your Comic Story is ready! "
                    f"(Model: {model_name})"
                )

        except Exception as error:

            message = str(error)
            lower = message.lower()

            if (
                "429" in message
                or "quota" in lower
                or "resource_exhausted" in lower
            ):
                st.error(
                    "⚠️ Gemini API quota or rate limit reached. "
                    "Please wait before trying again."
                )

            elif (
                "503" in message
                or "502" in message
                or "500" in message
                or "504" in message
                or "unavailable" in lower
                or "overloaded" in lower
            ):
                st.error(
                    "⚠️ Gemini is temporarily unavailable "
                    "after three attempts. Please wait a few "
                    "minutes and try again."
                )

            elif (
                "api key" in lower
                or "permission" in lower
                or "401" in message
                or "403" in message
            ):
                st.error(
                    "⚠️ The API key is invalid or does not "
                    "have permission. Check your Gemini API key."
                )

            elif "404" in message or "not found" in lower:
                st.error(
                    "⚠️ The selected model is unavailable "
                    "for your API key. Check your model access."
                )

            else:
                st.error(
                    "⚠️ Story generation failed. Check your "
                    "API key, model access and package versions."
                )

                with st.expander("View error details"):
                    st.code(message)


# ==========================================
# 9. DISPLAY GENERATED COMIC STORY
# ==========================================

if st.session_state["comic_story"]:

    story = st.session_state["comic_story"]

    st.divider()
    st.header("📖 Your Comic Story")

    # Separate the five panels.
    parts = re.split(
        r"(?=^\s*Panel\s+[1-5]\s*$)",
        story,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    panels = [
        part.strip()
        for part in parts
        if part.strip()
    ]

    for index, panel in enumerate(panels, start=1):

        st.markdown("---")

        lines = panel.splitlines()

        heading = (
            lines[0].strip()
            if lines
            else f"Panel {index}"
        )

        content = (
            "\n".join(lines[1:]).strip()
            if len(lines) > 1
            else ""
        )

        st.subheader(f"🎬 {heading}")

        if content:

            # Format the panel headings.
            content = re.sub(
                r"(?im)^\s*1\.\s*Scene\s*:?",
                "🎬 **Scene:**",
                content
            )

            content = re.sub(
                r"(?im)^\s*2\.\s*Character action\s*:?",
                "🎭 **Character Action:**",
                content
            )

            content = re.sub(
                r"(?im)^\s*3\.\s*Dialogue\s*:?",
                "💬 **Dialogue:**",
                content
            )

            content = re.sub(
                r"(?im)^\s*Scene\s*:",
                "🎬 **Scene:**",
                content
            )

            content = re.sub(
                r"(?im)^\s*Character action\s*:",
                "🎭 **Character Action:**",
                content
            )

            content = re.sub(
                r"(?im)^\s*Dialogue\s*:",
                "💬 **Dialogue:**",
                content
            )

            st.markdown(content)


    # ==========================================
    # 10. DOWNLOAD STORY
    # ==========================================

    st.download_button(
        "📥 Download Your Comic Story",
        data=story,
        file_name="Comic_Story.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ==========================================
# END OF COMIC STORY APPLICATION
# ==========================================
