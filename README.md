# CoreCheck - Application de Support Informatique

# Version: 1.0.0

# Date: Avril 2026

## Description

CoreCheck est une application de support informatique pour Windows qui permet de diagnostiquer rapidement un PC et d'effectuer certaines actions automatiques.

## Fonctionnalités

- **Informations système** : CPU, RAM, espace disque, nom du PC, OS
- **Test réseau** : Vérification connexion internet, temps de réponse
- **Analyse rapide** : Détection des problèmes (disque faible, RAM saturée, CPU élevé)
- **Actions rapides** : Nettoyer fichiers temporaires, gestionnaire des tâches, paramètres réseau, Flush DNS
- **Scan des processus** : Liste des processus actifs, tri par CPU, fermer un processus
- **Journal (logs)** : Historique des actions effectuées

## Installation

1. Assurez-vous d'avoir Python 3.7+ installé
2. Installez les dépendances :
   ```
   pip install psutil
   ```
3. Lancez l'application :
   - Double-cliquez sur `launcher.bat`
   - Ou via Python : `python main.py`

## Création de l'exécutable (optionnel)

Pour créer un fichier .exe :

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name CoreCheck main.py
```

L'exécutable sera dans le dossier `dist/`.

## Interface

L'application dispose d'une interface graphique moderne avec :

- Section Informations système
- Section Réseau
- Section Actions rapides
- Section Processus
- Section Logs
- Mode sombre
- Mise à jour automatique des stats (toutes les 2 secondes)

## Auteurs

- Développeur Python Senior

## Licence

MIT
