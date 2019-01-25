from models import Location, Button, Fatal
from bs4 import BeautifulSoup
from os import listdir
from os.path import join, isfile


class Editor:

    @classmethod
    def __init__(self, path='data/'):
        self.path = path

    @classmethod
    def delete_all(self):
        if not Fatal.select().first():
            return
        Fatal.delete().execute()

    @classmethod
    def add_file(self, file, file_name='fatal.xml', rewrite=True):
        file_path = self.path + file_name

        if not rewrite and isfile(fname):
            return ''

        with open(file_path, 'wb') as new_file:
            new_file.write(file)
        return file_path

    @classmethod
    def import_files_from_directory(self):
        directory = [self.path + f for f in listdir(self.path) if not f.startswith('.')]
        files = [f for f in directory if isfile(f)]

        for file in files:
            self.import_from_file(file)

    @classmethod
    def import_from_file(self, file_path):
        with open(file_path, 'r') as read_file:
            soup = BeautifulSoup(read_file, 'lxml')
            locations = soup.find_all('loc')

            for loc in locations:
                self.add_location(loc)

    @classmethod
    def add_location(self, loc):
        dsc = str(loc.find(text=True, recursive=False)).strip()
        location = Fatal.create(dsc=dsc)


class QuestEditor(Editor):

    @classmethod
    def delete_all(self):
        if not Location.select().first():
            return
        Location.delete().execute()
        Button.delete().execute()

    @classmethod
    def add_location(self,loc):
        dsc = str(loc.find(text=True, recursive=False)).strip()
        key = str(loc['key'])
        location = Location.create(key=key, dsc=dsc)
        loc_id = location.id
        buttons = loc.find_all('btn')
        for btn in buttons:
            btn_dsc = btn.text
            btn_act = btn['key']
            button = Button.create(loc=loc_id, act_key=btn_act, dsc=btn_dsc)

    @classmethod
    def is_correct(self):
        max_button_description = 100
        errlog = ""
        correct = True
        for btn in Button.select():
            ways_from_button = Location.select().where(Location.key == loc_key)
            if not ways_from_button.exists():
                correct = False
                button_location = Location.get(Location.id == btn.loc)
                error = "Error: No ways from button {}:{} at location {}:{}\n".format(btn.act_key, btn.dsc, loc.key, loc.dsc)
                errlog += error
            if len(btn.dsc) > max_button_description:
                warning = "Warning: Button {}:{} description is too big\n".format(btn.act_key, btn.dsc)
                errlog += warning

        return correct, errlog
