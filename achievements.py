from pychievements import tracker, Achievement
from pychievements.signals import receiver, goal_achieved, highest_level_achieved
from pychievements.backends import SQLiteAchievementBackend


def simple_quest_achievement_factory(name, description, unique_keyword):    
    goals = (
        {'level': 1, 'name': name,'description': description},
    )
    attrs = {'name': name, 'category': 'quest',
             'keywords': ('quest', unique_keyword),
             'goals': goals}
    new_achievement = type(unique_keyword, (Achievement,), attrs)
    return new_achievement


def init_achievements():
    db_name = "data/achievements.db"
    backend = SQLiteAchievementBackend(db_name)
    tracker.set_backend(backend)
    for dsc in get_achievement_descriptions():
        ach = simple_quest_achievement_factory(dsc['name'], dsc['description'], dsc['unique_keyword'])
        tracker.register(ach)


def get_achievement_descriptions():
    achievements = [
            {'name' : 'Убийца драконов',
             'description' : 'Хорошо собраться в поход и убить змия!',
             'unique_keyword' : 'dragon_killer'
            },
            {'name' : 'Судьба Феникса',
             'description' : 'Отправиться в безнадежное приключение с Фениксом',
             'unique_keyword' : 'phoenix_friend'
            },
            {'name' : 'Вор из Гастона',
             'description' : 'Украсть драгоценности в Башне трех мудрецов',
             'unique_keyword' : 'robber_of_tower_of_the_three_wise_man'
            },
            {'name' : 'Тесей',
             'description' : 'Выбраться из лабиринта',
             'unique_keyword' : 'maze_escape'
            },
            {'name' : 'Старший тестировщик ВегаРолл',
             'description' : 'Найти секретную концовку в симуляции',
             'unique_keyword' : 'simulation_win'
            },
            {'name' : 'Ценитель прекрасного',
             'description' : 'Поймать нимфу',
             'unique_keyword' : 'lake_nen_win'
            },
            {'name' : 'Небинарный',
             'description' : 'Выпить зелье троллиной похоти',
             'unique_keyword' : 'tavern_troll_sex'
            },
        ]
    return achievements
