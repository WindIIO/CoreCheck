"""
Module de nettoyage pour CoreCheck.
Nettoie les fichiers temporaires et libère de l'espace disque.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List


class Cleaner:
    """Classe pour le nettoyage du système."""
    
    # Dossiers temporaires à nettoyer
    TEMP_FOLDERS = [
        os.environ.get('TEMP', ''),
        os.environ.get('TMP', ''),
        r"C:\Windows\Temp",
    ]
    
    @staticmethod
    def get_temp_size() -> Dict[str, Any]:
        """Calcule la taille totale des fichiers temporaires.
        
        Returns:
            Dict avec la taille et le nombre de fichiers
        """
        total_size = 0
        file_count = 0
        
        for temp_folder in Cleaner.TEMP_FOLDERS:
            if temp_folder and os.path.exists(temp_folder):
                try:
                    for root, dirs, files in os.walk(temp_folder):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                            except Exception:
                                pass
                except Exception:
                    pass
        
        return {
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "size_gb": round(total_size / (1024 * 1024 * 1024), 2),
            "file_count": file_count
        }
    
    @staticmethod
    def clean_temp_files(progress_callback=None) -> Dict[str, Any]:
        """Nettoie les fichiers temporaires.
        
        Args:
            progress_callback: Fonction de callback pour la progression
            
        Returns:
            Dict avec le résultat du nettoyage
        """
        result = {
            "success": False,
            "files_deleted": 0,
            "space_freed": 0,
            "errors": []
        }
        
        total_size = 0
        files_deleted = 0
        
        folders = Cleaner.TEMP_FOLDERS
        total_folders = len(folders)
        
        for i, temp_folder in enumerate(folders):
            if not temp_folder or not os.path.exists(temp_folder):
                continue
            
            try:
                # Compter les fichiers avant
                file_count = 0
                for root, dirs, files in os.walk(temp_folder):
                    file_count += len(files)
                
                # Supprimer les fichiers
                for root, dirs, files in os.walk(temp_folder):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            # Essayer de supprimer le fichier
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            total_size += size
                            files_deleted += 1
                            
                            if progress_callback:
                                progress_callback(i / total_folders * 100)
                                
                        except Exception as e:
                            # Ignorer les fichiers verrouillés
                            pass
                    
                    # Supprimer les dossiers vides
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        try:
                            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                                os.rmdir(dir_path)
                        except Exception:
                            pass
                            
            except Exception as e:
                result["errors"].append(f"Erreur dans {temp_folder}: {str(e)}")
        
        result["success"] = True
        result["files_deleted"] = files_deleted
        result["space_freed"] = round(total_size / (1024 * 1024), 2)  # en MB
        
        return result
    
    @staticmethod
    def clean_browser_cache(browser: str = "all") -> Dict[str, Any]:
        """Nettoie le cache des navigateurs.
        
        Args:
            browser: Nom du navigateur ('chrome', 'firefox', 'edge', 'all')
            
        Returns:
            Dict avec le résultat
        """
        result = {
            "success": False,
            "message": ""
        }
        
        # Chemins des caches navigateur
        browser_caches = {
            "chrome": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
            "firefox": os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles"),
            "edge": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache")
        }
        
        if browser == "all":
            browsers = list(browser_caches.keys())
        else:
            browsers = [browser] if browser in browser_caches else []
        
        total_cleaned = 0
        
        for br in browsers:
            cache_path = browser_caches.get(br)
            if cache_path and os.path.exists(cache_path):
                try:
                    size = 0
                    for root, dirs, files in os.walk(cache_path):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                size += os.path.getsize(file_path)
                                os.remove(file_path)
                            except Exception:
                                pass
                    total_cleaned += size
                except Exception:
                    pass
        
        result["success"] = True
        result["message"] = f"Cache nettoyé: {round(total_cleaned / (1024 * 1024), 2)} Mo"
        
        return result
    
    @staticmethod
    def open_task_manager() -> bool:
        """Ouvre le gestionnaire des tâches Windows.
        
        Returns:
            True si réussi
        """
        try:
            subprocess.Popen("taskmgr")
            return True
        except Exception:
            return False
    
    @staticmethod
    def open_network_settings() -> bool:
        """Ouvre les paramètres réseau Windows.
        
        Returns:
            True si réussi
        """
        try:
            subprocess.Popen("ncpa.cpl")
            return True
        except Exception:
            return False
    
    @staticmethod
    def open_control_panel() -> bool:
        """Ouvre le panneau de configuration.
        
        Returns:
            True si réussi
        """
        try:
            subprocess.Popen("control")
            return True
        except Exception:
            return False
    
    @staticmethod
    def open_device_manager() -> bool:
        """Ouvre le gestionnaire de périphériques.
        
        Returns:
            True si réussi
        """
        try:
            subprocess.Popen("devmgmt.msc")
            return True
        except Exception:
            return False
    
    @staticmethod
    def open_system_properties() -> bool:
        """Ouvre les propriétés système.
        
        Returns:
            True si réussi
        """
        try:
            subprocess.Popen("sysdm.cpl")
            return True
        except Exception:
            return False