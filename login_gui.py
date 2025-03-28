from tkinter import messagebox
import customtkinter as ctk

from sign_up_gui import SignUpGui


class LoginGui:
    def __init__(self, gui_manager):
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
        username = self.username_entry.get()
        password = self.password_entry.get()


        if not all([username, password]):
            messagebox.showerror("Error", "All fields must be filled out")
            return


    def show(self):
        self.login_frame.pack()


    def hide(self):
        self.login_frame.pack_forget()
