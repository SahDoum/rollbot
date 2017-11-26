from peewee import *

database = SqliteDatabase('data/database.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database


class Button(BaseModel):
    act_key = CharField(null=True)
    dsc = TextField(null=True)
    loc = IntegerField(db_column='loc_id', null=True)

    class Meta:
        db_table = 'rollclub_buttons'


class Location(BaseModel):
    dsc = TextField(null=True)
    key = CharField(null=True)

    class Meta:
        db_table = 'rollclub_locations'


class SqliteSequence(BaseModel):
    name = UnknownField(null=True)  # 
    seq = UnknownField(null=True)  # 

    class Meta:
        db_table = 'sqlite_sequence'
        primary_key = False


class DuelUser(BaseModel):
    user_id = IntegerField()
    chat_id = IntegerField()
    name = TextField()

    wins = IntegerField()
    losses = IntegerField()
    ties = IntegerField()

    class Meta:
        db_table = 'duel_users'

    @staticmethod
    def login(chat_id, user_id):
        try:
            usr = DuelUser.select().where((DuelUser.chat_id == chat_id) & (DuelUser.user_id == user_id)).get()
            return usr
        except:
            return DuelUser.create(user_id=user_id,
                                   chat_id=chat_id,
                                   name='',
                                   wins=0,
                                   ties=0,
                                   losses=0)
"""
DuelUser.drop_table()
database.create_tables([DuelUser])
"""
