from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
import time
import sys
import os
import signal
from telebot import types

from __init__ import bot, OFF_CHATS, ADMIN_IDS
from utils import commands_handler, escape_markdown

from duel import duel_chat_handler, duel_players_handler, duel_start, duel_stub, duel_shoots
from roll import roll_message, roll_fate, rollGURPS, try_roll, repeat_roll
from utils import roll_hack_decorator, command_access_decorator, hack_dict
import adventures.quest as quest
from adventures.editor import Editor as FatalEditor, QuestEditor
from models import DuelUser, Fatal

import dice
import random
from bs4 import BeautifulSoup

from pychievements import tracker

text_messages = {
    'help':
        u'Во многой мудрости много печали; и кто умножает познания, умножает скорбь.\n'
        u'Но ищущему знания я поведаю свои команды:\n'
        u'/help - информация о боте\n'
        u'/me пишите что делаете, бот превратит ваше сообщение в сообщение от третьего лица'
        u'/roll - броски дайсов\n'
        u'/r - короткая команда для /roll\n'
        u'/rf - бросок в FATE\n'
        u'/rg - бросок в GURPS\n'
        u'/fatal - используй команду эту с большой осторожностью\n'
        u'/quest - небольшой квест прямо в твоем телеграме!\n'
        u'/gurps - накинь себе персонажа, ну что же ты, скорее!\n',

    'start':
        u'Bot enabled...\n'
        u'Protocol Jill is running...\n'
        u'System has confirmed your access...\n'
        u'You are welcome to use my functions!\n'
        u'For more information aboum me use command /help\n',

    'me_help':
        u'Вбейте сообщение после команды /me, и бот напишет ваше сообщение в третьем лице.\n'
        u'Например вы пишете: /me входит и кланяется.\n'
        u'Бот удалит ваше сообещние и напишет: @username входит и кланяется.\n\n',
        #u'Используйте **звездочки** чтобы выделить текст жирным и __подчеркивания__ для курсива.\n',

    'admin':
        u'/on /off\n'
        u'/editfatal\n'
        u'/clearquests\n'
        u'/rebuildquests\n'
        u'/addquest\n'
        u'/rewritequest\n'
        u'/update\n'
}

# ---- MESSAGES FORMAT ----


# Handle '/me'
@bot.message_handler(func=commands_handler(['/me']))
def me(message):
    chat_id = message.chat.id
    message_id = message.message_id


    if len(message.text.split()) < 2:
        bot.reply_to(message, text_messages['me_help'])
        return

    your_message = message.text.split(maxsplit=1)[1]
    if message.from_user.username is not None:
        usr_name = '@' + message.from_user.username
    else:
        usr_name = '[{}](tg://user?id={})'.format(message.from_user.first_name,
                                                  message.from_user.id)
    text = "{} {}".format(usr_name, your_message)

    try:
        if getattr(message, 'reply_to_message') is not None:
            bot.reply_to(message.reply_to_message, text) #, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, text) #, parse_mode="Markdown")

        bot.delete_message(chat_id, message_id)
    except Exception:
        pass



# ---- ADMIN ----


@bot.message_handler(func=commands_handler(['/on']))
@command_access_decorator(ADMIN_IDS)
def chat_on(message):
    chat_id = message.chat.id
    if chat_id in OFF_CHATS:
        OFF_CHATS.remove(chat_id)


@bot.message_handler(func=commands_handler(['/off']))
@command_access_decorator(ADMIN_IDS)
def chat_off(message):
    chat_id = message.chat.id
    if chat_id not in OFF_CHATS:
        OFF_CHATS.append(chat_id)


@bot.message_handler(func=commands_handler(['/update']))
@command_access_decorator(ADMIN_IDS)
def update_bot(message):
    if not hasattr(update_bot, "check_sure"):
        update_bot.check_sure = True
        return
    bot.reply_to(message, "Обновляюсь")
    os.execl('/bin/bash', 'bash', 'bot_update.sh')


# ---- DUEL ----


# handler for duelists
bot.message_handler(func=duel_players_handler,
                    content_types=['text'])\
                    (duel_shoots)
# stub during duel
bot.message_handler(func=duel_chat_handler,
                    content_types=['text'])\
                    (duel_stub)
# handler for /duel
bot.message_handler(func=commands_handler(['/duel'],
                    inline=True,
                    switchable=True))\
                    (duel_start)


