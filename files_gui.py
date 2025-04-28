import tkinter
from os import access

import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime


from file import File
from request import Request
from user import User
from user_access import UserAccess

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class FileManagerApp(ctk.CTk):
    def __init__(self, gui_manager):
        super().__init__()
        self.container = gui_manager.container
        self.client = gui_manager.client

        self.files_frame = ctk.CTkFrame(self.container)

        self.filtered_files = []

        self.create_widgets()
        # self.load_files()
        self.my_user = None

    def load_files(self):
        '''Receives the files from server - database as a list[File] object'''
        # print('Requesting file list from server...')

        file_objects = self.client.get_response_nowait()
        # print(f'file_objects : {file_objects}')
         # file_objects = Request('', [File('notes_file', 'hi this is my notes', 'txt', 'me', datetime.now())])
        print(type(file_objects))
        print(file_objects)

        if file_objects is not None:
            self.file_list = file_objects.data
            self.filtered_files = self.file_list.copy()

        self.display_files()

    def refresh_files(self):
        '''Receives the files from server - database as a list[File] object'''
        pass
        # print('Requesting file list from server...')
        self.client.send_request(Request('refresh-files', self.my_user))

        file_objects = self.client.get_response_nowait()
        print('file_objects: ')
        print(file_objects)

        if file_objects is not None:
            self.file_list = file_objects.data
            self.filtered_files = self.file_list.copy()

        self.display_files()

    def display_files(self):
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        for i, file in enumerate(self.filtered_files):
            action_btn = ctk.CTkButton(self.file_frame, text="⋮", width=30, command=lambda f=file: self.show_actions(f))
            action_btn.grid(row=i, column=0, padx=5, pady=5)

            name_label = ctk.CTkLabel(self.file_frame, text=file.filename, anchor="w", width=200)
            name_label.grid(row=i, column=1, sticky="w")
            name_label.bind("<Double-Button-1>", lambda e, f=file: self.open_file(f))

            ctk.CTkLabel(self.file_frame, text=file.owner, width=100).grid(row=i, column=2)
            ctk.CTkLabel(self.file_frame, text=file.creation_date, width=150).grid(row=i, column=3)

    def create_widgets(self):
        # Top bar
        top_bar = ctk.CTkFrame(self.files_frame)
        top_bar.pack(fill="x", padx=10, pady=10)

        self.disconnect_btn = ctk.CTkButton(top_bar, text="Disconnect", command=self.disconnect)
        self.disconnect_btn.pack(side="left")

        self.add_file_btn = ctk.CTkButton(top_bar, text="+ New File", command=self.add_file)
        self.add_file_btn.pack(side="left", padx=10)

        # Refresh button with Unicode icon
        self.refresh_btn = ctk.CTkButton(top_bar, text="↻", width=40, command=self.refresh_files)
        self.refresh_btn.pack(side="left", padx=5)

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

        self.file_frame = ctk.CTkScrollableFrame(self.files_frame)
        self.file_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.display_files()

    def search_files(self):
        query = self.search_entry.get().lower()
        self.filtered_files = [file for file in self.file_list if query in file.filename.lower()]
        self.display_files()

    def sort_files(self, criterion):
        if criterion == "Name":
            self.filtered_files.sort(key=lambda x: x.filename.lower())
        elif criterion == "Owner":
            self.filtered_files.sort(key=lambda x: x.owner.lower())
        elif criterion == "Date":
            self.filtered_files.sort(key=lambda x: x.creation_date.date(), reverse=True)
        self.display_files()



    # todo: be able to delete file only if im the file owner,
    #  be able to delete only for me only if im not owner and remove my read access for this file in database,
    #  rename the file will rename it in database,
    #  manage access will only accessible to owner return all the users that have an access to this file
    def show_actions(self, file):
        print(self.my_user)
        menu = tkinter.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Rename File", command=lambda: self.rename_file(file))
        # if file.owner != self.my_user.user_id:
        menu.add_command(label="🗑️ Delete Only For Me", command=lambda: self.delete_file_for_me(file))
        # if file.owner == self.my_user.user_id:
        menu.add_command(label="👥 Manage Access", command=lambda: self.client.send_request(Request("get-access-list", file)))
        menu.add_command(label="🗑️ Delete File", command=lambda: self.delete_file(file))

        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def rename_file(self, file):
        new_name = simpledialog.askstring("Rename File", "Enter new name:", initialvalue=file.filename)
        if new_name:
            self.client.send_request(Request("rename-file", [file, new_name]))
            file.filename = new_name
            self.search_files()

    def delete_file(self, file):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file.filename}'?")
        if confirm:
            self.client.send_request(Request("delete-file", [file, self.my_user]))
            self.file_list.remove(file)
            self.search_files()

    def delete_file_for_me(self, file):
        confirm = messagebox.askyesno("Confirm", f"Remove access to '{file.filename}' just for you?")
        if confirm:
            self.client.send_request(Request("delete-file-for-me", [file, self.my_user]))
            self.file_list.remove(file)
            self.search_files()

    # 👇 These are all now methods of your class (have 'self')
    def sync_read_write(self, read_var, write_var):
        if not read_var.get():
            write_var.set(False)
        if write_var.get() and not read_var.get():
            read_var.set(True)

    def create_user_row(self, username, read_default=True, write_default=False):
        user_row = len(self.access_vars) + 1

        read_var = ctk.BooleanVar(value=read_default)
        write_var = ctk.BooleanVar(value=write_default)

        ctk.CTkLabel(self.access_window, text=username).grid(row=user_row, column=0, padx=10, pady=5)

        read_switch = ctk.CTkSwitch(self.access_window, variable=read_var, text="")
        read_switch.grid(row=user_row, column=1, padx=10, pady=5)

        write_switch = ctk.CTkSwitch(self.access_window, variable=write_var, text="")
        write_switch.grid(row=user_row, column=2, padx=10, pady=5)

        read_switch.configure(command=lambda: self.sync_read_write(read_var, write_var))
        write_switch.configure(command=lambda: self.sync_read_write(read_var, write_var))

        self.access_vars[username] = (read_var, write_var)

    def add_user(self, user: User):
        if user is None:
            messagebox.showerror("User Not Found", "No such user exists in the database.")
            return

        if user.username in self.access_vars:
            messagebox.showwarning("Already Exists", "User already has access.")
            return

        self.create_user_row(user.username, read_default=True, write_default=False)

        new_row = len(self.access_vars) + 1
        self.new_user_entry.grid(row=new_row, column=0, padx=10, pady=10)
        self.save_btn.grid(row=new_row + 1, columnspan=3, pady=15)

        self.new_user_entry.delete(0, "end")

    def save_changes(self):
        updated_access = []
        for username, (read_var, write_var) in self.access_vars.items():
            access_entry = {
                "username": username,
                "read": read_var.get(),
                "write": write_var.get()
            }
            updated_access.append(access_entry)

        self.client.send_request(Request("update-access-table", [self.file, updated_access]))

    def save_changes_update_response(self, success: bool):
        if success:
            messagebox.showinfo("Access Updated", "Permissions successfully updated.")
            self.access_window.destroy()
        else:
            messagebox.showerror("Update Failed", "Failed to update permissions. Try again.")

    def manage_access(self, user_access_list: list[UserAccess]):
        if not user_access_list:
            messagebox.showerror("Error", "Failed to load access list.")
            return

        self.file = user_access_list[0].file

        self.access_window = ctk.CTkToplevel(self)
        self.access_window.title(f"Manage Access - {self.file.filename}")
        self.access_window.geometry("500x600")

        ctk.CTkLabel(self.access_window, text="Username").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.access_window, text="Read").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.access_window, text="Write").grid(row=0, column=2, padx=10, pady=5)

        self.access_vars = {}

        for user_access in user_access_list:
            self.create_user_row(user_access.user.username, user_access.can_read, user_access.can_write)

        self.new_user_entry = ctk.CTkEntry(self.access_window, placeholder_text="New username")
        self.save_btn = ctk.CTkButton(
            self.access_window,
            text="Save Changes",
            command=self.save_changes
        )
        self.add_user_btn = ctk.CTkButton(
            self.access_window,
            text="Add User",
            command=lambda: self.client.send_request(Request("check-user-exists", self.new_user_entry.get()))
        )

        starting_row = len(self.access_vars) + 1
        self.new_user_entry.grid(row=starting_row, column=0, padx=10, pady=10)
        self.add_user_btn.grid(row=starting_row, column=1, padx=10, pady=10)
        self.save_btn.grid(row=starting_row + 1, columnspan=3, pady=15)

    def open_file(self, file): # todo: use instead the already built editor that i have created
        new_window = ctk.CTkToplevel(self)
        new_window.title(file.filename)
        new_window.geometry("600x400")
        ctk.CTkLabel(new_window, text= f"{file.filename}", font= ("Arial", 16)).pack(pady=10)

        content_box = ctk.CTkTextbox(new_window, wrap="word", width=550, height=300)
        content_box.insert("1.0", file.content)
        content_box.pack(padx=20, pady=10)

    def add_file(self):
        new_name = simpledialog.askstring("New File", "Enter file name:")
        if new_name:
            new_file = File(filename= new_name, content= '', owner= self.my_user.username, creation_date= datetime.now().strftime("%Y-%m-%d"))

            self.client.send_request(Request("add-file", [new_file, self.my_user]))

            self.file_list.append(new_file)
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
    pass