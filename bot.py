# ##### bot.py #####

import os
from slackeventsapi import SlackEventAdapter
from slack import WebClient

# Credentials
slack_token = os.environ["SLACK_BOT_CLIENT"]
slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
slack_app_token = os.environ["SLACK_APP_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]
pinecone_api_key = os.environ["PINECONE_API_KEY"]
pinecone_environment = os.environ["PINECONE_ENV"]
bot_app_id = os.environ["BOT_APP_ID"]


# Initializing BabuLohar model
babulohar = BabuLohar(openai_api=openai_api_key,
                      pinecone_api=pinecone_api_key,
                      pinecone_env=pinecone_environment)


# Initializing slack web client and slack_events_adapter
slack_web_client = WebClient(token=slack_token)
slack_events_adapter = SlackEventAdapter(signing_secret=slack_signing_secret,
                                         endpoint="/listening")                                       

# send message to channel
def send_message(channel="testing_bot", text="I am online!"):
  slack_web_client.chat_postMessage(channel=channel, text=text)


# reply to
def bot_reply(channel, reply, thread_ts):
  slack_web_client.chat_postMessage(channel=channel,
                                    text=reply,
                                    thread_ts=thread_ts)


# PDFs handler
def handle_attachments(attachments):
  uploaded_pdfs = "./uploaded"
  if not os.path.exists(uploaded_pdfs):
    os.makedirs(uploaded_pdfs)

  file_name = attachments[0].get("title")
  file_path = os.path.join(uploaded_pdfs, file_name)

  if file_name.split('.')[-1].lower() != "pdf":
    send_message(channel="#uploadpdfs",
                 text=f"Error {file_name}: only PDFs are allowed")
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
      send_message(channel="#uploadpdfs",
                   text=f"Failed to download {file_name}")
  else:
    send_message(channel="#uploadpdfs",
                 text=f"Please try again for: {file_name}")


# event handler
def handle_events(slack_event):
  message = slack_event["event"]
  channel = message["channel"]
  # user = message.get("user") # might use for authorizing users in later versions
  thread = message.get("ts")
  print()
  print(message)
  print()
  if 'bot_id' not in message:  # if the sender is not bot
    try:  # detect mentions
      if message["blocks"][0]["elements"][0]["elements"][0][
          "user_id"] == bot_app_id:  # if the bot was mentioned
        if message.get("attachments"):  # found attachments
          print("found attachments")
          attachments = message["attachments"]
          handle_attachments(attachments)

        else:  # if only text
          text = message.get("text")
          bot_reply(channel=channel,
                    reply=babulohar.get_response(text),
                    thread_ts=thread)
        return
      else:
        return
    except:
      return


def start_bot_server():
  send_message()
  slack_events_adapter.start(port=7000)


# Start the server to receive Slack events
if __name__ == "__main__":
  start_bot_server()