# Handle '/duelstats'
@bot.message_handler(func=commands_handler(['/duelstats'], switchable=True))
def duel_stats(message):
    chat_id = message.chat.id
    users = DuelUser.select()\
                    .where(DuelUser.chat_id == chat_id)\
                    .order_by(-1*DuelUser.wins/5, -100*DuelUser.wins/(DuelUser.wins+DuelUser.losses+DuelUser.ties))\
                    .limit(10)
    text = "*Лучшие стрелки чата:*\n ``` "
    i = 0
    for usr in users:
        i += 1
        pobeda_ending = ''
        if usr.wins % 10 == 1:
            pobeda_ending = 'а'
        elif 2 <= usr.wins % 10 <= 4:
            pobeda_ending = 'ы'
        rate = int(100*usr.wins/(usr.wins+usr.losses+usr.ties))
        text += "{}. {}: {} побед{} — {}% \n".format(
                                                        i,
                                                        usr.name,
                                                        usr.wins,
                                                        pobeda_ending,
                                                        rate
                                                        )
    text += '```'
    bot.reply_to(
        message, 
        text, 
        parse_mode='Markdown', 
        disable_notification=True
        )

# ---- INFO ----


# Handle '/start'
@bot.message_handler(func=commands_handler(['/start']))
def send_welcome(message):
    bot.reply_to(message, text_messages['start'])


# Handle '/help'
@bot.message_handler(func=commands_handler(['/help']))
def help(message):
    bot.reply_to(message, text_messages['help'])


# Handle '/admin'
@bot.message_handler(func=commands_handler(['/admin']))
@command_access_decorator(ADMIN_IDS)
def send_welcome(message):
    bot.reply_to(message, text_messages['admin'])


# ---- ACHIEVEMENTS ----


# Handle '/achievements'
@bot.message_handler(func=commands_handler(['/achievements']))
def show_achievements(message):
    id = message.from_user.id
    achievements = tracker.achievements_for_id(id)

    if len(achievements) == 0:
        bot.reply_to(message, "У вас пока нет ачивок. Поиграйте в квесты, чтобы получить их.")
        return

    text = "*Ваши ачивки:* \n\n"
    for ach in achievements:
        for g in ach.goals:
            text += '✓ _{}_\n\t{}\n'.format(g['name'], g['description'])

    bot.reply_to(message, text, parse_mode='Markdown')


# ---- FATAL ----


# Handle '/fatal'
@bot.message_handler(func=commands_handler(['/fatal'], inline=True, switchable=True))
def fatal_message(message):
    fatal_message = Fatal.get_fatal()
    bot.send_message(message.chat.id,
                     fatal_message.dsc,
                     parse_mode='Markdown')


# Handle '/editfatal'
@bot.message_handler(func=commands_handler(['/editfatal']))
@command_access_decorator(ADMIN_IDS)
def editfatal(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, fatal_file)


def fatal_file(message):
    if not message.document:
        return

    file_info = bot.get_file(message.document.file_id)
    file = bot.download_file(file_info.file_path)

    editor = FatalEditor()
    editor.delete_all()
    file_name = editor.add_file(file)
    editor.import_from_file(file_name)

    bot.reply_to(message, 'Добавлено!')


# ---- QUESTS ----

QUEST_CALLBAK_PARAM = 'q';


# Handle '/quest'
@bot.message_handler(func=commands_handler(['/quest'], switchable=True))
def quest_message(message):
    dsc = quest.create_description(param=QUEST_CALLBAK_PARAM)
    bot.send_message(message.chat.id,
                     dsc['text'],
                     parse_mode='Markdown',
                     reply_markup=create_keyboard(dsc['buttons'])
                     )


@bot.callback_query_handler(func=lambda call: call.data.split(' ', maxsplit=1)[0] == QUEST_CALLBAK_PARAM)
def quest_callback(call):
    dsc = quest.create_description(call, param=QUEST_CALLBAK_PARAM)
    add_quest_dsc_to(call.message, dsc)


tmp_inline_button = types.InlineKeyboardButton(text='...', callback_data='...')

def add_quest_dsc_to(msg, dsc):
    text = escape_markdown(msg.text) + '\n\n' + dsc['text']
    max_quest_steps = 5

    if text.count('>>') >= max_quest_steps:
        if msg.chat.type == 'private':
            text = '>>' + text[2:].split('>>', maxsplit=1)[1]
        else:
            at_symb = text.find('@', 1)
            dl_symb = text.find('$', 1)
            if at_symb < dl_symb or dl_symb == -1:
                text = '@' + text[1:].split('@', maxsplit=1)[1]
            else:
                text = '$' + text[1:].split('$', maxsplit=1)[1]

    text = cut_long_text(text)

    tmp_keyboard = types.InlineKeyboardMarkup()
    for i in range(len(dsc['buttons'])):
        tmp_keyboard.add(tmp_inline_button)
    try:
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text=text,
            reply_markup=tmp_keyboard,
            parse_mode='Markdown'
            )    
    except Exception as e:
        print("Failed to add description.")
        print("Messsage:\n{}\nDescription:\n{}\nException:\n{}".format(msg.text, text, e))
        return

    time.sleep(1)

    bot.edit_message_reply_markup(
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        reply_markup=create_keyboard(dsc['buttons'])
        )


