from datetime import date


class Auth:
    def __init__(self, user_name: str, password: str, password_comfirm: str):
        self.user_name = user_name
        self.password = password
        self.password_comfirm = password_comfirm