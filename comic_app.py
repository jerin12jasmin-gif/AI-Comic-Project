import base64
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

# Load environment variables
load_dotenv()

# Connect to Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --------------------------------------------------
# Generate comic panel image with retry logic
# --------------------------------------------------
def generate_panel_image(image_prompt, panel_number):
  for attempt in range(3):
    try:
      response = client.models.generate_content(
          model="gemini-2.0-flash",
          contents=image_prompt,
          config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
      )

      for part in response.parts:
        if part.inline_data:
          image = part.as_image()
          image_path = f"comic_panel_{panel_number}.png"
          image.save(image_path)
          return image_path

      return None

    except Exception as e:
      if "503" in str(e) and attempt < 2:
        time.sleep(2)  # Wait 2 seconds before retrying
        continue
      if attempt == 2:
        st.error(f"Image generation error for Panel {panel_number}: {e}")
      return None
  return None


# --------------------------------------------------
# Page settings
# --------------------------------------------------
st.set_page_config(page_title="ComicCraft", page_icon="🎨")


# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🎨 ComicCraft")
st.write("Create your own AI comic story!")
st.caption("✨ Turn your imagination into a 5-panel comic story with AI!")


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
  st.header("🎨 About ComicCraft")
  st.write(
      "ComicCraft uses Gemini AI to transform your story idea into a 5-panel"
      " comic story."
  )
  st.divider()
  st.subheader("✨ Features")
  st.write("📖 AI Story Generation")
  st.write("🖼️ AI Comic Images")
  st.write("💬 Character Dialogues")
  st.write("🎭 Character Consistency")
  st.write("📥 Story Download")


st.divider()


# --------------------------------------------------
# Story input
# --------------------------------------------------
story_idea = st.text_area(
    "💡 Enter your comic story idea:",
    placeholder="Example: A village girl discovers a magical book...",
)

st.info("🎭 Characters will stay consistent across all 5 panels.")


# --------------------------------------------------
# Clear button
# --------------------------------------------------
if st.button("🗑️ Clear"):
  st.rerun()


# --------------------------------------------------
# Generate Comic
# --------------------------------------------------
if st.button("🚀 Generate My Comic"):
  if story_idea.strip():

    # ------------------------------------------
    # Generate Story with Retry Logic for 503
    # ------------------------------------------
    response = None
    with st.spinner("Creating your comic story..."):
      prompt = f"""
Create a short comic story based on this idea:

{story_idea}

Give the story in exactly 5 comic panels.

Use these exact headings:

Panel 1
Panel 2
Panel 3
Panel 4
Panel 5

For each panel, provide:

1. Scene
2. Character action
3. Dialogue
4. Image prompt

Make the image prompt detailed enough for an AI image generator.

The image prompt must include:

- Character appearance
- Character clothing
- Background
- Character pose and action
- Facial expression
- Lighting
- Comic art style

Keep the same characters consistent across all 5 panels.

For each character, maintain the same:

- Name
- Age
- Appearance
- Hairstyle
- Clothing
- Personality

Do not change the character's appearance or clothing
between panels.
"""

      for attempt in range(3):
        try:
          response = client.models.generate_content(
              model="gemini-1.5-flash", contents=prompt
          )
          break
        except Exception as e:
          error_message = str(e)
          if "503" in error_message and attempt < 2:
            time.sleep(3)  # Wait before retry on busy servers
            continue
          elif "503" in error_message:
            st.error(
                "⚠️ Gemini is temporarily busy. Please wait a moment and try"
                " again."
            )
            st.stop()
          elif "429" in error_message:
            st.error("⚠️ Gemini API quota has been reached. Try again later.")
            st.stop()
          elif "404" in error_message:
            st.error("⚠️ Gemini model was not found.")
            st.stop()
          else:
            st.error(f"⚠️ Gemini Error: {error_message}")
            st.stop()

    if not response:
      st.error("Failed to generate story after multiple attempts.")
      st.stop()

    # ------------------------------------------
    # Story ready
    # ------------------------------------------
    st.success("🎨 Your ComicCraft story is ready!")
    st.markdown("## 📖 Your Comic Story")
    st.markdown("### 🖼️ Comic Panels")
    st.info("✨ ComicCraft will now create an image for each panel.")

    # ------------------------------------------
    # Split panels
    # ------------------------------------------
    panels = response.text.split("Panel ")

    # ------------------------------------------
    # Display each panel
    # ------------------------------------------
    for panel_number, panel in enumerate(panels[1:], start=1):
      st.markdown("---")

      # --------------------------------------
      # Get Image Prompt
      # --------------------------------------
      image_prompt = ""
      if "Image Prompt:" in panel:
        image_prompt = panel.split("Image Prompt:", 1)[1].strip()
      elif "Image prompt:" in panel:
        image_prompt = panel.split("Image prompt:", 1)[1].strip()
      elif "4. Image prompt" in panel:
        image_prompt = panel.split("4. Image prompt", 1)[1].strip()
      elif "4. Image Prompt" in panel:
        image_prompt = panel.split("4. Image Prompt", 1)[1].strip()

      panel_image = None
      if image_prompt:
        with st.spinner(f"🎨 Generating Panel {panel_number} image..."):
          panel_image = generate_panel_image(image_prompt, panel_number)

      # --------------------------------------
      # Display Image
      # --------------------------------------
      if panel_image:
        st.image(
            panel_image,
            caption=f"🖼️ Comic Panel {panel_number}",
            use_container_width=True,
        )

      # --------------------------------------
      # Panel box
      # --------------------------------------
      lines = panel.split("\n", 1)

      st.markdown(
          f"""
                <div style="
                    padding: 20px;
                    border-radius: 15px;
                    border: 2px solid #dddddd;
                    margin-bottom: 20px;
                ">
                <h3>📖 Panel {lines[0]}</h3>
                """,
          unsafe_allow_html=True,
      )

      if len(lines) > 1:
        content = lines[1]
        content = (
            content.replace("1. Scene", "🎬 Scene")
            .replace("Scene:", "🎬 Scene:")
            .replace("2. Character action", "🎭 Character Action")
            .replace("Character action:", "🎭 Character Action:")
            .replace("3. Dialogue", "💬 Dialogue")
            .replace("Dialogue:", "💬 Dialogue:")
            .replace("4. Image prompt", "🖼️ Image Prompt")
            .replace("Image prompt:", "🖼️ Image Prompt:")
        )
        st.markdown(content)

      st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # Save & Download story
    # ------------------------------------------
    with open("comic_story.txt", "w", encoding="utf-8") as file:
      file.write(response.text)

    st.download_button(
        "📥 Download Your Comic Story",
        response.text,
        file_name="ComicCraft_Story.txt",
    )

  else:
    st.warning("💡 Please enter a story idea to create your comic!")
