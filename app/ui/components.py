import tkinter as tk
from tkinter import ttk


class SearchResultsTable(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self._documents = {}

        columns = ("name", "extension", "size", "path")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            style="Results.Treeview",
        )
        self.tree.heading("name", text="Nome")
        self.tree.heading("extension", text="Extensão")
        self.tree.heading("size", text="Tamanho")
        self.tree.heading("path", text="Caminho")

        self.tree.column("name", width=260, minwidth=140)
        self.tree.column("extension", width=90, minwidth=70, anchor=tk.CENTER)
        self.tree.column("size", width=100, minwidth=80, anchor=tk.E)
        self.tree.column("path", width=480, minwidth=220)

        vertical_scroll = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        horizontal_scroll = ttk.Scrollbar(
            self,
            orient=tk.HORIZONTAL,
            command=self.tree.xview,
        )
        self.tree.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )
        self.tree.tag_configure("even", background="#FFFFFF")
        self.tree.tag_configure("odd", background="#F8FAFD")

        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def set_documents(self, documents):
        self.tree.delete(*self.tree.get_children())
        self._documents.clear()

        for index, document in enumerate(documents):
            item = self.tree.insert("", tk.END, values=(
                document.name,
                (document.extension or "").upper(),
                self._format_size(document.size),
                str(document.path),
            ), tags=("even" if index % 2 == 0 else "odd",))
            self._documents[item] = document

    def selected_document(self):
        selection = self.tree.selection()
        return self._documents.get(selection[0]) if selection else None

    @staticmethod
    def _format_size(size):
        if size is None:
            return "-"

        if size < 1024:
            return f"{size} B"

        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"

        return f"{size / (1024 * 1024):.1f} MB"
