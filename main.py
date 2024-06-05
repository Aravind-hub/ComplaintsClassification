import io
import os
import six
import vertexai
from google.cloud import vision_v1p3beta1 as vision
from google.cloud import language_v1
from google.cloud import storage
from vertexai.preview.language_models import TextGenerationModel

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceAccountCreds.json'

def list_blobs(bucket_name):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)
    return blobs


visionClient = vision.ImageAnnotatorClient()
langClient = language_v1.LanguageServiceClient()


path = "./letters/Bala_ComplaintLetter.jpg"

with io.open(path, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)
image_context = vision.ImageContext(language_hints=["en-t-i0-handwrit"])

response = visionClient.document_text_detection(image=image, image_context=image_context)
#print(f"Full Text: {response.full_text_annotation.text}")

content = response.full_text_annotation.text
if isinstance(content, six.binary_type):
    content = content.decode("utf-8")

type_ = language_v1.Document.Type.PLAIN_TEXT
document = {"type_": type_, "content": content}

response = langClient.analyze_sentiment(request={"document": document})
sentiment = response.document_sentiment
print("Score: {}".format(sentiment.score))

project_id = "arcane-grin-424609-b5"
#vertexai.init(project=project_id, location="europe-west2")

parameters = {
    "temperature": .2,
    "max_output_tokens": 256,
    "top_p": .8,
    "top_k": 40,
}

model = TextGenerationModel.from_pretrained("text-bison@001")

if sentiment.score < 0:
    response = model.predict(
        "Tag the right label for the upcoming content as 'Account Related' or 'Card Related' or 'Loan Related' or 'Other Labels'. Your response should contain only one tag among the given option. I dont want any explanation on why the label is selected" + content,
        **parameters
    )

    label = str(response.text)
    print(label)

    path = path.split("/")
    if "Account" in label:
        outputPath = 'Account/' + path[len(path) - 1] + '.txt'
    elif "Card" in label:
        outputPath = 'Card/' + path[len(path) - 1] + '.txt'
    elif "Loan" in label:
        outputPath = 'Loan/' + path[len(path) - 1] + '.txt'
    else:
        outputPath = 'Others/' + path[len(path) - 1] + '.txt'

    response = model.predict(
        "Can you pick up 'name', 'date', 'time', 'address', 'account number', 'card number' from the text. Just pull up  only the available information. If it is not available ignore it" + content,
        **parameters
    )
    info = response.text
    print(info)

    with open(outputPath, 'w', encoding="utf-8") as r:
        r.write('==============Transcribed Text==============\n')
        r.write(content+"\n")
        r.write('==============Sentiment Score==============\n')
        r.write("Score: {}\n".format(sentiment.score))
        r.write('==============Complaint Label==============\n')
        r.write(label+"\n")
        r.write('==============Complaint Insight==============\n')
        r.write(info+"\n")