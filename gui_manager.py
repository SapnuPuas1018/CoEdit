import threading
from tkinter.messagebox import showerror

import customtkinter as ctk

import protocol
from login_gui import LoginGui
from sign_up_gui import SignUpGui
from client_new import Client

class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.signup_result = None
        self.title("CoEdit - login")
        self.geometry("400x300")

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.client = Client()
        self.client.connect()

        self.login_gui = LoginGui(self)

        self.signup_gui = SignUpGui(self)

        self.show_login_page()

        # self.next_state = {"signup": {"signup success": "login", "signup failed": "signup"}
        #     , "login": {"login success": "files screen", "login failed": "login"},
        #                    "files screen": {"files logout": "signup"}}

    def change_state(self):
        response = self.client.get_response()
        if not response:
            return
        elif response.request_type == 'signup-success' and response.data:
            self.show_login_page()
        elif response.request_type == 'login-success' and response.data:
            self.show_signup_page()


    def show_login_page(self):
        self.login_gui.show()
        self.signup_gui.hide()

    def show_signup_page(self):
        self.signup_gui.show()
        self.login_gui.hide()


if __name__ == "__main__":
    AuthApp().mainloop()
