from models import Location, Button

from telebot import types

# from telegram.utils.helpers import escape_markdown


def create_description(callback=None, param='q'):
    if callback:
        btn_id = int(callback.data.split(' ')[1])
        btn = Button.get(Button.id == btn_id)
        loc_key = btn.act_key

        if loc_key == 'default':
            return {'text': callback_title(callback),
                    'buttons': None
                    }
    else:
        loc_key = 'default'

    loc = Location.select().where(Location.key == loc_key).order_by(fn.Rand()).get()
    btn_list = Button.select().where(Button.loc == loc.id)

    dsc_title = callback_title(callback)
    text = dsc_title + loc.dsc
    markup = create_keyboard(btn_list, param)
    dsc = {'text': text, 'buttons': markup}
    return dsc


def create_keyboard(btn_list, param='q'):
    markup = None
    if btn_list:
        markup = types.InlineKeyboardMarkup()
        for btn in btn_list:
            inline_button = types.InlineKeyboardButton(
                text=btn.dsc,
                callback_data= param + " " + str(btn.id)
                )
            markup.add(inline_button)
    return markup


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
