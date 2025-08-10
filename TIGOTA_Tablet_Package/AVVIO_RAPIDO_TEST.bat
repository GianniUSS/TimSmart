@echo off
title TIGOTA - Avvio Rapido Test
echo.
echo 🚀 TIGOTA Sistema Timbratura - Test Rapido
echo ==========================================
echo.
echo Avvio del sistema in modalità test...
echo • Database SQLite integrato
echo • Modalità simulazione NFC attiva
echo • Premere SPAZIO per simulare badge
echo • Premere ESC per uscire
echo.
timeout /t 3 >nul

start "" "TIGOTA_Sistema_Timbratura.exe"

echo Sistema avviato!
echo Premere un tasto per chiudere questa finestra...
pause >nul
