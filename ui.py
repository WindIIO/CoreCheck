"""
Module d'interface graphique pour CoreCheck.
Utilise Tkinter pour créer une interface moderne.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import Dict, Any, List, Optional
import os

# Import des modules locaux
from system_info import SystemInfo
from network_tools import NetworkTools
from cleaner import Cleaner
from process_manager import ProcessManager
from logger import get_logger


class CoreCheckUI:
    """Interface graphique principale de CoreCheck."""
    
    # Couleurs pour le mode sombre
    COLORS = {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "accent": "#007acc",
        "success": "#4caf50",
        "warning": "#ff9800",
        "danger": "#f44336",
        "secondary": "#2d2d2d",
        "border": "#3d3d3d",
        "text_secondary": "#aaaaaa"
    }
    
    def __init__(self, root: tk.Tk):
        """Initialise l'interface graphique.
        
        Args:
            root: Fenêtre principale Tkinter
        """
        self.root = root
        self.root.title("CoreCheck - Support Informatique")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Initialiser le logger
        self.logger = get_logger()
        self.logger.info("Application CoreCheck démarrée")
        
        # Variables pour la mise à jour automatique
        self.update_running = False
        self.update_thread = None
        
        # Configurer le style
        self.setup_style()
        
        # Créer l'interface
        self.create_widgets()
        
        # Démarrer la mise à jour automatique
        self.start_auto_update()
        
        # Charger les données initiales
        self.refresh_all()
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_style(self):
        """Configure le style de l'interface."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurer les couleurs
        self.root.configure(bg=self.COLORS["bg"])
        
        # Style pour les frames
        style.configure("Card.TFrame", 
                       background=self.COLORS["secondary"],
                       relief="flat")
        
        # Style pour les labels
        style.configure("Title.TLabel",
                       background=self.COLORS["secondary"],
                       foreground=self.COLORS["fg"],
                       font=("Segoe UI", 14, "bold"))
        
        style.configure("Subtitle.TLabel",
                       background=self.COLORS["secondary"],
                       foreground=self.COLORS["text_secondary"],
                       font=("Segoe UI", 10))
        
        style.configure("Value.TLabel",
                       background=self.COLORS["secondary"],
                       foreground=self.COLORS["fg"],
                       font=("Segoe UI", 12))
        
        # Style pour les boutons
        style.configure("Action.TButton",
                       background=self.COLORS["accent"],
                       foreground=self.COLORS["fg"],
                       font=("Segoe UI", 10),
                       borderwidth=0,
                       padding=10)
        
        style.map("Action.TButton",
                 background=[("active", "#005a9e")])
        
        # Style pour le Treeview
        style.configure("Treeview",
                       background=self.COLORS["secondary"],
                       foreground=self.COLORS["fg"],
                       fieldbackground=self.COLORS["secondary"],
                       rowheight=25)
        
        style.configure("Treeview.Heading",
                       background=self.COLORS["bg"],
                       foreground=self.COLORS["fg"],
                       font=("Segoe UI", 10, "bold"))
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface."""
        # Container principal
        main_container = tk.Frame(self.root, bg=self.COLORS["bg"])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # En-tête
        self.create_header(main_container)
        
        # Panneau principal avec onglets
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, pady=(10, 0))
        
        # Créer les onglets
        self.tab_system = self.create_system_tab()
        self.tab_network = self.create_network_tab()
        self.tab_actions = self.create_actions_tab()
        self.tab_processes = self.create_processes_tab()
        self.tab_logs = self.create_logs_tab()
        
        # Barre de statut
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Crée l'en-tête de l'application."""
        header = tk.Frame(parent, bg=self.COLORS["bg"], height=60)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)
        
        # Titre
        title = tk.Label(header, text="CoreCheck",
                        font=("Segoe UI", 24, "bold"),
                        bg=self.COLORS["bg"],
                        fg=self.COLORS["accent"])
        title.pack(side="left", padx=10)
        
        # Sous-titre
        subtitle = tk.Label(header, text="Support Informatique",
                          font=("Segoe UI", 12),
                          bg=self.COLORS["bg"],
                          fg=self.COLORS["text_secondary"])
        subtitle.pack(side="left", padx=(0, 20))
        
        # Boutons de mode
        btn_frame = tk.Frame(header, bg=self.COLORS["bg"])
        btn_frame.pack(side="right", padx=10)
        
        self.btn_refresh = tk.Button(btn_frame, text="↻ Actualiser",
                                     command=self.refresh_all,
                                     bg=self.COLORS["accent"],
                                     fg=self.COLORS["fg"],
                                     relief="flat",
                                     padx=15,
                                     pady=5,
                                     font=("Segoe UI", 10))
        self.btn_refresh.pack(side="right", padx=5)
    
    def create_system_tab(self):
        """Crée l'onglet des informations système."""
        frame = tk.Frame(self.notebook, bg=self.COLORS["bg"])
        self.notebook.add(frame, text="  Système  ")
        
        # Container avec scroll
        canvas = tk.Canvas(frame, bg=self.COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Section CPU
        self.create_info_card(scrollable_frame, "CPU", [
            ("Utilisation", "cpu_usage", "cpu_percent"),
            ("Cœurs", "cpu_count", "text"),
            ("Fréquence", "cpu_freq", "text")
        ], row=0, col=0)
        
        # Section RAM
        self.create_info_card(scrollable_frame, "Mémoire RAM", [
            ("Utilisation", "ram_usage", "ram_percent"),
            ("Utilisé", "ram_used", "ram_gb"),
            ("Disponible", "ram_available", "ram_gb")
        ], row=0, col=1)
        
        # Section Disque
        self.create_info_card(scrollable_frame, "Disque Dur", [
            ("Utilisation", "disk_usage", "disk_percent"),
            ("Utilisé", "disk_used", "disk_gb"),
            ("Libre", "disk_free", "disk_gb")
        ], row=1, col=0)
        
        # Section Système
        self.create_info_card(scrollable_frame, "Système", [
            ("Nom du PC", "computer_name", "text"),
            ("Système", "os_name", "text"),
            ("Version OS", "os_version", "text")
        ], row=1, col=1)
        
        # Section Analyse rapide
        self.create_alerts_card(scrollable_frame, row=2, col=0, colspan=2)
        
        return frame
    
    def create_info_card(self, parent, title: str, fields: List[tuple], row: int, col: int):
        """Crée une carte d'information.
        
        Args:
            parent: Widget parent
            title: Titre de la carte
            fields: Liste des champs (nom, clé, type)
            row: Ligne dans le grid
            col: Colonne dans le grid
        """
        card = tk.Frame(parent, bg=self.COLORS["secondary"], relief="flat", bd=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Titre de la carte
        card_title = tk.Label(card, text=title,
                             font=("Segoe UI", 12, "bold"),
                             bg=self.COLORS["secondary"],
                             fg=self.COLORS["fg"],
                             pady=10)
        card_title.pack(fill="x")
        
        # Séparateur
        sep = tk.Frame(card, bg=self.COLORS["border"], height=1)
        sep.pack(fill="x")
        
        # Champs
        self.system_labels = getattr(self, 'system_labels', {})
        
        for field_name, field_key, field_type in fields:
            field_frame = tk.Frame(card, bg=self.COLORS["secondary"])
            field_frame.pack(fill="x", padx=15, pady=5)
            
            label = tk.Label(field_frame, text=field_name + ":",
                            font=("Segoe UI", 10),
                            bg=self.COLORS["secondary"],
                            fg=self.COLORS["text_secondary"])
            label.pack(side="left")
            
            value = tk.Label(field_frame, text="---",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.COLORS["secondary"],
                            fg=self.COLORS["fg"])
            value.pack(side="right")
            
            self.system_labels[field_key] = value
    
    def create_alerts_card(self, parent, row: int, col: int, colspan: int = 1):
        """Crée une carte d'alertes."""
        card = tk.Frame(parent, bg=self.COLORS["secondary"], relief="flat", bd=1)
        card.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")
        
        # Titre
        card_title = tk.Label(card, text="Analyse Rapide",
                             font=("Segoe UI", 12, "bold"),
                             bg=self.COLORS["secondary"],
                             fg=self.COLORS["fg"],
                             pady=10)
        card_title.pack(fill="x")
        
        # Séparateur
        sep = tk.Frame(card, bg=self.COLORS["border"], height=1)
        sep.pack(fill="x")
        
        # Container des alertes
        self.alerts_container = tk.Frame(card, bg=self.COLORS["secondary"])
        self.alerts_container.pack(fill="both", expand=True, padx=15, pady=10)
    
    def create_network_tab(self):
        """Crée l'onglet réseau."""
        frame = tk.Frame(self.notebook, bg=self.COLORS["bg"])
        self.notebook.add(frame, text="  Réseau  ")
        
        # Section connexion
        conn_frame = tk.Frame(frame, bg=self.COLORS["secondary"], relief="flat", bd=1)
        conn_frame.pack(fill="x", padx=10, pady=10)
        
        title = tk.Label(conn_frame, text="Connexion Internet",
                        font=("Segoe UI", 12, "bold"),
                        bg=self.COLORS["secondary"],
                        fg=self.COLORS["fg"],
                        pady=10)
        title.pack(fill="x")
        
        sep = tk.Frame(conn_frame, bg=self.COLORS["border"], height=1)
        sep.pack(fill="x")
        
        # Status de connexion
        status_frame = tk.Frame(conn_frame, bg=self.COLORS["secondary"])
        status_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(status_frame, text="Statut:",
                font=("Segoe UI", 10),
                bg=self.COLORS["secondary"],
                fg=self.COLORS["text_secondary"]).pack(side="left")
        
        self.lbl_connection_status = tk.Label(status_frame, text="Vérification...",
                                              font=("Segoe UI", 10, "bold"),
                                              bg=self.COLORS["secondary"],
                                              fg=self.COLORS["warning"])
        self.lbl_connection_status.pack(side="left", padx=10)
        
        tk.Label(status_frame, text="Temps de réponse:",
                font=("Segoe UI", 10),
                bg=self.COLORS["secondary"],
                fg=self.COLORS["text_secondary"]).pack(side="left", padx=(20, 0))
        
        self.lbl_response_time = tk.Label(status_frame, text="---",
                                         font=("Segoe UI", 10, "bold"),
                                         bg=self.COLORS["secondary"],
                                         fg=self.COLORS["fg"])
        self.lbl_response_time.pack(side="left", padx=10)
        
        # Bouton tester
        btn_frame = tk.Frame(conn_frame, bg=self.COLORS["secondary"])
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        btn_test = tk.Button(btn_frame, text="Tester la connexion",
                           command=self.test_network,
                           bg=self.COLORS["accent"],
                           fg=self.COLORS["fg"],
                           relief="flat",
                           padx=15,
                           pady=5,
                           font=("Segoe UI", 10))
        btn_test.pack(side="left")
        
        # IP locale
        tk.Label(btn_frame, text="IP Locale:",
                font=("Segoe UI", 10),
                bg=self.COLORS["secondary"],
                fg=self.COLORS["text_secondary"]).pack(side="left", padx=(20, 5))
        
        self.lbl_local_ip = tk.Label(btn_frame, text="---",
                                    font=("Segoe UI", 10),
                                    bg=self.COLORS["secondary"],
                                    fg=self.COLORS["fg"])
        self.lbl_local_ip.pack(side="left")
        
        # Section Flush DNS
        dns_frame = tk.Frame(frame, bg=self.COLORS["secondary"], relief="flat", bd=1)
        dns_frame.pack(fill="x", padx=10, pady=10)
        
        title = tk.Label(dns_frame, text="Cache DNS",
                        font=("Segoe UI", 12, "bold"),
                        bg=self.COLORS["secondary"],
                        fg=self.COLORS["fg"],
                        pady=10)
        title.pack(fill="x")
        
        sep = tk.Frame(dns_frame, bg=self.COLORS["border"], height=1)
        sep.pack(fill="x")
        
        btn_dns = tk.Button(dns_frame, text="Vider le cache DNS",
                          command=self.flush_dns,
                          bg=self.COLORS["accent"],
                          fg=self.COLORS["fg"],
                          relief="flat",
                          padx=15,
                          pady=8,
                          font=("Segoe UI", 10))
        btn_dns.pack(padx=15, pady=15)
        
        return frame
    
    def create_actions_tab(self):
        """Crée l'onglet des actions rapides."""
        frame = tk.Frame(self.notebook, bg=self.COLORS["bg"])
        self.notebook.add(frame, text="  Actions  ")
        
        # Nettoyage
        clean_frame = tk.Frame(frame, bg=self.COLORS["secondary"], relief="flat", bd=1)
        clean_frame.pack(fill="x", padx=10, pady=10)
        
        title = tk.Label(clean_frame, text="Nettoyage",
                        font=("Segoe UI", 12, "bold"),
                        bg=self.COLORS["secondary"],
                        fg=self.COLORS["fg"],
                        pady=10)
        title.pack(fill="x")
        
        sep = tk.Frame(clean_frame, bg=self.COLORS["border"], height=1)
        sep.pack(fill="x")
        
        # Info taille temp
        self.lbl_temp_size = tk.Label(clean_frame, text="Taille fichiers temporaires: ---",
                                     font=("Segoe UI", 10),
                                     bg=self.COLORS["secondary"],
                                     fg=self.COLORS["text_secondary"],
                                     pady=10)
        self.lbl_temp_size.pack()
        
        # Bouton nettoyer
        btn_clean = tk.Button(clean_frame, text="Nettoyer les fichiers temporaires",
                             command=self.clean_temp,
                             bg=self.COLORS["warning"],
                             fg=self.COLORS["fg"],
                             relief="flat",
                             padx=15,
                             pady=8,
                             font=("Segoe UI", 10))
        btn_clean.pack(pady=10)
        
        # Barre de progression
        self.progress_clean = ttk.Progressbar(clean_frame, mode='determinate',
                                              length=300)
        self.progress_clean.pack(pady=(0, 15))
        
        # Outils système
        tools_frame = tk.Frame(frame, bg=self.COLORS["secondary"], relief="flat", bd=1)
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        title = tk.Label(tools_frame, text="Outils Système",
                        font=("Segoe UI", 12, "bold"),
                        bg=self.COLORS["secondary"],
                        fg=self.COLORS["fg"],
                        pady=10)
        title.pack(fill="x")
        
        sep = tk.Frame(tools_frame, bg=self.COLORS["border"], height=1)
        sep.pack(fill="x")
        
        # Boutons d'outils
        buttons_frame = tk.Frame(tools_frame, bg=self.COLORS["secondary"])
        buttons_frame.pack(padx=15, pady=15)
        
        tools = [
            ("Gestionnaire des tâches", self.open_task_manager),
            ("Paramètres réseau", self.open_network_settings),
            ("Panneau de configuration", self.open_control_panel),
            ("Gestionnaire de périphériques", self.open_device_manager),
            ("Propriétés système", self.open_system_properties)
        ]
        
        for i, (text, cmd) in enumerate(tools):
            btn = tk.Button(buttons_frame, text=text,
                          command=cmd,
                          bg=self.COLORS["accent"],
                          fg=self.COLORS["fg"],
                          relief="flat",
                          padx=15,
                          pady=8,
                          font=("Segoe UI", 10))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        return frame
    
    def create_processes_tab(self):
        """Crée l'onglet des processus."""
        frame = tk.Frame(self.notebook, bg=self.COLORS["bg"])
        self.notebook.add(frame, text="  Processus  ")
        
        # Barre de recherche
        search_frame = tk.Frame(frame, bg=self.COLORS["bg"])
        search_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(search_frame, text="Rechercher:",
                font=("Segoe UI", 10),
                bg=self.COLORS["bg"],
                fg=self.COLORS["fg"]).pack(side="left")
        
        self.entry_search = tk.Entry(search_frame, font=("Segoe UI", 10),
                                    bg=self.COLORS["secondary"],
                                    fg=self.COLORS["fg"],
                                    relief="flat")
        self.entry_search.pack(side="left", padx=10, fill="x", expand=True)
        self.entry_search.bind("<Return>", lambda e: self.search_processes())
        
        btn_search = tk.Button(search_frame, text="Rechercher",
                             command=self.search_processes,
                             bg=self.COLORS["accent"],
                             fg=self.COLORS["fg"],
                             relief="flat",
                             padx=15)
        btn_search.pack(side="left", padx=5)
        
        btn_clear = tk.Button(search_frame, text="Afficher tout",
                             command=self.refresh_processes,
                             bg=self.COLORS["secondary"],
                             fg=self.COLORS["fg"],
                             relief="flat",
                             padx=15)
        btn_clear.pack(side="left")
        
        # Tableau des processus
        tree_frame = tk.Frame(frame, bg=self.COLORS["bg"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ("pid", "name", "cpu", "memory", "status")
        self.process_tree = ttk.Treeview(tree_frame, columns=columns,
                                         show="headings", selectmode="browse")
        
        # En-têtes
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("name", text="Nom du processus")
        self.process_tree.heading("cpu", text="CPU %")
        self.process_tree.heading("memory", text="Mémoire %")
        self.process_tree.heading("status", text="Statut")
        
        # Largeurs des colonnes
        self.process_tree.column("pid", width=80)
        self.process_tree.column("name", width=300)
        self.process_tree.column("cpu", width=100)
        self.process_tree.column("memory", width=100)
        self.process_tree.column("status", width=100)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                          command=self.process_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                          command=self.process_tree.xview)
        self.process_tree.configure(yscrollcommand=vsb.set,
                                   xscrollcommand=hsb.set)
        
        self.process_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Bouton tuer le processus
        btn_frame = tk.Frame(frame, bg=self.COLORS["bg"])
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_kill = tk.Button(btn_frame, text="Terminer le processus",
                           command=self.kill_selected_process,
                           bg=self.COLORS["danger"],
                           fg=self.COLORS["fg"],
                           relief="flat",
                           padx=15,
                           pady=8,
                           font=("Segoe UI", 10))
        btn_kill.pack(side="right")
        
        # Info nombre de processus
        self.lbl_process_count = tk.Label(btn_frame, text="",
                                         font=("Segoe UI", 10),
                                         bg=self.COLORS["bg"],
                                         fg=self.COLORS["text_secondary"])
        self.lbl_process_count.pack(side="left")
        
        return frame
    
    def create_logs_tab(self):
        """Crée l'onglet des logs."""
        frame = tk.Frame(self.notebook, bg=self.COLORS["bg"])
        self.notebook.add(frame, text="  Logs  ")
        
        # Zone de logs
        self.log_text = scrolledtext.ScrolledText(frame,
                                                   font=("Consolas", 10),
                                                   bg=self.COLORS["bg"],
                                                   fg=self.COLORS["fg"],
                                                   relief="flat")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(frame, bg=self.COLORS["bg"])
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_clear = tk.Button(btn_frame, text="Effacer les logs",
                            command=self.clear_logs,
                            bg=self.COLORS["secondary"],
                            fg=self.COLORS["fg"],
                            relief="flat",
                            padx=15,
                            pady=5)
        btn_clear.pack(side="left")
        
        btn_export = tk.Button(btn_frame, text="Exporter",
                              command=self.export_logs,
                              bg=self.COLORS["secondary"],
                              fg=self.COLORS["fg"],
                              relief="flat",
                              padx=15,
                              pady=5)
        btn_export.pack(side="right")
        
        return frame
    
    def create_status_bar(self, parent):
        """Crée la barre de statut."""
        status = tk.Frame(parent, bg=self.COLORS["secondary"], height=30)
        status.pack(fill="x", pady=(10, 0))
        status.pack_propagate(False)
        
        self.lbl_status = tk.Label(status, text="Prêt",
                                  font=("Segoe UI", 9),
                                  bg=self.COLORS["secondary"],
                                  fg=self.COLORS["text_secondary"])
        self.lbl_status.pack(side="left", padx=10)
        
        self.lbl_time = tk.Label(status, text="",
                                font=("Segoe UI", 9),
                                bg=self.COLORS["secondary"],
                                fg=self.COLORS["text_secondary"])
        self.lbl_time.pack(side="right", padx=10)
    
    # ==================== Méthodes de mise à jour ====================
    
    def start_auto_update(self):
        """Démarre la mise à jour automatique des données."""
        self.update_running = True
        self.update_thread = threading.Thread(target=self.auto_update_loop,
                                             daemon=True)
        self.update_thread.start()
    
    def auto_update_loop(self):
        """Boucle de mise à jour automatique."""
        while self.update_running:
            try:
                self.root.after(0, self.update_system_info)
                time.sleep(2)  # Mise à jour toutes les 2 secondes
            except Exception:
                pass
    
    def refresh_all(self):
        """Rafraîchit toutes les données."""
        self.update_system_info()
        self.test_network()
        self.update_temp_size()
        self.refresh_processes()
        self.update_logs()
        self.logger.info("Données actualisées")
    
    def update_system_info(self):
        """Met à jour les informations système."""
        try:
            info = SystemInfo.get_all_info()
            
            # CPU
            if "cpu_usage" in self.system_labels:
                self.system_labels["cpu_usage"].config(
                    text=f"{info['cpu']['usage']:.1f}%")
            
            if "cpu_count" in self.system_labels:
                self.system_labels["cpu_count"].config(
                    text=str(info['cpu']['count']))
            
            if "cpu_freq" in self.system_labels:
                self.system_labels["cpu_freq"].config(
                    text=info['cpu']['freq'])
            
            # RAM
            if "ram_usage" in self.system_labels:
                self.system_labels["ram_usage"].config(
                    text=f"{info['ram']['percent']:.1f}%")
            
            if "ram_used" in self.system_labels:
                self.system_labels["ram_used"].config(
                    text=f"{info['ram']['used']:.1f} Go")
            
            if "ram_available" in self.system_labels:
                self.system_labels["ram_available"].config(
                    text=f"{info['ram']['available']:.1f} Go")
            
            # Disque
            if "disk_usage" in self.system_labels:
                self.system_labels["disk_usage"].config(
                    text=f"{info['disk']['percent']:.1f}%")
            
            if "disk_used" in self.system_labels:
                self.system_labels["disk_used"].config(
                    text=f"{info['disk']['used']:.1f} Go")
            
            if "disk_free" in self.system_labels:
                self.system_labels["disk_free"].config(
                    text=f"{info['disk']['free']:.1f} Go")
            
            # Système
            if "computer_name" in self.system_labels:
                self.system_labels["computer_name"].config(
                    text=info['computer_name'])
            
            if "os_name" in self.system_labels:
                self.system_labels["os_name"].config(
                    text=info['os'])
            
            if "os_version" in self.system_labels:
                self.system_labels["os_version"].config(
                    text=info['os_version'][:30] + "...")
            
            # Mettre à jour les alertes
            self.update_alerts()
            
            # Mettre à jour l'heure
            import datetime
            self.lbl_time.config(
                text=datetime.datetime.now().strftime("%H:%M:%S"))
            
        except Exception as e:
            print(f"Erreur mise à jour système: {e}")
    
    def update_alerts(self):
        """Met à jour les alertes."""
        # Effacer les anciennes alertes
        for widget in self.alerts_container.winfo_children():
            widget.destroy()
        
        # Récupérer les alertes
        health = SystemInfo.check_system_health()
        
        for alert in health["alerts"]:
            alert_frame = tk.Frame(self.alerts_container,
                                  bg=self.COLORS["secondary"],
                                  relief="flat")
            alert_frame.pack(fill="x", pady=5)
            
            # Couleur selon le type
            colors = {
                "success": self.COLORS["success"],
                "warning": self.COLORS["warning"],
                "danger": self.COLORS["danger"]
            }
            color = colors.get(alert["type"], self.COLORS["fg"])
            
            # Indicateur
            indicator = tk.Frame(alert_frame, bg=color, width=4)
            indicator.pack(side="left", fill="y")
            
            # Titre
            title = tk.Label(alert_frame, text=alert["title"],
                           font=("Segoe UI", 10, "bold"),
                           bg=self.COLORS["secondary"],
                           fg=color,
                           padx=10,
                           pady=5)
            title.pack(side="left")
            
            # Message
            msg = tk.Label(alert_frame, text=alert["message"],
                          font=("Segoe UI", 10),
                          bg=self.COLORS["secondary"],
                          fg=self.COLORS["text_secondary"],
                          padx=10,
                          pady=5)
            msg.pack(side="left")
    
    # ==================== Méthodes réseau ====================
    
    def test_network(self):
        """Teste la connexion réseau."""
        self.lbl_connection_status.config(text="Test en cours...")
        
        def test():
            result = NetworkTools.check_internet_connection()
            self.root.after(0, lambda: self._update_network_result(result))
        
        thread = threading.Thread(target=test, daemon=True)
        thread.start()
    
    def _update_network_result(self, result):
        """Met à jour l'affichage du résultat réseau."""
        if result["connected"]:
            self.lbl_connection_status.config(
                text="Connecté",
                fg=self.COLORS["success"])
            self.lbl_response_time.config(
                text=f"{result['response_time']} ms")
        else:
            self.lbl_connection_status.config(
                text="Non connecté",
                fg=self.COLORS["danger"])
            self.lbl_response_time.config(text="---")
        
        # IP locale
        local_ip = NetworkTools.get_local_ip()
        self.lbl_local_ip.config(text=local_ip if local_ip else "N/A")
    
    def flush_dns(self):
        """Vide le cache DNS."""
        self.logger.info("Demande de vidage du cache DNS")
        
        def flush():
            result = NetworkTools.flush_dns()
            self.root.after(0, lambda: self._show_dns_result(result))
        
        thread = threading.Thread(target=flush, daemon=True)
        thread.start()
    
    def _show_dns_result(self, result):
        """Affiche le résultat du flush DNS."""
        if result["success"]:
            messagebox.showinfo("CoreCheck", result["message"])
            self.logger.success("Cache DNS vidé")
        else:
            messagebox.showwarning("CoreCheck", result["message"])
            self.logger.warning("Erreur lors du vidage du cache DNS")
    
    # ==================== Méthodes actions ====================
    
    def update_temp_size(self):
        """Met à jour la taille des fichiers temporaires."""
        try:
            size_info = Cleaner.get_temp_size()
            self.lbl_temp_size.config(
                text=f"Taille fichiers temporaires: {size_info['size_mb']:.2f} Mo ({size_info['file_count']} fichiers)")
        except Exception:
            self.lbl_temp_size.config(text="Taille fichiers temporaires: ---")
    
    def clean_temp(self):
        """Nettoie les fichiers temporaires."""
        self.logger.info("Démarrage du nettoyage des fichiers temporaires")
        self.progress_clean["value"] = 0
        self.lbl_status.config(text="Nettoyage en cours...")
        
        def clean():
            result = Cleaner.clean_temp_files(
                progress_callback=lambda p: self.root.after(0, lambda: self.progress_clean.__setitem__("value", p))
            )
            self.root.after(0, lambda: self._show_clean_result(result))
        
        thread = threading.Thread(target=clean, daemon=True)
        thread.start()
    
    def _show_clean_result(self, result):
        """Affiche le résultat du nettoyage."""
        self.progress_clean["value"] = 100
        self.lbl_status.config(text="Prêt")
        
        if result["success"]:
            msg = f"Fichiers supprimés: {result['files_deleted']}\nEspace libéré: {result['space_freed']} Mo"
            messagebox.showinfo("CoreCheck", msg)
            self.logger.success(f"Nettoyage terminé: {result['files_deleted']} fichiers, {result['space_freed']} Mo")
        else:
            messagebox.showwarning("CoreCheck", "Erreur lors du nettoyage")
            self.logger.error("Erreur lors du nettoyage")
        
        self.update_temp_size()
    
    def open_task_manager(self):
        """Ouvre le gestionnaire des tâches."""
        if Cleaner.open_task_manager():
            self.logger.info("Gestionnaire des tâches ouvert")
    
    def open_network_settings(self):
        """Ouvre les paramètres réseau."""
        if Cleaner.open_network_settings():
            self.logger.info("Paramètres réseau ouverts")
    
    def open_control_panel(self):
        """Ouvre le panneau de configuration."""
        if Cleaner.open_control_panel():
            self.logger.info("Panneau de configuration ouvert")
    
    def open_device_manager(self):
        """Ouvre le gestionnaire de périphériques."""
        if Cleaner.open_device_manager():
            self.logger.info("Gestionnaire de périphériques ouvert")
    
    def open_system_properties(self):
        """Ouvre les propriétés système."""
        if Cleaner.open_system_properties():
            self.logger.info("Propriétés système ouvertes")
    
    # ==================== Méthodes processus ====================
    
    def refresh_processes(self):
        """Rafraîchit la liste des processus."""
        self.entry_search.delete(0, tk.END)
        self._load_processes(ProcessManager.get_all_processes(sort_by="cpu"))
    
    def search_processes(self):
        """Recherche des processus."""
        query = self.entry_search.get().strip()
        if query:
            results = ProcessManager.search_processes(query)
            self._load_processes(results)
        else:
            self.refresh_processes()
    
    def _load_processes(self, processes: list):
        """Charge les processus dans le Treeview."""
        # Effacer l'ancien contenu
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Ajouter les processus (limiter à 100 pour la performance)
        for proc in processes[:100]:
            try:
                self.process_tree.insert("", "end", values=(
                    proc.get("pid", ""),
                    proc.get("name", ""),
                    f"{proc.get('cpu', 0):.1f}",
                    f"{proc.get('memory', 0):.1f}",
                    proc.get("status", "")
                ))
            except Exception:
                pass
        
        # Mettre à jour le compteur
        self.lbl_process_count.config(
            text=f"Nombre de processus: {len(processes)}")
    
    def kill_selected_process(self):
        """Tue le processus sélectionné."""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("CoreCheck", "Sélectionnez un processus à terminer")
            return
        
        item = self.process_tree.item(selection[0])
        values = item["values"]
        pid = values[0]
        name = values[1]
        
        # Confirmer
        if not messagebox.askyesno("CoreCheck",
                                   f"Voulez-vous terminer le processus '{name}' (PID: {pid})?"):
            return
        
        result = ProcessManager.kill_process(pid)
        
        if result["success"]:
            messagebox.showinfo("CoreCheck", result["message"])
            self.logger.success(result["message"])
        else:
            messagebox.showerror("CoreCheck", result["message"])
            self.logger.error(result["message"])
        
        self.refresh_processes()
    
    # ==================== Méthodes logs ====================
    
    def update_logs(self):
        """Met à jour l'affichage des logs."""
        logs = self.logger.get_logs()
        
        # Effacer et réécrire
        self.log_text.delete("1.0", tk.END)
        for log in logs:
            self.log_text.insert(tk.END, log + "\n")
        
        # Scroll vers le bas
        self.log_text.see(tk.END)
    
    def clear_logs(self):
        """Efface les logs."""
        self.logger.clear_logs()
        self.log_text.delete("1.0", tk.END)
        self.logger.info("Logs effacés")
    
    def export_logs(self):
        """Exporte les logs vers un fichier."""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Fichiers log", "*.log"), ("Tous les fichiers", "*.*")],
            initialfile=f"corecheck_logs_{time.strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    logs = self.logger.get_logs()
                    f.write("\n".join(logs))
                messagebox.showinfo("CoreCheck", f"Logs exportés vers:\n{file_path}")
                self.logger.success(f"Logs exportés vers {file_path}")
            except Exception as e:
                messagebox.showerror("CoreCheck", f"Erreur lors de l'export:\n{str(e)}")
    
    # ==================== Méthodes de gestion ====================
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application."""
        self.update_running = False
        self.logger.info("Application CoreCheck fermée")
        self.root.destroy()


def launch_ui():
    """Lance l'interface graphique."""
    root = tk.Tk()
    app = CoreCheckUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_ui()