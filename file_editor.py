import customtkinter as ctk
import tkinter as tk
class FileEditor(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("CoEdit")
        self.geometry("800x600")

        self.match_positions = []
        self.current_match_index = 0

        # Search
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
        self.text_area._textbox.config(undo=True, maxundo=-1)  # Enable undo/redo

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
