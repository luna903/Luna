import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from config import load_ignore_list, save_ignore_list


def show_info_dialog(message):
    """Displays an information dialog with the given message."""

    messagebox.showinfo("Information", message)


def show_warning_dialog(message):
    """Displays a warning dialog with the given message."""

    messagebox.showwarning("Warning", message)


def show_error_dialog(message):
    """Displays an error dialog with the given message."""

    messagebox.showerror("Error", message)


def ask_directory_selection(title="Select Directory"):
    """Opens a directory selection dialog and returns the selected path."""

    return filedialog.askdirectory(title=title)


def ask_file_selection(title="Select File"):
    """Opens a file selection dialog and returns the selected file path."""

    return filedialog.askopenfilename(title=title)


class IgnoreListDialog:
    def __init__(self, parent, source_folder):
        self.source_folder = source_folder
        self.ignore_list = load_ignore_list(source_folder)

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Игнор-лист")
        self.center_window()

        self.create_widgets()
        self.load_items()

    def center_window(self):
        """Центрировать окно на экране"""

        self.dialog.update_idletasks()

        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        window_width = 500
        window_height = 400

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Файлы в игнор-листе:").pack(anchor=tk.W, pady=5)

        self.listbox = tk.Listbox(frame, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = ttk.Frame(self.dialog, padding=10)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame, text="Удалить выбранные", command=self.remove_selected
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Закрыть", command=self.dialog.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def load_items(self):
        self.listbox.delete(0, tk.END)
        for item in self.ignore_list:
            self.listbox.insert(tk.END, item)

    def remove_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            return

        for index in reversed(selected):
            del self.ignore_list[index]

        save_ignore_list(self.source_folder, self.ignore_list)
        self.load_items()
        messagebox.showinfo("Успех", "Файлы удалены из игнор-листа")
