from models import Location, Button, Fatal
from bs4 import BeautifulSoup
from os import listdir
from os.path import join, isfile


def set_to_string(s):
    l = list(s)
    l.sort()
    return ''.join(l)


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

        if not rewrite and isfile(file_path):
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
    def import_from_file(self, file_path):
        with open(file_path, 'r') as read_file:
            soup = BeautifulSoup(read_file, 'lxml')
            unparsed_options = soup.find_all('option')
            locations = soup.find_all('loc')
            options = {}

            for opt in unparsed_options:
                options[opt['key']] = opt['char']

            for loc in locations:
                self.add_location(loc, options)

    @classmethod
    def add_location(self, loc, options):
        dsc = str(loc.find(text=True, recursive=False)).strip()
        key = str(loc['key'])

        #print(key)
        require_options = ""
        unrequire_options = ""
        if loc.has_attr('options'):
            #print("Options:", loc['options'])
            require_options, unrequire_options = self.parse_options(loc['options'], options)
            #print(require_options)
            #print(unrequire_options)

        require_options += 'z' * (len(options) - len(require_options))

        location = Location.create(
            key=key, 
            dsc=dsc, 
            require_options=require_options,
            unrequire_options=unrequire_options
            )

        buttons = loc.find_all('btn')
        for btn in buttons:
            self.create_button(btn, location.id, options)

    @classmethod
    def create_button(self, button, loc_id, options):
        description = button.text
        action = button['key']

        append_options = ''
        delete_options = ''
        if button.has_attr('opt'):
            append_options, delete_options = self.parse_options(button['opt'], options)

        require_options = ''
        unrequire_options = ''
        if button.has_attr('req'):
            require_options, unrequire_options = self.parse_options(button['req'], options)

        button = Button.create(
            loc=loc_id, 
            act_key=action, 
            dsc=description,
            require_options=require_options,
            unrequire_options=unrequire_options,
            append_options=append_options,
            delete_options=delete_options
            )

    @classmethod
    def parse_options(self, unparsed_options, options_dict):
        require_options_set = set()
        unrequire_options_set = set()
        for opt in unparsed_options.split():
            if opt[0] == '!':
                #add unrequire_options
                option_char = options_dict[opt[1:]]
                unrequire_options_set.add(option_char)
            else:
                # add require_options
                option_char = options_dict[opt]
                require_options_set.add(option_char)

        require_options = ''
        unrequire_options = ''
        if len(require_options_set) > 0:
            require_options = set_to_string(require_options_set)
        if len(unrequire_options_set) > 0:
            unrequire_options = set_to_string(unrequire_options_set)

        return require_options, unrequire_options

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
