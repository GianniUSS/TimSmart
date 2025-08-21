@echo off
echo ========================================
echo    TIGOTA SmartTIM - Reset Database
echo ========================================
echo.
echo Scegli un'opzione:
echo 1. Reset completo (cancella dipendenti e timbrature)
echo 2. Mantieni anagrafica (cancella solo timbrature)
echo 3. Aiuto
echo 4. Esci
echo.
set /p scelta="Inserisci il numero (1-4): "

if "%scelta%"=="1" goto reset_completo
if "%scelta%"=="2" goto mantieni_anagrafica
if "%scelta%"=="3" goto aiuto
if "%scelta%"=="4" goto esci
echo Scelta non valida!
pause
goto :eof

:reset_completo
echo.
echo ATTENZIONE: Questa operazione cancellera' TUTTI i dipendenti e le timbrature!
set /p conferma="Sei sicuro? (s/N): "
if /i not "%conferma%"=="s" goto annullato
echo.
echo Eseguendo reset completo...
AzzeraDatabase.exe
echo.
pause
goto :eof

:mantieni_anagrafica
echo.
echo Questa operazione manterra' i dipendenti ma cancellera' le timbrature e i badge.
set /p conferma="Continuare? (s/N): "
if /i not "%conferma%"=="s" goto annullato
echo.
echo Eseguendo reset con mantenimento anagrafica...
AzzeraDatabase.exe --mantieni-anagrafica
echo.
pause
goto :eof

:aiuto
echo.
AzzeraDatabase.exe --help
echo.
pause
goto :eof

:annullato
echo.
echo Operazione annullata.
echo.
pause
goto :eof

:esci
echo.
echo Arrivederci!
timeout /t 1 /nobreak >nul
