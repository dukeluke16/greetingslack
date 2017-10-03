import websocket
import json
import requests
import urllib
import os
import logging

# Suppress InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

###VARIABLES THAT YOU NEED TO SET MANUALLY IF NOT ON HEROKU#####
try:
    MESSAGE = os.environ['WELCOME-MESSAGE']
    TOKEN = os.environ['SLACK-TOKEN']
    UNFURL = os.environ['UNFURL-LINKS']
    CHANNELS = os.environ['SLACK-CHANNELS']
except:
    MESSAGE = 'Manually set the Message if youre not running through heroku or have not set vars in ENV'
    TOKEN = 'Manually set the API Token if youre not running through heroku or have not set vars in ENV'
    UNFURL = 'FALSE'
    CHANNELS = 'Manually set the Channels if youre not running through heroku or have not set vars in ENV'
###############################################################


def parse_join(message):
    logger = logging.getLogger()
    m = json.loads(message)
    if (m['type'] == "member_joined_channel"):
        logger.info(CHANNELS)
        if (m['channel'] in CHANNELS):
            x = requests.get(
                "https://slack.com/api/im.open?token=" + TOKEN + "&user=" + m["user"])
            x = x.json()
            x = x["channel"]["id"]
            if (UNFURL.lower() == "false"):
                xx = requests.post("https://slack.com/api/chat.postMessage?token=" + TOKEN + "&channel=" +
                                   x + "&text=" + urllib.quote(MESSAGE) + "&parse=full&as_user=true&unfurl_links=false")
            else:
                xx = requests.post("https://slack.com/api/chat.postMessage?token=" + TOKEN + "&channel=" +
                                   x + "&text=" + urllib.quote(MESSAGE) + "&parse=full&as_user=true")
            # DEBUG
            text = "HELLO SENT: " + m["user"]
            logger.info(text)
            #

# Connects to Slacks and initiates socket handshake
def start_rtm():
    r = requests.get(
        "https://slack.com/api/rtm.start?token=" + TOKEN, verify=False)
    logger = logging.getLogger()
    text = r.text
    logger.info(text)
    r = r.json()
    r = r["url"]
    return r


def on_message(ws, message):
    parse_join(message)


def on_error(ws, error):
    logger = logging.getLogger()
    logger.error("SOME ERROR HAS HAPPENED: " + error)


def on_close(ws):
    logger = logging.getLogger()
    logger.warn("Connection Closed")


def on_open(ws):
    logger = logging.getLogger()
    logger.info("Connection Started - Auto Greeting new joiners to the network")


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    r = start_rtm()
    logger.info("WebSocket URL:" + r)

    ws = websocket.WebSocketApp(
        r, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()
