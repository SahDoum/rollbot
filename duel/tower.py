import random

# ---- TOWER CLASS ----


class Tower:
    lines = {0:0, 1:2, 2:4, 3:5, 4:8, 5:10, 6:11, 7:12 , 8:13, 9:14}

    def __init__(self, max_time=0):
        self.time = 0
        self.max_time = max_time
        self.tower = get_empty_tower()
        self.symbol = None

    def next_bomm(self):
        text = None
        if self.time == self.max_time:
            text = 'Патрон: ' + self.symbol
        line = self.time + 1 # Tower.lines[self.time]
        add_text_to_tower(self.tower, line, text)
        tower = add_clock(self.tower, self.time + 1)
        self.time += 1
        return '```\n' + '\n'.join(tower) + '```'


def get_empty_tower():
    height = 15
    length = 12
    tower = []
    for i in range(0, height):
        s = ' ' * length
        if i == height-1:
            s = '-' * length
        tower.append(ascii_tower[i] + s)
    return tower


def add_text_to_tower(tower, line, text=None):
    if not text:
        text = 'Б' + 'О' * random.randint(1, 5) + 'М'
    length = 13
    start = 12
    # if length > len(text):
    #     start = random.randint(0, length - len(text)-1)
    tower[line] = tower[line][:start] + text + tower[line][start+len(text):]
    return tower


def add_clock(tower, time, max_time=None):
    time = time % 8
    length = 0 # 13

    clock_x = 5
    clock_y = 3
    clock_symbol = '@'

    clock_x += length
    new_tower = list(tower)
    if max_time:
        str = tower[clock_y]
        new_tower[clock_y] = str[:clock_x] + max_time + str[clock_x+1:]

    if time == 0:
        clock_symbol = '|'
        clock_y -= 1
    if time == 1:
        clock_symbol = '/'
        clock_x += 1
        clock_y -= 1
    if time == 2:
        clock_symbol = '-'
        clock_x += 2
    if time == 3:
        clock_symbol = '\\'
        clock_x += 1
        clock_y += 1
    if time == 4:
        clock_symbol = '|'
        clock_y += 1
    if time == 5:
        clock_symbol = '/'
        clock_x -= 1
        clock_y += 1
    if time == 6:
        clock_symbol = '-'
        clock_x -= 2
    if time == 7:
        clock_symbol = '\\'
        clock_x -= 1
        clock_y -= 1

    str = new_tower[clock_y]
    new_tower[clock_y] = str[:clock_x] + clock_symbol + str[clock_x+1:]

    return new_tower


ascii_tower = [
    '/         \\',
    '| 11 12 1 |',
    '|10      2|',
    '|9   @   3|',
    '|8       4|',
    '|  7 6 5  |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '|         |',
    '-----------'
]
