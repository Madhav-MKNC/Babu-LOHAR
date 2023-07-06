# ##### bot.py #####

import os
from slackeventsapi import SlackEventAdapter
from slack import WebClient
from babu_lohar import BabuLohar

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


# event handler
# NOTE: jugaad for stopping multiple replies
previous_timestamp = 0


def handle_events(slack_event):
  message = slack_event["event"]
  channel = message["channel"]
  user = message.get("user")
  text = message.get("text")
  thread = message.get("ts")
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
        bot_reply(channel=channel,
                  reply=babulohar.get_response(text),
                  thread_ts=thread)
    except:
      pass


def start_bot_server():
  send_message()
  slack_events_adapter.start(port=7000)


# Start the server to receive Slack events
if __name__ == "__main__":
  start_bot_server()
