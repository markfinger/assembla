from exceptions import Exception


class AssemblaError(Exception):

    error_codes = {
        100: "No authorisation credentials provided",
        110: "Assembla failed to authorise with credentials",
        120: "Failure to provide necessary arguments for function",
        130: "Unexpected response from Assembla, response ({status_code}) from '{url}'.",
        200: "Cannot find '{object}' with a primary key matching '{pk}'",
        210: "Multiple instances of '{object}' found with primary keys matching '{pk}'",
    }

    def __init__(self, code=None, *args, **kwargs):
        self.code = code
        self.error_message = self.error_codes[self.code].format(**kwargs)

    def __str__(self):
        return self.error_message