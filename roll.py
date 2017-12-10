from __init__ import bot
import dice
import signal

# ---- ROLLS ----


REPEAT_ROLLS = {}


# Handle '/roll' 'r'
def roll_message(message):
    arg = message.text.split(' ', maxsplit=1)
    if len(arg) > 1:
        if message.hack_result:
            bot.reply_to(message, "Вы выкинули:\n" + "[%s]" % str(message.hack_result))
        else:
            roll(arg[1], message)
    else:
        with open('data/dice_info.md', 'r') as info_file:
            bot.reply_to(message, info_file.read(), parse_mode='Markdown')


# Handle '/rf'
def roll_fate(message):
    roll = dice.roll('4d3')
    result = 0
    text = u"Вы выкинули:\n"
    for i in roll:
        if i == 1:
            text += "[-]"
        elif i == 2:
            text += "[0]"
        else:
            text += "[+]"
        result += i-2

    arg = message.text.split(' ')
    if len(arg) > 1:
        text += "+"+arg[1]
        result += int(arg[1])

    text += '=\n{0}'.format(result)
    bot.reply_to(message, text)


# Handle '/rg'
def rollGURPS(message):
    arg = message.text.split(' ')
    roll = dice.roll('3d6t')
    text = str(roll)
    if len(arg) > 1:
        if roll > int(arg[1]):
            text += " > "+arg[1]+u"\nПровал"
        else:
            text += " ≤ "+arg[1]+u"\nУспех"
    bot.reply_to(message, text)


def try_roll(message):
    text = message.text
    try:
        int(text)
        return
    except:
        pass

    roll(text, message)


def repeat_roll(message):
    print('repeat')
    chat_id = message.chat.id
    roll_id = int(message.text[7:].split('@')[0])
    print(roll_id)

    if chat_id not in REPEAT_ROLLS:
        return
    if roll_id not in REPEAT_ROLLS[chat_id]:
        return

    roll(REPEAT_ROLLS[chat_id][roll_id], message)


def roll(arg, reply_msg):
    ongoing = True

    def handler(signum, frame):
        if ongoing:
            raise TimeoutError("end of time")
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(5)

    try:
        result = dice.roll(arg)
        repeat_command = add_repeat(arg, reply_msg.chat.id, reply_msg.message_id)
        bot.reply_to(reply_msg, "Вы выкинули:\n" + str(result) + repeat_command)
    except TimeoutError:
        bot.reply_to(reply_msg, "Впредь без рекурсии, будьте аккуратнее.\n")
    except Exception as e:
        # print('Dice error: ' + str(e))
        pass
    finally:
        ongoing = False


def add_repeat(arg, chat_id, roll_id):
    if chat_id not in REPEAT_ROLLS:
        REPEAT_ROLLS[chat_id] = {}
    REPEAT_ROLLS[chat_id][roll_id] = arg
    return '\n /repeat{}'.format(roll_id)
