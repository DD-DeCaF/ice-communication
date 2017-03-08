default_settings = {
    "USER_NAME": "Administrator",
    "PASSWORD": "Administrator",
    "API_USER": None,
    "API_KEY": None,
    "HOST":  None,
    "PORT": None
}


class IceSettings(object):
    def __init__(self, settings=default_settings):
        super(IceSettings, self).__init__()

        self.user_name = None
        self.password = None
        self.api_key = None
        self.api_user = None
        self.host = "localhost"
        self.port = 8443

        self.check_settings(settings)

    def check_settings(self, settings):
        # Check settings
        if "USER_NAME" in settings and settings["USER_NAME"]:
            self.user_name = settings["USER_NAME"]

        if "PASSWORD" in settings and settings["PASSWORD"]:
            self.password = settings["PASSWORD"]

        if "API_KEY" in settings and settings["API_KEY"]:
            self.api_key = settings["API_KEY"]

        if "API_USER" in settings and settings["API_USER"]:
            self.api_user = settings["API_USER"]

        if "HOST" in settings and settings["HOST"]:
            self.host = settings["HOST"]

        if "PORT" in settings and settings["PORT"]:
            self.port = int(settings["PORT"])
