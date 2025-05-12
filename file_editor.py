import difflib
import time
from datetime import datetime

import customtkinter as ctk
import tkinter as tk

import protocol
from client import Client
from request import Request


class FileEditor(ctk.CTkToplevel):
    def __init__(self, client, file, my_user, content):
        super().__init__()
        self.title("CoEdit")
        self.geometry("800x600")

        self.current_file = file
        self.my_user = my_user
        self.client = client

        self.suppress_text_change = False
        self.match_positions = []
        self.current_match_index = 0

        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(pady=5, fill="x", padx=5)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="🔍Search...", width=200)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda event: self.find_text())

        self.prev_button = ctk.CTkButton(self.search_frame, text="⏮", width=30, command=self.prev_match)
        self.prev_button.pack(side="left")

        self.next_button = ctk.CTkButton(self.search_frame, text="⏭", width=30, command=self.next_match)
        self.next_button.pack(side="left")

        self.match_label = ctk.CTkLabel(self.search_frame, text="")
        self.match_label.pack(side="left", padx=10)

        # Text Widget
        self.text_area = ctk.CTkTextbox(self, wrap="word")
        self.text_area.pack(expand=True, fill="both", padx=5, pady=5)
        self.text_area._textbox.config(undo=True, maxundo=-1)
        self.text_area.bind("<<Modified>>", self.on_text_change)
        self.last_update = time.time()
        self.changes_history = []

        self.current_content = content
        self.text_area.insert("1.0", self.current_content)  # Initialize with content

        # Menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        # file_menu.add_command(label="Open", command=self.open_file)
        # file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        # Bindings
        self.bind("<Control-f>", lambda event: self.find_text())
        self.bind("<Control-z>", self.undo)
        self.bind("<Control-y>", self.redo)

    def find_text(self):
        self.text_area.tag_remove("highlight", "1.0", "end")
        search_text = self.search_entry.get()
        self.match_positions = []
        self.current_match_index = 0

        if search_text:
            start_pos = "1.0"
            while True:
                start_pos = self.text_area.search(search_text, start_pos, stopindex="end")
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_text)}c"
                self.match_positions.append((start_pos, end_pos))
                start_pos = end_pos

            for start, end in self.match_positions:
                self.text_area.tag_add("highlight", start, end)

            self.text_area.tag_config("highlight", background="yellow", foreground="black")

            if self.match_positions:
                self.show_match(0)
            else:
                self.match_label.configure(text="No matches")

    def show_match(self, index):
        if not self.match_positions:
            return

        self.current_match_index = index
        start, end = self.match_positions[index]
        self.text_area.tag_remove("current_match", "1.0", "end")
        self.text_area.tag_add("current_match", start, end)
        self.text_area.tag_config("current_match", background="orange", foreground="black")
        self.text_area.see(start)
        self.match_label.configure(text=f"Match {index + 1} of {len(self.match_positions)}")

    def next_match(self):
        if not self.match_positions:
            return
        self.current_match_index = (self.current_match_index + 1) % len(self.match_positions)
        self.show_match(self.current_match_index)

    def prev_match(self):
        if not self.match_positions:
            return
        self.current_match_index = (self.current_match_index - 1) % len(self.match_positions)
        self.show_match(self.current_match_index)

    def undo(self, event=None):
        try:
            print('undo')
            self.text_area._textbox.edit_undo()
        except tk.TclError:
            pass  # Nothing to undo
            print('Nothing to undo')

    def redo(self, event=None):
        try:
            print('redo')
            self.text_area._textbox.edit_redo()
        except tk.TclError:
            pass  # Nothing to redo
            print('Nothing to redo')

    def on_text_change(self, event):
        if self.suppress_text_change:
            return

        self.text_area.edit_modified(False)  # Reset the modified flag
        new_content = self.text_area.get("1.0", "end-1c")

        if new_content == self.current_content:
            return  # No actual change

        # Generate diffs
        diff_dict = self.get_diff_changes(self.current_content, new_content)

        # Append each change to history
        for change in diff_dict:
            self.changes_history.append(change)

        self.current_content = new_content
        self.last_update = time.time()

        # Send the changes to the server
        self.client.send_request(Request('file-content-update', [self.current_file, diff_dict, self.my_user]))
        print('sending request')

    def get_diff_changes(self, old: str, new: str) -> list[dict[str,str]]:
        changes = []

        sm = difflib.SequenceMatcher(None, old, new)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                continue

            old_sub = old[i1:i2]
            new_sub = new[j1:j2]

            # Compute line and character for i1 and j1
            line = old[:i1].count('\n')
            char = i1 - old.rfind('\n', 0, i1) - 1 if '\n' in old[:i1] else i1

            if tag == 'insert':
                changes.append({"insert": new_sub, "line": line, "char": char, "time": time.time()})
            elif tag == 'delete':
                changes.append({"delete": old_sub, "line": line, "char": char, "time": time.time()})
            elif tag == 'replace':
                changes.append({"delete": old_sub, "line": line, "char": char, "time": time.time()})
                changes.append({"insert": new_sub, "line": line, "char": char, "time": time.time()})

        return changes

    def apply_single_change(self, change):
        line = int(change['line']) + 1
        char = int(change['char'])
        index = f"{line}.{char}"

        if 'delete' in change:
            delete_len = len(change['delete'])
            end_index = f"{line}.{char + delete_len}"
            self.text_area.delete(index, end_index)

        if 'insert' in change:
            self.insert_text_preserve_cursor(index, change['insert'])

    def apply_changes(self, changes):
        cursor_index = self.text_area.index("insert")
        self.suppress_text_change = True

        try:
            for change in changes:
                # Find future changes to revert
                incoming_time = change['time']
                future_changes = [c for c in self.changes_history if c['time'] > incoming_time]

                # Revert future changes
                for fc in reversed(future_changes):
                    self.revert_change(fc)

                # Apply incoming change
                self.apply_single_change(change)

                # Add to history
                self.changes_history.append(change)
                self.changes_history.sort(key=lambda x: x['time'])  # Maintain order

                # Reapply future changes
                for fc in future_changes:
                    self.apply_single_change(fc)

            self.current_content = self.text_area.get("1.0", "end-1c")
            self.text_area.edit_modified(False)

        finally:
            self.suppress_text_change = False

    def revert_change(self, change):
        line = int(change['line']) + 1
        char = int(change['char'])
        index = f"{line}.{char}"

        if 'insert' in change:
            delete_len = len(change['insert'])
            end_index = f"{line}.{char + delete_len}"
            self.text_area.delete(index, end_index)
        elif 'delete' in change:
            self.text_area.insert(index, change['delete'])

    def insert_text_preserve_cursor(self, insert_index, content):
        cursor_index = self.text_area.index("insert")

        def index_to_tuple(index_str):
            line, char = map(int, index_str.split('.'))
            return line, char

        cursor_line, cursor_char = index_to_tuple(cursor_index)
        insert_line, insert_char = index_to_tuple(insert_index)

        # Insert the text
        self.text_area.insert(insert_index, content)

        # Decide if cursor needs to be adjusted
        if (insert_line, insert_char) < (cursor_line, cursor_char):
            # If insert is before the cursor, move the cursor forward by the inserted text length
            new_char_index = cursor_char + len(content)
            new_cursor_index = f"{cursor_line}.{new_char_index}"
            self.text_area.mark_set("insert", new_cursor_index)
        else:
            # Insert at or after cursor, keep cursor where it was
            self.text_area.mark_set("insert", cursor_index)

