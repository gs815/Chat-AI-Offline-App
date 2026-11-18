"""A compact Windows desktop chat client for a local Ollama server."""

from __future__ import annotations

import json
import os
import queue
import re
import sys
import threading
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


APP_NAME = "ChatAI"
DEFAULT_URL = "http://localhost:11434"
BG = "#171717"
SIDEBAR = "#141414"
PANEL = "#242424"
PANEL_HOVER = "#303030"
TEXT = "#eeeeee"
MUTED = "#929292"
ACCENT = "#e6e6e6"
ACCENT_TEXT = "#181818"
LINE = "#292929"
FONT = ("Segoe UI", 10)
CONTEXT_LENGTHS = (4096, 8192, 16384, 32768, 65536, 131072, 262144)
LANGUAGE_NAMES = {"en": "English", "it": "Italiano", "es": "Español", "fr": "Français"}
LANGUAGE_CODES = {name: code for code, name in LANGUAGE_NAMES.items()}
TRANSLATIONS = {
    "en": {
        "new_chat": "New chat", "settings": "Settings", "chat_history": "YOUR CHATS",
        "empty_history": "Your conversations\nwill appear here", "placeholder": "Write a message…",
        "welcome_title": "Where should we start?", "welcome_subtitle": "A private chat with the models on your computer.",
        "user": "You", "reasoning": "reasoning", "thinking_on": "Thinking  ON", "thinking_off": "Thinking  OFF",
        "no_models_refresh": "No models available. Check Ollama and press ↻.", "rename": "Rename", "delete": "Delete",
        "rename_title": "Rename chat", "new_name": "New chat name:", "invalid_name": "Invalid name",
        "enter_name": "Enter a name for the chat.", "delete_title": "Delete chat",
        "delete_confirm": "Delete “{title}” and all its messages?", "copy": "Copy", "copied": "Copied",
        "checking": "Checking Ollama…", "online": "Ollama online", "no_model": "No models installed",
        "download_start": "Install a model with Ollama to get started.", "unreachable": "Ollama unreachable",
        "cannot_reach": "Can't reach {url}. Start Ollama or check the address in Settings.",
        "offline": "Ollama is not connected. Start it and press ↻ to retry.",
        "model_missing": "No model found. Install a model in Ollama and press ↻.",
        "response_from": "Response from {model}…", "request_rejected": "Request rejected by Ollama ({code})",
        "connection_interrupted": "Connection to Ollama interrupted: {error}", "request_failed": "Request failed",
        "settings_title": "Settings", "language": "Language", "ollama_address": "Ollama server address",
        "usually": "Usually: http://localhost:11434", "context_description_1": "Context length determines how much of your conversation local models can remember",
        "context_description_2": "and use to generate responses.", "save": "Save",
    },
    "it": {
        "new_chat": "Nuova chat", "settings": "Impostazioni", "chat_history": "LE TUE CHAT",
        "empty_history": "Le tue conversazioni\nappariranno qui", "placeholder": "Scrivi un messaggio…",
        "welcome_title": "Da dove cominciamo?", "welcome_subtitle": "Una chat privata con i modelli sul tuo computer.",
        "user": "Tu", "reasoning": "ragionamento", "thinking_on": "Ragionamento  ON", "thinking_off": "Ragionamento  OFF",
        "no_models_refresh": "Nessun modello disponibile. Verifica Ollama e premi ↻.", "rename": "Rinomina", "delete": "Elimina",
        "rename_title": "Rinomina chat", "new_name": "Nuovo nome della chat:", "invalid_name": "Nome non valido",
        "enter_name": "Inserisci un nome per la chat.", "delete_title": "Elimina chat",
        "delete_confirm": "Vuoi eliminare “{title}” e tutti i suoi messaggi?", "copy": "Copia", "copied": "Copiato",
        "checking": "Verifico Ollama…", "online": "Ollama online", "no_model": "Nessun modello installato",
        "download_start": "Scarica un modello con Ollama per iniziare.", "unreachable": "Ollama non raggiungibile",
        "cannot_reach": "Non riesco a raggiungere {url}. Avvia Ollama o controlla l’indirizzo nelle impostazioni.",
        "offline": "Ollama non è connesso. Avvialo e premi ↻ per riprovare.",
        "model_missing": "Nessun modello trovato. Scarica un modello in Ollama e premi ↻.",
        "response_from": "Risposta da {model}…", "request_rejected": "Richiesta rifiutata da Ollama ({code})",
        "connection_interrupted": "Connessione a Ollama interrotta: {error}", "request_failed": "Richiesta non riuscita",
        "settings_title": "Impostazioni", "language": "Lingua", "ollama_address": "Indirizzo del server Ollama",
        "usually": "Di solito: http://localhost:11434", "context_description_1": "La lunghezza del contesto determina quanta parte della conversazione i modelli locali possono ricordare",
        "context_description_2": "e usare per generare le risposte.", "save": "Salva",
    },
    "es": {
        "new_chat": "Nuevo chat", "settings": "Configuración", "chat_history": "TUS CHATS",
        "empty_history": "Tus conversaciones\naparecerán aquí", "placeholder": "Escribe un mensaje…",
        "welcome_title": "¿Por dónde empezamos?", "welcome_subtitle": "Un chat privado con los modelos de tu ordenador.",
        "user": "Tú", "reasoning": "razonamiento", "thinking_on": "Razonamiento  ON", "thinking_off": "Razonamiento  OFF",
        "no_models_refresh": "No hay modelos disponibles. Comprueba Ollama y pulsa ↻.", "rename": "Cambiar nombre", "delete": "Eliminar",
        "rename_title": "Cambiar nombre del chat", "new_name": "Nuevo nombre del chat:", "invalid_name": "Nombre no válido",
        "enter_name": "Escribe un nombre para el chat.", "delete_title": "Eliminar chat",
        "delete_confirm": "¿Quieres eliminar “{title}” y todos sus mensajes?", "copy": "Copiar", "copied": "Copiado",
        "checking": "Comprobando Ollama…", "online": "Ollama conectado", "no_model": "No hay modelos instalados",
        "download_start": "Instala un modelo con Ollama para empezar.", "unreachable": "Ollama no está disponible",
        "cannot_reach": "No se puede acceder a {url}. Inicia Ollama o revisa la dirección en Configuración.",
        "offline": "Ollama no está conectado. Inícialo y pulsa ↻ para volver a intentarlo.",
        "model_missing": "No se encontró ningún modelo. Instala uno en Ollama y pulsa ↻.",
        "response_from": "Respuesta de {model}…", "request_rejected": "Ollama rechazó la solicitud ({code})",
        "connection_interrupted": "Se interrumpió la conexión con Ollama: {error}", "request_failed": "La solicitud no se completó",
        "settings_title": "Configuración", "language": "Idioma", "ollama_address": "Dirección del servidor Ollama",
        "usually": "Normalmente: http://localhost:11434", "context_description_1": "La longitud del contexto determina cuánto de la conversación pueden recordar los modelos locales",
        "context_description_2": "y usar para generar respuestas.", "save": "Guardar",
    },
    "fr": {
        "new_chat": "Nouvelle discussion", "settings": "Paramètres", "chat_history": "VOS DISCUSSIONS",
        "empty_history": "Vos conversations\napparaîtront ici", "placeholder": "Écrivez un message…",
        "welcome_title": "Par quoi commencer ?", "welcome_subtitle": "Une discussion privée avec les modèles de votre ordinateur.",
        "user": "Vous", "reasoning": "raisonnement", "thinking_on": "Réflexion  OUI", "thinking_off": "Réflexion  NON",
        "no_models_refresh": "Aucun modèle disponible. Vérifiez Ollama et appuyez sur ↻.", "rename": "Renommer", "delete": "Supprimer",
        "rename_title": "Renommer la discussion", "new_name": "Nouveau nom de la discussion :", "invalid_name": "Nom invalide",
        "enter_name": "Saisissez un nom pour la discussion.", "delete_title": "Supprimer la discussion",
        "delete_confirm": "Supprimer « {title} » et tous ses messages ?", "copy": "Copier", "copied": "Copié",
        "checking": "Vérification d’Ollama…", "online": "Ollama connecté", "no_model": "Aucun modèle installé",
        "download_start": "Installez un modèle avec Ollama pour commencer.", "unreachable": "Ollama inaccessible",
        "cannot_reach": "Impossible d’accéder à {url}. Démarrez Ollama ou vérifiez l’adresse dans les paramètres.",
        "offline": "Ollama n’est pas connecté. Démarrez-le et appuyez sur ↻ pour réessayer.",
        "model_missing": "Aucun modèle trouvé. Installez-en un dans Ollama et appuyez sur ↻.",
        "response_from": "Réponse de {model}…", "request_rejected": "Requête refusée par Ollama ({code})",
        "connection_interrupted": "Connexion à Ollama interrompue : {error}", "request_failed": "La requête a échoué",
        "settings_title": "Paramètres", "language": "Langue", "ollama_address": "Adresse du serveur Ollama",
        "usually": "En général : http://localhost:11434", "context_description_1": "La longueur du contexte détermine la quantité de conversation que les modèles locaux peuvent mémoriser",
        "context_description_2": "et utiliser pour générer des réponses.", "save": "Enregistrer",
    },
}


