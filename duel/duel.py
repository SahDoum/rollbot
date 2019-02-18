from models import DuelUser
from .user import User, UserStatus
from enum import Enum


def enemies_from_message(msg):
    enemies = []
    for ent in msg.entities:
        if ent.type == 'mention':
            enemy_username = msg.text[ent.offset + 1:ent.offset + ent.length]
            enemy = User(username=enemy_username)
            enemies.append(enemy)
        if ent.type == 'text_mention':
            enemy = User(usr=ent.user)
            enemies.append(enemy)
    return enemies


# ---- DUEL STATUS ----

class DuelStatus(Enum):
    Preparing = 0
    Active = 1
    Finished = 2


# ---- DUEL CLASS ----

class Duel:
    delay = 2*60

    def __init__(self):
        self.users = []
        self.enemies = []
        self.status = DuelStatus.Preparing
        self.symbol = None
        
    def __init__(self, users_=[], enemies_=[]):
        self.users = users_
        self.enemies = enemies_
        self.status = DuelStatus.Preparing
        self.symbol = None
        
# ---- starting duel methods ----

    def update_enemies(self, enemies):
        self.enemies += enemies
        if not enemies:
            text = self.users[0].duel_message(type="wait")
        else:
            text = self.users[0].duel_message(type="new enemies")
        return text
        
    def start_duel(self, user):
        text = user.duel_message(type="accept duel")
        self.users.append(user)
        self.status = DuelStatus.Active
        return text

    # вызов на дуэль
    def update_with_msg(self, msg):
        user = User(usr=msg.from_user)
        new_enemies = enemies_from_message(msg)

        print("duel users:", self.users)
        text = None
        
        # если не было вызовов, создадим вызов
        if not self.users:
            print("first challenge by:", user.name())
            self.users.append(user)
            self.enemies += new_enemies
            text = user.duel_message(type="new duel")
        # если пользователь снова вызывает дуэль, обновим вызываемых
        elif user in self.users:
            text = self.update_enemies(new_enemies)
        # если перекрестные вызовы, начнем дуэль
        elif (not self.enemies or user in self.enemies) and \
                (not new_enemies or self.users[0] in new_enemies):
             text = self.start_duel(user)
        # иначе, создадим новую дуэль
        else:
            print("Extra case")
            self = Duel([user], new_enemies)
            text = user.duel_message(type="new duel")
        return text
        
# ---- shooting ----

    def shoot(self, msg):
        if not self.symbol: 
            return

        usr = self.get_duel_user(msg.from_user)
        result = usr.shoot(msg.text, self.symbol)
        return result

    def update_status(self):
        text = None
        for usr in self.users:
            if usr.status == UserStatus.Winner:
                self.status = DuelStatus.Finished
                return None
            if usr.status == UserStatus.Equiped:
                return None
        self.status = DuelStatus.Finished
        return 'Оба стрелка промахнулись. Дуэль окончена без жертв.'
 
    def leave_duel(self):
        if not self.status == DuelStatus.Preparing:
            return None
        if not self.users: 
            return None

        text = self.users[0].duel_message(type="leave")

        self.users = []
        self.enemies = []

        return text
        
# ---- extra methods ----

    def update_score(self, chat_id):
        if all(user.status != UserStatus.Winner for user in self.users):
            for usr in self.users:
                duel_usr = DuelUser.login(chat_id, usr.user.id)
                duel_usr.name = usr.name()
                duel_usr.ties = duel_usr.ties + 1
                duel_usr.save()
            return
        for usr in self.users:
            duel_usr = DuelUser.login(chat_id, usr.user.id)
            duel_usr.name = usr.name()
            if usr.status == UserStatus.Winner:
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
