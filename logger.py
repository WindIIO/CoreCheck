"""
Module de gestion des logs pour CoreCheck.
Enregistre les actions effectuées et les erreurs.
"""

import os
import datetime
from pathlib import Path


class Logger:
    """Gestionnaire de logs pour l'application."""
    
    def __init__(self, log_file: str = None):
        """Initialise le logger.
        
        Args:
            log_file: Chemin du fichier de log. Si None, utilise un fichier par défaut.
        """
        if log_file is None:
            # Créer le dossier logs s'il n'existe pas
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"corecheck_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        
        self.log_file = str(log_file)
        self.logs = []  # Liste des logs en mémoire pour l'affichage UI
        
    def log(self, message: str, level: str = "INFO"):
        """Enregistre un message de log.
        
        Args:
            message: Le message à enregistrer
            level: Niveau du log (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Ajouter à la liste en mémoire
        self.logs.append(log_entry)
        
        # Limiter à 100 entrées en mémoire
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        
        # Écrire dans le fichier
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Erreur lors de l'écriture du log: {e}")
    
    def info(self, message: str):
        """Enregistre un message INFO."""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Enregistre un message WARNING."""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Enregistre un message ERROR."""
        self.log(message, "ERROR")
    
    def success(self, message: str):
        """Enregistre un message SUCCESS."""
        self.log(message, "SUCCESS")
    
    def get_logs(self, count: int = None) -> list:
        """Récupère les logs.
        
        Args:
            count: Nombre de logs à récupérer. Si None, retourne tous les logs.
            
        Returns:
            Liste des logs
        """
        if count is None:
            return self.logs.copy()
        return self.logs[-count:]
    
    def clear_logs(self):
        """Efface les logs en mémoire."""
        self.logs.clear()
        self.info("Logs effacés")
    
    def get_log_file_path(self) -> str:
        """Retourne le chemin du fichier de log."""
        return self.log_file


# Instance globale du logger
_logger = None

def get_logger() -> Logger:
    """Retourne l'instance globale du logger."""
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger