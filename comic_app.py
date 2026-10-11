import base64
import os
import io
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

# Load environment variables (Make sure your .env has GEMINI_API_KEY=your_key)
load_dotenv()

# Connect to Gemini - use your project ID if using Vertex AI
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --------------------------------------------------
# Generate comic panel image using Imagen 3
# --------------------------------------------------
def generate_panel_image(image_prompt, panel_number):
  try:
    # Explicitly using Imagen 3 for generating high-quality images.
    # Alternatives: "imagen-3.0-fast-generate-001" for speed.
    response = client.models.generate_images(
        model="imagen-3.0-generate-001",
        prompt=image_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",  # Standard for square comic panels
            add_watermark=False,  # Set to True if required by policy
            output_mime_type="image/png",
        ),
    )

    # Check if images were generated successfully
    if response.generated_images:
      generated_image = response.generated_images[0]
      
      # Determine if the output is the raw Image object or encoded bytes
      if generated_image.image:
        # Standard PIL Image object (often from vertex AI)
        image = generated_image.image
      elif generated_image.encoded_bytes:
        # Base64 encoded bytes (often from Google AI Studio)
        image_bytes = base64.b64decode(generated_image.encoded_bytes)
        image = Image.open(io.BytesIO(image_bytes))
      else:
        st.error(f"Error: Unknown image format received for Panel {panel_number}.")
        return None

      image_path = f"comic_panel_{panel_number}.png"
      image.save(image_path)
      return image_path

    else:
      # Handle cases where safety filters might have blocked generation
      st.warning(f"No image generated for Panel {panel_number}. The prompt might have triggered safety filters.")
      if response.safety_ratings:
         st.write("Safety ratings:", response.safety_ratings)
      return None

  except Exception as e:
    st.error(f"Image generation critical error for Panel {panel_number}: {e}")
    # Display the full error trace for easier debugging by the user
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
      "ComicCraft uses Gemini 1.5 Pro to write your story and create detailed"
      " prompts, and Imagen 3 to generate consistent, high-quality images for"
      " your 5-panel comic."
  )
  st.divider()
  st.subheader("✨ Features")
  st.write("📖 AI Story Generation (Gemini 1.5 Pro)")
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
    placeholder="Example: A futuristic detective investigates a robot that claims to have feelings...",
    height=150,
    label_visibility="collapsed"
)

st.info("🎭 Characters will stay consistent across all 5 panels. Specify details like clothing and hair color for best results.")

# --------------------------------------------------
# Main Action Buttons (Using Columns for layout)
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
    
    # Placeholder for status updates during generation
    status_placeholder = st.empty()
    status_placeholder.info("🔄 Process started. Requesting story structure from Gemini...")

    # ------------------------------------------
    # Generate Story Structur via Gemini 1.5 Pro
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
*   **Image prompt:** [Detailed, consistent, safe description suitable for Imagen 3 generation. Specify character consistency: "The same detective, Sarah (short brown hair, brown trenchcoat), stands..." Include details on pose, lighting, background, facial expression, and 'vibrant comic art style'.]

Keep the main characters visually consistent across all 5 panels.
"""

      try:
        # Using Gemini 1.5 Pro for its superior reasoning in story planning and prompt generation
        response = client.models.generate_content(
            model="gemini-1.5-pro", contents=prompt
        )
        
        # In case the model responds with multiple parts/calls, join them
        response_text = "".join([part.text for part in response.candidates[0].content.parts if part.text])

      except Exception as e:
        status_placeholder.empty()
        error_message = str(e)
        if "503" in error_message:
          st.error("⚠️ Gemini Pro is temporarily busy. Please wait and try again.")
        elif "429" in error_message:
          st.error("⚠️ Gemini API quota has been reached. Please check your billing or try later.")
        elif "404" in error_message:
          st.error("⚠️ Gemini model 'gemini-1.5-pro' not found. Please verify your API key access.")
        else:
          st.error("⚠️ Gemini Story Generation Error:")
          st.code(error_message)
        st.stop()

    # Clear previous info/spinner
    status_placeholder.empty()
    
    # ------------------------------------------
    # Story script is ready
    # ------------------------------------------
    st.success("🎨 Step 1 Complete: Your ComicCraft script is ready!")
    st.markdown("## 📖 Your Comic Script & Generated Panels")
    st.divider()

    # ------------------------------------------
    # Split story response into panels
    # ------------------------------------------
    # We split by '### Panel ' assuming the model followed instructions
    raw_panels = response_text.split("### Panel ")

    # The first element before the first '### Panel ' might be an intro or empty
    panel_data = raw_panels[1:] 

    if len(panel_data) < 5:
        st.error(f"Error: Gemini only generated {len(panel_data)} panels instead of 5. Please try generating again.")
        with st.expander("See raw output"):
            st.code(response_text)
        st.stop()


    # ------------------------------------------
    # Display each panel (Image + Text Box)
    # ------------------------------------------
    # Use Streamlit containers/columns for better panel layout (Image left, text right)
    for i, panel in enumerate(panel_data):
      panel_number = i + 1
      st.markdown(f"### 🖼️ Panel {panel_number}")
      
      # Use columns to put image and text side-by-side
      img_col, txt_col = st.columns([1, 1])

      # --------------------------------------
      # Parse Image Prompt from markdown
      # --------------------------------------
      image_prompt = ""
      if "**Image prompt:**" in panel:
        image_prompt = panel.split("**Image prompt:**", 1)[1].strip()
      elif "Image prompt:" in panel: # Fallback if bolding missed
        image_prompt = panel.split("Image prompt:", 1)[1].strip()
      
      # Clean up potential trailing markdown/headers
      if "\n###" in image_prompt:
          image_prompt = image_prompt.split("\n###")[0].strip()

      # --------------------------------------
      # Generate Panel Image via Imagen
      # --------------------------------------
      panel_image_path = None
      if image_prompt:
        with img_col:
            with st.spinner(f"🎨 Generating Image for Panel {panel_number}..."):
              panel_image_path = generate_panel_image(image_prompt, panel_number)

      # --------------------------------------
      # Display Image
      # --------------------------------------
      with img_col:
          if panel_image_path:
            st.image(
                panel_image_path,
                caption=f"Panel {panel_number} Generated by Imagen 3",
                use_container_width=True,
            )
          else:
            st.warning(f"⚠️ Image generation failed for Panel {panel_number}. You may need to refine the prompt below and generate again.")

      # --------------------------------------
      # Display Panel Script (Text Column)
      # --------------------------------------
      with txt_col:
        # Create a nice border box around the text content
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

        # Basic cleaning and formatting of the script content
        # Ensure we display everything except the image prompt, which is messy to read
        script_content = panel
        if "**Image prompt:**" in script_content:
             script_content = script_content.split("**Image prompt:**")[0].strip()

        if not script_content or script_content == "":
            st.write("*No script content parsed.*")
        else:
            # We must use st.markdown so the inner markdown bullet points/bolding are rendered
            st.markdown(script_content)

        st.markdown("</div>", unsafe_allow_html=True)

      st.divider() # Separation between panels

    # ------------------------------------------
    # Save & Download story script
    # ------------------------------------------
    # Store the script file locally for persistent history (optional)
    try:
        with open("comic_story_script.txt", "w", encoding="utf-8") as file:
          file.write(response_text)
    except Exception as save_error:
        st.warning(f"Could not save script locally: {save_error}")

    # Provided download button for the script
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
