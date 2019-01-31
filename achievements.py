from pychievements import tracker, Achievement
from pychievements.signals import receiver, goal_achieved, highest_level_achieved
from pychievements.backends import SQLiteAchievementBackend

from pychievements.cli import print_goal, print_goals_for_tracked
from pychievements import icons

class PartAchievement(Achievement):
    big_achievement_class_type = None

class AchievmentWithParts(Achievement):
    part_achievement_class_name = ''


@receiver(goal_achieved)
def check_multiple_achievment(tracked_id, achievement, goals, **kwargs):
    print("knjdsknjd")
    if not isinstance(achievement, PartAchievement):
        print(type(achievement))
        return
    #may be move to class method 
    ach = tracker.achievements_for_id(tracked_id, keywords=achievement.keywords, category='quest_part')
    big_ach = tracker.achievement_for_id(tracked_id, achievement.big_achievement_class_type)
    tracker.set_level(tracked_id, big_ach, len(ach))


def simple_achievement_factory(name, 
                               dsc, 
                               keywords=[], 
                               class_name=None, 
                               superclass_type=Achievement, 
                               category='quest'):  
    if not class_name:
        class_name = keywords[1]  
    goals = [{'level': 1, 'name': name, 'description': dsc}]
    attrs = {'name': name, 'category': category,
             'keywords': keywords, 'goals': goals}
    return type(class_name, (superclass_type,), attrs)


def part_achievement_factory(keywords=[], 
                             class_name='', 
                             category='quest_part',
                             big_type=Achievement):   
    goals = [{'level': 1}]
    attrs = {'name': '', 'category': category,
             'keywords': keywords, 'goals': goals, 'big_achievement_class_type': big_type}
    
    return type(class_name, (PartAchievement,), attrs)


def achievement_with_part_factory(name, description, final_description, unique_keyword, number_of_parts): 
    # generate goals for big achievment
    # may be move to init method of class
    goals = []
    for i in range(number_of_parts-1):
        subname = '{} ({}/{})'.format(name, i+1, number_of_parts)
        goals.append({'level': i+1, 'name': subname, 'description': description})
    subname = '{} ({}/{})'.format(name, number_of_parts, number_of_parts)
    goals.append({'level': number_of_parts, 'name': subname, 'description': final_description})
    print("GOALS:", goals)
    
    attrs = {'name': name, 'category': 'quest',
             'keywords': ('quest', unique_keyword),
             'goals': goals}
    new_achievement = type(unique_keyword, (AchievmentWithParts,), attrs)

    # generate part achievments    
    for i in range(number_of_parts):
        class_name = unique_keyword + '_' + str(i+1)
        print(class_name)
        ach = part_achievement_factory(
                                        keywords=[unique_keyword, 'quest_part'], 
                                        class_name=class_name, 
                                        category='quest_part',
                                        big_type=new_achievement
                                        )
        print(ach)
        tracker.register(ach)

    return new_achievement


def init_achievements():
    db_name = "data/achievements.db"
    backend = SQLiteAchievementBackend(db_name)
    tracker.set_backend(backend)
    
    for dsc in get_simple_achievement_descriptions():
        ach = simple_achievement_factory(dsc['name'], dsc['description'], ['quest', dsc['unique_keyword']])
        tracker.register(ach)

    for dsc in get_part_achievement_descriptions():
        ach = achievement_with_part_factory(dsc['name'], dsc['description'], dsc['final_description'], dsc['unique_keyword'], dsc['number_of_parts'])
        tracker.register(ach)


def get_simple_achievement_descriptions():
    achievements = [
            {'name' : 'Убийца драконов',
             'description' : 'Хорошо собраться в поход и убить змия!',
             'unique_keyword' : 'dragon_killer',
            },
            {'name' : 'Судьба Феникса',
             'description' : 'Отправиться в безнадежное приключение с Фениксом',
             'unique_keyword' : 'phoenix_friend',
            },
            {'name' : 'Вор из Гастона',
             'description' : 'Украсть драгоценности в Башне трех мудрецов',
             'unique_keyword' : 'robber_of_tower_of_the_three_wise_man',
            },
            {'name' : 'Тесей',
             'description' : 'Выбраться из лабиринта',
             'unique_keyword' : 'maze_escape',
            },
            {'name' : 'Старший тестировщик ВегаРолл',
             'description' : 'Найти секретную концовку в симуляции',
             'unique_keyword' : 'simulation_win',
            },
            {'name' : 'Ценитель прекрасного',
             'description' : 'Поймать нимфу',
             'unique_keyword' : 'lake_nen_win',
            },
            {'name' : 'Небинарный',
             'description' : 'Выпить зелье троллиной похоти',
             'unique_keyword' : 'tavern_troll_sex'
            },
            {'name' : 'Бесшумный убийца',
             'description' : 'Сделать работу без лишнего шума',
             'unique_keyword' : 'silent_killer'
            },
        ]
    return achievements

def get_part_achievement_descriptions():
    achievements = [
            {'name' : 'Исследователь',
             'description' : 'На пути познания',
             'final_description' : 'Познать все доступные миры',
             'unique_keyword' : 'discoverer',
             'number_of_parts' : 11,
            },
        ]
    return achievements

def test():
    test_id=155493213
    tracker.increment(test_id, 'test_keyword_part0')
    tracker.increment(test_id, 'test_keyword_part1')
    tracker.increment(test_id, 'test_keyword_part2')
    #tracker.increment(test_id, 'test_keyword_part3')
    #tracker.increment(test_id, 'test_keyword_part4')

if __name__ == "__main__":
    init_achievements()
    print_goals_for_tracked(test_id, achieved=True, unachieved=True, only_current=False, level=False)
