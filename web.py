# ##### web.py #####

from flask import Flask, request, make_response
from threading import Thread
from waitress import serve
from bot import send_message
from babu_lohar import BabuLohar

# Initializing Flask app
app = Flask('')

# API keys
openai_api_key = ""
pinecone_api_key = ""
pinecone_environment = ""

# Initializing BabuLohar model
babulohar = BabuLohar(openai_api=openai_api_key,
                      pinecone_api=pinecone_api_key,
                      pinecone_env=pinecone_environment)


# for keeping the bot alive
@app.route('/')
def home():
  return "Web-server for centauri slack bot in crypto<>llm is online"


# listening for events on the bot
@app.route("/listening", methods=["GET", "POST"])
def hears():
  slack_event = request.get_json()
  if "challenge" in slack_event:
    return make_response(slack_event["challenge"], 200,
                         {"content_type": "application/json"})

  if "event" in slack_event and slack_event["event"]["type"] == "message":
    message = slack_event["event"]
    channel = message["channel"]
    text = message.get("text")
    user = message.get("user")
    thread = message.get("ts")

    print("------------------------- start ---------------------------")
    print(message)
    # if bot was mentioned (except be itself)
    if 'bot_id' not in message:
      try:
        if message["blocks"][0]["elements"][0]["elements"][0][
            "user_id"] == "U05FA5J3MMX":
          send_message(channel,
                       reply=babulohar.get_response(text),
                       user=user,
                       thread_ts=thread)
          print("I WAS MENTIONED")
        else:
          print("SOMEBODY WAS MENTIONED")
      except:
        print("NOBODY GOT MENTIONED")
    print("######################### end ###############################")

  return make_response("Event received", 200)


# main run function
def run():
  serve(app, host="0.0.0.0", port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()
