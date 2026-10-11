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
      generated_image = response.generated_images
