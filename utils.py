from __init__ import BOT_NAME, OFF_CHATS, statistics, bot
import re

import filters


class EveryData:
    def __init__(self):
        self._data = {}
    def get(self, id):
        if not id in seld._data:
            self._data[id] = {}
        return self._data[id]


bot_data = EveryData()


def data_decorator(function):
    def wrapper(*args, **kwargs):
        chat_data = bot_data[args[0].chat.id]
        function(*args, **kwargs)
    return wrapper


hack_dict = {}  # user_id: result


def roll_hack_decorator(user_id):
    """Fast written decorator to roll predicted results
    :param int user_id: Telegram id of user """
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            message = args[0]
            message.hack_result = None
            result = hack_dict.get(user_id)
            if result and message.from_user.id == user_id:
                message.hack_result = result
                hack_dict.pop(user_id)
            function(*args, **kwargs)
        return wrapper
    return real_decorator


def command_access_decorator(user_ids):
    """Decorator which allows us to permit only some users use a command
    :param ids user_ids: Permitted users to use command
    :type ids: list of integers which are Telegram users ids"""
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            message = args[0]
            user_id = message.from_user.id
            if user_id in user_ids:
                function(*args, **kwargs)
            else:
                return None
        return wrapper
    return real_decorator


# Command list handler function
def commands_handler(cmnds, inline=False, switchable=False):

    def wrapped(msg):
        if not msg.text:
            return False
        if switchable and msg.chat.id in OFF_CHATS:
            return False

        split_message = re.split(r'[^\w@\/]', msg.text)
        if not inline:
            s = split_message[0]
            result = (s in cmnds) or (s.endswith(BOT_NAME) and s.split('@')[0] in cmnds)
        else:
            result = any(cmnd in split_message or cmnd + BOT_NAME in split_message for cmnd in cmnds)

        if result:
            statistics.track_by_message(BOT_NAME, 'Command: ' + cmnds[0], msg)
        return result

    return wrapped


def filter_decorator(function):
    def wrapper(*args, **kwargs):
        old_send_message = bot.send_message
        old_reply_to = bot.reply_to
        old_edit = bot.edit_message_text
        filter = filters.get_filter()
        def new_send_message(*_args, **_kwargs):
            _args = list(_args)
            _args[1] = filter(_args[1])
            old_send_message(*_args, **_kwargs)
        def new_reply_to(*_args, **_kwargs):
            _args = list(_args)
            _args[1] = filter(_args[1])
            old_reply_to(*_args, **_kwargs)
        def new_edit(*_args, **_kwargs):
            _args = list(_args)
            _args[1] = filter(_args[1])
            old_edit(*_args, **_kwargs)
        bot.send_message = new_send_message
        bot.reply_to = new_reply_to
        bot.edit_message_text = new_edit
        function(*args, **kwargs)
        bot.send_message = old_send_message
        bot.reply_to = old_reply_to
        bot.edit_message_text = old_edit
    return wrapper


def escape_markdown(text):
    text = text \
        .replace('_', '\\_') \
        .replace('*', '\\*') \
        .replace('[', '\\[') \
        .replace('`', '\\`')
    return text
