import customtkinter as ctk

from files_gui import FileManagerApp
from login_gui import LoginGui
from request import Request
from sign_up_gui import SignUpGui
from client_new import Client

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.signup_result = None
        self.title("CoEdit - login")
        self.geometry("1200x900")

        self.my_user = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.client = Client()
        self.client.connect()

        self.login_gui = LoginGui(self)
        self.signup_gui = SignUpGui(self)

        self.files_gui = FileManagerApp(self)

        self.login_gui.show()

        # Start polling the client's queue
        self.poll_client_response()


    def poll_client_response(self):
        """Check for new responses every 100ms."""
        response = self.client.get_response_nowait()
        if response:
            self.handle_response_change_state(response)
        self.after(100, self.poll_client_response)  # Schedule next poll

    def handle_response_change_state(self, response: Request):
        print(response.request_type)
        print(response.data)
        if response.request_type == 'signup-success' and response.data:
            self.show_login_page()
        elif response.request_type == 'login-success' and response.data[0]:
            self.my_user = response.data[1]
            print(self.my_user)
            self.show_files_page()
            self.files_gui.load_files()
            self.files_gui.my_user = self.my_user
        elif response.request_type == 'add-file-success':
            if not response.data[0]:
                self.files_gui.add_file_refresh(False, None)
            else:
                self.files_gui.add_file_refresh(True, response.data[1])
        elif response.request_type == 'rename-file-success':
            self.files_gui.rename_file_success(response.data)
        elif response.request_type == 'file-access':
            print('response file access type' + str(type(response.data)))
            self.files_gui.manage_access(response.data)
        elif response.request_type == 'user-exists-response':
            self.files_gui.add_user(response.data)
        elif response.request_type == 'update-access-response':
            self.files_gui.save_changes_update_response(response.data)
        elif response.request_type == 'file-list': # refresh files button
            self.files_gui.refresh_files(response.data)
        elif response.request_type == 'file-content':
            self.files_gui.open_file(response.data[0], response.data[1]) # response.data[0] = file: File, response.data[1] = content: str


    def show_login_page(self):
        self.login_gui.show()
        self.signup_gui.hide()

    def show_signup_page(self):
        self.signup_gui.show()
        self.login_gui.hide()

    def show_files_page(self):
        self.login_gui.hide()
        self.files_gui.show()


if __name__ == "__main__":
    AuthApp().mainloop()
