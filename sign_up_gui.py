from tkinter import messagebox
import customtkinter as ctk

from request import Request
from user import User


class SignUpGui:

    def __init__(self, gui_manager):
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

        signup_result = User('', first_name, last_name, username, password)
        print(signup_result)

        self.client.send_request(Request('signup', signup_result))
        # self.gui_manager.change_state()

    def show(self):
        self.signup_frame.pack()

    def hide(self):
        self.signup_frame.pack_forget()