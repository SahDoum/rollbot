from queue import PriorityQueue

weapons = [312, 180, 500, 5, 1, 1002]
hitpoint_generated = set()

with open('boss_template.txt', 'r') as myfile:
    template=myfile.read()

def generate(t):
    hitpoints = t[0]
    length = int(23 * (hitpoints/1000))
    lifebar = '=' * (23 - length) + ' ' * length
    return template.format(hitpoints, lifebar, 1000-hitpoints, *[hitpoints+t for t in weapons])


q = PriorityQueue()
q.put([0, set(weapons)])

while not q.empty():
    next = q.get()
    hitpoints = next[0]
    wpns = next[1]

    for w in wpns:
        result_hitpoints = hitpoints + w
        if result_hitpoints > 1000 or result_hitpoints in hitpoint_generated:
            continue
        hitpoint_generated.add(result_hitpoints)
        tmp_set = {w}
        t = [
            hitpoints+w, 
            wpns - tmp_set
            ]
        q.put(t)
        text = generate(t)
        print(text)
