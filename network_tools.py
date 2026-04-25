"""
Module d'outils réseau pour CoreCheck.
Vérifie la connexion internet et effectue des tests réseau.
"""

import subprocess
import socket
import time
from typing import Dict, Any, Optional


class NetworkTools:
    """Classe pour les outils réseau."""
    
    # Serveurs de test pour le ping
    PING_TARGETS = ["8.8.8.8", "1.1.1.1", "google.com"]
    
    @staticmethod
    def check_internet_connection(timeout: int = 3) -> Dict[str, Any]:
        """Vérifie la connexion internet en effectuant un ping.
        
        Args:
            timeout: Timeout en secondes pour le ping
            
        Returns:
            Dict avec le statut, temps de réponse, etc.
        """
        result = {
            "connected": False,
            "response_time": None,
            "target": None,
            "error": None
        }
        
        for target in NetworkTools.PING_TARGETS:
            try:
                start_time = time.time()
                
                # Effectuer un ping
                process = subprocess.Popen(
                    ["ping", "-n", "1", "-w", str(timeout * 1000), target],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                
                stdout, stderr = process.communicate(timeout=timeout + 1)
                output = stdout.decode('utf-8', errors='ignore')
                
                response_time = time.time() - start_time
                
                # Vérifier si le ping a réussi
                if process.returncode == 0 and "TTL=" in output.upper():
                    result["connected"] = True
                    result["response_time"] = round(response_time * 1000, 2)  # en ms
                    result["target"] = target
                    break
                else:
                    result["error"] = "Pas de réponse"
                    
            except subprocess.TimeoutExpired:
                result["error"] = "Timeout"
                continue
            except Exception as e:
                result["error"] = str(e)
                continue
        
        return result
    
    @staticmethod
    def get_local_ip() -> Optional[str]:
        """Retourne l'adresse IP locale de la machine.
        
        Returns:
            Adresse IP locale ou None si non trouvée
        """
        try:
            # Créer un socket pour déterminer l'IP locale
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None
    
    @staticmethod
    def get_hostname() -> str:
        """Retourne le nom d'hôte de la machine.
        
        Returns:
            Nom d'hôte
        """
        return socket.gethostname()
    
    @staticmethod
    def flush_dns() -> Dict[str, Any]:
        """Vide le cache DNS.
        
        Returns:
            Dict avec le résultat de l'opération
        """
        result = {
            "success": False,
            "message": ""
        }
        
        try:
            # Exécuter la commande ipconfig /flushdns
            process = subprocess.Popen(
                ["ipconfig", "/flushdns"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            stdout, stderr = process.communicate(timeout=10)
            output = stdout.decode('utf-8', errors='ignore')
            
            if "succès" in output.lower() or "success" in output.lower():
                result["success"] = True
                result["message"] = "Cache DNS vidé avec succès"
            else:
                result["message"] = "Commande exécutée"
                
        except Exception as e:
            result["message"] = f"Erreur: {str(e)}"
        
        return result
    
    @staticmethod
    def get_network_adapters() -> list:
        """Retourne la liste des adaptateurs réseau.
        
        Returns:
            Liste des adaptateurs réseau
        """
        adapters = []
        
        try:
            # Utiliser psutil pour récupérer les interfaces réseau
            import psutil
            interfaces = psutil.net_if_stats()
            
            for interface, stats in interfaces.items():
                if stats.isup:  # Only show active interfaces
                    adapters.append({
                        "name": interface,
                        "status": "Actif" if stats.isup else "Inactif",
                        "speed": f"{stats.speed} Mbps" if stats.speed > 0 else "N/A"
                    })
                    
        except Exception as e:
            pass
        
        return adapters
    
    @staticmethod
    def ping_host(host: str, count: int = 4) -> Dict[str, Any]:
        """Ping un hôte spécifique.
        
        Args:
            host: Adresse IP ou nom d'hôte
            count: Nombre de ping à effectuer
            
        Returns:
            Dict avec les résultats du ping
        """
        result = {
            "host": host,
            "success": False,
            "packets_sent": count,
            "packets_received": 0,
            "min_time": None,
            "max_time": None,
            "avg_time": None,
            "error": None
        }
        
        try:
            process = subprocess.Popen(
                ["ping", "-n", str(count), host],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            stdout, stderr = process.communicate(timeout=count * 5)
            output = stdout.decode('utf-8', errors='ignore')
            
            if process.returncode == 0:
                result["success"] = True
                
                # Parser les résultats
                lines = output.split('\n')
                for line in lines:
                    if "perte" in line.lower() or "loss" in line.lower():
                        # Extraire les statistiques de perte
                        parts = line.split(',')
                        for part in parts:
                            if "reçu" in part.lower() or "received" in part.lower():
                                try:
                                    result["packets_received"] = int(''.join(filter(str.isdigit, part)))
                                except:
                                    pass
                    
                    if "minimum" in line.lower() or "minimum" in line.lower():
                        # Extraire les temps
                        try:
                            times = line.split('=')[-1].split(',')
                            result["min_time"] = float(times[0].strip().replace('ms', ''))
                            result["max_time"] = float(times[1].strip().replace('ms', ''))
                            result["avg_time"] = float(times[2].strip().replace('ms', ''))
                        except:
                            pass
                            
        except Exception as e:
            result["error"] = str(e)
        
        return result