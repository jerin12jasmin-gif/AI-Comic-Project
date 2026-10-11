import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------
# 1. PAGE SETTINGS
# ---------------------------------------

st.set_page_config(
    page_title="ComicCraft",
    page_icon="🎨",
    layout="wide"
)

load_dotenv()

st.title("🎨 ComicCraft")
st.subheader("Create Your Own AI Comic Story")
st.write("✨ Turn your imagination into a five-panel comic!")

# ---------------------------------------
# 2. API CONFIGURATION
# ---------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error(
        "Gemini API key is missing. "
        "Add GEMINI_API_KEY to your .env file."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)

# ---------------------------------------
# 3. SESSION STATE
# ---------------------------------------

if "comic_story" not in st.session_state:
    st.session_state.comic_story = ""

if "comic_idea" not in st.session_state:
    st.session_state.comic_idea = ""

if "comic_images" not in st.session_state:
    st.session_state.comic_images = {}

# ---------------------------------------
# 4. SIDEBAR
# ---------------------------------------

with st.sidebar:
    st.header("🎨 About ComicCraft")
    st.write(
        "Create an original story and turn it "
        "into a five-panel comic."
    )

    st.divider()
    st.subheader("✨ Features")
    st.write("📖 AI Story Generation")
    st.write("🖼️ Comic Panel Images")
    st.write("💬 Character Dialogues")
    st.write("🎭 Character Consistency")
    st.write("📥 Download Your Story")

# ---------------------------------------
# 5. GENERATE STORY
# ---------------------------------------

