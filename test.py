import io
import os
import vertexai
from google.cloud import language_v1
from google.cloud import storage
from vertexai.generative_models import GenerativeModel

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceAccountCreds.json'
bucket_name = "mail_classification_bucket"
langClient = language_v1.LanguageServiceClient()
project_id = "arcane-grin-424609-b5"
vertexai.init(project=project_id, location="europe-west2")
model = GenerativeModel(model_name="gemini-1.0-pro-002", safety_settings=None)
storage_client = storage.Client()

def get_text_files(bucket_name):
    blobs = storage_client.list_blobs(bucket_name)
    return blobs

def sentiment_analysis(content):
    type_ = language_v1.Document.Type.PLAIN_TEXT
    document = {"type_": type_, "content": content}
    response = langClient.analyze_sentiment(request={"document": document})
    sentiment = response.document_sentiment
    print("Score: {}".format(sentiment.score))
    return sentiment

def content_label(content):
    response = model.generate_content(
        "Tag the right label for the upcoming content as 'Account Related' or 'Card Related' or 'Loan Related' or 'Other Labels'. Your response should contain only one tag among the given option. I dont want any explanation on why the label is selected" + content
    )
    return str(response.text)

def extract_information(content):
    response = model.generate_content(
        "Can you pick up 'name', 'date', 'time', 'address', 'account number', 'card number' from the text. Just pull up  only the available information. If it is not available ignore it" + content
    )
    return response.text

blob_object = get_text_files(bucket_name)
for blob in blob_object:
    print("File Name: {}".format(blob.name))
    content = blob.download_as_string().decode("utf-8")
    sentiment = sentiment_analysis(content)
    if sentiment.score < 0:
        label = content_label(content)
        print(f"Label = {label}")
        if "Account" in label:
            destination_blob_name = "account_related"
        elif "Card" in label:
            destination_blob_name = "card_related"
        elif "Loan" in label:
            destination_blob_name = "loan_related"
        else:
            destination_blob_name = "other_labels"

        bucket = storage_client.bucket(destination_blob_name)
        output_blob = bucket.blob(blob.name)

        text_file = io.StringIO()
        text_file.write("==============Sentiment Score==============\n Score: {}\n".format(sentiment.score))
        text_file.write("==============Complaint Label==============\n")
        text_file.write(label+"\n")

        text_file.write("==============Complaint Insight==============\n")
        info = extract_information(content)
        print(f"Info = {info}")
        text_file.write(info + "\n")

        output_blob.upload_from_string(text_file.getvalue())
        text_file.close()
