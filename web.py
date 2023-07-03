# ##### web.py #####

from flask import Flask, request, make_response
from threading import Thread
from waitress import serve
from bot import bot_reply, send_message
from babu_lohar import BabuLohar
import os
import requests

# API keys
openai_api_key = os.environ["OPENAI_API_KEY"]
pinecone_api_key = os.environ["PINECONE_API_KEY"]
pinecone_environment = os.environ["PINECONE_ENV"]

# Initializing Flask app
app = Flask('')

# Initializing BabuLohar model
babulohar = BabuLohar(
  openai_api=openai_api_key,
  pinecone_api=pinecone_api_key,
  pinecone_env=pinecone_environment
)


# PDFs handler
def handle_attachments(slack_event):
  uploaded_pdfs = "./uploaded"
  if not os.path.exists(uploaded_pdfs):
    os.makedirs(uploaded_pdfs)

  attachments = slack_event["event"]["attachments"]
  file_name = attachments[0].get("title")
  file_path = os.path.join(uploaded_pdfs, file_name)

  if not file_name.endswith(".pdf"):
    send_message(
      channel="#testing",
      text=f"Error {file_name}: only PDFs are allowed"
    )
  elif attachments[0].get("original_url"):
    file_url = attachments[0]["original_url"]
    response = requests.get(file_url)
    if response.status_code == 200:
      with open(file_path, "wb") as file:
        file.write(response.content)
      send_message(channel="#uploadpdfs",
                   text=f"Successfuly uploaded {file_name}")

      babulohar.add_PDF(file_path)
      babulohar.process(uploaded_pdfs)
      send_message(channel="#uploadpdfs", text=f"Loaded {file_name}")
  else:
    send_message(channel="#testing", text=f"Please try again for: {file_name}")


# event handler
def handle_events(slack_event):
  message = slack_event["event"]
  channel = message["channel"]
  # user = message.get("user") # might use for authorizing users in later versions
  thread = message.get("ts")

  if 'bot_id' not in message:  # if the sender is not bot
    try:  # detect mentions
      if message["blocks"][0]["elements"][0]["elements"][0][
          "user_id"] == "U05FA5J3MMX":  # if the bot was mentioned
        if slack_event["event"].get("attachments"):  # found attachments
          handle_attachments(slack_event)
        else:  # if only text
          text = message.get("text")
          bot_reply(channel=channel,
                    reply=babulohar.get_response(text),
                    thread_ts=thread)
        print("I WAS MENTIONED")

      else:
        print("SOMEBODY WAS MENTIONED")
    except:
      print("NOBODY GOT MENTIONED")
  print("######################### end ###############################")


# for keeping the bot alive
@app.route('/')
def home():
  return "Web-server for centauri slack bot in crypto<>llm is online"


# listening for events on the bot
@app.route("/listening", methods=["GET", "POST"])
def hears():
  slack_event = request.get_json()

  # auth
  if "challenge" in slack_event:
    return make_response(slack_event["challenge"], 200,
                         {"content_type": "application/json"})

  # events handler
  if "event" in slack_event and slack_event["event"]["type"] == "message":
    handle_events(slack_event)

  # response
  return make_response("Event received", 200)


# main run function
def run():
  serve(app, host="0.0.0.0", port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()
