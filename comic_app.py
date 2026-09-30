import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import html
import re

# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

st.set_page_config(
    page_title="ComicCraft",
    page_icon="🎨",
    layout="wide"
)

# =========================================================
# GEMINI API
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is not configured.")
    st.stop()

client = genai.Client(api_key=api_key)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 48px;
    font-weight: 800;
}

.subtitle {
    font-size: 20px;
    margin-bottom: 25px;
}

.panel-card {
    border: 2px solid #555;
    border-radius: 20px;
    padding: 28px;
    margin-top: 25px;
    margin-bottom: 30px;
    background: rgba(255,255,255,0.02);
}

.panel-title {
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 22px;
}

.section-title {
    font-size: 19px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 8px;
}

.dialogue-box {
    border-left: 6px solid #8b5cf6;
    padding: 15px 18px;
    margin-top: 8px;
    border-radius: 8px;
    background: rgba(139,92,246,0.08);
    font-size: 17px;
}

.image-prompt-box {
    border-left: 6px solid #06b6d4;
    padding: 15px 18px;
    margin-top: 8px;
    border-radius: 8px;
    background: rgba(6,182,212,0.08);
    font-size: 16px;
}

.story-box {
    border-radius: 15px;
    padding: 20px;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🎨 About ComicCraft")

    st.write(
        "ComicCraft uses Gemini AI to transform "
        "your story idea into a connected 5-panel comic story."
    )

    st.divider()

    st.subheader("✨ Features")

    st.write("📖 AI Story Generation")
    st.write("🖼️ AI Image Prompts")
    st.write("💬 Character Dialogues")
    st.write("🎭 Character Consistency")
    st.write("🔗 Story Continuity")
    st.write("📥 Story Download")

    st.divider()

    st.info(
        "💡 The free version generates the complete comic story "
        "and detailed image prompts for every panel."
    )

# =========================================================
# MAIN TITLE
# =========================================================

st.markdown(
    '<div class="main-title">🎨 ComicCraft</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Create your own AI comic story!</div>',
    unsafe_allow_html=True
)

st.write(
    "✨ Turn your imagination into a connected 5-panel comic story with AI!"
)

# =========================================================
# STORY INPUT
# =========================================================

story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    placeholder=(
        "Example: A college student builds an AI robot "
        "for a project, but the robot accidentally causes "
        "a funny problem during the college exhibition."
    ),
    height=160
)

st.info(
    "🎭 Characters stay consistent across all 5 panels, "
    "and every panel continues the previous scene."
)

# =========================================================
# BUTTONS
# =========================================================

col1, col2 = st.columns([1, 1])

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

# =========================================================
# CLEAR
# =========================================================

if clear_button:

    st.session_state.pop("comic_story", None)
    st.session_state.pop("story_title", None)

    st.rerun()

# =========================================================
# GENERATE COMIC
# =========================================================

if generate_button:

    if not story_idea.strip():

        st.warning(
            "💡 Please enter a comic story idea first."
        )

        st.stop()

    # -----------------------------------------------------
    # IMPORTANT GEMINI PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are a professional comic-book writer and visual storyteller.

Create ONE COMPLETE and CONTINUOUS 5-PANEL COMIC STORY
based on this user's idea:

"{story_idea}"

=========================================================
MAIN REQUIREMENT
=========================================================

This must feel like ONE real comic story.

Panel 1 starts the story.

Panel 2 MUST directly continue Panel 1.

Panel 3 MUST directly continue Panel 2.

Panel 4 MUST directly continue Panel 3.

Panel 5 MUST directly continue Panel 4 and finish the story.

Do NOT create five unrelated scenes.

=========================================================
CHARACTER CONSISTENCY
=========================================================

Create 1 to 3 main characters.

Introduce their appearance in Panel 1.

Keep the SAME characters throughout all five panels.

Keep consistent:

- Name
- Age
- Hair
- Face
- Clothing
- Colors
- Personality
- Important objects

Do not randomly change their clothes or appearance.

=========================================================
STORY STRUCTURE
=========================================================

Panel 1:
Introduce the characters, location and situation.

Panel 2:
A problem or unexpected event happens.

