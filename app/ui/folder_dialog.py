import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


class FolderSettingsDialog:

    def __init__(self, parent, service, on_saved=None):
        self.service = service
        self.on_saved = on_saved
        self.window = tk.Toplevel(parent)
        self.window.title("Pastas monitoradas")
        self.window.geometry("620x470")
        self.window.minsize(520, 400)
        self.window.transient(parent)
        self.window.grab_set()

        settings = service.load()
        self.downloads = tk.BooleanVar(value=settings.downloads)
        self.documents = tk.BooleanVar(value=settings.documents)
        self.desktop = tk.BooleanVar(value=settings.desktop)

        self._build()

        for path in settings.custom_folders:
            self.custom_folders.insert(tk.END, str(path))

    def _build(self):
        content = ttk.Frame(self.window, padding=22)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(6, weight=1)

        ttk.Label(
            content,
            text="Pastas monitoradas",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            content,
            text="Escolha as pastas padrão e adicione outros locais do computador.",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 14))

        ttk.Checkbutton(
            content,
            text="Downloads",
            variable=self.downloads,
        ).grid(row=2, column=0, sticky="w", pady=3)
        ttk.Checkbutton(
            content,
            text="Documentos",
            variable=self.documents,
        ).grid(row=3, column=0, sticky="w", pady=3)
        ttk.Checkbutton(
            content,
            text="Área de Trabalho",
            variable=self.desktop,
        ).grid(row=4, column=0, sticky="w", pady=3)

        ttk.Label(
            content,
            text="Pastas personalizadas",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=5, column=0, sticky="w", pady=(16, 7))

        list_frame = ttk.Frame(content)
        list_frame.grid(row=6, column=0, columnspan=2, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.custom_folders = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=("Segoe UI", 9),
            borderwidth=1,
            relief="solid",
        )
        self.custom_folders.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.custom_folders.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.custom_folders.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(content)
        actions.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(
            actions,
            text="Adicionar pasta...",
            command=self.add_folder,
        ).pack(side=tk.LEFT)
        ttk.Button(
            actions,
            text="Remover selecionadas",
            command=self.remove_selected,
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(
            actions,
            text="Salvar",
            command=self.save,
        ).pack(side=tk.RIGHT)
        ttk.Button(
            actions,
            text="Cancelar",
            command=self.window.destroy,
        ).pack(side=tk.RIGHT, padx=8)

    def add_folder(self):
        selected = filedialog.askdirectory(
            parent=self.window,
            title="Selecione uma pasta para monitorar",
            mustexist=True,
        )

        if not selected:
            return

        normalized = str(Path(selected).resolve(strict=False)).casefold()
        existing = {
            str(Path(value).resolve(strict=False)).casefold()
            for value in self.custom_folders.get(0, tk.END)
        }

        if normalized not in existing:
            self.custom_folders.insert(tk.END, selected)

    def remove_selected(self):
        for index in reversed(self.custom_folders.curselection()):
            self.custom_folders.delete(index)

    def save(self):
        try:
            settings = self.service.save(
                self.downloads.get(),
                self.documents.get(),
                self.desktop.get(),
                self.custom_folders.get(0, tk.END),
            )
        except OSError as error:
            messagebox.showerror(
                "Não foi possível salvar",
                str(error),
                parent=self.window,
            )
            return

        self.window.destroy()

        if self.on_saved:
            self.on_saved(settings)
