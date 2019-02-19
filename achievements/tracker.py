from pychievements.trackers import AchievementTracker


class OrderedTracker(AchievementTracker):
    def achievements_for_id(self, tracked_id, category=None, keywords=[]):
        result = []
        for ach in self.achievements(category, keywords):
            result += self._backend.achievements_for_id(tracked_id, [ach])
        return result
        
tracker = OrderedTracker()
