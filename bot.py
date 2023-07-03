# ##### bot.py #####

import os
# import json
from slackeventsapi import SlackEventAdapter
from slack import WebClient

# Credentials
slack_token = os.environ["SLACK_BOT_CLIENT"]
slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
slack_app_token = os.environ["SLACK_APP_TOKEN"]

# MESSAGE_BLOCK = {"type": "section", "text": {"type": "mrkdwn", "text": ""}}

# Initializing slack web client and slack_events_adapter
slack_web_client = WebClient(token=slack_token)
slack_events_adapter = SlackEventAdapter(signing_secret=slack_signing_secret,
                                         endpoint="/listening")

# # Event handler for message events
# @slack_events_adapter.on("message")
# def handle_message(event_data):
#   message = event_data["event"]
#   channel = message["channel"]
#   text = message.get("text")
#   user = message.get("user")

#   if user and not user.lower().startswith("b"):
#     reply = f"You said: {text}"
#     slack_web_client.chat_postMessage(channel=channel,
#                                       text=reply,
#                                       thread_ts=message.get("ts"))


# send message to channel
def send_message(channel="testing", text="I am online!"):
  slack_web_client.chat_postMessage(channel=channel, text=text)


# reply to
def bot_reply(channel, reply, thread_ts):
  slack_web_client.chat_postMessage(channel=channel,
                                    text=reply,
                                    thread_ts=thread_ts)


def start_bot_server():
  send_message()
  slack_events_adapter.start(port=7000)


# Start the server to receive Slack events
if __name__ == "__main__":
  start_bot_server()
