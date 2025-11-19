import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import load_config, save_config, load_ignore_list, save_ignore_list
from utils.file_analyzer import get_all_files, find_unsorted_files, format_file_size
from utils.file_operations import create_result_folder, copy_unsorted_files
from ui.dialogs import IgnoreListDialog


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор файлов")
        self.center_window()

        self.config = load_config()
        self.unsorted_files = []
        self.sort_column_name = None  # Текущая колонка сортировки
        self.sort_reverse = False  # Направление сортировки

        self.create_widgets()
        self.load_saved_paths()
        self.root.after(100, self.ask_previus_folder)

    def create_widgets(self):
        """Создание виджетов главного окна"""

        # Фрейм выбора папок
        path_frame = ttk.LabelFrame(self.root, text="Выбор папок", padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(path_frame, text="Исходная папка:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.source_entry = ttk.Entry(path_frame, width=60)
        self.source_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(path_frame, text="Обзор", command=self.select_source_folder).grid(
            row=0, column=2, pady=2
        )

        ttk.Label(path_frame, text="Папка отсортированных:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.sorted_entry = ttk.Entry(path_frame, width=60)
        self.sorted_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(path_frame, text="Обзор", command=self.select_sorted_folder).grid(
            row=1, column=2, pady=2
        )

        # Фрейм кнопок действий
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill=tk.X, padx=10)

        ttk.Button(action_frame, text="Анализировать", command=self.analyze_files).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="Копировать неотсортированные", command=self.copy_files
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Игнор-лист", command=self.show_ignore_list).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            action_frame, text="Очистить историю", command=self.clear_history
        ).pack(side=tk.LEFT, padx=5)

        # Фрейм результатов
        result_frame = ttk.LabelFrame(self.root, text="Результаты", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_label = ttk.Label(result_frame, text="Файлов не найдено")
        self.result_label.pack(anchor=tk.W, pady=5)

        # Таблица файлов
        columns = ("name", "size", "modified", "type", "path")
        self.tree = ttk.Treeview(
            result_frame, columns=columns, show="headings", selectmode=tk.EXTENDED
        )

        self.tree.heading("name", text="Имя", command=lambda: self.sort_column("name"))
        self.tree.heading(
            "size", text="Размер", command=lambda: self.sort_column("size")
        )
        self.tree.heading(
            "modified", text="Изменён", command=lambda: self.sort_column("modified")
        )
        self.tree.heading("type", text="Тип", command=lambda: self.sort_column("type"))
        self.tree.heading("path", text="Путь", command=lambda: self.sort_column("path"))

        self.tree.column("name", width=200)
        self.tree.column("size", width=100)
        self.tree.column("modified", width=150)
        self.tree.column("type", width=80)
        self.tree.column("path", width=300)

        scrollbar = ttk.Scrollbar(
            result_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Добавить в игнор-лист", command=self.add_to_ignore
        )
        self.tree.bind("<Button-2>", self.show_context_menu)  # ПКМ на Маке
        self.tree.bind("<Button-3>", self.show_context_menu)  # ПКМ на Windows/Linux

    def center_window(self):
        """Центрировать окно на экране"""

        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 900
        window_height = 600

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def load_saved_paths(self):
        self.source_entry.insert(0, self.config.get("source_folder", ""))
        self.sorted_entry.insert(0, self.config.get("sorted_folder", ""))

    def ask_previus_folder(self):
        """Предложить последний путь из истории для исходной папки"""

        if self.config.get("history"):
            last_path = self.config["history"][-1]
            if messagebox.askyesno(
                "Использовать последний каталог?",
                f"Использовать последний каталог из истории?\n\n{last_path}",
            ):
                self.source_entry.delete(0, tk.END)
                self.source_entry.insert(0, last_path)
                self.config["source_folder"] = last_path
                save_config(self.config)

    def select_source_folder(self):
        folder = filedialog.askdirectory(
            title="Выберите исходную папку", initialdir="./"
        )
        if folder:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)
            self.config["source_folder"] = folder
            save_config(self.config)

    def select_sorted_folder(self):
        folder = filedialog.askdirectory(
            title="Выберите папку отсортированных файлов", initialdir="./"
        )
        if folder:
            self.sorted_entry.delete(0, tk.END)
            self.sorted_entry.insert(0, folder)
            self.config["sorted_folder"] = folder
            save_config(self.config)

    def analyze_files(self):
        source_folder = self.source_entry.get()
        sorted_folder = self.sorted_entry.get()

        if not source_folder or not sorted_folder:
            messagebox.showwarning("Предупреждение", "Выберите обе папки")
            return

        self.tree.delete(*self.tree.get_children())

        source_files = get_all_files(source_folder)
        sorted_files = get_all_files(sorted_folder)
        ignore_list = load_ignore_list(source_folder)

        self.unsorted_files = find_unsorted_files(
            source_files, sorted_files, ignore_list
        )

        for file_info in self.unsorted_files:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    file_info["name"],
                    format_file_size(file_info["size"]),
                    file_info["modified"].strftime("%Y-%m-%d %H:%M:%S"),
                    file_info["extension"],
                    file_info["path"],
                ),
            )

        self.result_label.config(
            text=f"Найдено неотсортированных файлов: {len(self.unsorted_files)}"
        )

    def copy_files(self):
        if not self.unsorted_files:
            messagebox.showwarning("Предупреждение", "Нет файлов для копирования")
            return

        source_folder = self.source_entry.get()
        result_folder = create_result_folder(source_folder)

        copied, errors = copy_unsorted_files(
            self.unsorted_files, source_folder, result_folder
        )

        if errors:
            messagebox.showwarning(
                "Предупреждение", f"Скопировано: {copied}\nОшибок: {len(errors)}"
            )
        else:
            messagebox.showinfo(
                "Успех", f"Скопировано {copied} файлов в:\n{result_folder}"
            )

        # Сохранить в истории
        if "history" not in self.config:
            self.config["history"] = []
        self.config["history"].append(result_folder)
        if messagebox.askyesno(
            "Использовать новый каталог?",
            f"Использовать новый каталог?\n\n{result_folder}",
        ):
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, result_folder)
            self.config["source_folder"] = result_folder
        save_config(self.config)

    def show_ignore_list(self):
        source_folder = self.source_entry.get()
        if not source_folder:
            messagebox.showwarning("Предупреждение", "Выберите исходную папку")
            return

        dialog = IgnoreListDialog(self.root, source_folder)
        self.root.wait_window(dialog.dialog)

    def add_to_ignore(self):
        selected = self.tree.selection()
        if not selected:
            return

        source_folder = self.source_entry.get()
        ignore_list = load_ignore_list(source_folder)

        for item in selected:
            values = self.tree.item(item, "values")
            filename = values[0]
            if filename not in ignore_list:
                ignore_list.append(filename)

        save_ignore_list(source_folder, ignore_list)
        messagebox.showinfo("Успех", "Файлы добавлены в игнор-лист")
        self.analyze_files()

    def show_context_menu(self, event):
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def sort_column(self, col):
        if self.sort_column_name == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column_name = col
            self.sort_reverse = False

        data = [
            (self.tree.set(child, col), child) for child in self.tree.get_children("")
        ]
        data.sort(reverse=self.sort_reverse)

        for index, (_, child) in enumerate(data):
            self.tree.move(child, "", index)

        for column in ("name", "size", "modified", "type", "path"):
            heading = self.tree.heading(column, "text")
            heading = heading.split(" ")[0]

            if column == col:
                heading += " ↑" if self.sort_reverse else " ↓"

            if column != col:
                heading_map = {
                    "name": "Имя",
                    "size": "Размер",
                    "modified": "Изменён",
                    "type": "Тип",
                    "path": "Путь",
                }
                heading = heading_map.get(column, heading)

            self.tree.heading(column, text=heading)

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить историю созданных папок?"):
            self.config["history"] = []
            save_config(self.config)
            messagebox.showinfo("Успех", "История очищена")
