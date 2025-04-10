import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class FileManagerApp(ctk.CTk):
    def __init__(self, gui_manager):
        super().__init__()
        self.container = gui_manager.container
        self.client = gui_manager.client

        self.files_frame = ctk.CTkFrame(self.container)

        # Mock data (you can replace this with database data)
        self.files_data = [
            {"name": "Math Homework", "owner": "Me", "date": "2025-03-29"},
            {"name": "Project Plan", "owner": "Team", "date": "2025-03-29"},
            {"name": "Science Notes", "owner": "Me", "date": "2025-03-28"},
        ]
        self.filtered_files = self.files_data.copy()

        self.create_widgets()

    def create_widgets(self):
        # Top bar
        top_bar = ctk.CTkFrame(self.files_frame)
        top_bar.pack(fill="x", padx=10, pady=10)

        self.disconnect_btn = ctk.CTkButton(top_bar, text="Disconnect", command=self.disconnect)
        self.disconnect_btn.pack(side="left")

        self.add_file_btn = ctk.CTkButton(top_bar, text="+ New File", command=self.add_file)
        self.add_file_btn.pack(side="left", padx=10)

        self.sort_by = ctk.CTkOptionMenu(top_bar, values=["Name", "Owner", "Date"], command=self.sort_files)
        self.sort_by.set("Sort by")
        self.sort_by.pack(side="left", padx=10)

        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search files...")
        self.search_entry.pack(side="right", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_files())

        # File list headers
        header_frame = ctk.CTkFrame(self.files_frame)
        header_frame.pack(fill="x", padx=20)

        ctk.CTkLabel(header_frame, text="⋮", width=40).grid(row=0, column=0)
        ctk.CTkLabel(header_frame, text="File Name", width=200).grid(row=0, column=1)
        ctk.CTkLabel(header_frame, text="Owner", width=100).grid(row=0, column=2)
        ctk.CTkLabel(header_frame, text="Date Modified", width=150).grid(row=0, column=3)

        # File entries area
        self.file_frame = ctk.CTkScrollableFrame(self.files_frame)
        self.file_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.display_files()

    def display_files(self):
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        for i, file in enumerate(self.filtered_files):
            action_btn = ctk.CTkButton(self.file_frame, text="⋮", width=30, command=lambda f=file: self.show_actions(f))
            action_btn.grid(row=i, column=0, padx=5, pady=5)

            name_label = ctk.CTkLabel(self.file_frame, text=file["name"], anchor="w", width=200)
            name_label.grid(row=i, column=1, sticky="w")
            name_label.bind("<Double-Button-1>", lambda e, f=file: self.open_file(f))

            ctk.CTkLabel(self.file_frame, text=file["owner"], width=100).grid(row=i, column=2)
            ctk.CTkLabel(self.file_frame, text=file["date"], width=150).grid(row=i, column=3)

    def search_files(self):
        query = self.search_entry.get().lower()
        self.filtered_files = [file for file in self.files_data if query in file["name"].lower()]
        self.display_files()

    def sort_files(self, criterion):
        if criterion == "Name":
            self.filtered_files.sort(key=lambda x: x["name"].lower())
        elif criterion == "Owner":
            self.filtered_files.sort(key=lambda x: x["owner"].lower())
        elif criterion == "Date":
            self.filtered_files.sort(key=lambda x: x["date"], reverse=True)
        self.display_files()

    def show_actions(self, file):
        action = messagebox.askquestion("File Actions", f"What would you like to do with '{file['name']}'?\nYes: Rename\nNo: Delete", icon='question')
        if action == 'yes':
            new_name = simpledialog.askstring("Rename File", "Enter new name:", initialvalue=file["name"])
            if new_name:
                file["name"] = new_name
        elif action == 'no':
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file['name']}'?"):
                self.files_data.remove(file)
        self.search_files()

    def open_file(self, file):
        new_window = ctk.CTkToplevel(self)
        new_window.title(file["name"])
        new_window.geometry("600x400")
        ctk.CTkLabel(new_window, text=f"Opening file: {file['name']}", font=("Arial", 16)).pack(pady=20)

    def add_file(self):
        new_name = simpledialog.askstring("New File", "Enter file name:")
        if new_name:
            new_file = {
                "name": new_name,
                "owner": "Me",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            self.files_data.append(new_file)
            self.search_files()

    def disconnect(self):
        result = messagebox.askyesno("Disconnect", "Are you sure you want to disconnect?")
        if result:
            self.destroy()
    def show(self):
        self.files_frame.pack(fill="both", expand=True)
    
    def hide(self):
        self.files_frame.pack_forget()


if __name__ == "__main__":
    # app = FileManagerApp()
    # app.mainloop()
    pass