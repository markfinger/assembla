from models import API

class API(API):
    """
    Example initilisation of the Assembla API:
        `
        import assembla

        API = assembla.API(
            auth=(
                'Username',
                'Password',
                )
            )
        `

        :auth (a required argument of assembla.API)
            > should be in the form of a tuple denoting the username and password to
                use for authentication attempts against Assembla.
            > should be provided in the following format:
                `
                auth = (
                    '<username>',
                    '<password>',
                    )
                `
    """
    pass