from models import Location, Button, Fatal
from bs4 import BeautifulSoup
import os.path


class Editor:

    @classmethod
    def __init__(self, path='data/'):
        self.path = path
        return self

    @classmethod
    def delete_all(self):
        if not Fatal.select().first():
            continue
        Fatal.delete().execute()

    @classmethod
    def add_file(self, file, file_name='fatal.xml', rewrite=true):
        file_path = self.path + file_name

        if not rewrite and os.path.isfile(fname):
            return ''

        with open(file_path, 'wb') as new_file:
            new_file.write(file)
        return file_path

    @classmethod
    def import_files_from_directory(self):
        files = [f for f in join(path, os.path.listdir(path)) if os.path.isfile(f)]

        for file in files:
            QuestEditor().import_from_file(file)

    @classmethod
    def import_from_file(self, file_path):
        with open(file_path, 'r') as read_file:
            soup = BeautifulSoup(read_file, 'lxml')
            locations = soup.find_all('loc')

            for loc in locations:
                Editor.add_location(loc)

    @classmethod
    def add_location(self, loc):
        dsc = str(loc.find(text=True, recursive=False)).strip()
        location = Fatal.create(dsc=dsc)


class QuestEditor(Editor):

    @classmethod
    def delete_all():
        if not Location.select().first():
            return
        Location.delete().execute()
        Button.delete().execute()

    @classmethod
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

