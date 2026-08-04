import os
import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from app.ui.components import SearchResultsTable
from app.ui.folder_dialog import FolderSettingsDialog


class MainWindow:

    BACKGROUND = "#F4F7FB"
    SURFACE = "#FFFFFF"
    HEADER = "#111827"
    PRIMARY = "#5B5CE2"
    PRIMARY_HOVER = "#4748C7"
    TEXT = "#172033"
    MUTED = "#687386"
    BORDER = "#DDE3ED"

    def __init__(
        self,
        search_service,
        analysis_service=None,
        root=None,
        folder_service=None,
    ):
        self.search_service = search_service
        self.analysis_service = analysis_service
        self.folder_service = folder_service
        self.root = root or tk.Tk()
        self._batch_running = False
        self._batch_stop_requested = threading.Event()
        self._batch_clock_token = 0
        self._batch_events = queue.Queue()
        self.query = tk.StringVar(master=self.root)
        self.status = tk.StringVar(master=self.root, value="Pronto para pesquisar")
        self.analysis_activity = tk.StringVar(
            master=self.root,
            value="IA aguardando início da análise",
        )
        self.analysis_activity_details = tk.StringVar(
            master=self.root,
            value="Clique em “Analisar documentos pendentes” para iniciar.",
        )
        self.detail_name = tk.StringVar(master=self.root, value="Selecione um documento")
        self.detail_category = tk.StringVar(master=self.root, value="Sem categoria")
        self.detail_summary = tk.StringVar(
            master=self.root,
            value="O resumo gerado pelo Gemma aparecerá aqui.",
        )
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
            "DetailName.TLabel",
            background="#F8FAFD",
            foreground=self.TEXT,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "DetailText.TLabel",
            background="#F8FAFD",
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
        self.root.geometry("1280x760")
        self.root.minsize(980, 580)
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
        body = ttk.Frame(self.root, style="App.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        sidebar = tk.Frame(
            body,
            width=286,
            background="#EEF2F7",
            highlightbackground=self.BORDER,
            highlightthickness=1,
            padx=18,
            pady=22,
        )
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        self._build_sidebar(sidebar)

        content = ttk.Frame(body, style="App.TFrame", padding=(26, 24, 28, 20))
        content.grid(row=0, column=1, sticky="nsew")
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
        results_card.rowconfigure(3, weight=1)

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
            text="Analisar documentos pendentes",
            command=self.start_batch_analysis,
            style="Analysis.TButton",
        )
        self.analysis_button.grid(row=0, column=1, rowspan=2, sticky="e")

        self.pause_analysis_button = ttk.Button(
            results_card,
            text="Pausar após o atual",
            command=self.pause_batch_analysis,
            style="Analysis.TButton",
        )
        self.pause_analysis_button.grid(
            row=0, column=2, rowspan=2, sticky="e", padx=(8, 0)
        )
        self.pause_analysis_button.state(["disabled"])

        self.selected_analysis_button = ttk.Button(
            results_card,
            text="Analisar selecionado",
            command=self.start_selected_analysis,
            style="Analysis.TButton",
        )
        self.selected_analysis_button.grid(
            row=0,
            column=3,
            rowspan=2,
            sticky="e",
            padx=(8, 0),
        )
        self.selected_analysis_button.state(["disabled"])

        if self.analysis_service is None:
            self.analysis_button.state(["disabled"])
        else:
            self._update_analysis_button()

        activity_panel = tk.Frame(
            results_card,
            background="#EEF0FF",
            highlightbackground="#CDD1FF",
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        activity_panel.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(4, 12),
        )
        activity_panel.columnconfigure(0, weight=1)
        tk.Label(
            activity_panel,
            textvariable=self.analysis_activity,
            background="#EEF0FF",
            foreground=self.PRIMARY,
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="ew")
        tk.Label(
            activity_panel,
            textvariable=self.analysis_activity_details,
            background="#EEF0FF",
            foreground=self.TEXT,
            anchor="w",
            justify="left",
            wraplength=850,
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="ew", pady=(3, 0))

        self.results = SearchResultsTable(results_card)
        self.results.grid(row=3, column=0, columnspan=4, sticky="nsew")
        self.results.tree.bind("<Double-1>", self.open_selected_document)
        self.results.tree.bind("<<TreeviewSelect>>", self.show_selected_document)

        detail = ttk.Frame(results_card, style="Card.TFrame")
        detail.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(14, 0))
        detail.columnconfigure(1, weight=1)

        detail_surface = tk.Frame(
            detail,
            background="#F8FAFD",
            highlightbackground=self.BORDER,
            highlightthickness=1,
            padx=14,
            pady=11,
        )
        detail_surface.grid(row=0, column=0, sticky="ew")
        detail_surface.columnconfigure(0, weight=1)

        tk.Label(
            detail_surface,
            textvariable=self.detail_name,
            background="#F8FAFD",
            foreground=self.TEXT,
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="ew")
        tk.Label(
            detail_surface,
            textvariable=self.detail_category,
            background="#F8FAFD",
            foreground=self.PRIMARY,
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=1, column=0, sticky="ew", pady=(3, 2))
        tk.Label(
            detail_surface,
            textvariable=self.detail_summary,
            background="#F8FAFD",
            foreground=self.MUTED,
            anchor="w",
            justify="left",
            wraplength=900,
            font=("Segoe UI", 9),
        ).grid(row=2, column=0, sticky="ew")

        self.analysis_progress = ttk.Progressbar(
            content,
            mode="indeterminate",
            length=180,
        )
        self.analysis_progress.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        self.analysis_progress.grid_remove()

        ttk.Label(
            content,
            textvariable=self.status,
            style="Status.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(8, 0))

    def _build_sidebar(self, sidebar):
        tk.Label(
            sidebar,
            text="SEU ESPAÇO",
            background="#EEF2F7",
            foreground=self.MUTED,
            anchor="w",
            font=("Segoe UI", 8, "bold"),
        ).pack(fill=tk.X)
        tk.Label(
            sidebar,
            text="Pastas monitoradas",
            background="#EEF2F7",
            foreground=self.TEXT,
            anchor="w",
            font=("Segoe UI", 14, "bold"),
        ).pack(fill=tk.X, pady=(4, 3))
        tk.Label(
            sidebar,
            text="O BrAIn indexa estes locais ao iniciar.",
            background="#EEF2F7",
            foreground=self.MUTED,
            anchor="w",
            justify="left",
            wraplength=240,
            font=("Segoe UI", 9),
        ).pack(fill=tk.X, pady=(0, 14))

        self.folder_list = tk.Frame(sidebar, background="#EEF2F7")
        self.folder_list.pack(fill=tk.X)

        self.manage_folders_button = ttk.Button(
            sidebar,
            text="＋  Gerenciar pastas",
            command=self.open_folder_settings,
            style="Analysis.TButton",
        )
        self.manage_folders_button.pack(fill=tk.X, pady=(12, 0))

        if self.folder_service is None:
            self.manage_folders_button.state(["disabled"])
            self._render_folder_message("Configuração indisponível")
        else:
            self._refresh_folder_summary()

        ai_card = tk.Frame(
            sidebar,
            background="#E4E7FF",
            padx=13,
            pady=12,
        )
        ai_card.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(
            ai_card,
            text="●  IA LOCAL ATIVA",
            background="#E4E7FF",
            foreground="#3D9A68",
            anchor="w",
            font=("Segoe UI", 8, "bold"),
        ).pack(fill=tk.X)
        tk.Label(
            ai_card,
            text="Gemma 4 · Ollama",
            background="#E4E7FF",
            foreground=self.TEXT,
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        ).pack(fill=tk.X, pady=(4, 1))
        tk.Label(
            ai_card,
            text="Seus documentos permanecem neste computador.",
            background="#E4E7FF",
            foreground=self.MUTED,
            anchor="w",
            justify="left",
            wraplength=220,
            font=("Segoe UI", 8),
        ).pack(fill=tk.X)

    def _refresh_folder_summary(self, settings=None):
        if self.folder_service is None:
            return

        settings = settings or self.folder_service.load()
        folders = []

        if settings.downloads:
            folders.append(("Downloads", Path.home() / "Downloads"))

        if settings.documents:
            folders.append(("Documentos", Path.home() / "Documents"))

        if settings.desktop:
            folders.append(("Área de Trabalho", Path.home() / "Desktop"))

        folders.extend(
            (path.name or str(path), path)
            for path in settings.custom_folders
        )

        for child in self.folder_list.winfo_children():
            child.destroy()

        if not folders:
            self._render_folder_message("Nenhuma pasta configurada")
            return

        for name, path in folders[:6]:
            self._render_folder_item(name, path)

        if len(folders) > 6:
            self._render_folder_message(f"+ {len(folders) - 6} outra(s) pasta(s)")

    def _render_folder_item(self, name, path):
        item = tk.Frame(
            self.folder_list,
            background=self.SURFACE,
            highlightbackground=self.BORDER,
            highlightthickness=1,
            padx=10,
            pady=8,
        )
        item.pack(fill=tk.X, pady=3)

        tk.Label(
            item,
            text=f"●  {name}",
            background=self.SURFACE,
            foreground=self.TEXT,
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        ).pack(fill=tk.X)
        tk.Label(
            item,
            text=str(path),
            background=self.SURFACE,
            foreground=self.MUTED,
            anchor="w",
            font=("Segoe UI", 7),
        ).pack(fill=tk.X, pady=(2, 0))

    def _render_folder_message(self, message):
        tk.Label(
            self.folder_list,
            text=message,
            background="#EEF2F7",
            foreground=self.MUTED,
            anchor="w",
            font=("Segoe UI", 9),
        ).pack(fill=tk.X, pady=8)

    def search(self, _event=None):
        documents = self.search_service.search(self.query.get())
        self.results.set_documents(documents)
        self.status.set(f"{len(documents)} documento(s) encontrado(s)")

    def start_batch_analysis(self):
        if self.analysis_service is None:
            return

        if self._batch_running:
            return

        self._batch_running = True
        self._batch_stop_requested.clear()
        self.analysis_button.state(["disabled"])
        self.selected_analysis_button.state(["disabled"])
        self.pause_analysis_button.state(["!disabled"])
        self.analysis_progress.grid()
        self.analysis_progress.start(12)
        pending = self.analysis_service.pending_count()
        self.status.set(f"Iniciando análise de {pending} documento(s)...")
        self.analysis_activity.set("● Preparando o Gemma")
        self.analysis_activity_details.set(
            f"Fila iniciada com {pending} documento(s) pendente(s)."
        )
        self.root.after(100, self._poll_batch_events)
        threading.Thread(target=self._run_batch_analysis, daemon=True).start()

    def pause_batch_analysis(self):
        if not self._batch_running:
            return

        self._batch_stop_requested.set()
        self.pause_analysis_button.state(["disabled"])
        self.status.set("Pausa solicitada — concluindo o documento atual...")
        self.analysis_activity.set("● Pausa solicitada")

    def _run_batch_analysis(self):
        completed = 0
        failed = 0

        while not self._batch_stop_requested.is_set():
            document = self.analysis_service.next_pending_document()

            if document is None:
                break

            self._batch_events.put(
                ("started", document, completed, failed)
            )

            try:
                outcome = self.analysis_service.analyze_document(document)
            except Exception as error:
                failed += 1
                self._batch_events.put(
                    ("progress", completed, failed, None, error)
                )
                continue

            completed += 1
            self._batch_events.put(
                ("progress", completed, failed, outcome, None)
            )

        paused = self._batch_stop_requested.is_set()
        self._batch_events.put(("finished", completed, failed, paused))

    def _poll_batch_events(self):
        while True:
            try:
                event = self._batch_events.get_nowait()
            except queue.Empty:
                break

            kind, *payload = event

            if kind == "started":
                self._begin_batch_document(*payload)
            elif kind == "progress":
                self._update_batch_progress(*payload)
            elif kind == "finished":
                self._finish_batch_analysis(*payload)

        if self._batch_running:
            self.root.after(100, self._poll_batch_events)

    def _begin_batch_document(self, document, completed, failed):
        self._batch_clock_token += 1
        token = self._batch_clock_token
        started_at = time.monotonic()
        self._refresh_batch_clock(
            token,
            started_at,
            document.name,
            completed,
            failed,
        )

    def _refresh_batch_clock(
        self,
        token,
        started_at,
        document_name,
        completed,
        failed,
    ):
        if not self._batch_running or token != self._batch_clock_token:
            return

        elapsed = int(time.monotonic() - started_at)
        minutes, seconds = divmod(elapsed, 60)
        pending = self.analysis_service.pending_count()
        action = (
            "Pausa solicitada; aguardando este documento"
            if self._batch_stop_requested.is_set()
            else "Gemma analisando"
        )
        self.status.set(
            f"{action}: {document_name} | Tempo: {minutes:02d}:{seconds:02d} | "
            f"Sucessos: {completed} | Falhas: {failed} | Pendentes: {pending}"
        )
        self.analysis_activity.set(f"● {action}")
        self.analysis_activity_details.set(
            f"Arquivo: {document_name}\n"
            f"Tempo: {minutes:02d}:{seconds:02d}  •  Sucessos: {completed}  •  "
            f"Falhas: {failed}  •  Pendentes: {pending}"
        )
        self.root.after(
            1000,
            self._refresh_batch_clock,
            token,
            started_at,
            document_name,
            completed,
            failed,
        )

    def _update_batch_progress(self, completed, failed, outcome, error):
        pending = self.analysis_service.pending_count()

        if outcome is not None:
            detail = f"Concluído: {outcome.document.name}"
        else:
            detail = f"Arquivo ignorado após erro: {error}"

        self.status.set(
            f"{detail} | Sucessos: {completed} | Falhas: {failed} | "
            f"Pendentes: {pending}"
        )
        self.analysis_activity.set(
            "● Documento concluído" if outcome is not None else "● Falha ignorada"
        )
        self.analysis_activity_details.set(detail)

    def _finish_batch_analysis(self, completed, failed, paused):
        self._batch_running = False
        self._batch_clock_token += 1
        self._stop_analysis_progress()
        self.pause_analysis_button.state(["disabled"])
        self._update_analysis_button()
        self.results.set_documents(self.search_service.search(self.query.get()))
        prefix = (
            "Análise pausada com segurança"
            if paused
            else "Primeira análise concluída"
        )
        self.status.set(
            f"{prefix} | Sucessos: {completed} | Falhas ignoradas: {failed} | "
            f"Pendentes: {self.analysis_service.pending_count()}"
        )
        self.analysis_activity.set(f"● {prefix}")
        self.analysis_activity_details.set(
            f"Sucessos: {completed}  •  Falhas ignoradas: {failed}  •  "
            f"Pendentes: {self.analysis_service.pending_count()}"
        )

    def start_selected_analysis(self):
        document = self.results.selected_document()

        if not self.analysis_service.supports(document):
            return

        self._start_analysis(document)

    def _start_analysis(self, document=None):
        if self._batch_running:
            return

        self.analysis_button.state(["disabled"])
        self.selected_analysis_button.state(["disabled"])
        self.analysis_progress.grid()
        self.analysis_progress.start(12)
        target = document.name if document is not None else "o próximo documento"
        self.status.set(f"Gemma está analisando {target}...")
        threading.Thread(
            target=self._analyze_document,
            args=(document,),
            daemon=True,
        ).start()

    def _analyze_document(self, document):
        try:
            if document is None:
                outcome = self.analysis_service.analyze_next()
            else:
                outcome = self.analysis_service.analyze_document(document)
        except Exception as error:
            self.root.after(0, self._finish_analysis_error, error)
        else:
            self.root.after(0, self._finish_analysis, outcome)

    def _finish_analysis(self, outcome):
        self._stop_analysis_progress()
        self._update_analysis_button()

        if outcome is None:
            self.status.set("Nenhum documento compatível pendente de análise")
            return

        documents = self.search_service.search(self.query.get())
        self.results.set_documents(documents)
        document = self.results.select_path(outcome.document.path)

        if document is not None:
            self._show_document(document)
        else:
            self.detail_name.set(outcome.document.name)
            self.detail_category.set(outcome.analysis.category)
            self.detail_summary.set(outcome.analysis.summary)

        self.status.set(
            f"Análise concluída: {outcome.document.name} — "
            f"{outcome.analysis.category}"
        )

    def _finish_analysis_error(self, error):
        self._stop_analysis_progress()
        self._update_analysis_button()
        self.status.set("Não foi possível concluir a análise")
        messagebox.showerror("Erro na análise com Gemma", str(error))

    def _stop_analysis_progress(self):
        self.analysis_progress.stop()
        self.analysis_progress.grid_remove()

    def _update_analysis_button(self):
        if self.analysis_service is None:
            return

        pending = self.analysis_service.pending_count()
        self.analysis_button.configure(
            text=f"Analisar documentos pendentes ({pending})"
        )

        if pending and not self._batch_running:
            self.analysis_button.state(["!disabled"])
        else:
            self.analysis_button.state(["disabled"])

        self._update_selected_analysis_button()

    def show_selected_document(self, _event=None):
        document = self.results.selected_document()

        if document is not None:
            self._show_document(document)
            self._update_selected_analysis_button()

    def _update_selected_analysis_button(self):
        if not hasattr(self, "results"):
            self.selected_analysis_button.state(["disabled"])
            return

        document = self.results.selected_document()

        if (
            self.analysis_service is not None
            and not self._batch_running
            and self.analysis_service.supports(document)
        ):
            self.selected_analysis_button.state(["!disabled"])
        else:
            self.selected_analysis_button.state(["disabled"])

    def _show_document(self, document):
        self.detail_name.set(document.name)

        if document.analysis_error:
            self.detail_category.set("Falha na análise — selecione para tentar novamente")
            self.detail_summary.set(document.analysis_error)
        else:
            self.detail_category.set(document.category or "Ainda não categorizado")
            self.detail_summary.set(
                document.summary or "Este documento ainda não possui resumo."
            )

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

    def open_folder_settings(self):
        if self.folder_service is None:
            return

        FolderSettingsDialog(
            self.root,
            self.folder_service,
            on_saved=self._folder_settings_saved,
        )

    def _folder_settings_saved(self, settings):
        self._refresh_folder_summary(settings)
        total = sum((
            settings.downloads,
            settings.documents,
            settings.desktop,
            len(settings.custom_folders),
        ))
        self.status.set(
            f"Configuração salva: {total} pasta(s). "
            "Reinicie para executar uma nova indexação."
        )
