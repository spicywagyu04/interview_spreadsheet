import base64
import os
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT_FILTER

def llm_gemini(user_prompt, system_prompt="", temperature=0.0):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-preview-04-17"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_prompt),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text=system_prompt),
        ],
        temperature=temperature,
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    
    # parse ```json ... ``` to just the json
    data = response.text
    data = data.strip('` \n')

    if data.startswith('json'):
        data = data[4:]

    return data
