"""
CoreCheck - Application de Support Informatique pour Windows
Point d'entrée de l'application
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer l'interface
from ui import launch_ui

if __name__ == "__main__":
    print("=" * 50)
    print("  CoreCheck - Support Informatique")
    print("  Version 1.0.0")
    print("=" * 50)
    print()
    print("Démarrage de l'application...")
    print()
    
    try:
        launch_ui()
    except Exception as e:
        print(f"Erreur lors du démarrage: {e}")
        input("Appuyez sur Entrée pour quitter...")