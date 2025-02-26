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
        # Adjust font size based on window height
        new_font_size = max(10, event.height // 25)  # Set minimum font size to 10
        if new_font_size != self.font_size:  # Only update if the size has changed
            self.font_size = new_font_size
            self.update_font()

    def update_font(self):
        # Update the font size for all widgets
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
            # In a real application, you'd save the username and password here
            messagebox.showinfo("Sign Up Success", "You have successfully signed up!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SignUpPage(root)
    root.mainloop()
