import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from app.ui.components import SearchResultsTable


class MainWindow:

    BACKGROUND = "#F4F7FB"
    SURFACE = "#FFFFFF"
    HEADER = "#111827"
    PRIMARY = "#5B5CE2"
    PRIMARY_HOVER = "#4748C7"
    TEXT = "#172033"
    MUTED = "#687386"
    BORDER = "#DDE3ED"

    def __init__(self, search_service, analysis_service=None, root=None):
        self.search_service = search_service
        self.analysis_service = analysis_service
        self.root = root or tk.Tk()
        self.query = tk.StringVar(master=self.root)
        self.status = tk.StringVar(master=self.root, value="Pronto para pesquisar")
        self._configure_styles()
        self._build()

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        self.root.configure(background=self.BACKGROUND)
        style.configure("App.TFrame", background=self.BACKGROUND)
        style.configure("Header.TFrame", background=self.HEADER)
        style.configure("Card.TFrame", background=self.SURFACE)

        style.configure(
            "HeaderTitle.TLabel",
            background=self.HEADER,
            foreground="#FFFFFF",
            font=("Segoe UI", 17, "bold"),
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            background=self.HEADER,
            foreground="#AEB8CA",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background=self.BACKGROUND,
            foreground=self.TEXT,
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BACKGROUND,
            foreground=self.MUTED,
            font=("Segoe UI", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background=self.SURFACE,
            foreground=self.TEXT,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "CardHint.TLabel",
            background=self.SURFACE,
            foreground=self.MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Status.TLabel",
            background=self.BACKGROUND,
            foreground=self.MUTED,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Search.TEntry",
            fieldbackground="#F8FAFD",
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            insertcolor=self.TEXT,
            padding=(12, 10),
            font=("Segoe UI", 10),
        )
        style.map(
            "Search.TEntry",
            bordercolor=[("focus", self.PRIMARY)],
            lightcolor=[("focus", self.PRIMARY)],
            darkcolor=[("focus", self.PRIMARY)],
        )
        style.configure(
            "Primary.TButton",
            background=self.PRIMARY,
            foreground="#FFFFFF",
            borderwidth=0,
            padding=(22, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Primary.TButton",
            background=[
                ("pressed", self.PRIMARY_HOVER),
                ("active", self.PRIMARY_HOVER),
            ],
        )
        style.configure(
            "Analysis.TButton",
            background="#EEF0FF",
            foreground=self.PRIMARY,
            borderwidth=0,
            padding=(16, 8),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Analysis.TButton",
            background=[
                ("disabled", "#F1F3F7"),
                ("pressed", "#DFE2FF"),
                ("active", "#DFE2FF"),
            ],
            foreground=[("disabled", "#9AA3B2")],
        )
        style.configure(
            "Results.Treeview",
            background=self.SURFACE,
            fieldbackground=self.SURFACE,
            foreground=self.TEXT,
            borderwidth=0,
            relief="flat",
            rowheight=38,
            font=("Segoe UI", 9),
        )
        style.map(
            "Results.Treeview",
            background=[("selected", "#E7E8FF")],
            foreground=[("selected", self.TEXT)],
        )
        style.configure(
            "Results.Treeview.Heading",
            background="#F1F4F9",
            foreground=self.MUTED,
            borderwidth=0,
            relief="flat",
            padding=(10, 9),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Results.Treeview.Heading",
            background=[("active", "#E8ECF3")],
        )

    def _build(self):
        self.root.title("BrAIn — Busca de Documentos")
        self.root.geometry("1120x700")
        self.root.minsize(780, 500)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self._build_header()
        self._build_content()

    def _build_header(self):
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(28, 16))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        logo = tk.Label(
            header,
            text="B",
            width=2,
            height=1,
            background=self.PRIMARY,
            foreground="#FFFFFF",
            font=("Segoe UI", 16, "bold"),
        )
        logo.grid(row=0, column=0, rowspan=2, padx=(0, 12))

        ttk.Label(
            header,
            text="BrAIn",
            style="HeaderTitle.TLabel",
        ).grid(row=0, column=1, sticky="sw")
        ttk.Label(
            header,
            text="Organização inteligente de documentos locais",
            style="HeaderSubtitle.TLabel",
        ).grid(row=1, column=1, sticky="nw")

        privacy = tk.Label(
            header,
            text="● 100% local",
            background="#1F2937",
            foreground="#8BE0B0",
            padx=12,
            pady=6,
            font=("Segoe UI", 9, "bold"),
        )
        privacy.grid(row=0, column=2, rowspan=2)

    def _build_content(self):
        content = ttk.Frame(self.root, style="App.TFrame", padding=(32, 26, 32, 22))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)

        ttk.Label(
            content,
            text="Encontre seus documentos",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            content,
            text="Pesquise por nome, extensão, categoria ou caminho do arquivo.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 18))

        search_card = ttk.Frame(content, style="Card.TFrame", padding=18)
        search_card.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        search_card.columnconfigure(0, weight=1)

        search_entry = ttk.Entry(
            search_card,
            textvariable=self.query,
            style="Search.TEntry",
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_entry.bind("<Return>", self.search)
        search_entry.focus_set()

        ttk.Button(
            search_card,
            text="Buscar documentos",
            command=self.search,
            style="Primary.TButton",
        ).grid(row=0, column=1)

        results_card = ttk.Frame(content, style="Card.TFrame", padding=(18, 16))
        results_card.grid(row=3, column=0, sticky="nsew")
        results_card.columnconfigure(0, weight=1)
        results_card.rowconfigure(2, weight=1)

        ttk.Label(
            results_card,
            text="Documentos",
            style="CardTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            results_card,
            text="Dê um duplo clique para abrir um arquivo.",
            style="CardHint.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        self.analysis_button = ttk.Button(
            results_card,
            text="Analisar próximo TXT",
            command=self.start_analysis,
            style="Analysis.TButton",
        )
        self.analysis_button.grid(row=0, column=1, rowspan=2, sticky="e")

        if self.analysis_service is None:
            self.analysis_button.state(["disabled"])

        self.results = SearchResultsTable(results_card)
        self.results.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.results.tree.bind("<Double-1>", self.open_selected_document)

        ttk.Label(
            content,
            textvariable=self.status,
            style="Status.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(10, 0))

    def search(self, _event=None):
        documents = self.search_service.search(self.query.get())
        self.results.set_documents(documents)
        self.status.set(f"{len(documents)} documento(s) encontrado(s)")

    def start_analysis(self):
        if self.analysis_service is None:
            return

        self.analysis_button.state(["disabled"])
        self.status.set("Gemma está analisando o próximo documento TXT...")
        threading.Thread(target=self._analyze_next, daemon=True).start()

    def _analyze_next(self):
        try:
            outcome = self.analysis_service.analyze_next()
        except Exception as error:
            self.root.after(0, self._finish_analysis_error, error)
        else:
            self.root.after(0, self._finish_analysis, outcome)

    def _finish_analysis(self, outcome):
        self.analysis_button.state(["!disabled"])

        if outcome is None:
            self.status.set("Nenhum documento TXT pendente de análise")
            return

        documents = self.search_service.search(self.query.get())
        self.results.set_documents(documents)
        self.status.set(
            f"Análise concluída: {outcome.document.name} — "
            f"{outcome.analysis.category}"
        )

    def _finish_analysis_error(self, error):
        self.analysis_button.state(["!disabled"])
        self.status.set("Não foi possível concluir a análise")
        messagebox.showerror("Erro na análise com Gemma", str(error))

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