def data_dir() -> Path:
    root = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    folder = root / "ChatAI"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


class ChatAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        icon_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        try:
            self.iconbitmap(str(icon_root / "icon.ico"))
        except tk.TclError:
            pass
        self.geometry("1180x780")
        self.minsize(850, 620)
        self.configure(bg=BG)
        self.store_path = data_dir() / "chats.json"
        self.settings_path = data_dir() / "settings.json"
        self.settings = self._load_json(self.settings_path, {"url": DEFAULT_URL, "model": "", "thinking": False, "context_length": 8192, "language": "en"})
        configured_language = self.settings.get("language", "en")
        self.language = configured_language if isinstance(configured_language, str) and configured_language in TRANSLATIONS else "en"
        self.settings["language"] = self.language
        self.chats = self._load_json(self.store_path, [])
        self._update_legacy_chat_titles()
        self.active_id = None
        self.draft_chat = None
        self.busy = False
        self.connection_available = False
        self.checking_connection = False
        self.check_generation = 0
        self.events: queue.Queue = queue.Queue()
        self.message_widgets: dict[str, tk.Text] = {}
        self.pending_responses: dict[str, dict] = {}
        self.pending_chat_ids: dict[str, str] = {}
        self.active_request_id = None
        self.active_cancel_event = None
        self.active_responses = {}
        self.cancelled_requests = set()
        self.saved_model = self.settings.get("model", "")
        try:
            configured_context = int(self.settings.get("context_length", 8192))
        except (TypeError, ValueError):
            configured_context = 8192
        self.context_length = min(CONTEXT_LENGTHS, key=lambda value: abs(value - configured_context))
        self.model_var = tk.StringVar(value=self.saved_model)
        self.thinking_var = tk.BooleanVar(value=bool(self.settings.get("thinking", False)))
        self.status_var = tk.StringVar(value="")
        self.connection_text = tk.StringVar(value=self._t("checking"))
        self._style()
        self._build()
        self._refresh_chat_list()
        if self.chats:
            latest = max(self.chats, key=lambda chat: chat.get("updated", ""))
            self.open_chat(latest["id"])
        else:
            self.new_chat()
        self.after(160, self._poll_events)
        self.after(120, self.refresh_models)
        self.after(15000, self._periodic_connection_check)

    @staticmethod
    def _load_json(path: Path, fallback):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return fallback

    @staticmethod
    def _title_from_prompt(prompt, word_limit=5, char_limit=34):
        normalized = " ".join(prompt.split())
        words = normalized.split()
        title = " ".join(words[:word_limit])
        shortened = len(words) > word_limit
        if len(title) > char_limit:
            title = title[:char_limit - 1].rsplit(" ", 1)[0] or title[:char_limit - 1]
            shortened = True
        if shortened:
            title = title.rstrip(" .,!?;:") + "…"
        return title

    def _update_legacy_chat_titles(self):
        changed = False
        for chat in self.chats:
            first_user = next((message.get("content", "") for message in chat.get("messages", []) if message.get("role") == "user"), "")
            if not first_user:
                continue
            old_title = first_user.replace("\n", " ")
            legacy_title = old_title[:42] + ("…" if len(old_title) > 42 else "")
            if chat.get("title") in (legacy_title, first_user, " ".join(first_user.split())):
                chat["title"] = self._title_from_prompt(first_user)
                changed = True
        if changed:
            try:
                self.store_path.write_text(json.dumps(self.chats, ensure_ascii=False, indent=2), encoding="utf-8")
            except OSError:
                # Keep the normalized titles in memory if the app data folder is temporarily unavailable.
                pass

    def _save(self):
        self.store_path.write_text(json.dumps(self.chats, ensure_ascii=False, indent=2), encoding="utf-8")
        self.settings["model"] = self.saved_model
        self.settings["thinking"] = self.thinking_var.get()
        self.settings["context_length"] = self.context_length
        self.settings["language"] = self.language
        self.settings_path.write_text(json.dumps(self.settings, ensure_ascii=False, indent=2), encoding="utf-8")

    def _t(self, key, **values):
        template = TRANSLATIONS.get(self.language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
        return template.format(**values)

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=FONT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 15))
        style.configure("TButton", background=PANEL, foreground=TEXT, borderwidth=0, padding=(12, 8), font=FONT)
        style.map("TButton", background=[("active", PANEL_HOVER), ("disabled", BG)], foreground=[("disabled", MUTED)])
        style.configure("Accent.TButton", background=ACCENT, foreground=ACCENT_TEXT, padding=(15, 10), font=("Segoe UI Semibold", 10))
        style.map("Accent.TButton", background=[("active", "#ffffff"), ("disabled", "#555555")])
        style.configure("Chat.TCombobox", fieldbackground="#292929", background="#292929", foreground=TEXT, arrowcolor="#b6b6b6", borderwidth=0, padding=8, relief="flat", bordercolor=LINE, lightcolor="#292929", darkcolor="#292929", arrowsize=10)
        style.map("Chat.TCombobox", fieldbackground=[("readonly", "#292929"), ("disabled", "#222222")], foreground=[("readonly", TEXT), ("disabled", "#858585")], selectbackground=[("readonly", "#292929")], selectforeground=[("readonly", TEXT)])
        style.configure("Vertical.TScrollbar", background=PANEL, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)

    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=258, highlightthickness=1, highlightbackground="#242424")
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar_visible = True
        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(22, 30))
        self.sidebar_toggle = self._make_sidebar_toggle(brand, SIDEBAR)
        self.sidebar_toggle.pack(side="left", padx=(0, 12))
        mark = tk.Canvas(brand, width=31, height=31, bg=SIDEBAR, highlightthickness=0)
        mark.pack(side="left")
        mark.create_oval(2, 2, 29, 29, fill=ACCENT, outline="")
        mark.create_oval(9, 9, 22, 22, fill=SIDEBAR, outline="")
        tk.Label(brand, text="ChatAI", bg=SIDEBAR, fg=TEXT, font=("Segoe UI Semibold", 15)).pack(side="left", padx=10)
        self._side_button("＋   " + self._t("new_chat"), self.new_chat, selected=True).pack(fill="x", padx=12, pady=(0, 4))
        self._side_button("⚙   " + self._t("settings"), self.open_settings).pack(fill="x", padx=12, pady=4)
        tk.Frame(self.sidebar, bg=LINE, height=1).pack(fill="x", padx=18, pady=(20, 18))
        tk.Label(self.sidebar, text=self._t("chat_history"), bg=SIDEBAR, fg="#858585", font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=20, pady=(0, 10))
        self.chat_list = tk.Frame(self.sidebar, bg=SIDEBAR)
        self.chat_list.pack(fill="both", expand=True, padx=8)
        footer = tk.Frame(self.sidebar, bg=SIDEBAR)
        footer.pack(fill="x", padx=18, pady=17)
        tk.Frame(footer, bg=LINE, height=1).pack(fill="x", pady=(0, 14))
        footer_row = tk.Frame(footer, bg=SIDEBAR)
        footer_row.pack(fill="x")
        self.sidebar_status_dot = tk.Label(footer_row, text="●", bg=SIDEBAR, fg="#929292", font=("Segoe UI", 9))
        self.sidebar_status_dot.pack(side="left")
        self.sidebar_status_label = tk.Label(footer_row, textvariable=self.connection_text, bg=SIDEBAR, fg=MUTED, font=("Segoe UI", 9))
        self.sidebar_status_label.pack(side="left", padx=(7, 0))
        self.refresh_button = tk.Button(footer_row, text="↻", command=self.refresh_models, bg=SIDEBAR, fg=MUTED, activebackground="#262626", activeforeground=TEXT, relief="flat", bd=0, font=("Segoe UI", 14), cursor="hand2", padx=8, pady=0)
        self.refresh_button.pack(side="right")

        self.main = tk.Frame(self, bg=BG)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(1, weight=1)

        top = tk.Frame(self.main, bg=BG, height=68)
        top.grid(row=0, column=0, sticky="ew", padx=34)
        top.grid_propagate(False)
        self.main_sidebar_toggle = self._make_sidebar_toggle(top, BG)
        self.main_sidebar_toggle.pack(side="left", pady=16, padx=(0, 14))
        self.main_sidebar_toggle.pack_forget()
        self.chat_title = tk.Label(top, text=self._t("new_chat"), bg=BG, fg=TEXT, font=("Segoe UI Semibold", 12))
        self.chat_title.pack(side="left", pady=22)
        self.conversation_area = tk.Frame(self.main, bg=BG)
        self.conversation_area.grid(row=1, column=0, sticky="nsew")
        self.conversation_area.columnconfigure(0, weight=1)
        self.conversation_area.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.conversation_area, bg=BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.conversation_area, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG)
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_conversation)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._wheel)

        self.welcome = tk.Frame(self.scroll_frame, bg=BG)
        self.welcome.pack(expand=True, fill="both", pady=105)
        self._welcome_content(self.welcome)

        composer_wrap = tk.Frame(self.main, bg=BG)
        composer_wrap.grid(row=2, column=0, sticky="ew", padx=34, pady=(8, 20))
        composer_wrap.columnconfigure(0, weight=1)
        self.composer_canvas = tk.Canvas(composer_wrap, bg=BG, width=820, height=106, highlightthickness=0, borderwidth=0)
        self.composer_canvas.grid(row=0, column=0)
        composer_wrap.bind("<Configure>", self._fit_composer_width)
        self.composer = tk.Frame(self.composer_canvas, bg="#242424", bd=0, highlightthickness=0)
        self.composer_window = self.composer_canvas.create_window(10, 10, window=self.composer, anchor="nw")
        self.composer_canvas.bind("<Configure>", self._resize_composer)
        self.composer.columnconfigure(0, weight=1)
        self.input = tk.Text(self.composer, height=2, wrap="word", bg="#242424", fg=TEXT, insertbackground=ACCENT, relief="flat", borderwidth=0, font=("Segoe UI", 11), padx=16, pady=4, undo=True)
        self.input.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.input_placeholder = tk.Label(self.composer, text=self._t("placeholder"), bg="#242424", fg="#858585", font=("Segoe UI", 11), cursor="xterm")
        self.input_placeholder.place(x=16, y=14)
        self.input_placeholder.bind("<Button-1>", self._focus_input)
        self.input.bind("<FocusIn>", self._input_focus)
        self.input.bind("<FocusOut>", self._input_blur)
        self.input.bind("<KeyPress>", self._placeholder_key, add="+")
        self.input.bind("<KeyRelease>", lambda _event: self._draw_send_button(), add="+")
        self.input.bind("<Return>", self._enter_send)
        self.input.bind("<Shift-Return>", lambda _e: None)

        self.thinking_btn = tk.Canvas(self.composer, width=146, height=36, bg="#242424", highlightthickness=0, cursor="hand2")
        self.thinking_btn.grid(row=1, column=1, padx=(4, 6), pady=(0, 4))
        self.thinking_btn.bind("<Button-1>", lambda _e: self.toggle_thinking())
        self.available_models = []
        self.model_button = tk.Canvas(self.composer, width=188, height=36, bg="#242424", highlightthickness=0, cursor="hand2")
        self.model_button.grid(row=1, column=2, padx=5, pady=(0, 4))
        self.model_button.bind("<Button-1>", self._show_model_menu)
        self.model_menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg=TEXT, activebackground="#404040", activeforeground=TEXT, relief="flat", bd=0, font=FONT)
        self.send_btn = tk.Canvas(self.composer, width=38, height=38, bg="#242424", highlightthickness=0, cursor="hand2")
        self.send_btn.grid(row=1, column=3, padx=(5, 10), pady=(0, 4))
        self.send_btn.bind("<Button-1>", lambda _e: self._handle_send_click())
        self.send_btn.bind("<Enter>", lambda _e: self._draw_send_button(hover=True))
        self.send_btn.bind("<Leave>", lambda _e: self._draw_send_button())
        self.status_label = tk.Label(composer_wrap, textvariable=self.status_var, bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.status_label.grid(row=1, column=0, sticky="w", padx=6, pady=(5, 0))
        self._update_thinking_button()
        self._draw_model_button()
        self._draw_send_button()

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar.grid()
            self.main_sidebar_toggle.pack_forget()
        else:
            self.sidebar.grid_remove()
            self.main_sidebar_toggle.pack(side="left", before=self.chat_title, pady=16, padx=(0, 14))

    def _make_sidebar_toggle(self, parent, background):
        icon = tk.Canvas(parent, width=30, height=30, bg=background, highlightthickness=0, cursor="hand2")
        icon.create_rectangle(5, 6, 24, 23, outline="#bdbdbd", width=1.4)
        icon.create_line(12, 7, 12, 22, fill="#bdbdbd", width=1.2)
        icon.bind("<Button-1>", lambda _event: self.toggle_sidebar())
        icon.bind("<Enter>", lambda _event: icon.configure(bg="#292929"))
        icon.bind("<Leave>", lambda _event: icon.configure(bg=background))
        return icon

    def _side_button(self, text, command, selected=False):
        return tk.Button(self.sidebar, text=text, command=command, anchor="w", bg="#262626" if selected else SIDEBAR, fg=TEXT if selected else "#b3b9af", activebackground="#303030", activeforeground=TEXT, relief="flat", bd=0, padx=13, pady=11, font=("Segoe UI Semibold" if selected else "Segoe UI", 10), cursor="hand2")

    def _welcome_content(self, parent):
        tk.Label(parent, text="✳", bg=BG, fg=ACCENT, font=("Segoe UI Symbol", 39)).pack(pady=(13, 12))
        tk.Label(parent, text=self._t("welcome_title"), bg=BG, fg=TEXT, font=("Segoe UI Semibold", 23)).pack()
        tk.Label(parent, text=self._t("welcome_subtitle"), bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(pady=(9, 0))

    @staticmethod
    def _rounded_points(x1, y1, x2, y2, radius=18):
        return [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
                x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
                x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]

    def _resize_composer(self, event):
        self.composer_canvas.delete("panel")
        self.composer_canvas.create_polygon(*self._rounded_points(1, 3, event.width - 1, event.height - 3, 38), smooth=True, splinesteps=32, fill="#242424", outline="#303030", width=1, tags="panel")
        self.composer_canvas.tag_lower("panel")
        inset = 10
        self.composer_canvas.coords(self.composer_window, inset, inset)
        self.composer_canvas.itemconfigure(self.composer_window, width=max(100, event.width - inset * 2), height=max(80, event.height - inset * 2))

    def _fit_composer_width(self, event):
        width = min(max(320, event.width), 820)
        self.composer_canvas.configure(width=width)

    def _resize_conversation(self, event):
        self.canvas.itemconfigure(self.scroll_window, width=event.width)
        side_pad = self._content_side_padding(event.width)
        for child in self.scroll_frame.winfo_children():
            if getattr(child, "is_message_row", False):
                child.pack_configure(padx=side_pad)
        self.after_idle(self._update_scroll_region)

    @staticmethod
    def _content_side_padding(viewport_width):
        # Keep chat text comfortably centered on wide screens while using
        # nearly all available width on smaller windows.
        content_width = min(max(0, viewport_width - 48), 820)
        return max(24, (viewport_width - content_width) // 2)

    def _update_scroll_region(self, _event=None):
        bounds = self.canvas.bbox("all")
        if not bounds:
            return
        self.canvas.configure(scrollregion=bounds)
        content_height = bounds[3] - bounds[1]
        if content_height > self.canvas.winfo_height() + 4:
            self.scrollbar.grid()
        else:
            self.scrollbar.grid_remove()

    def _model_selected(self, _event=None):
        self.saved_model = self.model_var.get()
        self._save()
        self._draw_model_button()

    def _show_model_menu(self, _event=None):
        if not self.available_models:
            self.status_var.set(self._t("no_models_refresh"))
            self.refresh_models()
            return "break"
        self.model_menu.delete(0, "end")
        for model in self.available_models:
            self.model_menu.add_command(label=model, command=lambda value=model: self._choose_model(value))
        self.model_menu.tk_popup(self.model_button.winfo_rootx(), self.model_button.winfo_rooty() + self.model_button.winfo_height())
        return "break"

    def _choose_model(self, model):
        self.model_var.set(model)
        self._model_selected()

    def _draw_model_button(self):
        self.model_button.delete("all")
        width, height = 188, 36
        fill = "#303030" if self.available_models else "#282828"
        self.model_button.create_polygon(*self._rounded_points(1, 1, width - 1, height - 1, 34), smooth=True, splinesteps=24, fill=fill, outline="#3a3a3a", width=1)
        label = self.model_var.get() or "Scegli un modello"
        if len(label) > 21:
            label = label[:19] + "…"
        self.model_button.create_text(14, height // 2, text=label, anchor="w", fill="#d0d0d0" if self.available_models else "#858585", font=("Segoe UI", 9))

    @staticmethod
    def _display_message_content(message):
        content = message.get("content", "")
        names = [item.get("name", "Allegato") for item in message.get("files", [])]
        if names:
            label = "\n".join(f"📎 {name}" for name in names)
            content = f"{content}\n\n{label}" if content else label
        return content

    @staticmethod
    def _message_for_api(message):
        content = message.get("content", "")
        images = []
        for item in message.get("files", []):
            if item.get("kind") == "text":
                content += f"\n\n--- File allegato: {item.get('name', 'file')} ---\n{item.get('content', '')}"
            elif item.get("kind") == "image" and item.get("data"):
                images.append(item["data"])
        if not content and images:
            content = "Prendi in considerazione le immagini allegate."
        result = {"role": message.get("role", "user"), "content": content}
        if images:
            result["images"] = images
        return result

    def _draw_send_button(self, hover=False):
        self.send_btn.delete("all")
        has_text = bool(self.input.get("1.0", "end-1c").strip()) if hasattr(self, "input") else False
        emphasized = has_text and not self.busy
        fill = "#ffffff" if emphasized else ("#555555" if hover and not self.busy else "#484848")
        ink = "#191919" if emphasized or not self.busy else "#eeeeee"
        self.send_btn.create_oval(1, 1, 37, 37, fill=fill, outline="#5a5a5a" if not emphasized else "#ffffff", width=1)
        if self.busy:
            self.send_btn.create_rectangle(14, 14, 24, 24, fill=ink, outline="")
        else:
            self.send_btn.create_text(19, 17, text="↑", fill=ink, font=("Segoe UI Symbol", 16))

    def _handle_send_click(self):
        if self.busy:
            self.stop_generation()
        else:
            self.send_message()

    def stop_generation(self):
        request_id = self.active_request_id
        if not self.busy or not request_id:
            return
        if self.active_cancel_event:
            self.active_cancel_event.set()
        self.cancelled_requests.add(request_id)
        response_stream = self.active_responses.get(request_id)
        if response_stream:
            try:
                response_stream.close()
            except Exception:
                pass

        partial = self.pending_responses.pop(request_id, None)
        chat_id = self.pending_chat_ids.pop(request_id, None)
        if partial and not (partial.get("content") or partial.get("thinking")) and chat_id:
            chat = next((item for item in self.chats if item.get("id") == chat_id), None)
            if chat and partial in chat.get("messages", []):
                chat["messages"].remove(partial)

        self.active_request_id = None
        self.active_cancel_event = None
        self.active_responses.pop(request_id, None)
        self.busy = False
        self.status_var.set("")
        self._draw_send_button()
        self._render_messages()
        self._save()

    def _wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _input_focus(self, _event):
        self.input_placeholder.place_forget()

    def _placeholder_key(self, event):
        if not self.input.get("1.0", "end-1c").strip() and (event.keysym in ("BackSpace", "Delete") or (event.char and event.char.isprintable())):
            self.input_placeholder.place_forget()

    def _input_blur(self, _event):
        if not self.input.get("1.0", "end-1c").strip():
            self.input_placeholder.place(x=16, y=14)

    def _focus_input(self, _event=None):
        self.input.focus_set()
        self.input.mark_set("insert", "1.0")
        return "break"

    def _enter_send(self, event):
        if not (event.state & 0x0001):
            self.send_message()
            return "break"

    def toggle_thinking(self):
        self.thinking_var.set(not self.thinking_var.get())
        self._update_thinking_button()
        self._save()

    def _update_thinking_button(self):
        enabled = self.thinking_var.get()
        self.thinking_btn.delete("all")
        fill = "#414141" if enabled else "#303030"
        self.thinking_btn.create_polygon(*self._rounded_points(1, 1, 145, 35, 34), smooth=True, splinesteps=24, fill=fill, outline="#3c3c3c", width=1)
        self.thinking_btn.create_text(73, 18, text=self._t("thinking_on" if enabled else "thinking_off"), fill="#f1f1f1" if enabled else "#c4c4c4", font=("Segoe UI Semibold", 9))

    def _refresh_chat_list(self):
        for widget in self.chat_list.winfo_children():
            widget.destroy()
        ordered = sorted(self.chats, key=lambda item: item.get("updated", ""), reverse=True)
        if not ordered:
            tk.Label(self.chat_list, text=self._t("empty_history"), justify="left", bg=SIDEBAR, fg="#858585", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=8)
        for chat in ordered:
            item = tk.Frame(self.chat_list, bg=SIDEBAR)
            item.pack(fill="x", pady=2)
            active = chat["id"] == self.active_id
            title = chat.get("title", self._t("new_chat"))
            title = title if len(title) <= 27 else title[:26] + "…"
            b = tk.Button(item, text=title, command=lambda c=chat: self.open_chat(c["id"]), anchor="w", bg="#262626" if active else SIDEBAR, fg=TEXT if active else "#b3b9af", activebackground="#303030", activeforeground=TEXT, relief="flat", bd=0, padx=12, pady=9, font=FONT, cursor="hand2")
            b.pack(fill="x")
            b.bind("<Button-3>", lambda event, chat_id=chat["id"]: self._show_chat_menu(event, chat_id))
            item.bind("<Button-3>", lambda event, chat_id=chat["id"]: self._show_chat_menu(event, chat_id))

    def _show_chat_menu(self, event, chat_id):
        if self.active_id != chat_id:
            self.open_chat(chat_id)
        menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg=TEXT, activebackground="#404040", activeforeground=TEXT, relief="flat", bd=0, font=FONT)
        menu.add_command(label=self._t("rename"), command=lambda: self._rename_chat(chat_id))
        menu.add_command(label=self._t("delete"), command=lambda: self._delete_chat(chat_id))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
        return "break"

    def _rename_chat(self, chat_id):
        chat = next((item for item in self.chats if item["id"] == chat_id), None)
        if not chat:
            return
        title = simpledialog.askstring(self._t("rename_title"), self._t("new_name"), initialvalue=chat.get("title", self._t("new_chat")), parent=self)
        if title is None:
            return
        title = title.strip()
        if not title:
            messagebox.showinfo(self._t("invalid_name"), self._t("enter_name"), parent=self)
            return
        chat["title"] = title
        self._save()
        self._refresh_chat_list()
        if self.active_id == chat_id:
            self.chat_title.configure(text=title)

    def _delete_chat(self, chat_id):
        chat = next((item for item in self.chats if item["id"] == chat_id), None)
        if not chat:
            return
        title = chat.get("title", self._t("new_chat"))
        if not messagebox.askyesno(self._t("delete_title"), self._t("delete_confirm", title=title), parent=self):
            return
        self.chats.remove(chat)
        was_active = self.active_id == chat_id
        self._save()
        if was_active:
            self.active_id = None
            self.draft_chat = None
            if self.chats:
                latest = max(self.chats, key=lambda item: item.get("updated", ""))
                self.open_chat(latest["id"])
            else:
                self.new_chat()
        else:
            self._refresh_chat_list()

    def new_chat(self):
        if self.draft_chat is not None:
            self.draft_chat = None
        self.active_id = str(uuid.uuid4())
        self.draft_chat = {"id": self.active_id, "title": self._t("new_chat"), "messages": [], "updated": datetime.now().isoformat(timespec="seconds")}
        self._refresh_chat_list()
        self._render_messages()
        self.chat_title.configure(text=self._t("new_chat"))
        self.status_var.set("")

    def open_chat(self, chat_id):
        self.draft_chat = None
        self.active_id = chat_id
        chat = self._active_chat()
        self.chat_title.configure(text=chat.get("title", self._t("new_chat")))
        self._refresh_chat_list()
        self._render_messages()

    def _active_chat(self):
        if self.draft_chat and self.draft_chat["id"] == self.active_id:
            return self.draft_chat
        return next((chat for chat in self.chats if chat["id"] == self.active_id), None)

    def _render_messages(self):
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.message_widgets.clear()
        chat = self._active_chat()
        if not chat or not chat["messages"]:
            self.welcome = tk.Frame(self.scroll_frame, bg=BG)
            self.welcome.pack(expand=True, fill="both", pady=105)
            self._welcome_content(self.welcome)
            return
        for idx, msg in enumerate(chat["messages"]):
            pending_id = next((request_id for request_id, pending in self.pending_responses.items() if pending is msg), None)
            if pending_id:
                if msg.get("thinking"):
                    self._add_message_widget("thinking", msg["thinking"], f"{pending_id}-thinking")
                self._add_message_widget("assistant", msg.get("content", ""), f"{pending_id}-content")
            else:
                if msg.get("thinking"):
                    self._add_message_widget("thinking", msg["thinking"], f"history-think-{idx}")
                role = msg.get("role", "assistant")
                content = self._display_message_content(msg) if role == "user" else msg.get("content", "")
                self._add_message_widget(role, content, f"history-{idx}")
        self.after(60, lambda: self.canvas.yview_moveto(1.0))

    def _add_message_widget(self, role, content, key):
        outer = tk.Frame(self.scroll_frame, bg=BG)
        viewport = max(0, self.canvas.winfo_width())
        side_pad = self._content_side_padding(viewport) if viewport else 24
        outer.is_message_row = True
        outer.pack(fill="x", padx=side_pad, pady=(20, 3))
        inner = tk.Frame(outer, bg=BG)
        if role == "user":
            inner.pack(anchor="e", padx=(55, 0))
        else:
            inner.pack(fill="x")
        name = self._t("user") if role == "user" else ("AI · " + self._t("reasoning") if role == "thinking" else "AI")
        name_color = "#a8a8a8" if role == "user" else ("#b9b9b9" if role == "thinking" else "#dddddd")
        tk.Label(inner, text=name, bg=BG, fg=name_color, font=("Segoe UI Semibold", 9)).pack(anchor="e" if role == "user" else "w", pady=(0, 6))
        body_bg = "#292929" if role == "user" else ("#202020" if role == "thinking" else BG)
        if role == "user":
            bubble = tk.Canvas(inner, bg=BG, highlightthickness=0, borderwidth=0)
            bubble.pack(anchor="e")
            body = tk.Text(bubble, wrap="word", bg=body_bg, fg=TEXT, relief="flat", borderwidth=0, font=("Segoe UI", 11), padx=2, pady=1, width=70, height=1, state="normal", cursor="xterm", undo=False)
            self._render_markdown(body, content)
            self._fit_text(body, content)
            body.update_idletasks()
            width = body.winfo_reqwidth() + 28
            height = body.winfo_reqheight() + 18
            bubble.configure(width=width, height=height)
            bubble.create_polygon(*self._rounded_points(3, 3, width - 1, height - 1, 14), smooth=True, splinesteps=14, fill="#121212", outline="", tags="shadow")
            bubble.create_polygon(*self._rounded_points(1, 1, width - 3, height - 5, 14), smooth=True, splinesteps=14, fill=body_bg, outline="#333333", width=1, tags="bubble")
            bubble.create_window(14, 9, window=body, anchor="nw", width=width - 30, height=height - 20)
        else:
            body = tk.Text(inner, wrap="word", bg=body_bg, fg=TEXT, relief="flat", borderwidth=0, font=("Segoe UI", 11), padx=0, pady=0, width=92, height=1, state="normal", cursor="xterm", undo=False)
            body.pack(anchor="w", fill="x")
            self._render_markdown(body, content)
            self._fit_text(body, content)
        self._make_text_selectable_readonly(body)
        self.message_widgets[key] = body
        return body

    def _make_text_selectable_readonly(self, widget):
        # Keep Text widgets read-only while allowing mouse selection and copy.
        widget.configure(state="normal", cursor="xterm", insertwidth=0)
        widget.bind("<KeyPress>", lambda _event: "break")
        widget.bind("<Control-c>", lambda _event: self._copy_selection(widget))
        widget.bind("<Control-a>", lambda _event: self._select_all_text(widget))
        widget.bind("<<Paste>>", lambda _event: "break")
        widget.bind("<<Cut>>", lambda _event: "break")

    def _copy_selection(self, widget):
        try:
            selected_text = widget.get("sel.first", "sel.last")
        except tk.TclError:
            return "break"
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        return "break"

    @staticmethod
    def _select_all_text(widget):
        widget.tag_add("sel", "1.0", "end-1c")
        widget.mark_set("insert", "1.0")
        widget.see("insert")
        return "break"

    def _render_markdown(self, widget, content):
        widget.delete("1.0", "end")
        widget.tag_configure("bold", font=("Segoe UI Semibold", 11))
        widget.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        widget.tag_configure("bold_italic", font=("Segoe UI Semibold", 11, "italic"))
        widget.tag_configure("inline_code", font=("Cascadia Mono", 10), foreground="#e2e2e2", background="#3a3a3a")
        widget.tag_configure("code_block", font=("Cascadia Mono", 10), foreground="#e0e0e0", background="#252525", lmargin1=12, lmargin2=12, spacing1=4, spacing3=4)
        widget.tag_configure("sel", foreground="#ffffff", background="#365a7a")
        for level, size in enumerate((18, 16, 14, 12, 11, 11), start=1):
            widget.tag_configure(f"heading_{level}", font=("Segoe UI Semibold", size), foreground="#f4f4f4", spacing1=8 if level < 3 else 5, spacing3=3)
        for depth in range(8):
            left = 14 + depth * 20
            widget.tag_configure(f"list_{depth}", lmargin1=left, lmargin2=left + 17)
        widget.tag_configure("quote", foreground="#c2c2c2", lmargin1=16, lmargin2=32, spacing1=2, spacing3=2)
        widget.tag_configure("bullet", foreground="#c8c8c8")
        widget.tag_configure("link", foreground="#d0d0d0", underline=True)
        widget.tag_configure("strike", overstrike=True)
        widget.tag_configure("table", font=("Cascadia Mono", 9), foreground="#dedede", lmargin1=8, lmargin2=8, spacing1=2, spacing3=2)
        widget.tag_configure("table_header", font=("Cascadia Mono", 9, "bold"), foreground="#ffffff")
        widget.tag_raise("sel")

        lines = content.splitlines()
        index = 0
        previous_block = False
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue
            if previous_block:
                widget.insert("end", "\n\n")

            fence = re.match(r"^\s*(`{3,}|~{3,})", line)
            if fence:
                marker = fence.group(1)
                code_lines = []
                index += 1
                while index < len(lines) and not re.match(r"^\s*" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*$", lines[index]):
                    code_lines.append(lines[index])
                    index += 1
                if index < len(lines):
                    index += 1
                self._insert_code_block(widget, "\n".join(code_lines))
                previous_block = True
                continue

            heading = re.match(r"^\s{0,3}(#{1,6})(?:\s+|$)(.*?)\s*#*\s*$", line)
            if heading:
                self._insert_inline(widget, heading.group(2), (f"heading_{len(heading.group(1))}",))
                index += 1
                previous_block = True
                continue

            if self._is_horizontal_rule(line):
                widget.insert("end", "────────────────────────────────────────", ("bullet",))
                index += 1
                previous_block = True
                continue

            if re.match(r"^\s{0,3}>\s?", line):
                quote_lines = []
                while index < len(lines) and re.match(r"^\s{0,3}>\s?", lines[index]):
                    quote_lines.append(re.sub(r"^\s{0,3}>\s?", "", lines[index]))
                    index += 1
                for quote_index, quote_line in enumerate(quote_lines):
                    if quote_index:
                        widget.insert("end", "\n")
                    widget.insert("end", "▎  ", ("quote",))
                    self._insert_inline(widget, quote_line, ("quote",))
                previous_block = True
                continue

            if index + 1 < len(lines) and "|" in line and self._is_table_separator(lines[index + 1]):
                table_lines = [line]
                index += 2
                while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                    table_lines.append(lines[index])
                    index += 1
                self._insert_markdown_table(widget, table_lines)
                previous_block = True
                continue

            list_match = self._match_list_item(line)
            if list_match:
                list_items = []
                while index < len(lines):
                    item = self._match_list_item(lines[index])
                    if not item:
                        break
                    list_items.append(item)
                    index += 1
                for item_index, (depth, marker, body) in enumerate(list_items):
                    if item_index:
                        widget.insert("end", "\n")
                    tags = (f"list_{min(depth, 7)}",)
                    task = re.match(r"^\[([ xX])\]\s+(.*)$", body)
                    if task:
                        glyph = "☑" if task.group(1).strip() else "☐"
                        body = task.group(2)
                    else:
                        glyph = marker if marker[0].isdigit() else "•"
                    widget.insert("end", glyph + "  ", (*tags, "bullet"))
                    self._insert_inline(widget, body, tags)
                previous_block = True
                continue

            paragraph = [line.strip()]
            index += 1
            while index < len(lines) and lines[index].strip() and not self._starts_block(lines, index):
                paragraph.append(lines[index].strip())
                index += 1
            self._insert_inline(widget, " ".join(paragraph))
            previous_block = True

    @staticmethod
    def _is_horizontal_rule(line):
        return bool(re.match(r"^\s{0,3}(?:(?:\*\s*){3,}|(?:-\s*){3,}|(?:_\s*){3,})$", line))

    @staticmethod
    def _match_list_item(line):
        match = re.match(r"^(\s*)([-+*]|\d+[.)]|•)\s+(.*)$", line)
        if not match:
            return None
        depth = min(len(match.group(1).expandtabs(4)) // 2, 7)
        return depth, match.group(2), match.group(3)

    @staticmethod
    def _is_table_separator(line):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    @staticmethod
    def _starts_block(lines, index):
        line = lines[index]
        return bool(
            re.match(r"^\s{0,3}(?:`{3,}|~{3,}|#{1,6}(?:\s|$)|>|(?:[-+*]|\d+[.)]|•)\s+)", line)
            or ChatAIApp._is_horizontal_rule(line)
            or (index + 1 < len(lines) and "|" in line and ChatAIApp._is_table_separator(lines[index + 1]))
        )

    def _insert_markdown_table(self, widget, lines):
        rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
        columns = max(len(row) for row in rows)
        rows = [row + [""] * (columns - len(row)) for row in rows]
        widths = [min(max(3, *(len(row[col]) for row in rows)), 36) for col in range(columns)]
        for row_index, row in enumerate(rows):
            if row_index:
                widget.insert("end", "\n")
            for col, cell in enumerate(row):
                if col:
                    widget.insert("end", " │ ", ("table",))
                cell = cell[:widths[col]]
                widget.insert("end", cell.ljust(widths[col]), ("table", "table_header") if row_index == 0 else ("table",))

    def _insert_code_block(self, widget, code):
        toolbar = tk.Frame(widget, bg="#252525")
        copy_button = tk.Button(toolbar, text=self._t("copy"), command=lambda: self._copy_code(code, copy_button), bg="#363636", fg="#e5e5e5", activebackground="#484848", activeforeground="#ffffff", relief="flat", bd=0, padx=10, pady=3, font=("Segoe UI", 8), cursor="hand2")
        copy_button.pack(side="right", padx=7, pady=3)
        widget.window_create("end", window=toolbar, align="top", stretch=True, pady=4)
        widget.insert("end", "\n")
        if code:
            widget.insert("end", code, "code_block")
        widget.insert("end", "\n")

    def _copy_code(self, code, button):
        self.clipboard_clear()
        self.clipboard_append(code)
        self.update_idletasks()
        button.configure(text=self._t("copied"))
        button.after(1200, lambda: button.configure(text=self._t("copy")) if button.winfo_exists() else None)

    def _insert_inline(self, widget, text, extra_tags=()):
        index = 0
        while index < len(text):
            if text[index] == "\\" and index + 1 < len(text) and text[index + 1] in r"`*_{}[]()#+-.!|~\\":
                widget.insert("end", text[index + 1], extra_tags)
                index += 2
                continue

            if text[index] == "`":
                run_end = index
                while run_end < len(text) and text[run_end] == "`":
                    run_end += 1
                delimiter = text[index:run_end]
                close = self._find_inline_closer(text, delimiter, run_end)
                if close >= 0:
                    code = text[run_end:close].replace("\n", " ")
                    if len(code) > 1 and code.startswith(" ") and code.endswith(" ") and code.strip():
                        code = code[1:-1]
                    widget.insert("end", code, (*extra_tags, "inline_code"))
                    index = close + len(delimiter)
                    continue

            if text[index] == "[":
                link = re.match(r"\[([^\]]+)\]\((https?://[^\s)]+)(?:\s+[^)]*)?\)", text[index:])
                if link:
                    self._insert_inline(widget, link.group(1), (*extra_tags, "link"))
                    index += link.end()
                    continue

            if text.startswith(("***", "___"), index):
                delimiter = text[index:index + 3]
                close = self._find_inline_closer(text, delimiter, index + 3)
                if close > index + 3:
                    nested_tags = (*extra_tags, "bold_italic")
                    self._insert_inline(widget, text[index + 3:close], nested_tags)
                    index = close + 3
                    continue

            delimiter = None
            style = None
            for candidate, candidate_style in (("~~", "strike"), ("**", "bold"), ("__", "bold"), ("*", "italic"), ("_", "italic")):
                if text.startswith(candidate, index):
                    if candidate == "_" and index > 0 and index + 1 < len(text) and text[index - 1].isalnum() and text[index + 1].isalnum():
                        continue
                    close = self._find_inline_closer(text, candidate, index + len(candidate))
                    if close > index + len(candidate):
                        delimiter, style = candidate, candidate_style
                        break
            if delimiter:
                self._insert_inline(widget, text[index + len(delimiter):close], (*extra_tags, style))
                index = close + len(delimiter)
                continue

            widget.insert("end", text[index], extra_tags)
            index += 1

    @staticmethod
    def _find_inline_closer(text, delimiter, start):
        position = start
        while True:
            position = text.find(delimiter, position)
            if position < 0:
                return -1
            escapes = 0
            back = position - 1
            while back >= 0 and text[back] == "\\":
                escapes += 1
                back -= 1
            if escapes % 2:
                position += len(delimiter)
                continue
            if delimiter in ("**", "__") and position > start and text.startswith(delimiter[0] * 3, position):
                return position + 1
            if delimiter == "_" and position + 1 < len(text) and text[position - 1].isalnum() and text[position + 1].isalnum():
                position += 1
                continue
            return position

    @staticmethod
    def _fit_text(widget, content):
        width = max(30, int(widget.cget("width")) if widget.cget("width") else 78)
        lines = sum(max(1, len(line) // width + 1) for line in content.splitlines()) or 1
        fences = sum(line.strip().startswith("```") for line in content.splitlines())
        lines += (fences + 1) // 2
        widget.configure(height=min(max(lines, 1), 70))

    def refresh_models(self):
        if self.checking_connection:
            return
        self.checking_connection = True
        self.connection_text.set(self._t("checking"))
        self.sidebar_status_dot.configure(fg="#a0a0a0")
        self.sidebar_status_label.configure(fg=MUTED)
        self.status_var.set("")
        self.check_generation += 1
        generation = self.check_generation
        threading.Thread(target=self._fetch_models, args=(generation, self._base_url()), daemon=True).start()

    def _periodic_connection_check(self):
        self.refresh_models()
        self.after(20000, self._periodic_connection_check)

    def _base_url(self):
        return (self.settings.get("url") or DEFAULT_URL).rstrip("/")

    def _fetch_models(self, generation, base_url):
        try:
            req = urllib.request.Request(base_url + "/api/tags", headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=2.5) as response:
                data = json.loads(response.read().decode("utf-8"))
            models = [entry.get("name", "") for entry in data.get("models", []) if entry.get("name")]
            self.events.put(("models", generation, models))
        except Exception as exc:
            self.events.put(("connection_error", generation, str(exc)))

    def _poll_events(self):
        dirty_widgets = {}
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind in ("token", "done", "error", "stopped") and event[1] in self.cancelled_requests:
                    if kind in ("done", "error", "stopped"):
                        self.cancelled_requests.discard(event[1])
                    continue
                if kind == "models":
                    _kind, generation, models = event
                    if generation != self.check_generation:
                        continue
                    self.checking_connection = False
                    self.connection_available = True
                    self.available_models = models
                    current = self.model_var.get()
                    preferred = self.saved_model if self.saved_model in models else current
                    if not current or current not in models:
                        if models:
                            selected = preferred if preferred in models else models[0]
                            self.model_var.set(selected)
                            self.saved_model = selected
                            self._save()
                        else:
                            self.model_var.set(self._t("no_model"))
                    self.connection_text.set(self._t("online") if models else self._t("no_model"))
                    self._draw_model_button()
                    self.sidebar_status_dot.configure(fg="#bdbdbd")
                    self.sidebar_status_label.configure(fg="#bdbdbd")
                    self.status_var.set("" if models else self._t("download_start"))
                elif kind == "connection_error":
                    _kind, generation, _error = event
                    if generation != self.check_generation:
                        continue
                    self.checking_connection = False
                    self.connection_available = False
                    self.available_models = []
                    self.model_var.set(self._t("unreachable"))
                    self._draw_model_button()
                    self.connection_text.set(self._t("unreachable"))
                    self.sidebar_status_dot.configure(fg="#df8a7b")
                    self.sidebar_status_label.configure(fg="#d5a198")
                    self.status_var.set(self._t("cannot_reach", url=self._base_url()))
                elif kind == "token":
                    _req_id, channel, token = event[1], event[2], event[3]
                    widget_key = f"{_req_id}-{channel}"
                    widget = self.message_widgets.get(widget_key)
                    response = self.pending_responses.get(_req_id)
                    if response:
                        response[channel] += token
                    is_visible_chat = self.pending_chat_ids.get(_req_id) == self.active_id
                    if not widget and response and is_visible_chat:
                        widget = self._add_message_widget("thinking" if channel == "thinking" else "assistant", "", widget_key)
                    if widget and response:
                        dirty_widgets[widget_key] = (widget, response, channel)
                elif kind == "done":
                    self.pending_responses.pop(event[1], None)
                    self.pending_chat_ids.pop(event[1], None)
                    if self.active_request_id == event[1]:
                        self.active_request_id = None
                        self.active_cancel_event = None
                        self.active_responses.pop(event[1], None)
                    self.busy = False
                    self._draw_send_button()
                    self.status_var.set("")
                    self._save()
                elif kind == "error":
                    _req_id, detail, connection_lost = event[1], event[2], event[3]
                    partial = self.pending_responses.pop(_req_id, None)
                    self.pending_chat_ids.pop(_req_id, None)
                    if self.active_request_id == _req_id:
                        self.active_request_id = None
                        self.active_cancel_event = None
                        self.active_responses.pop(_req_id, None)
                    if partial and not (partial.get("content") or partial.get("thinking")):
                        collections = self.chats + ([self.draft_chat] if self.draft_chat else [])
                        for chat in collections:
                            for index, message in enumerate(chat["messages"]):
                                if message is partial:
                                    chat["messages"].pop(index)
                                    break
                        self._render_messages()
                    self.busy = False
                    self._draw_send_button()
                    self.status_var.set("")
                    if connection_lost:
                        self.connection_available = False
                        self.connection_text.set(self._t("unreachable"))
                        self.sidebar_status_dot.configure(fg="#df8a7b")
                        self.sidebar_status_label.configure(fg="#d5a198")
                    self.status_var.set(detail.splitlines()[0] if detail else self._t("request_failed"))
                    self._save()
                elif kind == "stopped":
                    self.cancelled_requests.discard(event[1])
        except queue.Empty:
            pass
        for widget, response, channel in dirty_widgets.values():
            widget.configure(state="normal")
            self._render_markdown(widget, response[channel])
            self._fit_text(widget, response[channel])
            self._make_text_selectable_readonly(widget)
        if dirty_widgets:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.yview_moveto(1.0)
        self.after(160, self._poll_events)

    def send_message(self):
        if self.busy:
            return
        text = self.input.get("1.0", "end-1c").strip()
        if not text:
            return
        if not self.connection_available:
            self.status_var.set(self._t("offline"))
            self.refresh_models()
            return
        model = self.model_var.get().strip()
        if not model:
            self.status_var.set(self._t("model_missing"))
            self.refresh_models()
            return
        chat = self._active_chat()
        if not chat:
            self.new_chat()
            chat = self._active_chat()
        self.welcome.destroy() if hasattr(self, "welcome") and self.welcome.winfo_exists() else None
        user_message = {"role": "user", "content": text}
        chat["messages"].append(user_message)
        if self.draft_chat is chat:
            self.chats.append(chat)
            self.draft_chat = None
        self.saved_model = model
        if len(chat["messages"]) == 1:
            chat["title"] = self._title_from_prompt(text)
            self.chat_title.configure(text=chat["title"])
        chat["updated"] = datetime.now().isoformat(timespec="seconds")
        self._refresh_chat_list()
        self._add_message_widget("user", self._display_message_content(user_message), f"user-{uuid.uuid4()}")
        request_id = f"assistant-{uuid.uuid4()}"
        cancel_event = threading.Event()
        self.active_request_id = request_id
        self.active_cancel_event = cancel_event
        chat["messages"].append({"role": "assistant", "content": "", "thinking": ""})
        self.pending_responses[request_id] = chat["messages"][-1]
        self.pending_chat_ids[request_id] = chat["id"]
        self.input.delete("1.0", "end")
        self.input_placeholder.place(x=16, y=14)
        self.focus_set()
        self.busy = True
        self._draw_send_button()
        self.status_var.set(self._t("response_from", model=model))
        self._save()
        history = [self._message_for_api(m) for m in chat["messages"][:-1]]
        payload = {"model": model, "messages": history, "stream": True, "think": bool(self.thinking_var.get()), "options": {"num_ctx": self.context_length}}
        threading.Thread(target=self._stream_reply, args=(payload, request_id, cancel_event), daemon=True).start()

    def _stream_reply(self, payload, request_id, cancel_event):
        response_stream = None
        try:
            if cancel_event.is_set():
                self.events.put(("stopped", request_id))
                return
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(self._base_url() + "/api/chat", data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=600) as response:
                response_stream = response
                self.active_responses[request_id] = response
                if cancel_event.is_set():
                    self.events.put(("stopped", request_id))
                    return
                for raw in response:
                    if cancel_event.is_set():
                        break
                    if not raw.strip():
                        continue
                    packet = json.loads(raw.decode("utf-8"))
                    msg = packet.get("message", {})
                    content = msg.get("content", "")
                    thinking = msg.get("thinking", "")
                    if thinking and payload.get("think"):
                        self.events.put(("token", request_id, "thinking", thinking))
                    if content:
                        self.events.put(("token", request_id, "content", content))
            if cancel_event.is_set():
                self.events.put(("stopped", request_id))
                return
            self.events.put(("done", request_id))
        except urllib.error.HTTPError as exc:
            if cancel_event.is_set():
                self.events.put(("stopped", request_id))
                return
            detail = exc.read().decode("utf-8", errors="replace")
            clean_detail = " ".join(detail.splitlines()).strip()
            message = self._t("request_rejected", code=exc.code)
            if clean_detail:
                message += f": {clean_detail[:110]}"
            self.events.put(("error", request_id, message, False))
        except Exception as exc:
            if cancel_event.is_set():
                self.events.put(("stopped", request_id))
                return
            self.events.put(("error", request_id, self._t("connection_interrupted", error=exc), True))
        finally:
            if self.active_responses.get(request_id) is response_stream:
                self.active_responses.pop(request_id, None)

    def open_settings(self):
        win = tk.Toplevel(self)
        win.title(self._t("settings_title"))
        win.configure(bg=BG)
        win.geometry("700x560")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        box = tk.Frame(win, bg=BG, padx=24, pady=22)
        box.pack(fill="both", expand=True)
        tk.Label(box, text=self._t("settings_title"), bg=BG, fg=TEXT, font=("Segoe UI Semibold", 17)).pack(anchor="w", pady=(0, 14))
        tk.Label(box, text=self._t("language"), bg=BG, fg=MUTED, font=FONT).pack(anchor="w")
        language_var = tk.StringVar(value=LANGUAGE_NAMES[self.language])
        language_picker = ttk.Combobox(box, textvariable=language_var, values=tuple(LANGUAGE_CODES), state="readonly", style="Chat.TCombobox", width=35)
        language_picker.pack(fill="x", ipady=3, pady=(6, 14))
        tk.Label(box, text=self._t("ollama_address"), bg=BG, fg=MUTED, font=FONT).pack(anchor="w")
        url_var = tk.StringVar(value=self.settings.get("url", DEFAULT_URL))
        entry = tk.Entry(box, textvariable=url_var, bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat", font=FONT, width=38)
        entry.pack(fill="x", ipady=7, pady=(6, 10))
        tk.Label(box, text=self._t("usually"), bg=BG, fg="#777777", font=("Segoe UI", 9)).pack(anchor="w")
        context_var = tk.IntVar(value=self.context_length)
        context_slider = tk.Canvas(box, height=150, bg=BG, highlightthickness=0, borderwidth=0)
        context_slider.pack(fill="x", pady=(14, 0))
        slider_index = {"value": CONTEXT_LENGTHS.index(self.context_length)}

        def draw_context_slider(_event=None):
            context_slider.delete("all")
            width = max(300, context_slider.winfo_width())
            context_slider.create_polygon(*self._rounded_points(1, 1, width - 1, 149, 16), smooth=True, splinesteps=16, fill="#242424", outline="")
            context_slider.create_text(18, 25, text="⚙", anchor="w", fill="#d0d0d0", font=("Segoe UI Symbol", 17))
            context_slider.create_text(48, 25, text="Context length", anchor="w", fill="#eeeeee", font=("Segoe UI Semibold", 10))
            context_slider.create_text(48, 48, text=self._t("context_description_1") + " " + self._t("context_description_2"), anchor="nw", width=max(220, width - 84), fill="#b8b8b8", font=("Segoe UI", 9))
            x1, x2, track_y = 58, width - 28, 108
            context_slider.create_line(x1, track_y, x2, track_y, fill="#4b4b4b", width=4, capstyle="round")
            step = (x2 - x1) / (len(CONTEXT_LENGTHS) - 1)
            for index, length in enumerate(CONTEXT_LENGTHS):
                x = x1 + step * index
                context_slider.create_text(x, 126, text=f"{length // 1024}k", fill="#b8b8b8", font=("Segoe UI", 8))
            knob_x = x1 + step * slider_index["value"]
            context_slider.create_oval(knob_x - 8, track_y - 8, knob_x + 8, track_y + 8, fill="#f4f4f4", outline="#ffffff", width=1)

        def set_context_from_pointer(event):
            width = max(300, context_slider.winfo_width())
            x1, x2 = 58, width - 28
            fraction = min(1.0, max(0.0, (event.x - x1) / (x2 - x1)))
            slider_index["value"] = round(fraction * (len(CONTEXT_LENGTHS) - 1))
            context_var.set(CONTEXT_LENGTHS[slider_index["value"]])
            draw_context_slider()

        context_slider.bind("<Configure>", draw_context_slider)
        context_slider.bind("<Button-1>", set_context_from_pointer)
        context_slider.bind("<B1-Motion>", set_context_from_pointer)

        def save_close():
            previous_language = self.language
            self.language = LANGUAGE_CODES.get(language_var.get(), "en")
            self.settings["url"] = url_var.get().strip().rstrip("/") or DEFAULT_URL
            self.context_length = context_var.get()
            self._save()
            win.destroy()
            if self.language != previous_language:
                self._rebuild_language_ui()
            self.checking_connection = False
            self.check_generation += 1
            self.refresh_models()
        ttk.Button(box, text=self._t("save"), style="Accent.TButton", command=save_close).pack(anchor="e", pady=(12, 0))
        entry.focus_set()

    def _rebuild_language_ui(self):
        was_sidebar_visible = self.sidebar_visible
        active_chat = self._active_chat()
        if self.draft_chat and not self.draft_chat["messages"]:
            self.draft_chat["title"] = self._t("new_chat")
        for child in self.winfo_children():
            child.destroy()
        self._build()
        if not was_sidebar_visible:
            self.toggle_sidebar()
        self._refresh_chat_list()
        self.chat_title.configure(text=(active_chat.get("title") if active_chat and active_chat.get("messages") else self._t("new_chat")))
        self._render_messages()
        self.status_var.set("")


if __name__ == "__main__":
    app = ChatAIApp()
    app.mainloop()
