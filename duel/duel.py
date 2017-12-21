from __init__ import bot
import time
from models import DuelUser


# ---- DUEL CLASS ----

class Duel:
    delay = 2*60

    def __init__(self):
        self.users = []
        self.enemies = []
        self.active = False
        self.symbol = None
        self.time = time.time()

    # вызов на дуэль
    def update_with_duel_msg(self, msg):
        # print('{} - {}'.format(time.time(), self.time))
        # if time.time() - self.time > self.delay:
        #     self.users = []
        #     self.enemies = []
        #     print("Сброс настроек по времени")

        user = User(msg.from_user)
        new_enemies = []
        for ent in msg.entities:
            if ent.type == 'mention':
                enemy_username = msg.text[ent.offset + 1:ent.offset + ent.length]
                enemy = User(enemy_username)
                new_enemies.append(enemy)
            if ent.type == 'text_mention':
                enemy = User(ent.user)
                new_enemies.append(enemy)

        text = None

        # если кто-то новый вызывает дуэль
        if user not in self.users:
            # перезапись дуэли
            if len(self.enemies) > 0 and user not in self.enemies or \
               len(new_enemies) > 0 and len(self.users) > 0 and self.users[0] not in new_enemies:
                self.enemies = []
                self.users = []
                print('New duel initiation by: ' + str(user))

            if len(self.users) > 0:
                text = user.accept_duel_msg()
            elif len(new_enemies) > 0:
                text = user.new_challenge()
            else:
                text = user.new_duel_msg()
            self.users.append(user)

        elif len(new_enemies) == 0:
            text = user.wait_msg()
        else:
            text = user.new_enemies_msg()

        self.enemies.extend(new_enemies)
        self.time = time.time()

        print('Duel initiation by: ' + str(user))

        if len(self.users) > 1:
            self.active = True
            print('Start duel: ' + str(user))

        return text

    # выстрел
    def shoot(self, msg):
        if not self.symbol: return

        usr = self.duel_user(msg.from_user)
        result = usr.shoot(msg.text, self.symbol)
        bot.reply_to(msg, result, parse_mode='Markdown')

        if usr.status == 1:
            self.symbol = None
            self.active = False
        else:
            if all(user.status != 0 for user in self.users): # не должно работать
                bot.send_message(msg.chat.id, 'Оба стрелка промахнулись. Дуэль окончена без жертв.')
                self.active = False

        if not self.active:
            # self.update_score()
            print('Duel end')

    # покинуть дуэль
    def leave_duel(self):
        if self.active: return None
        if len(self.users) == 0: return None

        text = self.users[0].leave_msg()

        self.users = []
        self.enemies = []

        return text

    # обновление счета
    def update_score(self, chat_id):
        if all(user.status != 1 for user in self.users):
            for usr in self.users:
                duel_usr = DuelUser.login(chat_id, usr.user.id)
                duel_usr.name = usr.name()
                duel_usr.ties = duel_usr.ties + 1
                duel_usr.save()
            return
        for usr in self.users:
            duel_usr = DuelUser.login(chat_id, usr.user.id)
            duel_usr.name = usr.name()
            if usr.status == 1:
                duel_usr.wins = duel_usr.wins + 1
            else:
                duel_usr.losses = duel_usr.losses + 1
            duel_usr.save()

    # дополнительные функции
    def name(self, usr_num):
        return self.users[usr_num].name()

    def duel_user(self, user):
        search = User(user)
        for i in self.users:
            if search == i:
                return i
        return None

# ---- USER CLASS ----

class User:
    def __init__(self, usr):
        self.status = 0
        if isinstance(usr, str):
            self.username = usr
        else:
            self.user = usr

    def __eq__(usr1, usr2):
        if hasattr(usr1, 'user') and hasattr(usr2, 'user') :
            return usr1.user.id == usr2.user.id
        elif hasattr(usr1, 'user'):
            if usr1.user.username == usr2.username:
                usr2.user = usr1.user
                return True
        elif hasattr(usr2, 'user'):
            if usr2.user.username == usr1.username:
                usr1.user = usr2.user
        else:
            return usr1.username == usr2.username
        return False

    def shoot(self, text, symbol):
        if text[0] == symbol and self.status == 0:
            self.status = 1
            return '{} выхватывает свой пистолет и точным выстрелом убивает противника!'.format(self.name())
        elif text[0] == symbol:
            return 'Пистолет разряжен!!!'
        elif self.status == 0:
            self.status = -1
            return 'Мимо!'
        else:
            return 'Патроны кончились!'

    def name(self):
        if hasattr(self, 'user'):
            return '[{}](tg://user?id={})'.format(self.user.first_name, self.user.id)
        else:
            return '@' + self.username

    def stats_name(self):
        name = '*' + self.user.first_name + ' '
        if hasattr(self.user, 'last_name'):
            name += self.user.last_name + ' '
        name += '* '
        if hasattr(self.user, 'username'):
            name += self.user.username + ' '
        return name

    def wait_msg(self):
        return '{} стоит на площади и бьет себя кулаком в грудь, ожидая боя!'.format(self.name())

    def new_challenge(self):
        return 'Вызов брошен! Последует ли на него ответ?'

    def new_duel_msg(self):
        return '{} выходит на главную площадь стреляться. Местные жители попрятались по домам'.format(self.name())

    def new_enemies_msg(self):
        return 'Больше вызовов богу вызовов!'

    def accept_duel_msg(self):
        return '{} принимает вызов!'.format(self.name())

    def leave_msg(self):
        return '{} не дожидается противника и уходит.'.format(self.name())
