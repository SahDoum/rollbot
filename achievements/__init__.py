from .tracker import tracker 
from .achievements import init_achievements


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
