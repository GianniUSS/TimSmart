@echo off
echo.
echo ===========================================
echo    🏪 TIGOTÀ Elite - Store Configuration
echo       SISTEMA TIMBRATURA PERSONALIZZATO
echo ===========================================
echo.

REM Controlla se esiste il file di configurazione
if exist "config_negozio.ini" (
    echo ✅ File configurazione trovato
    
    REM Leggi il numero del negozio dal file
    for /f "tokens=2 delims== " %%a in ('findstr "numero" config_negozio.ini 2^>nul') do set STORE_NUM=%%a
    
    if defined STORE_NUM (
        echo 🏪 Store configurato: %%STORE_NUM%%
    ) else (
        echo 🏪 Store: Configurazione di default
    )
) else (
    echo ⚠️  File configurazione non trovato
    echo 📝 Verrà usata configurazione di default (Store 001)
    echo.
    echo 💡 Per personalizzare il negozio:
    echo    1. Crea il file config_negozio.ini
    echo    2. Imposta il numero del negozio
    echo    3. Riavvia l'applicazione
)

echo.
echo 🔄 Avvio applicazione...
timeout /t 2 /nobreak >nul

REM Controlla se l'eseguibile esiste
if exist "dist\TIGOTA_Elite_Store_v12.exe" (
    start "" "dist\TIGOTA_Elite_Store_v12.exe"
    echo ✅ TIGOTÀ Elite avviato con successo!
) else (
    echo ❌ Eseguibile non trovato: dist\TIGOTA_Elite_Store_v12.exe
    echo 🔧 Assicurati che l'eseguibile sia stato compilato
    echo.
    echo 📂 File necessari:
    echo    - dist\TIGOTA_Elite_Store_v12.exe
    echo    - config_negozio.ini (opzionale)
    pause
    exit /b 1
)

echo.
echo 📁 Database: C:\ProgramData\TIGOTA_Timbratura\
echo 🔒 Backup automatici attivi
echo 🏪 Configurazione negozio personalizzabile
echo.
echo Premi un tasto per chiudere questa finestra...
pause >nul
