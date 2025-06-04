from rest_framework.routers import SimpleRouter


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Router(SimpleRouter):
    """
    Common URL router for entire application.

    Disables necessity of trailing slash.
    """

    def __init__(self, trailing_slash=True):
        super().__init__(trailing_slash)
