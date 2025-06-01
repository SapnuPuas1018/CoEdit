from tkinter import messagebox
import customtkinter as ctk

from request import Request
from user import User


class LoginGui:
    def __init__(self, gui_manager):
        """
        Initializes the login GUI with entry fields and buttons.

        :param gui_manager: The GUI manager that controls screen navigation and contains the client and container.
        :type gui_manager: object
        """
        self.client = gui_manager.client
        self.container = gui_manager.container
        self.login_frame = ctk.CTkFrame(self.container)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.authenticate)
        self.login_button.pack(pady=5)

        self.signup_button = ctk.CTkButton(self.login_frame, text="Don't have an account? Sign up", fg_color="gray",
                                           text_color="white", command=gui_manager.show_signup_page)
        self.signup_button.pack(pady=5)

    def authenticate(self):
        """
        Authenticates the user by retrieving credentials from entry fields and sending a login request.

        :return: None
        """
        username = self.username_entry.get()
        password = self.password_entry.get()


        if not all([username, password]):
            messagebox.showerror("Error", "All fields must be filled out")
            return

        login_user = User('','', '', username, password)
        print(login_user)
        self.client.send_request(Request('login', login_user))

    def show(self):
        """
        Displays the login frame in the GUI.

        :return: None
        """
        self.login_frame.pack()


    def hide(self):
        """
        Hides the login frame from the GUI.

        :return: None
        """
        self.login_frame.pack_forget()
