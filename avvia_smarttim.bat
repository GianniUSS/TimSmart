@echo off
echo ================================================
echo SmartTIM - Sistema di Timbratura
echo Avvio applicazione...
echo ================================================

REM Cambia directory al percorso dello script
cd /d "%~dp0"

REM Verifica che Python sia installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non e' installato o non e' nel PATH
    echo Scarica Python da: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Avvia l'applicazione
python start_app.py

REM In caso di errore, mantieni la finestra aperta
if errorlevel 1 (
    echo.
    echo Si e' verificato un errore. Premere un tasto per chiudere.
    pause
)
