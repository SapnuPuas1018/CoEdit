import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login Screen")
        self.geometry("400x300")

        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=50)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.authenticate)
        self.login_button.pack(pady=5)

        self.signup_button = ctk.CTkButton(self.login_frame, text="Don't have an account? Sign up", fg_color="gray",
                                           text_color="white", command=self.open_signup)
        self.signup_button.pack(pady=5)

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "password":
            messagebox.showinfo("Login Successful", "Welcome!")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def open_signup(self):
        self.withdraw()
        signup_window = SignupApp(self)
        signup_window.mainloop()


class SignupApp(ctk.CTk):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.title("Sign Up Screen")
        self.geometry("400x300")

        self.signup_frame = ctk.CTkFrame(self)
        self.signup_frame.pack(pady=50)

        self.username_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Choose Username", width=250)
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Choose Password", show="*", width=250)
        self.password_entry.pack(pady=5)

        self.confirm_password_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Confirm Password", show="*",
                                                   width=250)
        self.confirm_password_entry.pack(pady=5)

        self.signup_button = ctk.CTkButton(self.signup_frame, text="Sign Up", command=self.register)
        self.signup_button.pack(pady=5)

        self.back_button = ctk.CTkButton(self.signup_frame, text="Already have an account? Login", fg_color="gray",
                                         text_color="white", command=self.open_login)
        self.back_button.pack(pady=5)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        messagebox.showinfo("Success", "Account created successfully!")
        self.open_login()

    def open_login(self):
        self.destroy()
        self.login_window.deiconify()


if __name__ == "__main__":
    LoginApp().mainloop()