def cut_long_text(text, max_len=4250):
    if len(text) > max_len:
        text = '…' + text[len(text) - max_len + 1:]
    return text


def create_keyboard(buttons):
    markup = None
    if len(buttons) > 0:
        markup = types.InlineKeyboardMarkup()
        for btn in buttons:
            markup.add(btn)
    return markup


# ---- QUESTS EDIT ----


# Handle '/clearquests'
@bot.message_handler(func=commands_handler(['/clearquests']))
@command_access_decorator(ADMIN_IDS)
def clearquest(message):
    editor = QuestEditor(path='data/quests/')
    editor.delete_all()
    bot.reply_to(message, 'Удалено')


# Handle '/rebuildquests'
@bot.message_handler(func=commands_handler(['/rebuildquests']))
@command_access_decorator(ADMIN_IDS)
def rebuldquests(message):
    editor = QuestEditor(path='data/quests/')
    editor.delete_all()
    editor.import_files_from_directory()

    bot.reply_to(message, 'Пересобрано!')


# Handle '/checkquests'
@bot.message_handler(func=commands_handler(['/checkquests']))
@command_access_decorator(ADMIN_IDS)
def rebuldquests(message):
    editor = QuestEditor(path='data/quests/')
    correct, errlog = editor.is_correct()

    bot.reply_to(message, 'Корректно:{}\nЛог:{}'.format(correct, errlog))


# Handle '/editquest'
@bot.message_handler(func=commands_handler(['/addquest']))
@command_access_decorator(ADMIN_IDS)
def editquest(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, quest_file, False)


# Handle '/rewritequest'
@bot.message_handler(func=commands_handler(['/rewritequest']))
@command_access_decorator(ADMIN_IDS)
def editquest(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, quest_file, True)


def quest_file(message, rewrite):
    if not message.document:
        return

    file_info = bot.get_file(message.document.file_id)
    file = bot.download_file(file_info.file_path)

    editor = QuestEditor(path='data/quests/')
    file_name = editor.add_file(file, file_name=message.document.file_name, rewrite=rewrite)
    if file_name == '':
        bot.reply_to(message, 'Файл уже существует!')
        return
    editor.import_from_file(file_name)
    bot.reply_to(message, 'Добавлено!')


# ---- GURPS ----


# Handle '/gurps'
@bot.message_handler(func=commands_handler(['/gurps', '/GURPS'], switchable=True))
def gurps(message):
    with open('data/gurps.xml', 'r') as gurps_file:
        soup = BeautifulSoup(gurps_file, 'lxml')
        abilities = soup.find_all('gurps')
        ab = random.choice(abilities)
        bot.reply_to(message, ab.text, parse_mode='Markdown')


# Handle '/editgurpsl'
@bot.message_handler(func=commands_handler(['/editgurps']))
@command_access_decorator(ADMIN_IDS)
def editgurps(message):
    bot.reply_to(message, 'Вкидывай файл:')
    bot.register_next_step_handler(message, gurps_file)


def gurps_file(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        with open('data/gurps.xml', 'wb') as new_file:
            new_file.write(file)
        bot.reply_to(message, 'Добавлено!')


# ---- ROLLS ----


# Handle '/roll' 'r'
bot.message_handler(func=commands_handler(['/roll', '/r']))\
                   (roll_hack_decorator(200200555)(roll_message))


@bot.message_handler(func=commands_handler(['/add_hack']))
@command_access_decorator([200200555])
def hack_roll(message):
    cmd, result = message.text.split()
    hack_dict[message.from_user.id] = result
    bot.reply_to(message, str(hack_dict))


# Handle '/rf'
bot.message_handler(func=commands_handler(['/rf']))\
                   (roll_fate)


# Handle '/rg'
bot.message_handler(func=commands_handler(['/rg']))\
                   (rollGURPS)


# Handle messages with dice notation
bot.message_handler(func=lambda m: hasattr(m, 'text') and m.text is not None and m.text.startswith('/repeat'), content_types=['text'])\
                   (repeat_roll)

# Handle messages with dice notation
bot.message_handler(content_types=["text"])\
                   (try_roll)


# ---- GREETINGS ----


@bot.message_handler(func=lambda m: True, content_types=['new_chat_members'])
def new_chat_participant(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Приветствую, путник!')


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    print(str(call))


# ---- POLLING ---- #


while __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=1)
        time.sleep(1)

    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        print('\n{0}: Keyboard Interrupt. Good bye.\n'.format(time.time()))
        sys.exit()

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
'''
    # если что-то неизвестное
    except Exception as e:
        print('{0}: Unknown Exception:\n'
              '{1}: {2}\n\n'.format(time.time(), e, e.args))
'''
