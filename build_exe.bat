@echo off
chcp 65001 >nul
title CoreCheck - Créer l'exécutable

echo ========================================
echo   CoreCheck - Créateur d'exécutable
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé
    pause
    exit /b 1
)

echo Installation de PyInstaller si nécessaire...
pip install pyinstaller

echo.
echo Création de l'exécutable...
echo.

REM Créer l'exécutable
pyinstaller --onefile --windowed --name CoreCheck --add-data "logs;logs" main.py

echo.
echo ========================================
echo   Opération terminée!
echo ========================================
echo.
echo L'exécutable se trouve dans le dossier dist/
echo.
pause