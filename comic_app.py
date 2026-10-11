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
        model="gemini-2.0-flash",   # <-- Updated from gemini-2.5-flash
        contents=prompt
    )

    if not response.text:
        raise ValueError("The AI returned an empty story.")

    return response.text
