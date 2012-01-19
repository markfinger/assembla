from .base_models import AssemblaObject

class Ticket(AssemblaObject):

    def __init__(self, *args, **kwargs):
        super(Ticket, self).__init__(*args, **kwargs)