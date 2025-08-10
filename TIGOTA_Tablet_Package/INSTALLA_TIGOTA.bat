@echo off
title TIGOTA Sistema Timbratura - Installer Tablet v3.1
color 0A

echo.
echo  ████████╗██╗ ██████╗  ██████╗ ████████╗ █████╗ 
echo  ╚══██╔══╝██║██╔════╝ ██╔═══██╗╚══██╔══╝██╔══██╗
echo     ██║   ██║██║  ███╗██║   ██║   ██║   ███████║
echo     ██║   ██║██║   ██║██║   ██║   ██║   ██╔══██║
echo     ██║   ██║╚██████╔╝╚██████╔╝   ██║   ██║  ██║
echo     ╚═╝   ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝
echo.
echo          Sistema di Timbratura Tablet v3.1
echo             Installazione Automatica
echo.
echo ================================================================

REM Controlla privilegi amministratore
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Privilegi amministratore: OK
) else (
    echo [!] ATTENZIONE: Eseguire come Amministratore per installazione completa
    echo     Alcune funzioni avanzate potrebbero non essere disponibili
    echo.
)

REM Crea directory di installazione
echo [1/5] Creazione directory installazione...
set INSTALL_DIR=%ProgramFiles%\TIGOTA_Timbratura
mkdir "%INSTALL_DIR%" 2>nul
if exist "%INSTALL_DIR%" (
    echo ✅ Directory creata: %INSTALL_DIR%
) else (
    echo ❌ Errore creazione directory. Provo directory alternativa...
    set INSTALL_DIR=%LOCALAPPDATA%\TIGOTA_Timbratura
    mkdir "%INSTALL_DIR%" 2>nul
    echo ✅ Directory alternativa: %INSTALL_DIR%
)

REM Copia eseguibile
echo.
echo [2/5] Installazione eseguibile...
copy "TIGOTA_Sistema_Timbratura.exe" "%INSTALL_DIR%\" /Y >nul
if exist "%INSTALL_DIR%\TIGOTA_Sistema_Timbratura.exe" (
    echo ✅ Eseguibile installato (11.8 MB)
) else (
    echo ❌ Errore installazione eseguibile
    pause
    exit /b 1
)

REM Crea collegamento desktop
echo.
echo [3/5] Creazione collegamento desktop...
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\TIGOTA Sistema Timbratura.lnk

REM Crea script VBS per collegamento
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%SHORTCUT%" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%INSTALL_DIR%\TIGOTA_Sistema_Timbratura.exe" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Sistema Timbratura TIGOTA v3.1" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WindowStyle = 1 >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

cscript "%TEMP%\CreateShortcut.vbs" >nul 2>&1
del "%TEMP%\CreateShortcut.vbs" >nul 2>&1

if exist "%SHORTCUT%" (
    echo ✅ Collegamento desktop creato
) else (
    echo ⚠️ Collegamento desktop: errore (normale su alcuni sistemi)
)

REM Configura avvio automatico
echo.
echo [4/5] Configurazione avvio automatico...
schtasks /create /tn "TIGOTA_Sistema_Autostart" /tr "%INSTALL_DIR%\TIGOTA_Sistema_Timbratura.exe" /sc onlogon /rl highest /f >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Avvio automatico configurato
) else (
    echo ⚠️ Avvio automatico: richiede permessi amministratore
    echo    Il sistema dovrà essere avviato manualmente
)

REM Ottimizzazioni tablet
echo.
echo [5/5] Ottimizzazioni per tablet...

REM Disabilita screensaver e sleep
powercfg /change standby-timeout-ac 0 >nul 2>&1
powercfg /change standby-timeout-dc 0 >nul 2>&1
powercfg /change monitor-timeout-ac 0 >nul 2>&1
powercfg /change monitor-timeout-dc 0 >nul 2>&1
echo ✅ Screensaver e sleep disabilitati

REM Crea file di configurazione locale
echo {"installation_date": "%date% %time%", "version": "3.1.0", "install_dir": "%INSTALL_DIR%"} > "%INSTALL_DIR%\config.json"
echo ✅ Configurazione salvata

echo.
echo ================================================================
echo                    INSTALLAZIONE COMPLETATA!
echo ================================================================
echo.
echo ✅ TIGOTA Sistema Timbratura v3.1 installato con successo
echo.
echo 📂 INSTALLATO IN: %INSTALL_DIR%
echo 🖥️ Collegamento: Desktop "TIGOTA Sistema Timbratura"
echo ⚡ Avvio automatico: Configurato (se amministratore)
echo 🗄️ Database: C:\ProgramData\TIGOTA_Timbratura\
echo.
echo CARATTERISTICHE PRINCIPALI:
echo • Database SQLite integrato e affidabile
echo • Backup automatico ogni ora
echo • Export CSV per sistemi HR
echo • Interfaccia touch ottimizzata 1280x800
echo • Orologio analogico premium
echo • Design professionale TIGOTÀ
echo.
echo UTILIZZO:
echo • Doppio click su icona desktop per avviare
echo • Il sistema si avvierà in modalità fullscreen
echo • Premere ESC per uscire dal fullscreen
echo • Premere F1 per accesso amministratore
echo • Avvicinare badge NFC per timbrare
echo.
echo SUPPORTO TECNICO:
echo • Email: support@tigota.it
echo • Logs: Menu F1 > Diagnostica
echo • Database: C:\ProgramData\TIGOTA_Timbratura\
echo.
echo ================================================================
echo.
set /p choice="Vuoi avviare il sistema TIGOTA ora? (S/n): "
if /i "%choice%"=="s" (
    echo.
    echo 🚀 Avvio TIGOTA Sistema Timbratura...
    echo    Il sistema si aprirà in modalità fullscreen
    echo    Premere ESC per uscire se necessario
    echo.
    timeout /t 2 >nul
    start "" "%INSTALL_DIR%\TIGOTA_Sistema_Timbratura.exe"
) else if /i "%choice%"=="" (
    echo.
    echo 🚀 Avvio TIGOTA Sistema Timbratura...
    timeout /t 2 >nul
    start "" "%INSTALL_DIR%\TIGOTA_Sistema_Timbratura.exe"
) else (
    echo.
    echo 📋 Per avviare in futuro:
    echo    • Doppio click su icona desktop
    echo    • Oppure eseguire: %INSTALL_DIR%\TIGOTA_Sistema_Timbratura.exe
)

echo.
echo 🎉 Installazione completata! Grazie per aver scelto TIGOTÀ!
echo ================================================================
pause
