
class AssemblaObject(object):
    """
    Base object for Assembla objects
    """

    def __init__(self):
        self._spaces = []
        self._milestones = []
        self._users = []
        self._tickets = []

    def space(self, name):
        return reduce(
            lambda space: space.name==name,
            self._spaces
        )

    def spaces(self):
        return self._spaces

    def milestone(self, title):
        return reduce(
            lambda milestone: milestone.title==title,
            self._milestones
        )

    def milestones(self):
        return self._milestones

    def user(self, login_name):
        return reduce(
            lambda user: user.login_name==login_name,
            self._users
        )

    def users(self):
        return self._users

    def ticket(self, number):
        return reduce(
            lambda ticket: ticket.number==number,
            self._tickets
        )

    def tickets(self):
        return self._tickets


class AssemblaError(Exception):

    error_codes = {
        100: "No authorisation credentials provided",
        110: "Assembla failed to authorised with credentials",
    }

    def __init__(self, code):
        self.code = code
        raise self

    def __str__(self):
        return self.error_codes[self.code]
