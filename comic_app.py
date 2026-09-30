import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import html

# Load environment variables
load_dotenv()

# Page settings
st.set_page_config(
    page_title="ComicCraft",
    page_icon="🎨",
    layout="wide"
)

# Gemini API
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

# Custom CSS
st.markdown("""
<style>
.panel-card {
    border: 2px solid #777;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 25px;
}

.panel-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 15px;
}

.section-title {
    font-size: 18px;
    font-weight: bold;
    margin-top: 15px;
}

.dialogue-box {
    border-left: 5px solid #7c4dff;
    padding: 12px;
    margin-top: 8px;
    border-radius: 8px;
}

.image-prompt-box {
    border-left: 5px solid #00a8cc;
    padding: 12px;
    margin-top: 8px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:

    st.header("🎨 About ComicCraft")

    st.write(
        "ComicCraft uses Gemini AI to transform "
        "your story idea into a 5-panel comic story."
    )

    st.divider()

    st.subheader("✨ Features")

    st.write("📖 AI Story Generation")
    st.write("🖼️ AI Image Prompts")
    st.write("💬 Character Dialogues")
    st.write("🎭 Character Consistency")
    st.write("📥 Story Download")

    st.divider()

    st.info(
        "💡 Free version: generates the comic story, "
        "dialogues and detailed image prompts."
    )

# Title
st.title("🎨 ComicCraft")

st.write("Create your own AI comic story!")

st.caption(
    "✨ Turn your imagination into a 5-panel comic story with AI!"
)

# Story input
story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    placeholder=(
        "Example: A college student creates an AI robot "
        "that helps save the college..."
    ),
    height=150
)

st.info(
    "🎭 Characters will stay consistent across all 5 panels."
)

# Clear button
if st.button("🗑️ Clear"):

    st.session_state.pop("comic_story", None)
    st.rerun()

# Generate button
if st.button("🚀 Generate My Comic", type="primary"):

    if not story_idea.strip():

        st.warning(
            "💡 Please enter a story idea to create your comic!"
        )
        st.stop()

    prompt = f"""
You are an expert comic-book story writer.

Create a short and interesting comic story based on:

{story_idea}

Create EXACTLY 5 comic panels.

Use this exact format:

Panel 1
Scene:
Character Action:
Dialogue:
Image Prompt:

Panel 2
Scene:
Character Action:
Dialogue:
Image Prompt:

Panel 3
Scene:
Character Action:
Dialogue:
Image Prompt:

Panel 4
Scene:
Character Action:
Dialogue:
Image Prompt:

Panel 5
Scene:
Character Action:
Dialogue:
Image Prompt:

CHARACTER CONSISTENCY:

Keep the same characters throughout all 5 panels.

For every character maintain:

- Name
- Age
- Appearance
- Hairstyle
- Clothing
- Personality

Do not change their appearance or clothing.

STORY:

Panel 1 = Introduction
Panel 2 = Problem
Panel 3 = Main action
Panel 4 = Solution
Panel 5 = Ending

DIALOGUE:

Keep dialogue short and natural.

IMAGE PROMPT:

Create a detailed image prompt for every panel.

Include:

- Character appearance
- Clothing
- Background
- Pose
- Action
- Facial expression
- Lighting
- Camera view
- Comic art style

Do not create anything outside the 5 panels.
"""

    # Generate story
    with st.spinner("✨ Creating your AI comic story..."):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            comic_story = response.text

        except Exception as e:

            error_message = str(e)

            if "429" in error_message:

                st.error(
                    "⚠️ Gemini API quota has been reached. "
                    "Please try again later."
                )

            elif "503" in error_message:

                st.error(
                    "⚠️ Gemini is temporarily busy. "
                    "Please try again."
                )

            else:

                st.error("⚠️ Gemini Error:")
                st.code(error_message)

            st.stop()

    st.session_state["comic_story"] = comic_story


# Display result
if "comic_story" in st.session_state:

    comic_story = st.session_state["comic_story"]

    st.success("🎉 Your ComicCraft story is ready!")

    st.markdown("## 📖 Your AI Comic Story")

    st.info(
        "✨ Your 5-panel comic has been created with AI. "
        "Each panel contains a scene, action, dialogue "
        "and image prompt."
    )

    st.markdown("## 🖼️ Comic Panels")

    panels = comic_story.split("Panel ")

    for index, panel in enumerate(panels[1:6], start=1):

        panel = panel.strip()

        lines = panel.split("\n", 1)

        if len(lines) > 1:
            content = lines[1]
        else:
            content = panel

        scene = ""
        action = ""
        dialogue = ""
        image_prompt = ""

        current_section = ""

        for line in content.splitlines():

            text = line.strip()

            lower = text.lower()

            if lower.startswith("scene:"):

                current_section = "scene"
                scene = text.split(":", 1)[1].strip()

            elif lower.startswith("character action:"):

                current_section = "action"
                action = text.split(":", 1)[1].strip()

            elif lower.startswith("dialogue:"):

                current_section = "dialogue"
                dialogue = text.split(":", 1)[1].strip()

            elif lower.startswith("image prompt:"):

                current_section = "image"
                image_prompt = text.split(":", 1)[1].strip()

            elif text:

                if current_section == "scene":
                    scene += " " + text

                elif current_section == "action":
                    action += " " + text

                elif current_section == "dialogue":
                    dialogue += " " + text

                elif current_section == "image":
                    image_prompt += " " + text

        scene = html.escape(scene)
        action = html.escape(action)
        dialogue = html.escape(dialogue)
        image_prompt = html.escape(image_prompt)

        st.markdown(
            f"""
<div class="panel-card">

<div class="panel-title">
🎬 Panel {index}
</div>

<div class="section-title">
🎬 Scene
</div>

<div>
{scene}
</div>

<div class="section-title">
🎭 Character Action
</div>

<div>
{action}
</div>

<div class="section-title">
💬 Dialogue
</div>

<div class="dialogue-box">
{dialogue}
</div>

<div class="section-title">
🖼️ AI Image Prompt
</div>

<div class="image-prompt-box">
{image_prompt}
</div>

</div>
""",
            unsafe_allow_html=True
        )

    # Download
    st.divider()

    st.markdown("## 📥 Download")

    st.download_button(
        "📥 Download Your Comic Story",
        comic_story,
        file_name="ComicCraft_Story.txt",
        mime="text/plain"
    )

    st.success(
        "🎨 ComicCraft completed successfully!"
    )

st.divider()

st.caption(
    "🎨 ComicCraft • AI-Powered 5-Panel Comic Story Generator"
)
