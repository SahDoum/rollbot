from __init__ import bot
import time
from models import DuelUser
from user import User


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
