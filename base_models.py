
class AssemblaObject(object):
    """
    Base object
    """
    # A string denoting the key identifier for the model
    primary_key = None
    # Python formattable string, which denotes a relative path to
    # the model's HTML page on Assembla.
    relative_url = None
    # Python formattable string, which denotes a relative path to
    # the model on Assembla's API.
    relative_api_url = None
    # A URL which is prepended to all relative URLs to generate absolute
    # URLs to HTML pages.
    base_url = 'https://www.assembla.com/'
    # A URL which is prepended to all relative URLs to generate absolute
    # URLs to API links.
    base_api_url = base_url

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return unicode(self.pk)

    @property
    def pk(self):
        """
        Returns the value of the attribute denoted by self.primary_key
        """
        return getattr(self, self.primary_key)

    @property
    def url(self):
        """
        Returns a string representing the absolute url to the model's
        corresponding HTML page on Assembla
        """
        return ''.join([
            self.base_url,
            self.relative_url,
        ]).format(**{
            'space': self._get_pk('space'),
            'milestone': self._get_pk('milestone'),
            'user': self._get_pk('user'),
            'ticket': self._get_pk('ticket'),
            'pk': self.pk,
        })

    @property
    def api_url(self):
        """
        Returns a string representing the absolute url to the model on
        Assembla's API
        """
        return ''.join([
            self.base_api_url,
            self.relative_api_url,
        ]).format(**{
            'space': self._get_pk('space'),
            'milestone': self._get_pk('milestone'),
            'user': self._get_pk('user'),
            'ticket': self._get_pk('ticket'),
            'pk': self.pk,
        })

    def _get_pk(self, attr, default=None):
        """
        Attempts to return the primary key of the attribute denoted by :attr.

        Takes an optional argument :default, which acts in a similar manner
        to getattr's
        """
        return getattr(getattr(self, attr, default), 'pk', default)

class HasObjects(object):
    """
    Base object
    """

#    could probably do some automated stuff to avoid all
#    the boilerplate below
    
    # has_harvested_<name> = False
    pass

class HasSpaces(HasObjects):

    def __init__(self):
        self._spaces = []

    def space(self, name):
        return reduce(
            lambda space: space.name==name,
            self._spaces
        )

    def spaces(self):
        return self._spaces

class HasMilestones(HasObjects):

    def __init__(self):
        self._milestones = []

    def milestone(self, title):
        return reduce(
            lambda milestone: milestone.title==title,
            self._milestones
        )

    def milestones(self):
        return self._milestones

class HasUsers(HasObjects):

    def __init__(self):
        self._users = []

    def user(self, login_name):
        return reduce(
            lambda user: user.login_name==login_name,
            self._users
        )

    def users(self):
        return self._users

class HasTickets(HasObjects):

    def __init__(self):
        self._tickets = []

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
