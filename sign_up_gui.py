import re
from tkinter import messagebox

import bcrypt
import customtkinter as ctk
from request import Request
from user import User


class SignUpGui:
    def __init__(self, gui_manager):
        """
        Initializes the sign-up GUI with input fields and navigation buttons.

        :param gui_manager: The GUI manager that controls navigation and provides client and container objects.
        :type gui_manager: object
        """
        self.gui_manager = gui_manager
        self.client = gui_manager.client
        self.container = gui_manager.container
        self.signup_frame = ctk.CTkFrame(self.container)

        self.first_name_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="First Name", width=250)
        self.first_name_entry.pack(pady=5)

        self.last_name_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Last Name", width=250)
        self.last_name_entry.pack(pady=5)

        self.new_username_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Choose Username", width=250)
        self.new_username_entry.pack(pady=5)

        self.new_password_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Choose Password", show="*",
                                               width=250)
        self.new_password_entry.pack(pady=5)

        self.confirm_password_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Confirm Password", show="*",
                                                   width=250)
        self.confirm_password_entry.pack(pady=5)

        self.signup_button = ctk.CTkButton(self.signup_frame, text="Sign Up", command=self.register_new_user)
        self.signup_button.pack(pady=5)

        self.back_button = ctk.CTkButton(self.signup_frame, text="Already have an account? Login", fg_color="gray",
                                         text_color="white", command=gui_manager.show_login_page)
        self.back_button.pack(pady=5)


    def register_new_user(self):
        """
        Registers a new user by validating form fields and sending a signup request to the server.

        :return: None
        """
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not all([first_name, last_name, username, password, confirm_password]):
            messagebox.showerror("Error", "All fields must be filled out")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return
        if not re.search(r"[A-Z]", password):
            messagebox.showerror("Error", "Password must contain at least one uppercase letter")
            return
        if not re.search(r"[a-z]", password):
            messagebox.showerror("Error", "Password must contain at least one lowercase letter")
            return
        if not re.search(r"\d", password):
            messagebox.showerror("Error", "Password must contain at least one digit")
            return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        signup_result = User('', first_name, last_name, username, hashed_password)
        print(signup_result)

        self.client.send_request(Request('signup', signup_result))

    def show(self):
        """
        Displays the signup frame on the GUI.

        :return: None
        """
        self.signup_frame.pack()

    def hide(self):
        """
        Hides the signup frame from the GUI.

        :return: None
        """
        self.signup_frame.pack_forget()
