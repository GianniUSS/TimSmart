@echo off
echo ================================================
echo TIGOTA - Sistema di Timbratura
echo Avvio applicazione TIGOTA...
echo ================================================
echo.
echo Belli, Puliti, Profumati
echo.

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

echo Avvio dell'app TIGOTA...
echo.

REM Prova prima la versione grafica avanzata
E:/Progetti/ProgettoSmartTIM/.venv/Scripts/python.exe app_timbratura_grafica.py

REM Se fallisce, prova la versione standard
if errorlevel 1 (
    echo.
    echo Tentativo con versione standard...
    E:/Progetti/ProgettoSmartTIM/.venv/Scripts/python.exe app_timbratura_tigota.py
)

REM In caso di errore, mantieni la finestra aperta
if errorlevel 1 (
    echo.
    echo Si e' verificato un errore. Premere un tasto per chiudere.
    pause
)
