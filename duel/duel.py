from models import DuelUser
from .user import User


def enemies_from_message(message):
    enemies = []
    for ent in msg.entities:
        if ent.type == 'mention':
            enemy_username = msg.text[ent.offset + 1:ent.offset + ent.length]
            enemy = User(username=enemy_username)
            enemies.append(enemy)
        if ent.type == 'text_mention':
            enemy = User(usr=ent.user)
            enemies.append(enemy)
    return emenies
    

# ---- DUEL CLASS ----

class Duel:
    delay = 2*60

    def __init__(self, users=[], enemies=[]):
        self.users = users
        self.enemies = enemies
        self.active = False
        self.symbol = None
        
    def update(self, enemies):
        self.enemies.append(enemies)
        elif not new_enemies:
            text = self.users[0].duel_message(type="wait")
        else:
            text = self.users[0].duel_message(type="new enemies")
        return text
        
    def start(self, user):
        text = user.duel_message(type="accept duel")
        self.users.append(user)
        self.active = True
        print('Start duel: ' + str(user))

        return text

    # вызов на дуэль
    def update_with_msg(self, msg):
        user = User(usr=msg.from_user)
        new_enemies = enemies_from_message(msg)

        text = None
        # если пользователь снова вызывает дуэль
        if user in users:
            text = self.update(new_enemies)
            # обновить дуэль
        # если перекрестные вызовы
        elif (user in self.enemies or not self.enemies) and \
             (self.users[0] in new_enemies or not new enemies):
             text = self.start(user)
           # начать дуэль
        else:
            self = Duel([user], new_enemies)
            text = user.duel_message(type="new duel")
            # создать новую дуэль
        return text

    def shoot(self, msg):
        if not self.symbol: 
            return

        usr = self.get_duel_user(msg.from_user)
        result = usr.shoot(msg.text, self.symbol)
        return result

    def update_status(self, msg):
        text = None
        for usr in self.users:
            if usr.status == 1:
                self.active = False
            if not user.status == -1:
                self.active = False
                text = 'Оба стрелка промахнулись. Дуэль окончена без жертв.'
        if not self.active:
            print('Duel end')
        return text

    def leave_duel(self):
        if self.active: return None
        if not self.users: return None

        text = self.users[0].duel_message(type="leave")

        self.users = []
        self.enemies = []

        return text

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

    def name(self, usr_num):
        return self.users[usr_num].name()

    def link(self, usr_num):
        return self.users[usr_num].link()

    def get_duel_user(self, user):
        search = User(user)
        for i in self.users:
            if search == i:
                return i
        return None
