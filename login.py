import customtkinter as ctk
from tkinter import messagebox
from user import User

class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.signup_result = None
        self.title("CoEdit - login")
        self.geometry("400x300")

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.create_login_frame()
        self.create_signup_frame()

        self.show_login()

    def create_login_frame(self):
        self.login_frame = ctk.CTkFrame(self.container)

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=5)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.authenticate)
        self.login_button.pack(pady=5)

        self.signup_button = ctk.CTkButton(self.login_frame, text="Don't have an account? Sign up", fg_color="gray",
                                           text_color="white", command=self.show_signup)
        self.signup_button.pack(pady=5)

    def create_signup_frame(self):
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
                                         text_color="white", command=self.show_login)
        self.back_button.pack(pady=5)

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()


        if not all([username, password]):
            messagebox.showerror("Error", "All fields must be filled out")
            return

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

        signup_result = User(first_name, last_name, username, password)
        print(signup_result)

        # messagebox.showinfo("Success", "Account created successfully")
        self.show_login()


    def show_login(self):
        self.signup_frame.pack_forget()
        self.login_frame.pack()

    def show_signup(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack()

    def mainloop(self):
        super().mainloop()
        return self.signup_result

if __name__ == "__main__":
    AuthApp().mainloop()
