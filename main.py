##### main.py #####

def main():
  print("[Starting script...]")
  from bot import start_bot_server
  from web import keep_alive

  keep_alive()
  start_bot_server()

try:
  main()
except ImportError:
  from os import system as cmd
  print("[+] Installing from requirements.txt")
  cmd("pip install -r requirements.txt")
  main()
