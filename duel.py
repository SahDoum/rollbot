from __init__ import bot, commands_handler
import time
import random
import threading
from models import DuelUser


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

        second_user = None
        for ent in msg.entities:
            if ent.type == 'mention':
                second_user = msg.text[ent.offset+1:ent.offset+ent.length]
                #second_user = bot.get_chat_member()
                break
            if ent.type == 'text_mention':
                second_user = ent.user
                break

        if True or second_user and not self.compare_users(first_user, second_user):
            self.users.append(second_user)
            print('Second usr: ' + str(second_user))

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

    # def update_statistic_with_winner(self, winner_num):
        # winner_usr = self.users.pop(winner_num)
        # lose_usr = self.users.pop()


DUELS = {}

# handler for players shoots
duel_players_handler = lambda m: m.chat.id in DUELS and \
                                 DUELS[m.chat.id].active and \
                                 DUELS[m.chat.id].usr_num(m.from_user) != -1

# handler for other user messages
duel_chat_handler = lambda m: m.chat.id in DUELS and \
                              DUELS[m.chat.id].active and \
                              DUELS[m.chat.id].usr_num(m.from_user) == -1

# Handle shoots of players
@bot.message_handler(func=duel_players_handler,
                     content_types=['text'])
def duel_shoots(message):
    duel = DUELS[message.chat.id]

    if not duel.symbol: return

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
            print('Duel end')
        else:
            bot.reply_to(message, 'Пистолет разряжен!!!')
    else:
        if duel.status[num] == 0:
            duel.status[num] = -1
            bot.reply_to(message, 'Осечка!')
            if not 0 in duel.status:
                bot.send_message(message.chat.id, 'Оба стрелка промахнулись. Дуэль окончена без жертв.')
                print('Duel end')
                DUELS.pop(message.chat.id)
        else:
            bot.reply_to(message, 'Патроны кончились!')


# Handle all messages during duel
@bot.message_handler(func=duel_chat_handler,
                     content_types=['text'])
def duel_stub(message):
    chat_id = message.chat.id
    #bot.send_message(chat_id, 'Дуэль в процессе, не мешай ей!')


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
    m = bot.send_message(chat_id, text, parse_mode='HTML')

    tower = Tower(num_of_bom)

    for i in range(num_of_bom):
        time.sleep(random.randint(2, 10))
        text = tower.next_bomm()
        bot.edit_message_text(chat_id=chat_id, message_id=m.message_id, text=text, parse_mode='Markdown')

    duel_symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ',', '№', '§', '~', 'ё', 'й', 'z', 'G', 'F', '😀', '🤣', '😱']
    duel.symbol = random.choice(duel_symbols)
    tower.symbol = duel.symbol
    text = tower.next_bomm()
    bot.edit_message_text(chat_id=chat_id, message_id=m.message_id, text=text, parse_mode='Markdown')


class Tower:
    lines = {0:0, 1:2, 2:4, 3:5, 4:8, 5:10, 6:11, 7:12 , 8:13, 9:14}

    def __init__(self, max_time=0):
        self.time = 0
        self.max_time = max_time
        self.tower = get_empty_tower()
        self.symbol = None

    def next_bomm(self):
        text = None
        if self.time == self.max_time:
            text = 'Патрон: ' + self.symbol
        line = self.time + 1 # Tower.lines[self.time]
        add_text_to_tower(self.tower, line, text)
        tower = add_clock(self.tower, self.time + 1, str(self.max_time-self.time))
        self.time += 1
        return '```\n' + '\n'.join(tower) + '```'


def get_empty_tower():
    height = 15
    length = 13
    tower = []
    for i in range(0, height):
        s = ' ' * length
        if i == height-1:
            s = '-' * length
        tower.append(ascii_tower[i] + s)
    return tower


def add_text_to_tower(tower, line, text=None):
    if not text:
        text = 'Б' + 'О' * random.randint(1, 5) + 'М'
    length = 13
    start = 12
    # if length > len(text):
    #     start = random.randint(0, length - len(text)-1)
    tower[line] = tower[line][:start] + text + tower[line][start+len(text):]
    return tower


def add_clock(tower, time, max_time=None):
    time = time % 8
    length = 0 # 13

    clock_x = 5
    clock_y = 3
    clock_symbol = '@'

    clock_x += length
    new_tower = list(tower)
    if max_time:
        str = tower[clock_y]
        new_tower[clock_y] = str[:clock_x] + max_time + str[clock_x+1:]

    if time == 0:
        clock_symbol = '|'
        clock_y -= 1
    if time == 1:
        clock_symbol = '/'
        clock_x += 1
        clock_y -= 1
    if time == 2:
        clock_symbol = '-'
        clock_x += 2
    if time == 3:
        clock_symbol = '\\'
        clock_x += 1
        clock_y += 1
    if time == 4:
        clock_symbol = '|'
        clock_y += 1
    if time == 5:
        clock_symbol = '/'
        clock_x -= 1
        clock_y += 1
    if time == 6:
        clock_symbol = '-'
        clock_x -= 2
    if time == 7:
        clock_symbol = '\\'
        clock_x -= 1
        clock_y -= 1

    str = new_tower[clock_y]
    new_tower[clock_y] = str[:clock_x] + clock_symbol + str[clock_x+1:]

    return new_tower


ascii_tower = [
    '/         \\',
    '| 11 12 1 |',
    '|10      2|',
    '|9   @   3|',
    '|8       4|',
    '|  7 6 5  |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '-----------'
]