def generate_story(idea):
    prompt = f"""
Create an original comic story using this idea:

{idea}

Create exactly five panels.

Use this format:

Panel 1
Scene: ...
Character Action: ...
Dialogue: ...
Image Prompt: ...

Repeat for Panel 2, Panel 3, Panel 4 and Panel 5.

Rules:
- Write a complete story with a beginning and ending.
- Keep the same character names and appearances.
- Keep clothing and hairstyles consistent.
- Describe the background, poses, expressions and lighting.
- Make each image prompt suitable for a comic illustration.
- Do not add any extra panels.
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    if not response.text:
        raise ValueError("The AI returned an empty story.")

    return response.text


# ---------------------------------------
# 6. GENERATE ONE PANEL IMAGE
# ---------------------------------------

def generate_panel_image(image_prompt, panel_number):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=(
            "Create one complete colourful comic-book "
            "illustration. Do not create a collage or "
            "multiple panels. Keep the same character "
            "appearance described in this prompt.\n\n"
            + image_prompt
        ),
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"]
        )
    )

    for part in response.parts or []:
        if part.inline_data:
            image = part.as_image()
            image_path = f"comic_panel_{panel_number}.png"
            image.save(image_path)
            return image_path

    raise ValueError("The model returned no image.")


# ---------------------------------------
# 7. EXTRACT PANELS
# ---------------------------------------

def extract_panels(story):
    pattern = r"(?im)^\s*Panel\s+([1-5])\s*:?\s*$"
    matches = list(re.finditer(pattern, story))
    panels = []

    for i, match in enumerate(matches):
        start = match.end()
        end = (
            matches[i + 1].start()
            if i + 1 < len(matches)
            else len(story)
        )

        panels.append({
            "number": int(match.group(1)),
            "content": story[start:end].strip()
        })

    return panels


def get_image_prompt(content):
    match = re.search(
        r"(?im)^\s*(?:4\.\s*)?Image\s*Prompt\s*:\s*",
        content
    )

    if match:
        return content[match.end():].strip()

    return content


# ---------------------------------------
# 8. STORY INPUT
# ---------------------------------------

story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    value=st.session_state.comic_idea,
    placeholder=(
        "Example: A girl discovers a magical "
        "book in her college library..."
    ),
    height=120
)

col1, col2 = st.columns(2)

with col1:
    generate_button = st.button(
        "🚀 Generate My Comic",
        type="primary",
        use_container_width=True
    )

with col2:
    clear_button = st.button(
        "🗑️ Clear",
        use_container_width=True
    )

if clear_button:
    st.session_state.comic_story = ""
    st.session_state.comic_idea = ""
    st.session_state.comic_images = {}
    st.rerun()


# ---------------------------------------
# 9. CREATE THE STORY
# ---------------------------------------

if generate_button:
    if not story_idea.strip():
        st.warning("Please enter a story idea first.")

    else:
        try:
            with st.spinner("📖 Creating your comic story..."):
                story = generate_story(story_idea.strip())

            st.session_state.comic_story = story
            st.session_state.comic_idea = story_idea.strip()
            st.session_state.comic_images = {}

            st.success("Your comic story is ready!")

        except Exception as e:
            error = str(e)

            if "429" in error or "RESOURCE_EXHAUSTED" in error:
                st.error(
                    "Gemini API quota exceeded. Check your "
                    "API quota and try again after it resets."
                )
            elif "404" in error or "NOT_FOUND" in error:
                st.error(
                    "The text model was not found. Check "
                    "the available models for your API key."
                )
            elif "403" in error or "PERMISSION_DENIED" in error:
                st.error(
                    "API access denied. Check your API key "
                    "and project permissions."
                )
            else:
                st.error(f"Story generation failed: {error}")


# ---------------------------------------
# 10. DISPLAY STORY
# ---------------------------------------

if st.session_state.comic_story:
    story = st.session_state.comic_story
    panels = extract_panels(story)

    st.divider()
    st.header("📖 Your Comic Story")
    st.markdown(story)

    st.download_button(
        "📥 Download Your Comic Story",
        data=story,
        file_name="ComicCraft_Story.txt",
        mime="text/plain"
    )

    st.divider()
    st.header("🖼️ Your Five Comic Panels")

    if len(panels) != 5:
        st.warning(
            f"The AI returned {len(panels)} numbered panels. "
            "You can still read and download the story."
        )

    # -----------------------------------
    # 11. GENERATE IMAGES ONLY ONCE
    # -----------------------------------

    if st.button("🎨 Generate Panel Images", type="primary"):

        if not panels:
            st.error("No numbered panels were found.")

        else:
            for panel in panels:
                number = panel["number"]
                content = panel["content"]

                st.subheader(f"🖼️ Panel {number}")

                # Reuse an image if already generated
                if number in st.session_state.comic_images:
                    st.image(
                        st.session_state.comic_images[number],
                        caption=f"Comic Panel {number}",
                        use_container_width=True
                    )
                    st.markdown(content)
                    continue

                image_prompt = get_image_prompt(content)

                try:
                    with st.spinner(
                        f"Generating Panel {number}..."
                    ):
                        image_path = generate_panel_image(
                            image_prompt,
                            number
                        )

                    # Save result in session state
                    st.session_state.comic_images[number] = image_path

                    st.image(
                        image_path,
                        caption=f"Comic Panel {number}",
                        use_container_width=True
                    )

                    with open(image_path, "rb") as image_file:
                        st.download_button(
                            f"📥 Download Panel {number}",
                            data=image_file.read(),
                            file_name=f"ComicCraft_Panel_{number}.png",
                            mime="image/png",
                            key=f"download_panel_{number}"
                        )

                    st.markdown(content)

                except Exception as e:
                    error = str(e)

                    if (
                        "429" in error
                        or "RESOURCE_EXHAUSTED" in error
                    ):
                        st.error(
                            "Image API quota exceeded. "
                            "The remaining images were not requested. "
                            "Check your quota before trying again."
                        )
                        break

                    elif "404" in error or "NOT_FOUND" in error:
                        st.error(
                            "Image model not found. Check the "
                            "supported image-generation models."
                        )
                        break

                    elif (
                        "403" in error
                        or "PERMISSION_DENIED" in error
                    ):
                        st.error(
                            "Image-generation access denied. "
                            "Check your API key and permissions."
                        )
                        break

                    else:
                        st.error(
                            f"Panel {number} failed: {error}"
                        )
                        break

                st.divider()

# ---------------------------------------
# 12. FOOTER
# ---------------------------------------

st.divider()
st.caption("🎨 ComicCraft — Bring Your Imagination to Life!")
