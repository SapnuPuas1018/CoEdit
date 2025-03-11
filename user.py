

class User:
    def __init__(self, name, password, files):
        self.name = name
        self.password = password
        self.files = files

    def change_password(self, new_password):
        self.password = new_password

    def __repr__(self):
        # return "name: ('{}', {}, {}) password: ".format(self.name, self.password, self.files)
        pass