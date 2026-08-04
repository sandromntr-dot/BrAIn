import os
import tkinter as tk
from tkinter import messagebox, ttk

from app.ui.components import SearchResultsTable


class MainWindow:

    def __init__(self, search_service, root=None):
        self.search_service = search_service
        self.root = root or tk.Tk()
        self.query = tk.StringVar(master=self.root)
        self.status = tk.StringVar(master=self.root, value="Digite para pesquisar")
        self._build()

    def _build(self):
        self.root.title("BrAIn — Busca de Documentos")
        self.root.geometry("1000x620")
        self.root.minsize(720, 420)

        container = ttk.Frame(self.root, padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        title = ttk.Label(
            container,
            text="BrAIn",
            font=("Segoe UI", 20, "bold"),
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        search_entry = ttk.Entry(container, textvariable=self.query)
        search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        search_entry.bind("<Return>", self.search)
        search_entry.focus_set()

        search_button = ttk.Button(
            container,
            text="Buscar",
            command=self.search,
        )
        search_button.grid(row=1, column=1)

        self.results = SearchResultsTable(container)
        self.results.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(12, 8),
        )
        self.results.tree.bind("<Double-1>", self.open_selected_document)

        status_label = ttk.Label(container, textvariable=self.status)
        status_label.grid(row=3, column=0, columnspan=2, sticky="w")

    def search(self, _event=None):
        documents = self.search_service.search(self.query.get())
        self.results.set_documents(documents)
        self.status.set(f"{len(documents)} documento(s) encontrado(s)")

    def open_selected_document(self, _event=None):
        document = self.results.selected_document()

        if document is None:
            return

        if not document.path.exists():
            messagebox.showwarning(
                "Arquivo indisponível",
                f"O arquivo não foi encontrado:\n{document.path}",
            )
            return

        try:
            os.startfile(document.path)
        except OSError as error:
            messagebox.showerror(
                "Não foi possível abrir o arquivo",
                str(error),
            )

    def run(self):
        self.root.mainloop()
