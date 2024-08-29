from flask import Flask, request, jsonify
from markupsafe import escape
from flask_cors import CORS
import base64
import os
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
import time

app = Flask(__name__)
CORS(app, support_credentials=True)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceAccountCreds2.json'

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
def generate(video):
    model = GenerativeModel(
        "gemini-1.5-flash-001",
    )
    responses = model.generate_content(
        [video,
         """Provide a description of the conversation happened in the video with all points discussed in it under heading "Description". Results should be displayed in pointers. And also tell the sentiment of the customer under heading "Customer Feedback" and representative sentiment under heading "Representative feedback". Can you also provide sentiment score of customer and colleague under the heading "SentimentScore"."""],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )

    return responses.text

def fetchVideo(videoFile):
    with open(videoFile, "rb") as video_file:
        video_data = video_file.read()
        encoded_video = base64.b64encode(video_data).decode("utf-8")

    video = Part.from_data(mime_type="video/mp4", data=base64.b64decode(encoded_video))
    return video

def fectchTranscript(transcriptFile):
    with open(transcriptFile, "r") as file:
        text_data = file.read()
        encoded_text = base64.b64encode(text_data.encode("utf-8")).decode("utf-8")

    transcript = Part.from_data(mime_type="text/plain", data=base64.b64decode(encoded_text))
    return transcript

def constructResponse(responses):
    responseList = responses.split('\n\n')
    if 'Description' not in responseList[0]:
        responseList.pop(0)
    print(responseList)
    videoDict = {}
    videoDict['description'] = responseList[1].strip()
    videoDict['cust_feedback'] = responseList[3].strip()
    videoDict['rep_feedback'] = responseList[5].strip()
    sentiment = responseList[7].strip().split('\n')
    print(sentiment)
    videoDict['cust_sentimentScore'] = sentiment[0].strip()
    videoDict['rep_sentimentScore'] = sentiment[1].strip()
    return videoDict


@app.route('/file/<file_path>')
def hello(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        file = fectchTranscript(file_path)
    else:
        file = fetchVideo(file_path)

    response = generate(file)
    #print(response)
    responseJson = constructResponse(response)
    return jsonify(responseJson)