"""
Module de gestion des processus pour CoreCheck.
Affiche et gère les processus actifs.
"""

import psutil
from typing import Dict, Any, List, Optional


class ProcessManager:
    """Classe pour gérer les processus système."""
    
    @staticmethod
    def get_all_processes(sort_by: str = "cpu") -> List[Dict[str, Any]]:
        """Retourne la liste de tous les processus.
        
        Args:
            sort_by: Critère de tri ('cpu', 'memory', 'name')
            
        Returns:
            Liste des processus avec leurs informations
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                # Récupérer les informations de base
                info = proc.info
                
                # Ajouter des champs supplémentaires
                try:
                    info['cpu'] = info.get('cpu_percent', 0) or 0
                    info['memory'] = info.get('memory_percent', 0) or 0
                    info['status'] = info.get('status', 'unknown')
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                
                processes.append(info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Trier les processus
        if sort_by == "cpu":
            processes.sort(key=lambda x: x.get('cpu', 0), reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x.get('memory', 0), reverse=True)
        elif sort_by == "name":
            processes.sort(key=lambda x: x.get('name', '').lower())
        
        return processes
    
    @staticmethod
    def get_process_by_pid(pid: int) -> Optional[Dict[str, Any]]:
        """Retourne les informations d'un processus par son PID.
        
        Args:
            pid: ID du processus
            
        Returns:
            Dict avec les informations du processus ou None
        """
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'cpu': proc.cpu_percent(interval=0.1),
                'memory': proc.memory_info().rss / (1024 * 1024),  # en MB
                'status': proc.status(),
                'create_time': proc.create_time(),
                'num_threads': proc.num_threads(),
                'username': proc.username()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    @staticmethod
    def kill_process(pid: int) -> Dict[str, Any]:
        """Termine un processus.
        
        Args:
            pid: ID du processus à terminer
            
        Returns:
            Dict avec le résultat de l'opération
        """
        result = {
            "success": False,
            "message": ""
        }
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()  # Envoyer SIGTERM
            
            # Attendre un peu et vérifier si le processus est terminé
            try:
                proc.wait(timeout=3)
                result["success"] = True
                result["message"] = f"Processus {proc.name()} (PID: {pid}) terminé avec succès"
            except psutil.TimeoutExpired:
                # Forcer l'arrêt si le processus ne répond pas
                proc.kill()
                result["success"] = True
                result["message"] = f"Processus {proc.name()} (PID: {pid}) forcé à s'arrêter"
                
        except psutil.NoSuchProcess:
            result["message"] = f"Processus {pid} non trouvé"
        except psutil.AccessDenied:
            result["message"] = f"Accès refusé pour terminer le processus {pid}"
        except Exception as e:
            result["message"] = f"Erreur: {str(e)}"
        
        return result
    
    @staticmethod
    def get_system_processes() -> Dict[str, Any]:
        """Retourne un résumé des processus système.
        
        Returns:
            Dict avec les statistiques des processus
        """
        return {
            "total": len(psutil.pids()),
            "running": len([p for p in psutil.process_iter() if p.status() == psutil.STATUS_RUNNING]),
            "sleeping": len([p for p in psutil.process_iter() if p.status() == psutil.STATUS_SLEEPING])
        }
    
    @staticmethod
    def search_processes(query: str) -> List[Dict[str, Any]]:
        """Recherche des processus par nom.
        
        Args:
            query: Chaîne de recherche
            
        Returns:
            Liste des processus correspondants
        """
        query = query.lower()
        results = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if query in info.get('name', '').lower():
                    results.append({
                        'pid': info.get('pid'),
                        'name': info.get('name'),
                        'cpu': info.get('cpu_percent', 0) or 0,
                        'memory': info.get('memory_percent', 0) or 0
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return results
    
    @staticmethod
    def get_top_processes(limit: int = 10, by: str = "cpu") -> List[Dict[str, Any]]:
        """Retourne les principaux processus.
        
        Args:
            limit: Nombre de processus à retourner
            by: Critère de tri ('cpu', 'memory')
            
        Returns:
            Liste des processus principaux
        """
        processes = ProcessManager.get_all_processes(sort_by=by)
        return processes[:limit]
    
    @staticmethod
    def get_process_tree() -> Dict[int, List[int]]:
        """Retourne l'arbre des processus (PID -> enfants).
        
        Returns:
            Dict avec les processus parents et leurs enfants
        """
        tree = {}
        
        for proc in psutil.process_iter(['pid', 'ppid']):
            try:
                info = proc.info
                pid = info.get('pid')
                ppid = info.get('ppid')
                
                if ppid not in tree:
                    tree[ppid] = []
                tree[ppid].append(pid)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return tree