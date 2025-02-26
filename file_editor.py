import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar
import os


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("CoEdit")
        self.root.geometry("800x600")

        # Frame for text area and scroll bar
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(expand=True, fill="both")

        self.text_area = tk.Text(self.text_frame, wrap="word", undo=True)
        self.text_area.pack(side="left", expand=True, fill="both")

        # Set the scrollbar to be thicker
        self.scroll_bar = Scrollbar(self.text_frame, command=self.text_area.yview, width=20)  # Width set to 20
        self.scroll_bar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scroll_bar.set)

        # Search frame
        self.search_frame = tk.Frame(self.root)
        self.search_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.search_entry = tk.Entry(self.search_frame, width=30)
        self.search_entry.pack(side="left", padx=(0, 5))

        self.search_button = tk.Button(self.search_frame, text="Find", command=self.find_text)
        self.search_button.pack(side="left")

        self.next_button = tk.Button(self.search_frame, text="Next", command=self.next_occurrence)
        self.next_button.pack(side="left", padx=(5, 0))

        self.prev_button = tk.Button(self.search_frame, text="Previous", command=self.prev_occurrence)
        self.prev_button.pack(side="left", padx=(5, 0))

        self.result_label = tk.Label(self.search_frame, text="")
        self.result_label.pack(side="left", padx=(5, 0))

        # Menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_command(label="Print", command=self.print_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Bind Ctrl+F to find_text method
        self.root.bind('<Control-f>', self.find_text)
        self.root.bind('<Control-MouseWheel>', self.change_font_size)

        # Initialize occurrence tracking
        self.current_occurrence = 0
        self.occurrences = []
        self.current_font_size = 12  # Default font size
        self.min_font_size = 8       # Minimum font size limit
        self.max_font_size = 36      # Maximum font size limit
        self.text_area.configure(font=("Helvetica", self.current_font_size))

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
                self.root.title(f"Simple Text Editor - {file_path}")

    def save_file(self):
        try:
            file_path = self.root.title().split(" - ")[1]
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
        except IndexError:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.root.title(f"Simple Text Editor - {file_path}")

    def print_file(self):
        try:
            file_path = "temp_print.txt"
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
            os.startfile(file_path, "print")
        except Exception as e:
            messagebox.showerror("Print Error", str(e))

    def change_font_size(self, event):
        # Increase or decrease font size based on scroll direction
        if event.delta > 0:  # Scroll up
            self.current_font_size = min(self.max_font_size, self.current_font_size + 1)
        elif event.delta < 0:  # Scroll down
            self.current_font_size = max(self.min_font_size, self.current_font_size - 1)

        # Update text area font
        self.text_area.configure(font=("Helvetica", self.current_font_size))

    def find_text(self, event=None):
        # Clear previous highlights before finding new occurrences
        self.text_area.tag_remove("highlight", 1.0, tk.END)
        self.occurrences = []  # Reset occurrences list
        self.current_occurrence = 0  # Reset current occurrence

        search_term = self.search_entry.get()
        if search_term:
            content = self.text_area.get(1.0, tk.END)
            start_idx = 0
            while True:
                start_idx = content.lower().find(search_term.lower(), start_idx)
                if start_idx == -1:
                    break
                end_idx = start_idx + len(search_term)
                self.text_area.tag_add("highlight", f"1.0 + {start_idx} chars", f"1.0 + {end_idx} chars")
                self.occurrences.append(start_idx)  # Store the start index
                start_idx += len(search_term)  # Move past this match to find the next

            self.text_area.tag_config("highlight", background="yellow")

            if self.occurrences:
                self.result_label.config(text=f"Found {len(self.occurrences)} occurrences.")
                self.current_occurrence = 0  # Reset to first occurrence
                self.jump_to_occurrence()
            else:
                self.result_label.config(text="No occurrences found.")

    def jump_to_occurrence(self):
        if self.occurrences:
            self.text_area.mark_set("insert", f"1.0 + {self.occurrences[self.current_occurrence]} chars")
            self.text_area.see("insert")
            self.highlight_current_occurrence()

    def highlight_current_occurrence(self):
        # Remove previous highlights
        self.text_area.tag_remove("current", 1.0, tk.END)
        start = self.occurrences[self.current_occurrence]
        end = start + len(self.search_entry.get())
        self.text_area.tag_add("current", f"1.0 + {start} chars", f"1.0 + {end} chars")
        self.text_area.tag_config("current", background="lightblue")

    def next_occurrence(self):
        if self.occurrences:
            self.current_occurrence = (self.current_occurrence + 1) % len(self.occurrences)
            self.jump_to_occurrence()

    def prev_occurrence(self):
        if self.occurrences:
            self.current_occurrence = (self.current_occurrence - 1) % len(self.occurrences)
            self.jump_to_occurrence()


if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()
