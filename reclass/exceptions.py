class UnknownSettingError(Exception):
    def __init__(self, setting_name):
        super().__init__()
        self.setting_name = setting_name
