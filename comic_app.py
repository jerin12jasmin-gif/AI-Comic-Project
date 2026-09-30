import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import html

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

# --------------------------------------------------
# Page settings
# --------------------------------------------------

st.set_page_config(
    page_title="ComicCraft",
    page_icon="🎨",
    layout="wide"
)

# --------------------------------------------------
# Connect to Gemini
# --------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY is not configured. "
        "Please add your Gemini API key."
    )
    st.stop()

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        margin-bottom: 5px;
    }

    .tagline {
        text-align: center;
        font-size: 16px;
        opacity: 0.75;
        margin-bottom: 30px;
    }

    .panel-card {
        border: 2px solid #777;
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 25px;
        background: rgba(255,255,255,0.04);
    }

    .panel-title {
        font-size: 27px;
        font-weight: 700;
        margin-bottom: 15px;
    }

    .section-title {
        font-size: 17px;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 5px;
    }

    .dialogue-box {
        border-left: 5px solid #7c4dff;
        padding: 12px 15px;
        margin-top: 8px;
        border-radius: 8px;
        background: rgba(124,77,255,0.10);
        font-style: italic;
    }

    .image-prompt-box {
        border-left: 5px solid #00a8cc;
        padding: 12px 15px;
        margin-top: 8px;
        border-radius: 8px;
        background: rgba(0,168,204,0.08);
        font-size: 14px;
    }

    .comic-number {
        font-size: 50px;
        text-align: center;
        margin-bottom: 5px;
    }

    .comic-label {
        text-align: center;
        font-weight: 700;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

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
        "💡 This free version generates the comic story, "
        "dialogues and detailed image prompts without "
        "using paid image-generation APIs."
    )


# --------------------------------------------------
# Title
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🎨 ComicCraft</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Create your own AI comic story!</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tagline">'
    '✨ Turn your imagination into a 5-panel comic story with AI!'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# Story input
# --------------------------------------------------

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


# --------------------------------------------------
# Clear button
# --------------------------------------------------

if st.button("🗑️ Clear"):

    st.session_state.pop("comic_story", None)
    st.rerun()


# --------------------------------------------------
# Generate Comic
# --------------------------------------------------

if st.button("🚀 Generate My Comic", type="primary"):

    if not story_idea.strip():

        st.warning(
            "💡 Please enter a story idea to create your comic!"
        )
        st.stop()

    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------

    prompt = f"""
You are an expert comic-book story writer.

Create a short and engaging comic story based on this idea:

{story_idea}

Create EXACTLY 5 comic panels.

Use this exact structure:

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

IMPORTANT CHARACTER CONSISTENCY:

Create a small group of main characters.

For every character maintain the same:

- Name
- Age
- Appearance
- Hairstyle
- Clothing
- Personality

Do not change their appearance or clothing between panels.

STORY REQUIREMENTS:

- Panel 1 should introduce the characters and situation.
- Panel 2 should introduce a problem or challenge.
- Panel 3 should show the main action.
- Panel 4 should show the solution or important turning point.
- Panel 5 should provide a satisfying ending.

DIALOGUE:

- Keep dialogue short and natural.
- Use quotation marks.
- Give dialogue to the relevant character.

IMAGE PROMPT:

For every panel, create a detailed prompt that could be
given to an AI image generator.

Each image prompt must describe:

- Character appearance
- Character clothing
- Background
- Character pose
- Character action
- Facial expression
- Lighting
- Camera/view
- Comic art style
- Consistent character appearance

Do not generate anything outside the 5 panels.
"""


    # --------------------------------------------------
    # Generate Story
    # --------------------------------------------------

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
                    "Please wait and try again."
                )

            elif "404" in error_message:

                st.error(
                    "⚠️ Gemini model was not found. "
                    "Please check the model name."
                )

            else:

                st.error("⚠️ Gemini Error:")
                st.code(error_message)

            st.stop()


    # --------------------------------------------------
    # Save result in session
    # --------------------------------------------------

    st.session_state["comic_story"] = comic_story


