from __init__ import BOT_NAME, OFF_CHATS

#import sys
#sys.path.append("../statistics display")
#import bot_statistics as statistics

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

        #if result:
            #statistics.track_by_message(BOT_NAME, 'Command: ' + cmnds[0], msg)
        return result

    return wrapped


def escape_markdown(text):
    text = text \
        .replace('_', '\\_') \
        .replace('*', '\\*') \
        .replace('[', '\\[') \
        .replace('`', '\\`')
    return text
