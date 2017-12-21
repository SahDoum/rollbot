from __init__ import bot
import time
import random
import threading
from .tower import Tower
from .duel import Duel


DUELS = {}


class DuelView:
    def __init__(self):
        self.messages = []
        self.duel = Duel()


# handler for players shoots
def duel_players_handler(m):
    return m.chat.id in DUELS and \
           DUELS[m.chat.id].duel.active and \
           DUELS[m.chat.id].duel.duel_user(m.from_user)


# handler for other user messages
def duel_chat_handler(m):
    return m.chat.id in DUELS and \
           DUELS[m.chat.id].duel.active and \
           DUELS[m.chat.id].duel.duel_user(m.from_user)


def duel_stub(message):
    return


def duel_shoots(message):
    print('SHOOT')
    chat_duel = DUELS[message.chat.id].duel
    chat_duel.shoot(message)
    if not chat_duel.active:
        chat_duel.update_score(message.chat.id)
        DUELS.pop(message.chat.id)


def duel_start(message):
    chat_id = message.chat.id
    if chat_id not in DUELS:
        DUELS[chat_id] = DuelView()
    chat_duel = DUELS[chat_id].duel
    text = chat_duel.update_with_duel_msg(message)

    if text:
        msg = bot.send_message(chat_id, text, parse_mode='Markdown')
        DUELS[chat_id].messages.append(msg)

    if chat_duel.active:
        t = threading.Thread(target=bomm, args=(message,))
        t.daemon = True
        t.start()
        print(str(DUELS))
        print(str(chat_duel.active))
        print(str(message.chat.id in DUELS))
        return
    else:
        t = threading.Thread(target=leave, args=(message,))
        t.daemon = True
        t.start()


'''
# handler for duelists
bot.message_handler(func=duel_players_handler,
                    content_types=['text'])\
                    (duel_shoots)
# stub during duel
bot.message_handler(func=duel_chat_handler,
                    content_types=['text'])\
                    (duel_stub)
'''


def leave(message):
    delay = 2*60
    time.sleep(delay)
    chat_id = message.chat.id
    if chat_id not in DUELS: return
    chat_duel = DUELS[chat_id].duel
    text = chat_duel.leave_duel()
    if text:
        bot.edit_message_text(chat_id=chat_id,
                              message_id=DUELS[chat_id].messages[-1].message_id,
                              text=text,
                              parse_mode='Markdown')


def bomm(message):
    chat_id = message.chat.id
    chat_duel = DUELS[chat_id].duel
    num_of_bom = 2 + random.randint(0, 10)%7
    text = 'На главной площади города сошлись заклятые враги {} и {}.\n' \
           'Часы начинают отбивать удары. Скоро будет пролита кровь.' \
           'Когда прозвучит последний удар, оба стреляют.\n' \
           'С последним ударом вы увидите символ, которым надо выстрелить.\n' \
           'У кого рука окажется быстрее, тот выиграет дуэль.'.format(chat_duel.name(0), chat_duel.name(1), num_of_bom)
    m = bot.send_message(chat_id, text, parse_mode='Markdown')
    DUELS[chat_id].messages.append(m)

    twr = Tower(num_of_bom)
    time.sleep(5)

    for i in range(num_of_bom):
        text = twr.next_bomm()
        bot.edit_message_text(chat_id=chat_id, message_id=m.message_id, text=text, parse_mode='Markdown')
        time.sleep(random.randint(2, 10))

    duel_symbols = ['!', '$', '%', '^', '&', '*', '(', ')', ',', '§', '~', 'z', 'G', 'F', '-', '=', 'Z', 'l', '😀']
    chat_duel.symbol = random.choice(duel_symbols)
    twr.symbol = chat_duel.symbol
    text = twr.next_bomm()
    bot.edit_message_text(chat_id=chat_id, message_id=m.message_id, text=text, parse_mode='Markdown')