# --------------------------------------------------
# Display Comic
# --------------------------------------------------

if "comic_story" in st.session_state:

    comic_story = st.session_state["comic_story"]

    st.success("🎉 Your ComicCraft story is ready!")

    st.markdown("## 📖 Your AI Comic Story")

    st.markdown(
        """
        <div style="
            padding:15px;
            border-radius:12px;
            background:rgba(30,100,180,0.15);
            margin-bottom:25px;
        ">
        ✨ Your 5-panel comic has been created with AI.
        Each panel includes a scene, character action,
        dialogue and a detailed image prompt.
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # Split panels
    # --------------------------------------------------

    panels = comic_story.split("Panel ")

    valid_panels = []

    for panel in panels[1:]:

        panel = panel.strip()

        if panel:
            valid_panels.append(panel)


    # --------------------------------------------------
    # Comic Panels
    # --------------------------------------------------

    st.markdown("## 🖼️ Comic Panels")

    for index, panel in enumerate(valid_panels[:5], start=1):

        # ----------------------------------------------
        # Separate panel heading/content
        # ----------------------------------------------

        lines = panel.split("\n", 1)

        panel_number = str(index)

        if len(lines) > 1:
            content = lines[1]
        else:
            content = panel

        # ----------------------------------------------
        # Extract sections
        # ----------------------------------------------

        scene = ""
        action = ""
        dialogue = ""
        image_prompt = ""

        lines_content = content.splitlines()

        current_section = ""

        for line in lines_content:

            clean_line = line.strip()

            lower_line = clean_line.lower()

            if lower_line.startswith("scene:"):

                current_section = "scene"
                scene = clean_line.split(":", 1)[1].strip()

            elif lower_line.startswith("character action:"):

                current_section = "action"
                action = clean_line.split(":", 1)[1].strip()

            elif lower_line.startswith("dialogue:"):

                current_section = "dialogue"
                dialogue = clean_line.split(":", 1)[1].strip()

            elif lower_line.startswith("image prompt:"):

                current_section = "image_prompt"
                image_prompt = clean_line.split(":", 1)[1].strip()

            elif clean_line:

                if current_section == "scene":
                    scene += " " + clean_line

                elif current_section == "action":
                    action += " " + clean_line

                elif current_section == "dialogue":
                    dialogue += " " + clean_line

                elif current_section == "image_prompt":
                    image_prompt += " " + clean_line


        # ----------------------------------------------
        # Escape HTML
        # ----------------------------------------------

        scene_html = html.escape(scene)
        action_html = html.escape(action)
        dialogue_html = html.escape(dialogue)
        image_prompt_html = html.escape(image_prompt)


        # ----------------------------------------------
        # Display Panel
        # ----------------------------------------------

        st.markdown(
            f"""
            <div class="panel-card">

                <div class="comic-number">
                    🎬
                </div>

                <div class="comic-label">
                    PANEL {panel_number}
                </div>

                <div class="section-title">
                    🎬 Scene
                </div>

                <div>
                    {scene_html}
                </div>

                <div class="section-title">
                    🎭 Character Action
                </div>

                <div>
                    {action_html}
                </div>

                <div class="section-title">
                    💬 Dialogue
                </div>

                <div class="dialogue-box">
                    {dialogue_html}
                </div>

                <div class="section-title">
                    🖼️ AI Image Prompt
                </div>

                <div class="image-prompt-box">
                    {image_prompt_html}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------
    # Story download
    # --------------------------------------------------

    st.divider()

    st.markdown("## 📥 Download")

    st.download_button(
        label="📥 Download Your Comic Story",
        data=comic_story,
        file_name="ComicCraft_Story.txt",
        mime="text/plain"
    )

    st.success(
        "🎨 ComicCraft completed successfully!"
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "🎨 ComicCraft • AI-Powered 5-Panel Comic Story Generator"
)