Panel 3:
The characters react and try to solve the problem.

Panel 4:
The main solution or important action happens.

Panel 5:
Show the result and give the story a satisfying ending.
The ending can be funny, emotional, inspiring or surprising.

=========================================================
VERY IMPORTANT PANEL MATCHING
=========================================================

For EACH panel:

The Scene must describe what is happening.

The Character Action must describe what the characters
are physically doing in that exact scene.

The Dialogue must be something the characters would naturally
say during that exact moment.

The Image Prompt must visually show EXACTLY the same moment.

Do NOT create an image prompt that shows a different event.

Do NOT introduce objects or characters in the image prompt
that are not part of the scene.

=========================================================
IMAGE PROMPT REQUIREMENTS
=========================================================

Every Image Prompt must include:

- Same character appearance
- Same clothing
- Character position
- Character action
- Facial expression
- Location
- Important objects
- Background
- Camera angle
- Lighting
- Comic-book art style

The image prompt must match the Scene,
Character Action and Dialogue.

=========================================================
EXAMPLE OF CORRECT CONTINUITY
=========================================================

Panel 1:

Scene:
Leo is building a small robot in his college room.

Character Action:
Leo connects a battery to the robot while sitting at his desk.

Dialogue:
Leo: "Come on, Bot-C. Work this time!"

Image Prompt:
Comic-book panel showing Leo with messy brown hair,
green T-shirt and blue jeans sitting at his college desk,
connecting a battery to the same small white robot.
The robot is on the desk. College room in the background.
Leo looks focused. Bright comic-book lighting.

Panel 2:

Scene:
The robot suddenly turns on after Leo connects the battery.

Character Action:
The robot's blue eyes begin glowing while Leo jumps back
from the desk in surprise.

Dialogue:
Leo: "Whoa! You actually turned on!"

Image Prompt:
Comic-book panel showing the SAME Leo wearing the SAME
green T-shirt and blue jeans in the SAME college room.
The SAME small white robot is on the SAME desk with glowing
blue LED eyes. Leo is stepping backward with a surprised face.
Same desk and background. Dynamic comic-book style.

Notice that Panel 2 continues directly from Panel 1.

=========================================================
OUTPUT FORMAT
=========================================================

Return EXACTLY this format:

TITLE:
[short interesting comic title]

CHARACTERS:
[character 1 description]
[character 2 description if needed]

Panel 1
Scene:
[scene]

Character Action:
[action]

Dialogue:
[dialogue]

Image Prompt:
[detailed matching image prompt]

Panel 2
Scene:
[scene]

Character Action:
[action]

Dialogue:
[dialogue]

Image Prompt:
[detailed matching image prompt]

Panel 3
Scene:
[scene]

Character Action:
[action]

Dialogue:
[dialogue]

Image Prompt:
[detailed matching image prompt]

Panel 4
Scene:
[scene]

Character Action:
[action]

Dialogue:
[dialogue]

Image Prompt:
[detailed matching image prompt]

Panel 5
Scene:
[scene]

Character Action:
[action]

Dialogue:
[dialogue]

Image Prompt:
[detailed matching image prompt]

=========================================================
STYLE
=========================================================

Make the story:

- Interesting
- Easy to understand
- Visual
- Natural
- Suitable for a college project
- Creative
- Funny, emotional or inspiring when appropriate

Keep dialogue short.

