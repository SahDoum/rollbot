from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
import time
import sys

from __init__ import bot, commands_handler

import fatal
import dice

import random
from bs4 import BeautifulSoup




text_messages = {
    'help':
        u'Во многой мудрости много печали; и кто умножает познания, умножает скорбь.\n'
        u'Но ищущему знания я поведаю свои команды:\n'
        u'/help - информация о боте\n'
        u'/roll - броски дайсов\n'
        u'/r - короткая команда для /roll\n'
        u'/rf - бросок в FATE\n'
        u'/rg - бросок в GURPS\n'
        u'/fatal - используй команду эту с большой осторожностью\n'
        u'/gurps - накинь себе персонажа, ну что же ты, скорее!\n',

    'start':
        u'Bot enabled...\n'
        u'Protocol alpha is running...\n'
        u'System has confirmed your access...\n'
        u'You are welcome to use!\n'
        u'For more information use command /help\n'
}

# ---- DUEL ----


import duel


# ---- INFO ----


# Handle '/start'
@bot.message_handler(func=commands_handler(['/start']))
def send_welcome(message):
    bot.reply_to(message, text_messages['start'])


# Handle '/help'
@bot.message_handler(func=commands_handler(['/help']))
def help(message):
    bot.reply_to(message, text_messages['help'])

# ---- FATAL ----


# Handle '/fatal'
@bot.message_handler(func=commands_handler(['/fatal']))
def fatal_message(message):
    # title = ''
    # if message.chat.type != 'private':
    #         title = fatal.user_to_author(message.from_user)
    # title += '*>> /fatal*\n\n'

    dsc = fatal.create_description()
    bot.send_message(message.chat.id,
                     dsc['text'],
                     parse_mode='Markdown',
                     reply_markup=dsc['buttons'])


@bot.callback_query_handler(func=lambda call: call.data.split(' ')[0] == 'f')
def fatal_callback(call):
    dsc = fatal.create_description(call)
    add_fatal_dsc_to(call.message, dsc)


def add_fatal_dsc_to(msg, dsc):
    text = fatal.escape_markdown(msg.text) + '\n\n' + dsc['text']
    if text.count('>>') >= 3:
        if msg.chat.type == 'private':
            text = '>>' + text[2:].split('>>', maxsplit=1)[1]
        else:
            at_symb = text.find('@', 1)
            dl_symb = text.find('$', 1)
            if at_symb < dl_symb or dl_symb == -1:
                text = '@' + text[1:].split('@', maxsplit=1)[1]
            else:
                text = '$' + text[1:].split('$', maxsplit=1)[1]

    bot.edit_message_text(
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        text=text,
        reply_markup=dsc['buttons'],
        parse_mode='Markdown'
        )


# Handle '/editfatal'
@bot.message_handler(func=commands_handler(['/editfatal']))
def editfatal(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, fatal_file)


def fatal_file(message):
    if message.document:

        fatal.Editor.delete_all()

        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        with open('locations.xml', 'wb') as new_file:
            new_file.write(file)
        with open('locations.xml', 'r') as read_file:
            fatal.Editor.import_from_file(read_file)

        bot.reply_to(message, 'Добавлено!')

# ---- ----
# ---- Different rolls ----


# Handle '/roll' 'r'
@bot.message_handler(func=commands_handler(['/roll', '/r']))
def roll(message):
    arg = message.text.split(' ')
    if len(arg) > 1:
        try:
            result = dice.roll(arg[1])
            bot.reply_to(message, "Вы выкинули:\n"+str(result))
        except:
            bot.reply_to(message, "Неправильное выражение.")
    else:
        bot.reply_to(message, u'Вжух:\n'+str(dice.roll('4d6')))


# Handle '/rf'
@bot.message_handler(func=commands_handler(['/rf']))
def rollFate(message):
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
@bot.message_handler(func=commands_handler(['/rg']))
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


# ---- GURPS ----


# Handle '/gurps'
@bot.message_handler(func=commands_handler(['/gurps', '/GURPS']))
def gurps(message):
    with open('gurps.xml', 'r') as gurps_file:
        soup = BeautifulSoup(gurps_file, 'lxml')
        abilities = soup.find_all('gurps')
        ab = random.choice(abilities)
        bot.reply_to(message, ab.text, parse_mode='Markdown')


# Handle '/editgurpsl'
@bot.message_handler(func=commands_handler(['/editgurps']))
def editgurps(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, gurps_file)


def gurps_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        with open('gurps.xml', 'wb') as new_file:
            new_file.write(file)
        bot.reply_to(message, 'Добавлено!')

# ---- NOT-COMAND HANDLERS ---- #


@bot.message_handler(func=lambda m: True, content_types=['new_chat_members'])
def new_chat_participant(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Приветствую, путник!')


# ---- POLLING ---- #

while __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=1)
        time.sleep(1)

    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout as e:
        print('{0}: Read Timeout. Because of Telegram API.\n '
              'We are offline. Reconnecting in 5 seconds.\n'.format(time.time()))
        time.sleep(5)

    # если пропало соединение, то пытаемся снова через минуту
    except ConnectionError as e:
        print('{0}: Connection Error.\n'
              'We are offline. Reconnecting in 60 seconds.\n'.format(time.time()))
        time.sleep(60)

    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        print('{0}: Runtime Error.\n'
              'Retrying in 3 seconds.\n'.format(time.time()))
        time.sleep(3)

    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        print('\n{0}: Keyboard Interrupt. Good bye.\n'.format(time.time()))
        sys.exit()

    # если что-то неизвестное — от греха вырубаем с корнем. Создаём алёрт файл для .sh скрипта
    except Exception as e:
        print('{0}: Unknown Exception:\n'
              '{1}: {2}\n\n'
              'Shutting down.'.format(time.time(), str(e), e.args))
