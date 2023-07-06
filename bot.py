# ##### bot.py #####

import os
from slackeventsapi import SlackEventAdapter
from slack import WebClient
from babu_lohar import BabuLohar
import requests

# Credentials
slack_token = os.environ["SLACK_BOT_CLIENT"]
slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
slack_app_token = os.environ["SLACK_APP_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]
pinecone_api_key = os.environ["PINECONE_API_KEY"]
pinecone_environment = os.environ["PINECONE_ENV"]

# Initializing BabuLohar model
babulohar = BabuLohar(openai_api=openai_api_key,
                      pinecone_api=pinecone_api_key,
                      pinecone_env=pinecone_environment)

# Initializing slack web client and slack_events_adapter
slack_web_client = WebClient(token=slack_token)
slack_events_adapter = SlackEventAdapter(signing_secret=slack_signing_secret,
                                         endpoint="/listening")
bot_app_id = slack_web_client.api_call("auth.test")['user_id']


# send message to channel
def send_message(channel="testing", text="I am online!"):
  slack_web_client.chat_postMessage(channel=channel, text=text)


# reply to
def bot_reply(channel, reply, thread_ts):
  slack_web_client.chat_postMessage(channel=channel,
                                    text=reply,
                                    thread_ts=thread_ts)


# PDFs handler
def handle_attachments(attachment):
  uploaded_pdfs = "./uploaded"
  if not os.path.exists(uploaded_pdfs):
    os.makedirs(uploaded_pdfs)
  print(0)

  file_name = attachment.get("title")
  file_path = os.path.join(uploaded_pdfs, file_name)
  print(1)
  print(file_name)
  print(file_path)

  if attachment.get("filetype").lower() != "pdf":
    return send_message(channel="testing",
                        text=f"Error {file_name}: only PDFs are allowed")
  print(2)

  download_url = attachment.get("url_private")
  print(2.1)
  headers = {"Authorization": f"Bearer {slack_token}"}
  print(2.2)
  response = requests.get(download_url, headers=headers)
  print(3)

  if response.status_code == 200:
    print(31)
    with open(file_path, "wb") as file:
      file.write(response.content)
      print(f"Attachment downloaded to: {file_path}")
      send_message(channel="testing", text=babulohar.summarize(file_path))
  else:
    print(30)
    print("Failed to download attachment.")
    send_message(channel="testing", text=f"Upload failed: {file_name}")


# event handler
# NOTE: jugaad for stopping multiple replies
previous_timestamp = 0


def handle_events(slack_event):
  message = slack_event["event"]
  channel = message["channel"]
  user = message.get("user")
  text = message.get("text")
  thread = message.get("ts")
  attachments = message.get("files")

  print()
  print(message)
  print()

  if user != bot_app_id:  # if the sender is not bot
    global previous_timestamp
    if thread == previous_timestamp: return
    else: previous_timestamp = thread

    try:  # detect mentions
      if message["blocks"][0]["elements"][0]["elements"][0][
          "user_id"] == bot_app_id:  # if the bot was mentioned
        if attachments:  # found attachments
          print("found attachments")
          handle_attachments(attachments[0])
        else:  # reply to text
          bot_reply(channel=channel,
                    reply=babulohar.get_response(text),
                    thread_ts=thread)
    except:
      pass


# start bot server
def start_bot_server():
  send_message()
  slack_events_adapter.start(port=7000)


# Start the server to receive Slack events
if __name__ == "__main__":
  start_bot_server()
