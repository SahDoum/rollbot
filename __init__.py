import logging
import telebot
from achievements import init_achievements

#import sys
#sys.path.append("../statistics display")
#import bot_statistics as statistics

from data.settings import API_TOKEN1

ADMIN_IDS = [155493213, 120046977]
OFF_CHATS = [-1001119348463]
BOT_NAME = '@rollclub_bot'
#statistics.init_track(BOT_NAME)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(API_TOKEN1, threaded=False)
init_achievements()
