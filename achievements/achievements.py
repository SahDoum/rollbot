from .tracker import tracker
from data.achievements_data import achievements

from pychievements import Achievement
from pychievements.signals import receiver, goal_achieved, highest_level_achieved

from pychievements.backends import SQLiteAchievementBackend



# ---- ACHIEVEMENTS ---X


class PartAchievement(Achievement):
    complete_class_type = None

class AchievementWithParts(Achievement):
    part_achievement_class_name = ''


@receiver(goal_achieved)
def check_multiple_achievement(tracked_id, achievement, goals, **kwargs):
    if not isinstance(achievement, PartAchievement):
        return
    #may be move to class method 
    ach = tracker.achievements_for_id(tracked_id, keywords=achievement.keywords, category='quest_part')
    big_ach = tracker.achievement_for_id(tracked_id, achievement.complete_class_type)
    tracker.set_level(tracked_id, big_ach, len(ach))


# ---- FACTORIES ----


def simple_achievement_factory(dsc): 
    goals = [{'level': 1, 'name': dsc['name'], 'description': dsc['description']}]
    attrs = {
            'name': dsc['name'], 
            'category': 'quest',
            'keywords': ['quest', dsc['unique_keyword']], 
            'goals': goals
            }
    return type(dsc['unique_keyword'], (Achievement,), attrs)


def part_achievement_factory(keyword, class_name, big_type):   
    goals = [{'level': 1}]
    attrs = {'category': 'quest_part',
             'keywords': ['quest_part', keyword], 
             'goals': goals, 
             'complete_class_type': big_type}
    
    return type(class_name, (PartAchievement,), attrs)


def achievement_with_parts_factory(dsc): 
    # generate goals for big achievement
    # may be move to init method of class
    goals = []
    for i in range(dsc['parts']-1):
        subname = '{} ({}/{})'.format(dsc['name'], i+1, dsc['parts'])
        goals.append({'level': i+1, 'name': subname, 'description': dsc['description']})
    subname = '{0} ({1}/{1})'.format(dsc['name'], dsc['parts'])
    goals.append({'level': dsc['parts'], 'name': subname, 'description': dsc['final_description']})
    
    attrs = {'name': dsc['name'], 'category': 'quest',
             'keywords': ('quest', dsc['unique_keyword']),
             'goals': goals}

    new_achievement = type(dsc['unique_keyword'], (AchievementWithParts,), attrs)

    # generate part achievements    
    for i in range(dsc['parts']):
        class_name = dsc['unique_keyword'] + '_' + str(i+1)
        print(class_name)
        ach = part_achievement_factory(dsc['unique_keyword'], class_name, new_achievement)
        print(ach)
        tracker.register(ach)

    return new_achievement


def fatal_achievement_factory(dsc):
    goals = []
    for key, goal in dsc['goals'].items():
        goals.append({'level': key, 'name': goal['name'], 'description' : goal['dsc']})
    
    attrs = {'category': 'quest', 'keywords': ('quest', 'fatal'), 'goals': goals}
    return type('fatal', (Achievement,), attrs)


def quest_die_achievement(dsc):
    return None

# ---- INIT ----

def init_achievements():
    db_name = "data/achievements.db"
    backend = SQLiteAchievementBackend(db_name)
    tracker.set_backend(backend)

    for ach_dsc in achievements:
        if ach_dsc['type'] == 'simple_achievement':
            ach = simple_achievement_factory(ach_dsc)
            tracker.register(ach)
        if ach_dsc['type'] == 'part_achievement':
            ach = achievement_with_parts_factory(ach_dsc)
            tracker.register(ach)
        if ach_dsc['type'] == 'fatal_achievement':
            ach = fatal_achievement_factory(ach_dsc)
            tracker.register(ach)
        if ach_dsc['type'] == 'quest_die_achievement':
            ach = quest_die_achievement(ach_dsc)
            tracker.register(ach)

