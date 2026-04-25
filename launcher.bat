@echo off
chcp 65001 >nul
title CoreCheck - Support Informatique

echo ========================================
echo   CoreCheck - Support Informatique
echo   Version 1.0.0
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python 3.7+ depuis https://www.python.org/
    pause
    exit /b 1
)

REM Vérifier si psutil est installé
python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo Installation de psutil...
    pip install psutil
    if errorlevel 1 (
        echo ERREUR: Impossible d'installer psutil
        pause
        exit /b 1
    )
)

echo Lancement de CoreCheck...
echo.

REM Lancer l'application
python "%~dp0main.py"

if errorlevel 1 (
    echo.
    echo Une erreur s'est produite. Appuyez sur une touche pour quitter...
    pause >nul
)