from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
import time
import threading
import sys
import logging
import re

from settings import API_TOKEN1
import telebot

import fatal
import dice

import random
from bs4 import BeautifulSoup


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

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN1, threaded=False)

# ---- DUEL ----


class Duel:
    def __init__(self):
        self.users = []
        self.status = [0, 0]
        self.active = False
        self.symbol = None

    def init_with_msg(self, msg):
        first_user = self.handle_user(msg.from_user)
        self.users.append(first_user)
        print('Init with message: first usr: ' + str(first_user))

        if not hasattr(msg, 'entities'):
            return

        for ent in msg.entities:
            if ent.type == 'mention':
                second_user = msg.text[ent.offset+1:ent.offset+ent.length]
                break
            if ent.type == 'text_mention':
                second_user = ent.user
                break

        if not self.compare_users(first_user, second_user):
            self.users.append(second_user)
            print('Second usr: ' + str(second_user))

    @staticmethod
    def handle_user(usr):
        if hasattr(usr, 'username') and \
           usr.username is not None:
            return usr.username
        else:
            return usr

    @staticmethod
    def compare_users(usr1, usr2):
        if hasattr(usr1, 'id') and hasattr(usr2, 'id') :
            return usr1.id == usr2.id
        if hasattr(usr1, 'username'):
            return usr1.username == usr2
        if hasattr(usr2, 'username'):
            return usr2.username == usr1
        return usr1 == usr2

    def name(self, usr_num):
        usr = self.users[usr_num] # self.first_usr if usr_num == 1 else self.second_usr
        if hasattr(usr, 'first_name'):
            return '<a href="tg://user?id={}">{}</a>'.format(usr.id, usr.first_name)
        else:
            return '@'+usr

    def usr_num(self, user):
        try:
            num = self.users.index(user.username)
            return num
        except Exception:
            pass

        for i in range(len(self.users)):
            usr = self.users[i]
            if hasattr(usr, 'id') and usr.id == user.id:
                return i

        return -1


DUELS = {}


# Handle shoots of players
@bot.message_handler(func=lambda m: m.chat.id in DUELS and
                                    DUELS[m.chat.id].symbol and
                                    DUELS[m.chat.id].usr_num(m.from_user) != -1,
                     content_types=['text'])
def duel_shoots(message):
    duel = DUELS[message.chat.id]

    num = duel.usr_num(message.from_user)
    if message.text[0] == duel.symbol:
        if duel.status[num] == 0:
            duel.status[num] = 1
            duel.symbol = None
            bot.reply_to(message,
                         '{} выхватывает свой пистолет ' \
                         'и точным выстрелом убивает противника!'.format(duel.name(num)),
                         parse_mode='HTML')
            DUELS.pop(message.chat.id)
        else:
            bot.reply_to(message, 'Пистолет разряжен!!!')
    else:
        if duel.status[num] == 0:
            duel.status[num] = -1
            bot.reply_to(message, 'Осечка!')
            if not 0 in duel.status:
                bot.send_message(message.chat.id, 'Оба стрелка промахнулись. Дуэль окончена без жертв.')
                DUELS.pop(message.chat.id)
        else:
            bot.reply_to(message, 'Патроны кончились!')


# Handle all messages during duel
@bot.message_handler(func=lambda m: m.chat.id in DUELS and
                                    DUELS[m.chat.id].active and
                                    DUELS[m.chat.id].usr_num(m.from_user) == -1,
                     content_types=['text'])
def duel_stub(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Дуэль в процессе, не мешай ей!')


# Handle '/duel'
@bot.message_handler(func=commands_handler(['/duel'], inline=True))
def duel_start(message):
    chat_id = message.chat.id
    duel = DUELS[chat_id] if chat_id in DUELS else None

    # если чувака вызвали на дуэль и он вызвал команду, дуэль начинается
    if duel and \
       duel.compare_users(message.from_user, duel.users[1]) and \
       not duel.active:
        duel.active = True
        t = threading.Thread(target=bomm, args=(message,))
        t.daemon = True
        t.start()
        return

    # иначе, создаем новую дуэль
    duel = Duel()
    duel.init_with_msg(message)
    if len(duel.users) == 2:
        DUELS[chat_id] = duel
        bot.send_message(chat_id, 'Вызов брошен! Последует ли на него ответ?')
    else:
        bot.reply_to(message, 'Надо упомянуть противника, которому кидаешь вызов!')


def bomm(message):
    chat_id = message.chat.id
    duel = DUELS[chat_id]
    num_of_bom = 5 + random.randint(0, 4)
    text = 'На главной площади города сошлись заклятые враги {} и {}.\n' \
           'Часы бьют <b>{} часов</b>. ' \
           'Когда прозвучит последний удар, оба стреляют.\n' \
           'С последним ударом вы увидите символ, которым надо выстрелить.\n' \
           'У кого рука окажется быстрее, тот выиграет дуэль.'.format(duel.name(0), duel.name(1), num_of_bom)
    bot.send_message(chat_id, text, parse_mode='HTML')

    for i in range(num_of_bom):
        time.sleep(random.randint(2, 10))
        bot.send_message(chat_id, 'Б{}М'.format('О' * random.randint(1, 10)))

    duel_symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ',', '№', '§', '~', 'ё', 'й', 'z', 'G', 'F', '😀', '🤣', '😱']
    duel.symbol = random.choice(duel_symbols)
    bot.send_message(chat_id, 'Стреляйтесь: ' + duel.symbol)

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
        ''' 
        fatal.Editor.delete_all()

        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        with open('locations.xml', 'wb') as new_file:
            new_file.write(file)
        with open('locations.xml', 'r') as read_file:
            fatal.Editor.import_from_file(read_file)
        '''
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
