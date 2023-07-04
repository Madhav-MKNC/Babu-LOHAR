# ##### web.py #####

from flask import Flask, request, make_response
from threading import Thread
from waitress import serve
from bot import bot_reply, send_message
from babu_lohar import BabuLohar
import os
import requests

# Initializing Flask app
app = Flask(__init__)


# for keeping the bot alive
@app.route('/')
def home():
  return "Web-server for centauri slack bot in crypto<>llm is online"


# listening for events from the bot
@app.route("/listening", methods=["GET", "POST"])
def hears():
  slack_event = request.get_json()

  # auth
  if "challenge" in slack_event:
    return make_response(slack_event["challenge"], 200,
                         {"content_type": "application/json"})

  # events handler
  if "event" in slack_event and slack_event["event"]["type"] == "message":
    if slack_event.get("event_id") != request.headers.get(
        "X-Slack-Retry-Reason"):
      handle_events(slack_event)

  # response
  return make_response("Event received", 200)


# main run function
def run():
  serve(app, host="0.0.0.0", port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()
