import tkinter as tk
from tkinter import messagebox


class SignUpPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Up Page")
        self.root.geometry("300x250")

        # Initialize font size
        self.font_size = 10

        # Create UI elements
        self.username_label = tk.Label(root, text="Username:", font=("Helvetica", self.font_size))
        self.username_label.pack(pady=(20, 5))
        self.username_entry = tk.Entry(root, font=("Helvetica", self.font_size))
        self.username_entry.pack(pady=(0, 10))

        self.password_label = tk.Label(root, text="Password:", font=("Helvetica", self.font_size))
        self.password_label.pack(pady=(5, 5))
        self.password_entry = tk.Entry(root, show="*", font=("Helvetica", self.font_size))
        self.password_entry.pack(pady=(0, 10))

        self.confirm_password_label = tk.Label(root, text="Confirm Password:", font=("Helvetica", self.font_size))
        self.confirm_password_label.pack(pady=(5, 5))
        self.confirm_password_entry = tk.Entry(root, show="*", font=("Helvetica", self.font_size))
        self.confirm_password_entry.pack(pady=(0, 10))

        self.sign_up_button = tk.Button(root, text="Sign Up", command=self.sign_up, font=("Helvetica", self.font_size))
        self.sign_up_button.pack(pady=(10, 5))

        # Bind the resize event
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        new_font_size = max(10, event.height // 25)
        if new_font_size != self.font_size:
            self.font_size = new_font_size
            self.update_font()

    def update_font(self):
        self.username_label.config(font=("Helvetica", self.font_size))
        self.username_entry.config(font=("Helvetica", self.font_size))
        self.password_label.config(font=("Helvetica", self.font_size))
        self.password_entry.config(font=("Helvetica", self.font_size))
        self.confirm_password_label.config(font=("Helvetica", self.font_size))
        self.confirm_password_entry.config(font=("Helvetica", self.font_size))
        self.sign_up_button.config(font=("Helvetica", self.font_size))

    def sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Sign Up Failed", "Passwords do not match.")
        elif username == "":
            messagebox.showerror("Sign Up Failed", "Username cannot be empty.")
        else:
            messagebox.showinfo("Sign Up Success", "You have successfully signed up!")


class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Page")
        self.root.geometry("300x200")

        self.font_size = 10

        self.username_label = tk.Label(root, text="Username:", font=("Helvetica", self.font_size))
        self.username_label.pack(pady=(20, 5))
        self.username_entry = tk.Entry(root, font=("Helvetica", self.font_size))
        self.username_entry.pack(pady=(0, 10))

        self.password_label = tk.Label(root, text="Password:", font=("Helvetica", self.font_size))
        self.password_label.pack(pady=(5, 5))
        self.password_entry = tk.Entry(root, show="*", font=("Helvetica", self.font_size))
        self.password_entry.pack(pady=(0, 10))

        self.login_button = tk.Button(root, text="Login", command=self.login, font=("Helvetica", self.font_size))
        self.login_button.pack(pady=(10, 5))

        self.sign_up_label = tk.Label(root, text="Don't have an account? Create here!",
                                      font=("Helvetica", self.font_size), fg="blue")
        self.sign_up_label.pack(pady=(5, 5))
        self.sign_up_label.bind("<Button-1>", self.open_sign_up)

        self.forgot_password_button = tk.Button(root, text="Forgot Password?", command=self.forgot_password,
                                                font=("Helvetica", self.font_size), fg="blue")
        self.forgot_password_button.pack(pady=(5, 5))

        # Sample credentials
        self.valid_username = "user"
        self.valid_password = "pass"

        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        new_font_size = max(10, event.height // 20)
        if new_font_size != self.font_size:
            self.font_size = new_font_size
            self.update_font()

    def update_font(self):
        self.username_label.config(font=("Helvetica", self.font_size))
        self.username_entry.config(font=("Helvetica", self.font_size))
        self.password_label.config(font=("Helvetica", self.font_size))
        self.password_entry.config(font=("Helvetica", self.font_size))
        self.login_button.config(font=("Helvetica", self.font_size))
        self.sign_up_label.config(font=("Helvetica", self.font_size))
        self.forgot_password_button.config(font=("Helvetica", self.font_size))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == self.valid_username and password == self.valid_password:
            messagebox.showinfo("Login Success", "You have successfully logged in!")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def open_sign_up(self, event):
        self.root.destroy()  # Close the login window
        sign_up_root = tk.Tk()  # Create a new window for sign-up
        SignUpPage(sign_up_root)
        sign_up_root.mainloop()

    def forgot_password(self):
        # Here you can implement password recovery logic or show a message
        messagebox.showinfo("Forgot Password", "Password recovery options will be implemented here.")


if __name__ == "__main__":
    root = tk.Tk()
    app = LoginPage(root)
    root.mainloop()
