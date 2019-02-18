from .duel_view import DuelView, DUELS
from .duel import DuelStatus

# ---- DUEL HANDLERS ----

# handler for players shoots
def duel_players_handler(m):
    return m.chat.id in DUELS and \
           DUELS[m.chat.id].duel.status == DuelStatus.Active and \
           DUELS[m.chat.id].duel.get_duel_user(m.from_user)


# handler for other user messages
def duel_chat_handler(m):
    return m.chat.id in DUELS and \
           DUELS[m.chat.id].duel.status == DuelStatus.Active


# ---- DUEL WRAPPERS ----
# called only if duel active


def duel_stub(message):
    return
    

def duel_shoots(message):
    print('SHOOT')
    chat_duel = DUELS[message.chat.id]
    chat_duel.shoot(message)
    if chat_duel.duel.status == DuelStatus.Finished:
        chat_duel.duel.update_score(message.chat.id)
        DUELS.pop(message.chat.id)
        print("duel end")


def duel_challenge(message):
    chat_id = message.chat.id
    if chat_id not in DUELS:
        print("creating new duel")
        DUELS[chat_id] = DuelView()
    DUELS[chat_id].update(message)
