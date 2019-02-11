from duel_view import DuelView, DUELS

# ---- DUEL HANDLERS ----

# handler for players shoots
def duel_players_handler(m):
    return m.chat.id in DUELS and \
           DUELS[m.chat.id].duel.active and \
           DUELS[m.chat.id].duel.duel_user(m.from_user)


# handler for other user messages
def duel_chat_handler(m):
    return m.chat.id in DUELS and \
           DUELS[m.chat.id].duel.active


# handler for all messages
def duel_stub(message):
    return
    

# ---- DUEL WRAPPER ----


def duel_shoots(message):
    print('SHOOT')
    chat_duel = DUELS[message.chat.id].duel
    chat_duel.shoot(message)
    if not chat_duel.active:
        chat_duel.update_score(message.chat.id)
        DUELS.pop(message.chat.id)


def duel_challenge(message):
    chat_id = message.chat.id
    if chat_id not in DUELS:
        DUELS[chat_id] = DuelView()
    DUELS[chat_id].update(message)
