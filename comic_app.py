
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# ---------------------------------------
# Comic Story - AI Comic Story Creator
# ---------------------------------------

load_dotenv()

st.set_page_config(
    page_title="Comic Story",
    page_icon="📖",
    layout="centered"
)

# ---------------- PAGE DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f0ff, #e6f7ff);
}
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #673ab7;
}
.subtitle {
    text-align: center;
    font-size: 18px;
    color: #444;
}
.panel {
    background-color: white;
    border: 2px solid #b39ddb;
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📖 Comic Story</div>',
            unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Create your own AI comic story!</div>',
    unsafe_allow_html=True
)

st.write("")
st.info("✨ Turn your imagination into a 5-panel comic story with AI.")

# ---------------- API KEY ----------------

api_key = None

try:
    api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key is missing.")
    st.info(
        "Add GEMINI_API_KEY to Streamlit Secrets "
        "or your local .env file."
    )
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------- USER INPUT ----------------

st.subheader("✨ Create Your Story")

story_idea = st.text_area(
    "Enter your comic story idea",
    placeholder=(
        "Example: A young girl discovers a magical forest "
        "and helps a lost baby dragon."
    ),
    height=120
)

genre = st.selectbox(
    "Choose a story genre",
    [
        "Adventure",
        "Fantasy",
        "Comedy",
        "Friendship",
        "Mystery",
        "Science Fiction",
        "Educational"
    ]
)

character_name = st.text_input(
    "Main character name (optional)",
    placeholder="Example: Maya"
)

create_button = st.button(
    "🚀 Generate Comic Story",
    use_container_width=True
)

# ---------------- GENERATE STORY ----------------

if create_button:

    if not story_idea.strip():
        st.warning("Please enter your story idea first.")

    else:
        prompt = f"""
You are a creative comic story writer.

Create a complete comic story using exactly five panels.

USER STORY IDEA:
{story_idea}

GENRE:
{genre}

MAIN CHARACTER NAME:
{character_name.strip() or "Choose a suitable name"}

IMPORTANT REQUIREMENTS:

1. Create exactly five panels.
2. Keep all characters visually and personally consistent.
3. Give the main character the same name, appearance,
   clothing, age range, and personality in every panel.
4. Do not change a character's appearance between panels.
5. Continue the same story from panel 1 to panel 5.
6. Include scene descriptions, actions, and dialogue.
7. Make each panel interesting and easy to understand.
8. Give the story a satisfying ending.
9. Use simple English.
10. Do not skip any panel.

Use this exact format:

STORY TITLE:
Write the title.

CHARACTER GUIDE:
Describe each character's name, appearance, clothing,
and personality. Keep these details unchanged.

PANEL 1:
Scene:
Action:
Dialogue:

PANEL 2:
Scene:
Action:
Dialogue:

PANEL 3:
Scene:
Action:
Dialogue:

PANEL 4:
Scene:
Action:
Dialogue:

PANEL 5:
Scene:
Action:
Dialogue:
"""

        # Change the model if it is unavailable
        # for your API key or project.
        model_name = "gemini-2.5-flash"

        try:
            with st.spinner("✨ Creating your five-panel comic story..."):

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                story = response.text

                if not story:
                    st.error(
                        "Gemini returned an empty response. "
                        "Please try again."
                    )
                else:
                    st.session_state["comic_story"] = story
                    st.session_state["comic_idea"] = story_idea

        except errors.ClientError as e:
            message = str(e)
            lowered = message.lower()

            if "429" in message or "quota" in lowered or "rate limit" in lowered:
                st.error(
                    "⚠️ Gemini API quota or rate limit reached."
                )
                st.write(
                    "Check your model quota and usage in Google AI Studio. "
                    "Wait for the limit to reset or use an available model."
                )

            elif "401" in message or "403" in message:
                st.error(
                    "🔑 API authentication failed. Check your API key "
                    "and project permissions."
                )

            elif "404" in message:
                st.error(
                    "The selected Gemini model is unavailable. "
                    "Check the models supported by your API key."
                )

            else:
                st.error("Gemini API request failed.")
                st.caption(message[:500])

        except Exception as e:
            st.error("Something went wrong while generating your story.")
            st.caption(str(e)[:500])

# ---------------- DISPLAY STORY ----------------

if st.session_state.get("comic_story"):

    st.divider()
    st.subheader("🎨 Your Generated Comic Story")

    story = st.session_state["comic_story"]

    st.markdown(story)

    st.download_button(
        label="⬇️ Download Comic Story",
        data=story,
        file_name="comic_story.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.success("Your five-panel comic story is ready!")

# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    "<p style='text-align:center;color:#673ab7;'>"
    "Made with ❤️ using Python, Streamlit and Gemini AI"
    "</p>",
    unsafe_allow_html=True
)
