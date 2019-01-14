from bs4 import BeautifulSoup
from models import Location, Button, Fatal


class Editor:

    @classmethod
    def delete_all(self):
        if not Fatal.select().first():
            continue
        Fatal.delete().execute()

    @classmethod
    def import_from_file(self, file):
        soup = BeautifulSoup(file, 'lxml')
        locations = soup.find_all('loc')

        for loc in locations:
            Editor.add_location(loc)

    @classmethod
    def add_location(self, loc):
        dsc = str(loc.find(text=True, recursive=False)).strip()
        location = Fatal.create(dsc=dsc)


class QuestEditor(Editor):

    @staticmethod
    def delete_all():
        if not Location.select().first():
            return
        Location.delete().execute()
        Button.delete().execute()

    @staticmethod
    def add_location(loc):
        dsc = str(loc.find(text=True, recursive=False)).strip()
        key = str(loc['key'])
        location = Location.create(key=key, dsc=dsc)
        loc_id = location.id
        buttons = loc.find_all('btn')
        print(location)
        for btn in buttons:
            btn_dsc = btn.text
            btn_act = btn['key']
            button = Button.create(loc=loc_id, act_key=btn_act, dsc=btn_dsc)
            print(button)

