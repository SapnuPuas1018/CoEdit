import customtkinter as ctk

from files_gui import FileManagerApp
from login_gui import LoginGui
from request import Request
from sign_up_gui import SignUpGui
from client import Client

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class GuiManager(ctk.CTk):
    """
    Main application class for CoEdit, managing user authentication (login and signup),
    client-server communication, and navigation to the file manager screen.

    Inherits from:
        ctk.CTk: CustomTkinter's main window class.
    """
    def __init__(self):
        """
        Initializes the AuthApp window, sets up client connection, GUI components
        for login, signup, and file management, and begins polling for server responses.
        """
        super().__init__()
        self.signup_result = None
        self.title("CoEdit - login")
        self.geometry("1200x900")

        self.my_user = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.client = Client()
        self.client.connect()

        self.login_gui = LoginGui(self)
        self.signup_gui = SignUpGui(self)

        self.files_gui = FileManagerApp(self)

        self.login_gui.show()

        # Start polling the client's queue
        self.poll_client_response()


    def poll_client_response(self):
        """
        Handles server responses and updates the application state accordingly.
        """
        response = self.client.get_response_nowait()
        if response:
            self.handle_response_change_state(response)
        self.after(100, self.poll_client_response)

    def handle_response_change_state(self, response: Request):
        """
        Handles server responses and updates the application state accordingly.

        :param response: The response object received from the server.
        :type response: Request
        """
        print(response.request_type)
        print(response.data)
        if response.request_type == 'signup-success' and response.data:
            self.show_login_page()
        elif response.request_type == 'login-success' and response.data[0]:
            self.my_user = response.data[1]
            self.files_gui.initialize_user_interface(self.my_user)
            self.show_files_page()
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
            self.files_gui.open_file(response.data[0], response.data[1])
        elif response.request_type == 'file-content-update':
            file, changes = response.data
            self.files_gui.apply_file_update(file, changes)
        elif response.request_type == 'write-access-response':
            file, write_access = response.data
            self.files_gui.write_access_response(file, write_access)
        elif response.request_type == 'logout_success':
            success = response.data
            if success:
                self.return_to_login_page()

    def return_to_login_page(self):
        self.files_gui.hide()
        self.login_gui.show()

    def show_login_page(self):
        """
        Displays the login screen and hides the signup screen.
        """
        self.login_gui.show()
        self.signup_gui.hide()

    def show_signup_page(self):
        """
        Displays the signup screen and hides the login screen.
        """
        self.signup_gui.show()
        self.login_gui.hide()

    def show_files_page(self):
        """
        Displays the file manager interface and hides the login screen.
        """
        self.login_gui.hide()
        self.files_gui.show()

    def on_closing(self):
        """
        Called when the user closes the window. Ensures a clean disconnect from the server.
        """
        try:
            if self.my_user:
                # Send logout request
                self.client.send_request(Request("logout", self.my_user))
            self.client.disconnect()
        except Exception as e:
            print(f"Error while disconnecting: {e}")
        finally:
            self.destroy()
            quit()


if __name__ == "__main__":
    GuiManager().mainloop()
