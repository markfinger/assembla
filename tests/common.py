
class AssemblaObject:
    """
    Base object for Assembla objects
    """

    def __init__(self):
        self._spaces = []
        self._milestones = []
        self._users = []
        self._tickets = []

    def milestone(self, name):
        pass

    def milestones(self):
        return self._milestones

    def user(self, username):
        pass

    def users(self):
        return self._users

    def ticket(self, number):
        pass

    def tickets(self):
        return self._tickets