Do not add explanations outside the requested format.
"""

    # =====================================================
    # CALL GEMINI
    # =====================================================

    with st.spinner("✨ Creating your connected comic story..."):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            comic_story = response.text

        except Exception as e:

            error_message = str(e)

            if "429" in error_message:

                st.error(
                    "⚠️ Gemini API quota has been reached. "
                    "Please wait and try again."
                )

            elif "403" in error_message:

                st.error(
                    "⚠️ Gemini API key does not have permission "
                    "to use this model."
                )

            elif "404" in error_message:

                st.error(
                    "⚠️ Gemini model was not found. "
                    "Please check the model name."
                )

            else:

                st.error("⚠️ Gemini API Error:")
                st.code(error_message)

            st.stop()

    # =====================================================
    # SAVE RESULT
    # =====================================================

    st.session_state["comic_story"] = comic_story

# =========================================================
# DISPLAY COMIC
# =========================================================

if "comic_story" in st.session_state:

    comic_story = st.session_state["comic_story"]

    st.divider()

    st.success(
        "🎉 Your connected 5-panel comic story is ready!"
    )

    # =====================================================
    # EXTRACT TITLE
    # =====================================================

    title_match = re.search(
        r"TITLE:\s*(.*)",
        comic_story,
        re.IGNORECASE
    )

    if title_match:

        title = title_match.group(1).strip()

    else:

        title = "My AI Comic Story"

    st.markdown(
        f"## 📖 {html.escape(title)}"
    )

    st.info(
        "✨ Each panel continues the previous panel, "
        "with matching scene, action, dialogue and image prompt."
    )

    # =====================================================
    # CHARACTER INFORMATION
    # =====================================================

    character_match = re.search(
        r"CHARACTERS:\s*(.*?)(?=\nPanel 1)",
        comic_story,
        re.IGNORECASE | re.DOTALL
    )

    if character_match:

        characters = character_match.group(1).strip()

        if characters:

            st.markdown("### 🎭 Characters")

            st.markdown(
                f"""
<div class="story-box">
{html.escape(characters).replace(chr(10), "<br>")}
</div>
""",
                unsafe_allow_html=True
            )

    # =====================================================
    # SPLIT PANELS
    # =====================================================

    panel_matches = re.findall(
        r"Panel\s+([1-5])\s*(.*?)(?=\nPanel\s+[1-5]|\Z)",
        comic_story,
        re.IGNORECASE | re.DOTALL
    )

    st.markdown("## 🖼️ Comic Panels")

    # =====================================================
    # DISPLAY EACH PANEL
    # =====================================================

    for panel_number, panel_content in panel_matches:

        scene = ""
        action = ""
        dialogue = ""
        image_prompt = ""

        # -----------------------------------------------
        # Scene
        # -----------------------------------------------

        scene_match = re.search(
            r"Scene:\s*(.*?)(?=\nCharacter Action:|\Z)",
            panel_content,
            re.IGNORECASE | re.DOTALL
        )

        if scene_match:

            scene = scene_match.group(1).strip()

        # -----------------------------------------------
        # Character Action
        # -----------------------------------------------

        action_match = re.search(
            r"Character Action:\s*(.*?)(?=\nDialogue:|\Z)",
            panel_content,
            re.IGNORECASE | re.DOTALL
        )

        if action_match:

            action = action_match.group(1).strip()

        # -----------------------------------------------
        # Dialogue
        # -----------------------------------------------

        dialogue_match = re.search(
            r"Dialogue:\s*(.*?)(?=\nImage Prompt:|\Z)",
            panel_content,
            re.IGNORECASE | re.DOTALL
        )

        if dialogue_match:

            dialogue = dialogue_match.group(1).strip()

        # -----------------------------------------------
        # Image Prompt
        # -----------------------------------------------

        image_match = re.search(
            r"Image Prompt:\s*(.*)",
            panel_content,
            re.IGNORECASE | re.DOTALL
        )

        if image_match:

            image_prompt = image_match.group(1).strip()

        # -----------------------------------------------
        # Escape HTML
        # -----------------------------------------------

        scene_html = html.escape(scene)
        action_html = html.escape(action)
        dialogue_html = html.escape(dialogue)
        image_prompt_html = html.escape(image_prompt)

        # -----------------------------------------------
        # PANEL CARD
        # -----------------------------------------------

        st.markdown(
            f"""
<div class="panel-card">

    <div class="panel-title">
        🎬 Panel {html.escape(panel_number)}
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

# =========================================================
# DOWNLOAD
# =========================================================

if "comic_story" in st.session_state:

    st.divider()

    st.markdown("## 📥 Download")

    st.download_button(
        label="📥 Download Comic Story",
        data=st.session_state["comic_story"],
        file_name="ComicCraft_Story.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.success(
        "🎨 Your ComicCraft project is complete!"
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎨 ComicCraft • AI-Powered Connected 5-Panel Comic Generator"
)
