from __init__ import bot
import time
import random
import threading
from .tower import Tower
from  .duel import Duel


DUELS = {}


# handler for players shoots
def duel_players_handler(m): m.chat.id in DUELS and \
                             DUELS[m.chat.id].active and \
                             DUELS[m.chat.id].duel_user(m.from_user)


# handler for other user messages
def duel_chat_handler(m): m.chat.id in DUELS and \
                          DUELS[m.chat.id].active and \
                          DUELS[m.chat.id].duel_user(m.from_user)


def duel_stub(message):
    return


def duel_shoots(message):
    chat_duel = DUELS[message.chat.id]
    chat_duel.shoot(message)
    if not chat_duel.active:
        chat_duel.update_score(message.chat.id)
        DUELS.pop(message.chat.id)


def duel_start(message):
    chat_id = message.chat.id
    if chat_id not in DUELS:
        DUELS[chat_id] = Duel()
    chat_duel = DUELS[chat_id]
    chat_duel.update_with_duel_msg(message)

    if chat_duel.active:
        t = threading.Thread(target=bomm, args=(message,))
        t.daemon = True
        t.start()
        return


def bomm(message):
    chat_id = message.chat.id
    duel = DUELS[chat_id]
    num_of_bom = 2 + random.randint(0, 10)%7
    text = 'На главной площади города сошлись заклятые враги {} и {}.\n' \
           'Часы начинают отбивать удары. Скоро будет пролита кровь.' \
           'Когда прозвучит последний удар, оба стреляют.\n' \
           'С последним ударом вы увидите символ, которым надо выстрелить.\n' \
           'У кого рука окажется быстрее, тот выиграет дуэль.'.format(duel.name(0), duel.name(1), num_of_bom)
    m = bot.send_message(chat_id, text, parse_mode='Markdown')

    twr = Tower(num_of_bom)
    time.sleep(5)

    for i in range(num_of_bom):
        text = twr.next_bomm()
        bot.edit_message_text(chat_id=chat_id, message_id=m.message_id, text=text, parse_mode='Markdown')
        time.sleep(random.randint(2, 10))

    duel_symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ',', '№', '§', '~', 'ё', 'й', 'z', 'G', 'F', '😀', '🤣', '😱']
    duel.symbol = random.choice(duel_symbols)
    twr.symbol = duel.symbol
    text = twr.next_bomm()
    bot.edit_message_text(chat_id=chat_id, message_id=m.message_id, text=text, parse_mode='Markdown')
