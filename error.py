from exceptions import Exception


class AssemblaError(Exception):

    error_codes = {
        100: "No authorisation credentials provided",
        110: "Assembla failed to authorised with credentials",
        200: "Object with a matching primary key cannot be found. pk: {pk}"
    }

    def __init__(self, code, *args, **kwargs):
        self.code = code
        import pdb; pdb.set_trace
        raise self

    def __str__(self):
        return self.error_codes[self.code]