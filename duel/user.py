import random

# ---- DUEL MESSAGES ----

wait_messages = [
        '{} стоит на площади и бьет себя кулаком в грудь, ожидая боя!',
        '{} в нетерпении смотрит на часы',
        '{} сдувает со своего плеча пылинку',
    ]

new_challenge_messages = [
        'Вызов брошен! Последует ли на него ответ?',
        'Салун затихает, и все ждут, не струсит ли вызываемый',
        'Перчатка брошена, пути назад нет',
    ]

new_duel_messages = [
        '{} выходит на главную площадь стреляться. Местные жители попрятались по домам',
        '{} стоит на главной улице. Никто из местных не решается перейти ему дорогу',
        '{} хлопает кружкой о барную стойку и орет, заглушая пианино: "Салаги, я любого из вас застрелю, даже не смейте переходить мне дорогу!"'
    ]

new_enemies_messages = [
        'Больше вызовов богу вызовов!'
    ]

accept_duel_messages = [
        '{} принимает вызов!'
    ]

leave_messages = [
        '{} не дожидается противника и уходит в закат'
    ]

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
            return self.user.first_name#'[{}](tg://user?id={})'.format(, self.user.id)
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
        return random.choice(wait_messages).format(self.name())

    def new_challenge(self):
        return random.choice(new_challenge_messages).format(self.name())

    def new_duel_msg(self):
        return random.choice(new_duel_messages).format(self.name())

    def new_enemies_msg(self):
        return random.choice(new_enemies_messages).format(self.name())

    def accept_duel_msg(self):
        return random.choice(accept_duel_messages).format(self.name())

    def leave_msg(self):
        return random.choice(leave_messages).format(self.name())
