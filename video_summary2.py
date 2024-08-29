import base64
import os
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceAccountCreds2.json'


def generate():
    model = GenerativeModel(
        "gemini-1.5-flash-001",
    )
    responses = model.generate_content(
        [video,
         """Provide a description of the conversation happened in the video with all points discussed in it under heading "Description". Results should be displayed in pointers. And also tell the sentiment of the customer under heading "Customer Feedback" and representative sentiment under heading "Representative feedback". Can you also provide sentiment score of customer and colleague"""],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )

    #for response in responses:
    print(responses.text)


with open("video2.mp4", "rb") as video_file:
    video_data = video_file.read()
    encoded_video = base64.b64encode(video_data).decode("utf-8")

video = Part.from_data(
    mime_type="video/mp4",
    data=base64.b64decode(encoded_video))

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

generate()
