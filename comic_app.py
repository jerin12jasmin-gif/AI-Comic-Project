import base64
import io
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

# Load environment variables
load_dotenv()

# Connect to Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --------------------------------------------------
# Generate comic panel image using Imagen 3
# --------------------------------------------------
def generate_panel_image(image_prompt, panel_number):
  try:
    response = client.models.generate_images(
        model="imagen-3.0-generate-001",
        prompt=image_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
            add_watermark=False,
            output_mime_type="image/png",
        ),
    )

    if response.generated_images:
      generated_image = response.generated_images[0]
      
      if generated_image.image:
        image = generated_image.image
      elif generated_image.encoded_bytes:
        image_bytes = base64.b64decode(generated_image.encoded_bytes)
        image = Image.open(io.BytesIO(image_bytes))
      else:
        st.error(f"Error: Unknown image format received for Panel {panel_number}.")
        return None

      image_path = f"comic_panel_{panel_number}.png"
      image.save(image_path)
      return image_path

    else:
      st.warning(f"No image generated for Panel {panel_number}. The prompt might have triggered safety filters.")
      return None

  except Exception as e:
    st.error(f"Image generation critical error for Panel {panel_number}: {e}")
    with st.expander("Show detailed error"):
        st.code(str(e))
    return None


# --------------------------------------------------
# Page settings
# --------------------------------------------------
st.set_page_config(page_title="ComicCraft", page_icon="🎨", layout="wide")

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
      "ComicCraft uses Gemini to write your story and create detailed"
      " prompts, and Imagen 3 to generate consistent, high-quality images for"
      " your 5-panel comic."
  )
  st.divider()
  st.subheader("✨ Features")
  st.write("📖 AI Story Generation (Gemini Flash)")
  st.write("🖼️ AI Comic Images (Imagen 3)")
  st.write("💬 Character Dialogues")
  st.write("🎭 Character Consistency")
  st.write("📥 Story Download")

st.divider()

# --------------------------------------------------
# Story input
# --------------------------------------------------
st.subheader("💡 Enter your comic story idea:")
story_idea = st.text_area(
    label="Comic Idea Input",
    placeholder="Example: A young girl with a blue scarf finds an old, glowing leather book hidden inside a hollow tree trunk.",
    height=150,
    label_visibility="collapsed"
)

st.info("🎭 Characters will stay consistent across all 5 panels.")

# --------------------------------------------------
# Main Action Buttons
# --------------------------------------------------
col1, col2 = st.columns([1, 5])
with col1:
    generate_btn = st.button("🚀 Generate My Comic", type="primary")
with col2:
    if st.button("🗑️ Clear", type="secondary"):
        st.rerun()

# --------------------------------------------------
# Generate Comic Logic
# --------------------------------------------------
if generate_btn:
  if story_idea.strip():
    
    status_placeholder = st.empty()
    status_placeholder.info("🔄 Process started. Requesting story structure from Gemini...")

    # ------------------------------------------
    # Generate Story Structure via Gemini 1.5 Flash
    # ------------------------------------------
    with st.spinner("Step 1: Gemini is writing your comic script..."):
      prompt = f"""
Create a detailed short comic story script based on this idea:

{story_idea}

Give the story in exactly 5 comic panels. Provide the response structure in markdown.

Use these exact headings for structure:
### Panel 1
### Panel 2
### Panel 3
### Panel 4
### Panel 5

For each panel, strictly provide only these fields, formatted exactly like this:
*   **Scene:** [Detailed description of the setting and time]
*   **Character action:** [Specific movements or poses for each character present]
*   **Dialogue:** [Character Name]: "[Dialogue text]" (Leave blank if no dialogue)
*   **Image prompt:** [Detailed, consistent description suitable for Imagen 3 generation. Specify character consistency: "The same girl with a blue scarf stands..." Include details on pose, lighting, background, facial expression, and 'vibrant comic art style'.]

Keep the main characters visually consistent across all 5 panels.
"""

      try:
        # Switched to gemini-1.5-flash for universal availability
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
        )
        
        response_text = "".join([part.text for part in response.candidates[0].content.parts if part.text])

      except Exception as e:
        status_placeholder.empty()
        error_message = str(e)
        if "503" in error_message:
          st.error("⚠️ Gemini is temporarily busy. Please wait and try again.")
        elif "429" in error_message:
          st.error("⚠️ Gemini API quota has been reached. Please try later.")
        elif "404" in error_message:
          st.error("⚠️ Gemini model not found. Please verify your API key.")
        else:
          st.error("⚠️ Gemini Story Generation Error:")
          st.code(error_message)
        st.stop()

    status_placeholder.empty()
    
    st.success("🎨 Step 1 Complete: Your ComicCraft script is ready!")
    st.markdown("## 📖 Your Comic Script & Generated Panels")
    st.divider()

    raw_panels = response_text.split("### Panel ")
    panel_data = raw_panels[1:] 

    if len(panel_data) < 5:
        st.error(f"Error: Gemini generated {len(panel_data)} panels instead of 5. Please try again.")
        with st.expander("See raw output"):
            st.code(response_text)
        st.stop()

    for i, panel in enumerate(panel_data):
      panel_number = i + 1
      st.markdown(f"### 🖼️ Panel {panel_number}")
      
      img_col, txt_col = st.columns([1, 1])

      image_prompt = ""
      if "**Image prompt:**" in panel:
        image_prompt = panel.split("**Image prompt:**", 1)[1].strip()
      elif "Image prompt:" in panel:
        image_prompt = panel.split("Image prompt:", 1)[1].strip()
      
      if "\n###" in image_prompt:
          image_prompt = image_prompt.split("\n###")[0].strip()

      panel_image_path = None
      if image_prompt:
        with img_col:
            with st.spinner(f"🎨 Generating Image for Panel {panel_number}..."):
              panel_image_path = generate_panel_image(image_prompt, panel_number)

      with img_col:
          if panel_image_path:
            st.image(
                panel_image_path,
                caption=f"Panel {panel_number} Generated by Imagen 3",
                use_container_width=True,
            )
          else:
            st.warning(f"⚠️ Image generation failed for Panel {panel_number}.")

      with txt_col:
        st.markdown(
            f"""
                <div style="
                    padding: 15px;
                    border-radius: 10px;
                    border: 1px solid #444444;
                    background-color: #1a1a1a;
                    margin-bottom: 10px;
                ">
                <h4>📖 Panel {panel_number} Script</h4>
                """,
            unsafe_allow_html=True,
        )

        script_content = panel
        if "**Image prompt:**" in script_content:
             script_content = script_content.split("**Image prompt:**")[0].strip()

        if script_content:
            st.markdown(script_content)
        else:
            st.write("*No script content parsed.*")

        st.markdown("</div>", unsafe_allow_html=True)

      st.divider()

    try:
        with open("comic_story_script.txt", "w", encoding="utf-8") as file:
          file.write(response_text)
    except Exception as save_error:
        st.warning(f"Could not save script locally: {save_error}")

    st.download_button(
        label="📥 Download Your Comic Script (Text)",
        data=response_text,
        file_name="ComicCraft_Script.txt",
        mime="text/plain",
        key="download-script"
    )
    
    st.success("🎉 Comic Generation Complete!")

  else:
    st.warning("💡 Please enter a story idea to create your comic!")
