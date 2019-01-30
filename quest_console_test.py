import adventures.quest as quest
import adventures.editor as editor

import optparse

quest.LOG_MODE = True

class Callback:
    def __init__(self, callback):
        self.data = callback


def print_quest_dsc(dsc, log):
    print(dsc['text'])
    for num, btn in enumerate(dsc['buttons']):
        print('{}) {}'.format(num, btn.text))
        if log:
            print(btn.callback_data)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-l", "--log", action='store_true', dest="log", help="Logging")
    options, args = parser.parse_args()

    print(args)

    editor = editor.QuestEditor(path='../data/quests/')
    editor.delete_all()
    for file_name in args:
        editor.import_from_file(file_name)


    dsc = quest.create_description()
    print_quest_dsc(dsc, options.log)

    while True:
        next = int(input())
        callback = Callback(dsc['buttons'][next].callback_data)
        dsc = quest.create_description(callback)
        print_quest_dsc(dsc, options.log)
