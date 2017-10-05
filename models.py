from peewee import *

database = SqliteDatabase('database.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database


class RCButton(BaseModel):
    act_key = CharField(null=True)
    dsc = TextField(null=True)
    loc = IntegerField(db_column='loc_id', null=True)

    class Meta:
        db_table = 'rollclub_buttons'

class RCLocation(BaseModel):
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

