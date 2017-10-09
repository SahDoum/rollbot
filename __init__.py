import re
import logging
import telebot
from settings import API_TOKEN1


# Command list handler function
def commands_handler(cmnds, inline=False):
    BOT_NAME = '@rollclub_bot'

    def wrapped(msg):
        if not msg.text:
            return False
        split_message = re.split(r'[^\w@\/]', msg.text)
        if not inline:
            s = split_message[0]
            return (s in cmnds) or (s.endswith(BOT_NAME) and s.split('@')[0] in cmnds)
        else:
            return any(cmnd in split_message or cmnd + BOT_NAME in split_message for cmnd in cmnds)

    return wrapped


logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(API_TOKEN1, threaded=False)
