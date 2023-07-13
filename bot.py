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
BOT_CHANNEL = "C05ENBGTJUT"

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
def send_message(channel="test_bot", text="I am online!"):
  slack_web_client.chat_postMessage(channel=channel, text=text)


# reply to
def bot_reply(channel, reply, thread_ts):
  slack_web_client.chat_postMessage(channel=channel,
                                    text=reply,
                                    thread_ts=thread_ts)


# download files from attachments
# allowed files: pdf, txt, doc, docx
def handle_attachments(attachment, channel, ts):
  allowed_files = ["pdf", "txt", "doc", "docx"]

  uploaded_pdfs = "./uploaded"
  if not os.path.exists(uploaded_pdfs):
    os.makedirs(uploaded_pdfs)
  print(0)

  file_name = attachment.get("title")
  file_path = os.path.join(uploaded_pdfs, file_name)
  print(1)
  print(file_name)
  print(file_path)

  if file_name.split('.')[-1].lower() not in allowed_files:
    return bot_reply(channel, "Error: Filetype not allowed", ts)
  print(2)

  download_url = attachment.get("url_private")
  print(attachment)
  print(2.1)
  headers = {"Authorization": f"Bearer {slack_token}"}
  print(2.2)
  response = requests.get(download_url, headers=headers)
  print(3)

  if response.status_code == 200:
    print(31)
    with open(file_path, "wb") as downloaded:
      downloaded.write(response.content)
    print(f"Attachment downloaded to: {file_path}")
    print(f"loading {file_name}", channel, ts)
    # send_message(channel, "loading")
    # send_message(channel, babulohar.summarize(file_path))
    bot_reply(channel, "Loading...", ts)
    bot_reply(channel, babulohar.summarize(file_path), ts)
  else:
    print(30)
    print("Failed to download attachment.")
    bot_reply(channel, f"Failed to load {file_name}", ts)
  print("file handled")


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

  print(channel, BOT_CHANNEL)

  if channel != BOT_CHANNEL:  # channel is BOT_CHANNEL
    return

  if user != bot_app_id:  # if the sender is not bot
    global previous_timestamp
    if thread == previous_timestamp: return
    else: previous_timestamp = thread

    try:
      if message["blocks"][0]["elements"][0]["elements"][0][
          "user_id"] == bot_app_id:
        if attachments:
          print("found attachments")
          handle_attachments(attachments[0], channel, thread)
        else:
          flag = False
          try:
            url = message["blocks"][0]["elements"][0]["elements"][2]["url"]
            flag = True
          except:
            pass

          if flag:  # if url found, summarize the url
            bot_reply(channel, "Loading URL...", thread)
            bot_reply(channel=channel,
                      reply=babulohar.summarize(url),
                      thread_ts=thread)
            print("\nsummarized\n")
          else:  # qna with docs from ./data
            bot_reply(channel=channel,
                      reply=babulohar.get_response(text),
                      thread_ts=thread)
    except Exception as e:
      print(e)


# start bot server
def start_bot_server():
  send_message()
  slack_events_adapter.start(port=7000)


# Start the server to receive Slack events
if __name__ == "__main__":
  start_bot_server()
