from models import Location, Button
from utils import escape_markdown
from telebot import types

from pychievements import tracker


LOG_MODE = False


def create_description(callback=None, param='q'):
    options = ''
    if callback:
        args = callback.data.split()
        btn_id = int(args[1])
        if len(args) > 2:
            options = args[2]

        btn = Button.get(Button.id == btn_id)
        loc_key = btn.act_key

        if loc_key == 'default': # end of a quest
            return {
                    'text': callback_title(callback),
                    'buttons': None,
                    }

        options = btn.update_options(options)
        loc = Location.get_with_options(loc_key, set(options))
    else:
        loc = Location.get_default()

    check_achievement(loc, callback)

    btn_list = None
    btn_list = Button.select_with_options(loc.id, options)
    dsc_title = callback_title(callback)
    text = dsc_title + loc.dsc
    buttons = create_keyboard(btn_list, options, param)
    dsc = {'text': text, 'buttons': buttons}
    return dsc


def create_keyboard(btn_list, options, param='q'):
    buttons = []
    if btn_list:
        for btn in btn_list:
            inline_button = types.InlineKeyboardButton(
                text=btn.dsc,
                callback_data= param + ' ' + str(btn.id) + ' ' + options
                )
            buttons.append(inline_button)
    return buttons


def callback_title(callback):
    if not callback:
        return ''

    author = ''
    if not LOG_MODE and callback.message.chat.type != 'private':
        author = user_to_author(callback.from_user)
    btn_id = int(callback.data.split(' ')[1])
    btn = Button.get(Button.id == btn_id)
    title = author + '*>> ' + btn.dsc + '*\n\n'
    return title


def user_to_author(usr):
    if usr.username:
        author = '@' + usr.username + ' '
    else:
        author = '$ ' + usr.first_name + ' '
    return escape_markdown(author)


def check_achievement(location, callback):
    if not location.achievement or not callback:
        return

    print(tracker.achievements())
    print(location.achievement)

    id = callback.from_user.id
    tracker.evaluate(id, location.achievement, 0, 1)
