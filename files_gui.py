import os
import tkinter

import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime


from file import File
from file_editor import FileEditor
from request import Request
from user import User
from user_access import UserAccess

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class FileManagerApp(ctk.CTk):
    def __init__(self, gui_manager):
        """
        Initializes the FileManagerApp.

        :param gui_manager: The GUI manager providing the container and client.
        :type gui_manager: Any
        """
        super().__init__()
        self.open_editors = {}
        self.container = gui_manager.container
        self.client = gui_manager.client

        self.files_frame = ctk.CTkFrame(self.container)

        self.filtered_files = []

        self.create_widgets()
        self.my_user = None



    def load_files(self):
        """
        Loads files from the server and displays them.

        :return: None
        :rtype: None
        """
        file_objects = self.client.get_response_nowait()
        print(type(file_objects))
        print(file_objects)

        if file_objects is not None:
            self.file_list = file_objects.data
            self.filtered_files = self.file_list.copy()

        self.display_files()

    def refresh_files(self, files):
        """
        Refreshes the file list with the provided files.

        :param files: List of File objects to update the UI with.
        :type files: list[File]

        :return: None
        :rtype: None
        """
        if files is not None:
            self.file_list = files
            self.filtered_files = self.file_list.copy()

        self.display_files()

    def display_files(self):
        """
        Displays the filtered files in the UI.

        :return: None
        :rtype: None
        """
        for widget in self.file_frame.winfo_children():
            widget.destroy()

        for i, file in enumerate(self.filtered_files):
            action_btn = ctk.CTkButton(self.file_frame, text="⋮", width=30, command=lambda f=file: self.show_actions(f))
            action_btn.grid(row=i, column=0, padx=5, pady=5)

            name_label = ctk.CTkLabel(self.file_frame, text=file.filename, anchor="w", width=200)
            name_label.grid(row=i, column=1, sticky="w")
            name_label.bind("<Double-Button-1>", lambda e, f=file: self.client.send_request(Request("open-file", [self.my_user, f])))

            ctk.CTkLabel(self.file_frame, text=file.owner.username, width=100).grid(row=i, column=2)
            ctk.CTkLabel(self.file_frame, text=file.creation_date, width=150).grid(row=i, column=3)

    def create_widgets(self):
        """
        Creates and packs all the widgets for the file manager UI.

        :return: None
        :rtype: None
        """
        # Top bar
        top_bar = ctk.CTkFrame(self.files_frame)
        top_bar.pack(fill="x", padx=10, pady=10)

        self.disconnect_btn = ctk.CTkButton(top_bar, text="Disconnect", command=self.disconnect)
        self.disconnect_btn.pack(side="left")

        self.add_file_btn = ctk.CTkButton(top_bar, text="+ New File", command=self.add_file)
        self.add_file_btn.pack(side="left", padx=10)

        # Refresh button with Unicode icon
        self.refresh_btn = ctk.CTkButton(
            top_bar,
            text="↻",
            width=40,
            command=lambda: self.client.send_request(Request('refresh-files', self.my_user))
        )
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
        """
        Filters the file list based on the search query.

        :return: None
        :rtype: None
        """
        query = self.search_entry.get().lower()
        self.filtered_files = [file for file in self.file_list if query in file.filename.lower()]
        self.display_files()

    def sort_files(self, criterion):
        """
        Sorts the filtered file list based on the selected criterion.

        :param criterion: Sorting criterion: "Name", "Owner", or "Date".
        :type criterion: str

        :return: None
        :rtype: None
        """
        if criterion == "Name":
            self.filtered_files.sort(key=lambda x: x.filename.lower())
        elif criterion == "Owner":
            self.filtered_files.sort(key=lambda x: x.owner.username.lower())
        elif criterion == "Date":
            self.filtered_files.sort(key=lambda x: x.creation_date.date(), reverse=True)
        self.display_files()



    def show_actions(self, file):
        """
        Shows context menu with actions based on user access.

        :param file: The file to manage actions for.
        :type file: File

        :return: None
        :rtype: None
        """
        print(self.my_user)
        menu = tkinter.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Rename File", command=lambda: self.rename_file(file))
        if file.owner.user_id != self.my_user.user_id:
            menu.add_command(label="🗑️ Delete For Me", command=lambda: self.delete_file_for_me(file))
        if file.owner.user_id == self.my_user.user_id:
            menu.add_command(label="👥 Manage Access", command=lambda: self.client.send_request(Request("get-access-list", file)))
            menu.add_command(label="🗑️ Delete File", command=lambda: self.delete_file(file))

        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def rename_file(self, file):
        """
        Renames the specified file after prompting the user.

        :param file: The file to rename.
        :type file: File

        :return: None
        :rtype: None
        """
        new_name = simpledialog.askstring("Rename File", "Enter new name:", initialvalue=file.filename)
        if new_name:
            self.client.send_request(Request("rename-file", [file, new_name]))

    def rename_file_success(self, success_rename: bool):
        """
        Handles the result of a rename file operation.

        :param success_rename: Whether the rename operation was successful.
        :type success_rename: bool

        :return: None
        :rtype: None
        """
        if success_rename:
            messagebox.showinfo("rename", 'rename was successful')
        else:
            messagebox.showerror("rename", 'rename was unsuccessful')
        #     file.filename = new_name
        self.search_files()

    def delete_file(self, file):
        """
        Deletes the specified file if the user confirms.

        :param file: The file to delete.
        :type file: File

        :return: None
        :rtype: None
        """
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file.filename}'?")
        if confirm:
            self.client.send_request(Request("delete-file", [file, self.my_user]))
            self.file_list.remove(file)
            self.search_files()

    def delete_file_for_me(self, file):
        """
        Removes the user's access to a file without deleting it globally.

        :param file: The file to remove access from.
        :type file: File

        :return: None
        :rtype: None
        """
        confirm = messagebox.askyesno("Confirm", f"Remove access to '{file.filename}' just for you?")
        if confirm:
            self.client.send_request(Request("delete-file-for-me", [file, self.my_user]))
            self.file_list.remove(file)
            self.search_files()

    def sync_read_write(self, read_var, write_var):
        """
        Synchronizes the read/write toggles to ensure valid permission settings.

        :param read_var: Read permission variable.
        :type read_var: ctk.BooleanVar

        :param write_var: Write permission variable.
        :type write_var: ctk.BooleanVar

        :return: None
        :rtype: None
        """
        if not read_var.get():
            write_var.set(False)
        if write_var.get() and not read_var.get():
            read_var.set(True)

    def create_user_row(self, username, read_default=True, write_default=False):
        """
        Creates a row in the access control window for a user.

        :param username: Username of the user to add.
        :type username: str

        :param read_default: Whether read is checked by default.
        :type read_default: bool

        :param write_default: Whether write is checked by default.
        :type write_default: bool

        :return: None
        :rtype: None
        """
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

    def update_access_controls_layout(self):
        """
        Updates the layout of the access control window.

        :return: None
        :rtype: None
        """
        new_row = len(self.access_vars) + 1
        self.new_user_entry.grid(row=new_row, column=0, padx=10, pady=10)
        self.add_user_btn.grid(row=new_row, column=1, padx=10, pady=10)
        self.save_btn.grid(row=new_row + 1, columnspan=3, pady=15)

    def add_user(self, user: User):
        """
        Adds a new user to the file's access list.

        :param user: The user to add.
        :type user: User

        :return: None
        :rtype: None
        """
        if user is None:
            messagebox.showerror("User Not Found", "No such user exists in the database.")
            return

        if user.username in self.access_vars:
            messagebox.showwarning("Already Exists", "User already has access.")
            return

        self.create_user_row(user.username, read_default=True, write_default=False)
        self.update_access_controls_layout()
        self.new_user_entry.delete(0, "end")

    def save_changes(self):
        """
        Sends updated access permissions to the server.

        :return: None
        :rtype: None
        """
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
        """
        Handles the server's response to an access update request.

        :param success: Whether the update was successful.
        :type success: bool

        :return: None
        :rtype: None
        """
        if success:
            messagebox.showinfo("Access Updated", "Permissions successfully updated.")
            self.access_window.destroy()
        else:
            messagebox.showerror("Update Failed", "Failed to update permissions. Try again.")

    def manage_access(self, user_access_list: list[UserAccess]):
        """
        Opens the access control window with the current access list.

        :param user_access_list: List of UserAccess objects for the file.
        :type user_access_list: list[UserAccess]

        :return: None
        :rtype: None
        """
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

    def open_file(self, file: File, content: str):
        """
        Opens the file in an editor window if content is available.

        :param file: File to open.
        :type file: File

        :param content: File content to load in editor.
        :type content: str

        :return: None
        :rtype: None
        """
        if content is not None:
            editor_window = FileEditor(self.client, file, self.my_user, content)  # Pass content here
            editor_window.title(file.filename)
            self.open_editors[file.file_id] = editor_window
        else:
            messagebox.showinfo("no permission", "You don't have permissions for this file.")

    def apply_file_update(self, file: File, changes: list[dict]):
        """
        Applies incoming changes to an open file editor.

        :param file: File object being edited.
        :type file: File

        :param changes: List of changes to apply.
        :type changes: list[dict]

        :return: None
        :rtype: None
        """
        editor = self.open_editors.get(file.file_id)
        if editor:
            editor.apply_changes(changes)

    def write_access_response(self, file: File, write_access):
        """
        Handles server response indicating write access status.

        :param file: File object for which access is being checked.
        :type file: File

        :param write_access: Whether the user has write access.
        :type write_access: bool

        :return: None
        :rtype: None
        """
        editor = self.open_editors.get(file.file_id)
        if editor and write_access:
            editor.on_text_change()
        elif not write_access:
            editor.show_no_write_access_message()

    def add_file(self):
        """
        Prompts user for a file name and sends a request to create it.

        :return: None
        :rtype: None
        """
        new_name = simpledialog.askstring("New File", "Enter file name:")
        if new_name:
            file_path = os.path.join('CoEdit_users', self.my_user.username, new_name)

            new_file = File(
                filename=new_name,
                owner=self.my_user,  # Assuming my_user holds the logged-in user
                path=file_path,  # Path to be created and stored on the server
                creation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date and time
            )

            # Send the file creation request to the server
            self.client.send_request(Request("add-file", [new_file, self.my_user]))

    def add_file_refresh(self, success: bool, new_file):
        """
        Handles the result of a file creation request.

        :param success: Whether file creation was successful.
        :type success: bool

        :param new_file: The newly created File object.
        :type new_file: File

        :return: None
        :rtype: None
        """
        if success:
            self.file_list.append(new_file)
            messagebox.showinfo("File Added", f"New file '{new_file.filename}' created successfully.")
        else:
            messagebox.showinfo("File Added", f"New file '{new_file.filename}' failed to be created.")
        self.search_files()

    def disconnect(self):
        """
        Asks for confirmation and disconnects the user.

        :return: None
        :rtype: None
        """
        result = messagebox.askyesno("Disconnect", "Are you sure you want to disconnect?")
        if result:
            self.destroy()

    def show(self):
        """
        Displays the file manager frame.

        :return: None
        :rtype: None
        """
        self.files_frame.pack(fill="both", expand=True)

    def hide(self):
        """
        Hides the file manager frame.

        :return: None
        :rtype: None
        """
        self.files_frame.pack_forget()


if __name__ == "__main__":
    pass