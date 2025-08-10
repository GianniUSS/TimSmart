# TIGOTÀ Sistema Timbratura - Build Script per EXE
# Crea eseguibile standalone per distribuzione tablet

import os
import sys
import shutil
from pathlib import Path

def build_tigota_exe():
    """Compila TIGOTÀ come eseguibile standalone"""
    
    print("🔨 TIGOTÀ - Build EXE per Tablet")
    print("="*50)
    
    # Verifica PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller disponibile")
    except ImportError:
        print("❌ PyInstaller non trovato. Installazione in corso...")
        os.system("pip install pyinstaller")
        
    # Directory di build
    build_dir = Path("./dist")
    build_dir.mkdir(exist_ok=True)
    
    # Specfile personalizzato per TIGOTÀ
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tigota_elite_dashboard.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config_tablet.py', '.'),
        ('database_sqlite.py', '.'),
        ('nfc_manager.py', '.'),
        ('requirements.txt', '.'),
        ('PRODUCTION_READY.md', '.'),
        ('DEPLOYMENT_GUIDE.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk', 
        'sqlite3',
        'json',
        'datetime',
        'threading',
        'hashlib',
        'csv',
        'pathlib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TIGOTA_Sistema_Timbratura',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='tigota_icon.ico' if os.path.exists('tigota_icon.ico') else None,
    version_file='version_info.txt' if os.path.exists('version_info.txt') else None,
)
'''
    
    # Salva spec file
    with open('tigota_tablet.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Spec file creato: tigota_tablet.spec")
    
    return True

def create_version_info():
    """Crea file informazioni versione per l'exe"""
    version_info = '''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(3,1,0,0),
    prodvers=(3,1,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'TIGOTÀ S.r.l.'),
        StringStruct(u'FileDescription', u'Sistema di Timbratura TIGOTÀ'),
        StringStruct(u'FileVersion', u'3.1.0.0'),
        StringStruct(u'InternalName', u'TIGOTA_Sistema_Timbratura'),
        StringStruct(u'LegalCopyright', u'© 2025 TIGOTÀ S.r.l.'),
        StringStruct(u'OriginalFilename', u'TIGOTA_Sistema_Timbratura.exe'),
        StringStruct(u'ProductName', u'TIGOTÀ Sistema Timbratura'),
        StringStruct(u'ProductVersion', u'3.1.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✅ Version info creato")

def compile_exe():
    """Compila l'eseguibile"""
    print("\n🔨 Compilazione in corso...")
    
    # Comando PyInstaller
    cmd = "pyinstaller --onefile --windowed --name TIGOTA_Sistema_Timbratura tigota_tablet.spec"
    
    print(f"Comando: {cmd}")
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Compilazione completata!")
        return True
    else:
        print("❌ Errore durante la compilazione")
        return False

def create_installer_package():
    """Crea pacchetto completo per installazione"""
    print("\n📦 Creazione pacchetto installazione...")
    
    # Directory pacchetto
    package_dir = Path("./TIGOTA_Tablet_Package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copia eseguibile
    exe_source = Path("./dist/TIGOTA_Sistema_Timbratura.exe")
    if exe_source.exists():
        shutil.copy2(exe_source, package_dir / "TIGOTA_Sistema_Timbratura.exe")
        print("✅ EXE copiato nel pacchetto")
    
    # Copia documentazione
    docs = [
        "PRODUCTION_READY.md",
        "DEPLOYMENT_GUIDE.md", 
        "PRODUCTION_MANUAL.md",
        "requirements.txt"
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy2(doc, package_dir)
            print(f"✅ {doc} copiato")
    
    # Crea installer batch semplificato
    installer_bat = '''@echo off
title TIGOTA Sistema Timbratura - Installer Tablet
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
echo               Installazione Rapida
echo.
echo ================================================================

REM Crea directory di installazione
set INSTALL_DIR=%ProgramFiles%\\TIGOTA_Timbratura
mkdir "%INSTALL_DIR%" 2>nul

REM Copia eseguibile
echo [1/4] Installazione eseguibile...
copy "TIGOTA_Sistema_Timbratura.exe" "%INSTALL_DIR%\\" /Y
if %errorLevel% == 0 (
    echo ✅ Eseguibile installato
) else (
    echo ❌ Errore installazione eseguibile
    pause
    exit /b 1
)

REM Crea shortcut sul desktop
echo [2/4] Creazione collegamento desktop...
set DESKTOP=%USERPROFILE%\\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\\TIGOTA Sistema Timbratura.lnk" >> "%TEMP%\\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.TargetPath = "%INSTALL_DIR%\\TIGOTA_Sistema_Timbratura.exe" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.Description = "Sistema Timbratura TIGOTA" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\\CreateShortcut.vbs"
cscript "%TEMP%\\CreateShortcut.vbs" >nul
del "%TEMP%\\CreateShortcut.vbs"
echo ✅ Collegamento desktop creato

REM Configura avvio automatico
echo [3/4] Configurazione avvio automatico...
schtasks /create /tn "TIGOTA_Autostart" /tr "%INSTALL_DIR%\\TIGOTA_Sistema_Timbratura.exe" /sc onlogon /rl highest /f >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Avvio automatico configurato
) else (
    echo ⚠️ Avvio automatico: richiede permessi amministratore
)

REM Disabilita screensaver
echo [4/4] Ottimizzazione tablet...
powercfg /change standby-timeout-ac 0 >nul 2>&1
powercfg /change monitor-timeout-ac 0 >nul 2>&1
echo ✅ Screensaver disabilitato

echo.
echo ================================================================
echo                    INSTALLAZIONE COMPLETATA!
echo ================================================================
echo.
echo ✅ TIGOTA Sistema Timbratura installato con successo
echo 📂 Installato in: %INSTALL_DIR%
echo 🖥️ Collegamento creato sul desktop
echo ⚡ Avvio automatico configurato
echo.
echo UTILIZZO:
echo • Doppio click sull'icona desktop per avviare
echo • Il sistema si avvierà automaticamente al login
echo • Premere ESC per uscire dalla modalità fullscreen
echo • Premere F1 per accesso amministratore
echo.
echo ================================================================
echo.
set /p choice="Vuoi avviare il sistema ora? (S/n): "
if /i "%choice%"=="s" (
    echo Avvio TIGOTA Sistema Timbratura...
    start "" "%INSTALL_DIR%\\TIGOTA_Sistema_Timbratura.exe"
) else if /i "%choice%"=="" (
    echo Avvio TIGOTA Sistema Timbratura...
    start "" "%INSTALL_DIR%\\TIGOTA_Sistema_Timbratura.exe"
)

echo.
echo Installazione completata. Grazie per aver scelto TIGOTA!
pause'''
    
    with open(package_dir / "INSTALLA_TIGOTA.bat", 'w', encoding='utf-8') as f:
        f.write(installer_bat)
    
    print("✅ Installer batch creato")
    
    # Crea README per il pacchetto
    readme_package = '''# 📱 TIGOTÀ Sistema Timbratura - Pacchetto Tablet

## 🚀 INSTALLAZIONE RAPIDA

### Metodo 1: Installazione Automatica (Consigliato)
1. **Eseguire come Amministratore**: `INSTALLA_TIGOTA.bat`
2. Seguire le istruzioni a schermo
3. Il sistema si installerà automaticamente

### Metodo 2: Installazione Manuale
1. Copiare `TIGOTA_Sistema_Timbratura.exe` in una cartella a scelta
2. Creare collegamento sul desktop
3. Eseguire l'applicazione

## 💻 REQUISITI SISTEMA

- **OS**: Windows 10/11
- **RAM**: 4GB+ 
- **Storage**: 500MB liberi
- **Display**: 1280x800 o superiore
- **NFC**: Lettore compatibile (opzionale per test)

## 🎯 UTILIZZO

- **Avvio**: Doppio click su icona desktop
- **Fullscreen**: Automatico (ESC per uscire)
- **Amministrazione**: Tasto F1
- **Chiusura**: ESC + conferma

## 📊 CARATTERISTICHE

✅ **Database SQLite integrato**
✅ **Backup automatico**
✅ **Export CSV per HR**
✅ **Interfaccia touch ottimizzata**
✅ **Orologio analogico premium**
✅ **Design TIGOTÀ professionale**

## 🔧 CONFIGURAZIONE

Il sistema è preconfigurato per l'uso immediato:
- Database: `C:\\ProgramData\\TIGOTA_Timbratura\\`
- Backup automatici ogni ora
- Export giornalieri
- Logs completi per diagnostica

## 📞 SUPPORTO

- **Email**: support@tigota.it
- **Documentazione**: File inclusi nel pacchetto
- **Logs**: Menu F1 > Diagnostica

---
**TIGOTÀ Sistema Timbratura v3.1**  
*Professional Tablet Edition*
'''
    
    with open(package_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_package)
    
    print("✅ README pacchetto creato")
    
    # Calcola dimensioni
    total_size = sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file())
    print(f"📦 Pacchetto creato: {total_size / (1024*1024):.1f} MB")
    
    return package_dir

if __name__ == "__main__":
    try:
        # Step 1: Prepara build
        print("🔧 Preparazione build...")
        build_tigota_exe()
        create_version_info()
        
        # Step 2: Compila EXE
        if compile_exe():
            print("\n✅ EXE compilato con successo!")
            
            # Step 3: Crea pacchetto
            package_path = create_installer_package()
            
            print(f"\n🎉 PACCHETTO COMPLETO PRONTO!")
            print(f"📂 Directory: {package_path}")
            print(f"📱 Pronto per installazione su tablet!")
            
            # Apri la directory
            os.system(f'explorer "{package_path}"')
            
        else:
            print("\n❌ Errore durante la compilazione")
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
