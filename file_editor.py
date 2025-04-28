
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog


class FileEditor(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("CoEdit")
        self.geometry("800x600")

        # Search
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(pady=5)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search...", width=200)
        self.search_entry.pack(side="left", padx=5)

        self.search_button = ctk.CTkButton(self.search_frame, text="🔍", width=30, command=self.find_text)
        self.search_button.pack(side="right", padx=5)

        # Text Widget
        self.text_area = ctk.CTkTextbox(self, wrap="word")
        self.text_area.pack(expand=True, fill="both", padx=5, pady=5)

        # Menu using Tkinter
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        # Keyboard bindings
        self.bind("<Control-f>", lambda event: self.find_text())

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", file.read())

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get("1.0", "end-1c"))

    def find_text(self):
        self.text_area.tag_remove("highlight", "1.0", "end")
        search_text = self.search_entry.get()
        if search_text:
            start_pos = "1.0"
            while True:
                start_pos = self.text_area.search(search_text, start_pos, stopindex="end")
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_text)}c"
                self.text_area.tag_add("highlight", start_pos, end_pos)
                start_pos = end_pos
            self.text_area.tag_config("highlight", background="yellow", foreground="black")


if __name__ == "__main__":
    app = FileEditor()
    app.mainloop()
