#
#   type : simple_achievement
#   name
#   description
#   unique_keyboard
#
#   type : part_achievement
#   name
#   description
#   final_description
#   parts
#   unique_keyword
#
#   type : fatal_achievement
#   dict:
#       number : name, description
#
#   type : quest_die_achievement
#   dict:
#       number : name, description
#

achievements = [
    {
        'type' : 'fatal_achievement',
        'goals' : {
            10 : {'name' : 'Нарушитель спокойствия', 'dsc' : 'За 10 фаталов в общем чате'},
            20 : {'name' : 'Сосочный террорист', 'dsc' : 'За 20 необходимых фаталов в общем чате'},
            50 : {'name' : 'Последователь гея-огра', 'dsc' : 'За 50 сочных фаталов в общем чате'},
            100 : {'name' : 'F.A.T.A.L. E.X.P.E.R.T', 'dsc' : 'За 100 отборных фаталов в общем чате'},
        }
    },
    {
        'type' : 'part_achievement', 
        'name' : 'Исследователь',
        'description' : 'На пути познания',
        'final_description' : 'Познать все доступные миры',
        'parts' : 11,
        'unique_keyword' : 'discoverer',
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Убийца драконов',
        'description' : 'Хорошо собраться в поход и убить змия!',
        'unique_keyword' : 'dragon_killer',
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Судьба Феникса',
        'description' : 'Отправиться в безнадежное приключение с Фениксом',
        'unique_keyword' : 'phoenix_friend',
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Вор из Гастона',
        'description' : 'Украсть драгоценности в Башне трех мудрецов',
        'unique_keyword' : 'robber_of_tower_of_the_three_wise_man',
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Тесей',
        'description' : 'Выбраться из лабиринта',
        'unique_keyword' : 'maze_escape',
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Старший тестировщик ВегаРолл',
        'description' : 'Найти секретную концовку в симуляции',
        'unique_keyword' : 'simulation_win',
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Ценитель прекрасного',
        'description' : 'Поймать нимфу',
        'unique_keyword' : 'lake_nen_win',
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Небинарный',
        'description' : 'Выпить зелье троллиной похоти',
        'unique_keyword' : 'tavern_troll_sex'
    },
    {
        'type' : 'simple_achievement',
        'name' : 'Бесшумный убийца',
        'description' : 'Сделать работу без лишнего шума',
        'unique_keyword' : 'silent_killer'
    },
]