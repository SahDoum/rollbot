from models import Location, Button
from telebot import types
# from telegram.utils.helpers import escape_markdown

def create_description(callback=None, param='q'):
    options = ''
    loc_key = 'default'

    if callback:
        args = callback.data.split()
        btn_id = int(args[1])
        if len(args) > 2:
            options = args[2]

        btn = Button.get(Button.id == btn_id)
        loc_key = btn.act_key
        options = btn.update_options(options)

        if loc_key == 'default':
            return {
                    'text': callback_title(callback),
                    'buttons': None, # Why None ? types.InlineKeyboardMarkup()
                    }

    loc = Location.get_with_options(loc_key, set(options)) #.where(Location.key == loc_key).order_by(fn.Random()).get()
    btn_list = None
    btn_list = Button.select_with_options(loc.id, options)#.where(Button.loc == loc.id)

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
    if callback.message.chat.type != 'private':
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


def escape_markdown(str):
    return str.replace('_', '\_')
