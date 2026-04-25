"""
Module d'informations système pour CoreCheck.
Récupère les informations sur le CPU, RAM, disque, etc.
"""

import psutil
import platform
import socket
from typing import Dict, Any


class SystemInfo:
    """Classe pour récupérer les informations système."""
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Retourne l'utilisation du CPU en pourcentage.
        
        Returns:
            Pourcentage d'utilisation du CPU (0-100)
        """
        return psutil.cpu_percent(interval=0.1)
    
    @staticmethod
    def get_cpu_count() -> int:
        """Retourne le nombre de cœurs CPU.
        
        Returns:
            Nombre de cœurs
        """
        return psutil.cpu_count()
    
    @staticmethod
    def get_cpu_freq() -> str:
        """Retourne la fréquence CPU actuelle.
        
        Returns:
            Fréquence CPU formatée
        """
        try:
            freq = psutil.cpu_freq()
            if freq:
                return f"{freq.current:.0f} MHz"
        except Exception:
            pass
        return "N/A"
    
    @staticmethod
    def get_ram_usage() -> Dict[str, Any]:
        """Retourne les informations de RAM.
        
        Returns:
            Dict avec total, disponible, utilisé (en Go) et pourcentage
        """
        mem = psutil.virtual_memory()
        return {
            "total": round(mem.total / (1024**3), 2),
            "available": round(mem.available / (1024**3), 2),
            "used": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        }
    
    @staticmethod
    def get_disk_usage() -> Dict[str, Any]:
        """Retourne les informations sur le disque principal.
        
        Returns:
            Dict avec total, disponible, utilisé (en Go) et pourcentage
        """
        try:
            # Récupérer le disque système (généralement C:)
            disk = psutil.disk_usage('C:\\')
            return {
                "total": round(disk.total / (1024**3), 2),
                "free": round(disk.free / (1024**3), 2),
                "used": round(disk.used / (1024**3), 2),
                "percent": disk.percent
            }
        except Exception:
            # Essayer d'autres lettres de lecteur
            for letter in ['D:', 'E:', 'F:']:
                try:
                    disk = psutil.disk_usage(letter)
                    if disk.total > 0:
                        return {
                            "total": round(disk.total / (1024**3), 2),
                            "free": round(disk.free / (1024**3), 2),
                            "used": round(disk.used / (1024**3), 2),
                            "percent": disk.percent
                        }
                except Exception:
                    continue
            
            return {
                "total": 0,
                "free": 0,
                "used": 0,
                "percent": 0
            }
    
    @staticmethod
    def get_computer_name() -> str:
        """Retourne le nom de l'ordinateur.
        
        Returns:
            Nom de l'ordinateur
        """
        return socket.gethostname()
    
    @staticmethod
    def get_os_info() -> Dict[str, str]:
        """Retourne les informations du système d'exploitation.
        
        Returns:
            Dict avec les informations OS
        """
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
    
    @staticmethod
    def get_all_info() -> Dict[str, Any]:
        """Retourne toutes les informations système.
        
        Returns:
            Dict avec toutes les informations
        """
        ram = SystemInfo.get_ram_usage()
        disk = SystemInfo.get_disk_usage()
        os_info = SystemInfo.get_os_info()
        
        return {
            "cpu": {
                "usage": SystemInfo.get_cpu_usage(),
                "count": SystemInfo.get_cpu_count(),
                "freq": SystemInfo.get_cpu_freq()
            },
            "ram": ram,
            "disk": disk,
            "computer_name": SystemInfo.get_computer_name(),
            "os": f"{os_info['system']} {os_info['release']}",
            "os_version": os_info['version']
        }
    
    @staticmethod
    def check_system_health() -> Dict[str, Any]:
        """Analyse rapide de l'état du système.
        
        Returns:
            Dict avec les alertes et recommandations
        """
        alerts = []
        
        # Vérifier l'espace disque
        disk = SystemInfo.get_disk_usage()
        if disk["percent"] > 90:
            alerts.append({
                "type": "danger",
                "title": "Espace disque critique",
                "message": f"Disque à {disk['percent']}% -仅有 {disk['free']:.1f} Go disponibles"
            })
        elif disk["percent"] > 80:
            alerts.append({
                "type": "warning",
                "title": "Espace disque faible",
                "message": f"Disque à {disk['percent']}% - {disk['free']:.1f} Go disponibles"
            })
        
        # Vérifier la RAM
        ram = SystemInfo.get_ram_usage()
        if ram["percent"] > 90:
            alerts.append({
                "type": "danger",
                "title": "RAM saturée",
                "message": f"Mémoire à {ram['percent']}% -仅有 {ram['available']:.1f} Go disponibles"
            })
        elif ram["percent"] > 80:
            alerts.append({
                "type": "warning",
                "title": "RAM élevée",
                "message": f"Mémoire à {ram['percent']}% - {ram['available']:.1f} Go disponibles"
            })
        
        # Vérifier le CPU
        cpu = SystemInfo.get_cpu_usage()
        if cpu > 90:
            alerts.append({
                "type": "danger",
                "title": "CPU très élevé",
                "message": f"Utilisation CPU à {cpu}%"
            })
        elif cpu > 80:
            alerts.append({
                "type": "warning",
                "title": "CPU élevé",
                "message": f"Utilisation CPU à {cpu}%"
            })
        
        # Si tout va bien
        if not alerts:
            alerts.append({
                "type": "success",
                "title": "Système sain",
                "message": "Tous les paramètres sont normaux"
            })
        
        return {
            "alerts": alerts,
            "disk": disk,
            "ram": ram,
            "cpu": cpu
        }