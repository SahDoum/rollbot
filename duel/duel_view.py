from __init__ import bot
import time
import random
import threading
from .tower import Tower
from .duel import Duel, DuelStatus


DUELS = {}
DUEL_SYMBOLS = ['!', '$', '%', '^', 'Y', '1', '*', '(', ')', ',', 'v', '~', 'z', 'G', 'F', '-', '=', 'Z', 'l', '😀']


class DuelView:
    def __init__(self):
        self.duel = Duel([], [])
        self.tower = None
        self.time = time.time()
        
    def update(self, message):
        if self.duel.status is not DuelStatus.Preparing:
            return
            
        text = self.duel.update_with_msg(message)
        if text:
            msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')

        if self.duel.status == DuelStatus.Active:
            t = threading.Thread(target=self.start, args=(message,))
            t.daemon = True
            t.start()
            
            print("Starting duel")
            print(str(message.chat.id))
        else:
            t = threading.Thread(target=self.leave, args=(message,))
            t.daemon = True
            t.start()
    
    def leave(self, message):
        time.sleep(self.duel.delay)
        
        if self.duel.status is not DuelStatus.Preparing:
            return
            
        if message.chat.id in DUELS:
            DUELS.pop(message.chat.id)
        
        text = self.duel.leave_duel()
        bot.send_message(
                chat_id=message.chat.id,
                text=text,
                parse_mode='Markdown'
                )

    def start(self, message):
        chat_id = message.chat.id
        num_of_boms = 2 + random.randint(0, 10) % 7
    
        text = self.duel.get_start_text()
        m = bot.send_message(chat_id, text, parse_mode='Markdown')
        time.sleep(15)
        
        self.tower = Tower(num_of_boms)
        for i in range(num_of_boms):
            self.bomm(m)
            
        self.shooting(m)
        
    def bomm(self, m):
        text = self.tower.next_bomm()
        bot.edit_message_text(
                chat_id=m.chat.id, 
                message_id=m.message_id, 
                text=text, 
                parse_mode='Markdown'
                )
        time.sleep(random.randint(2, 10))
        
    def shooting(self, msg):
        symbol = random.choice(DUEL_SYMBOLS)
        self.duel.symbol = symbol
        self.tower.symbol = symbol
        
        text = self.tower.next_bomm()
        bot.edit_message_text(
            chat_id=msg.chat.id, 
            message_id=msg.message_id, 
            text=text, 
            parse_mode='Markdown'
            )
            
    def shoot(self, msg):
        if not self.duel.symbol:
            return

        text = self.duel.shoot(msg)
        if text:
            bot.send_message(msg.chat.id, text, parse_mode='Markdown')
        
        text = self.duel.update_status()
        if text:
            bot.send_message(msg.chat.id, text, parse_mode='Markdown')
            
        if self.duel.status == DuelStatus.Finished:
            print("End duel")
