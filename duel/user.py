import random
from enum import Enum

# ---- DUEL MESSAGES ----

duel_messages = {
    "wait" : [
        '{} стоит на площади и бьет себя кулаком в грудь, ожидая боя!',
        '{} в нетерпении смотрит на часы',
        '{} сдувает со своего плеча пылинку',
    ],

    "new challenge" : [
        'Вызов брошен! Последует ли на него ответ?',
        'Салун затихает, и все ждут, не струсит ли вызываемый',
        'Перчатка брошена, пути назад нет',
    ],

    "new duel" : [
        '{} выходит на главную площадь стреляться. Местные жители попрятались по домам',
        '{} стоит на главной улице. Никто из местных не решается перейти ему дорогу',
        '{} хлопает кружкой о барную стойку и орет, заглушая пианино: "Салаги, я любого из вас застрелю, даже не смейте переходить мне дорогу!"',
        'Все в салуне притихли. Кто-нибудь ответит {} на вызов?',
    ],

    "new enemies" : [
        'Больше вызовов богу вызовов!',
        '{} готов стреляться со всеми!'
    ],

    "accept duel" : [
        '{} принимает вызов!',
        '{} выходит стреляться!',
        '{} не сомневается в своей победе',
    ],

    "leave" : [
        '{} не дожидается противника и уходит в закат',
        'Никто не вышел сражаться с {}. А часовня сегодня уже звонить не будет',
    ],
    
    "kill" : [
        '{} выхватываетсвой пистолет и точным выстрелом убивает противника',
        'Бах! \n{} медленно опускает свой кольт, смотря как его противник истекает кровью'
    ]
}

# ---- USER STATUS ----

class UserStatus(Enum):
    Equiped = 0
    Empty = 1
    Winner = 2

# ---- USER CLASS ----

class User:
    def __init__(self, usr=None, username=None):
        self.status = UserStatus.Equiped
        self.user = usr
        if username:
            self.username = username
            self.id = None
        if usr:
            self.username = usr.username
            self.id = usr.id

    def __eq__(usr1, usr2):
        if usr1.user and usr2.user:
            return usr1.id == usr2.id
        elif usr1.user:
            if usr1.username == usr2.username:
                usr2.user = usr1.user
                usr2.id = usr1.id
                return True
        elif usr2.user:
            if usr2.username == usr1.username:
                usr1.user = usr2.user
                usr1.id = usr2.id
        else:
            return usr1.username == usr2.username
        return False

    def shoot(self, text, symbol):
        if text[0] == symbol \
        and self.status == UserStatus.Equiped:
            self.status = UserStatus.Winner
            return self.duel_message(type='kill')
        elif text[0] == symbol:
            return 'Пистолет разряжен!!!'
        elif self.status == UserStatus.Equiped:
            self.status = UserStatus.Empty
            return 'Мимо!'
        else:
            return 'Патроны кончились!'

    def name(self):
        if self.user:
            return self.user.first_name
        else:
            return '```@' + self.username + '```'

    def link(self):
        if self.user:
            return '[{}](tg://user?id={})'.format(self.user.first_name, self.id)
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

    def duel_message(self, usr_link='', type="wait message"):
        return random.choice(duel_messages[type]).format(self.link(), usr_link)
