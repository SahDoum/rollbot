from peewee import *

database = SqliteDatabase('data/database.db', **{})


class BaseModel(Model):
    class Meta:
        database = database


class Button(BaseModel):
    act_key = CharField(null=True)
    dsc = TextField(null=True)
    loc = IntegerField(db_column='loc_id', null=True)
    require_options = CharField(null=True)
    unrequire_options = CharField(null=True)
    append_options = CharField(null=True)
    delete_options = CharField(null=True)

    class Meta:
        db_table = 'rollclub_buttons'

    @staticmethod
    def select_with_options(loc_id, options):
        options_set = set(options)
        result = []
        for btn in Button.select().where(Button.loc == loc_id):
            if not options_set.issuperset(set(btn.require_options)):
                continue
            if not options_set.isdisjoint(set(btn.unrequire_options)):
                continue
            result.append(btn)
        return result

    def update_options(self, options):
        opt = set(options)
        opt.update(set(self.append_options))
        opt.difference_update(set(self.delete_options))
        l = list(opt)
        l.sort()
        return ''.join(l)


class Location(BaseModel):
    dsc = TextField(null=True)
    key = CharField(null=True)
    require_options = CharField(null=True)
    unrequire_options = CharField(null=True)

    class Meta:
        db_table = 'rollclub_locations'

    @staticmethod
    def get_with_options(loc_key, options):
        preselect = Location.select().where(Location.key == loc_key)
        all_options = set()
        for loc in preselect:
            all_options.update(set(loc.require_options))
            
        select = Location.select_with_options(loc_key, options, all_options - options - {'z'}, preselect)
        return select.order_by(fn.Random()).get()

    @staticmethod
    def get_default():
        return Location.select().where(Location.key == 'default').order_by(fn.Random()).get()

    @staticmethod
    def select_with_options(loc_key, options, dop_options, select):

        # select without unrequired options
        # deselect withput required options
        # sort by required leksigraphiccaly
        # get max
        # select by max required options

        for opt in options:
            select = select.where(~(Location.unrequire_options.contains(opt)))

        for opt in dop_options:
            select = select.where(~(Location.require_options.contains(opt)))

        select = select.order_by(Location.require_options)
        max_require = select.get().require_options
        return select.where(Location.require_options == max_require)


class Fatal(BaseModel):
    dsc = TextField(null=True)

    class Meta:
        db_table = 'fatal'

    @staticmethod
    def get_fatal():
        return Fatal.select().order_by(fn.Random()).get()


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



if __name__ == '__main__':
    Button.drop_table()
    Location.drop_table()
    database.create_tables([Fatal, Button, Location])
