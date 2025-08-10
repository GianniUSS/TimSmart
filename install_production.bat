@echo off
title TIGOTA Sistema Timbratura - Installer Produzione
color 0A

echo.
echo  ████████╗██╗ ██████╗  ██████╗ ████████╗ █████╗ 
echo  ╚══██╔══╝██║██╔════╝ ██╔═══██╗╚══██╔══╝██╔══██╗
echo     ██║   ██║██║  ███╗██║   ██║   ██║   ███████║
echo     ██║   ██║██║   ██║██║   ██║   ██║   ██╔══██║
echo     ██║   ██║╚██████╔╝╚██████╔╝   ██║   ██║  ██║
echo     ╚═╝   ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝
echo.
echo          Sistema di Timbratura Aziendale
echo               Installer Produzione v3.1
echo.
echo ================================================================
echo.

REM Verifica privilegi amministratore
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Privilegi amministratore: OK
) else (
    echo [!] ATTENZIONE: Privilegi amministratore non rilevati
    echo     Alcune operazioni potrebbero fallire
    echo.
    pause
)

REM Verifica Python
echo [1/7] Verifica Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Python installato: OK
    python --version
) else (
    echo [✗] Python NON trovato!
    echo     Scaricare e installare Python 3.8+ da python.org
    pause
    exit /b 1
)

REM Installa dipendenze
echo.
echo [2/7] Installazione dipendenze Python...
echo Aggiornamento pip...
python -m pip install --upgrade pip

echo Installazione requirements...
python -m pip install -r requirements.txt
if %errorLevel% == 0 (
    echo [✓] Dipendenze installate: OK
) else (
    echo [✗] Errore installazione dipendenze
    pause
    exit /b 1
)

REM Esegue installer Python
echo.
echo [3/7] Esecuzione installer principale...
python installer.py
if %errorLevel% == 0 (
    echo [✓] Installer principale: OK
) else (
    echo [✗] Errore installer principale
    pause
    exit /b 1
)

REM Crea script di avvio quick
echo.
echo [4/7] Creazione script avvio rapido...
echo @echo off > start_tigota_quick.bat
echo title TIGOTA Sistema Timbratura >> start_tigota_quick.bat
echo cd /d "%~dp0" >> start_tigota_quick.bat
echo python production_launcher.py >> start_tigota_quick.bat
echo pause >> start_tigota_quick.bat
echo [✓] Script avvio rapido creato

REM Crea script di test
echo.
echo [5/7] Creazione script di test...
echo @echo off > test_system.bat
echo title TIGOTA - Test Sistema >> test_system.bat
echo echo Testando sistema TIGOTA... >> test_system.bat
echo python -c "import sys; print('Python:', sys.version)" >> test_system.bat
echo python -c "import tkinter; print('Tkinter: OK')" >> test_system.bat
echo python -c "from datetime import datetime; print('DateTime: OK')" >> test_system.bat
echo echo. >> test_system.bat
echo echo Test completato! >> test_system.bat
echo pause >> test_system.bat
echo [✓] Script di test creato

REM Configurazione Windows
echo.
echo [6/7] Configurazione sistema Windows...

REM Disabilita screensaver
powercfg /change standby-timeout-ac 0 >nul 2>&1
powercfg /change standby-timeout-dc 0 >nul 2>&1
powercfg /change monitor-timeout-ac 0 >nul 2>&1
powercfg /change monitor-timeout-dc 0 >nul 2>&1
echo [✓] Screensaver e sleep disabilitati

REM Crea task scheduler per avvio automatico
schtasks /create /tn "TIGOTA_Autostart" /tr "%CD%\start_tigota_quick.bat" /sc onlogon /rl highest /f >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Task avvio automatico creato
) else (
    echo [!] Task avvio automatico: Errore (normale se non admin)
)

REM Finalizzazione
echo.
echo [7/7] Finalizzazione installazione...

REM Crea file di configurazione finale
echo {> config_quick.json
echo   "installation_date": "%date% %time%",>> config_quick.json
echo   "version": "3.1.0",>> config_quick.json
echo   "environment": "production",>> config_quick.json
echo   "auto_configured": true>> config_quick.json
echo }>> config_quick.json
echo [✓] Configurazione finale salvata

echo.
echo ================================================================
echo                    INSTALLAZIONE COMPLETATA!
echo ================================================================
echo.
echo [✓] Sistema TIGOTA installato con successo
echo [✓] Configurazione produzione attiva
echo [✓] Script di avvio e test creati
echo.
echo PROSSIMI PASSI:
echo 1. Collegare lettore NFC/RFID
echo 2. Eseguire: test_system.bat
echo 3. Avviare sistema: start_tigota_quick.bat
echo 4. Configurare badge dipendenti
echo.
echo FILE UTILI CREATI:
echo • start_tigota_quick.bat  - Avvio rapido sistema
echo • test_system.bat         - Test componenti
echo • PRODUCTION_MANUAL.md    - Manuale completo
echo • DEPLOYMENT_GUIDE.md     - Guida deployment
echo.
echo SUPPORTO TECNICO:
echo • Email: support@tigota.it
echo • Documentazione: README.md
echo • Logs: C:\ProgramData\TIGOTA_Timbratura\logs\
echo.
echo ================================================================
echo          TIGOTA Sistema Timbratura pronto per l'uso!
echo ================================================================
echo.
pause

REM Opzione avvio immediato
echo.
set /p choice="Vuoi avviare il sistema ora? (S/n): "
if /i "%choice%"=="s" (
    echo.
    echo Avvio sistema TIGOTA...
    start "" "start_tigota_quick.bat"
) else if /i "%choice%"=="" (
    echo.
    echo Avvio sistema TIGOTA...
    start "" "start_tigota_quick.bat"
)

echo.
echo Installazione terminata. Arrivederci!
timeout /t 3 >nul
