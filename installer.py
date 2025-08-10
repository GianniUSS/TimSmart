#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOTÀ Installer - Setup Produzione
Installa e configura il sistema di timbratura per produzione
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class TigotaInstaller:
    def __init__(self):
        self.app_name = "TIGOTÀ Sistema Timbratura"
        self.version = "3.1.0 Elite"
        self.install_dir = Path("C:/Program Files/TIGOTA_Timbratura")
        self.data_dir = Path("C:/ProgramData/TIGOTA_Timbratura")
        self.startup_dir = Path(os.path.expanduser("~")) / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        
    def check_admin_rights(self):
        """Verifica privilegi amministratore"""
        try:
            return os.getuid() == 0
        except AttributeError:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    def install_dependencies(self):
        """Installa dipendenze Python"""
        print("📦 Installazione dipendenze...")
        
        try:
            # Aggiorna pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                          check=True, capture_output=True)
            
            # Installa requirements
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True, capture_output=True)
            
            print("✅ Dipendenze installate con successo")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Errore installazione dipendenze: {e}")
            return False
    
    def create_directories(self):
        """Crea directory di installazione"""
        print("📁 Creazione directory...")
        
        try:
            # Directory principali
            self.install_dir.mkdir(parents=True, exist_ok=True)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Sottodirectory
            (self.data_dir / "logs").mkdir(exist_ok=True)
            (self.data_dir / "backup").mkdir(exist_ok=True)
            (self.data_dir / "config").mkdir(exist_ok=True)
            (self.data_dir / "database").mkdir(exist_ok=True)
            
            print("✅ Directory create con successo")
            return True
            
        except Exception as e:
            print(f"❌ Errore creazione directory: {e}")
            return False
    
    def copy_application_files(self):
        """Copia file applicazione"""
        print("📋 Copia file applicazione...")
        
        try:
            # File principali da copiare
            files_to_copy = [
                "tigota_elite_dashboard.py",
                "tigota_professional.py", 
                "tigota_modern_dashboard.py",
                "nfc_manager.py",
                "config_tablet.py",
                "config_tablet_perfect.py",
                "requirements.txt",
                "README.md"
            ]
            
            for file_name in files_to_copy:
                if Path(file_name).exists():
                    shutil.copy2(file_name, self.install_dir / file_name)
                    print(f"  ✓ Copiato: {file_name}")
            
            print("✅ File applicazione copiati")
            return True
            
        except Exception as e:
            print(f"❌ Errore copia file: {e}")
            return False
    
    def create_startup_script(self):
        """Crea script avvio automatico"""
        print("🚀 Configurazione avvio automatico...")
        
        try:
            # Script batch per avvio
            startup_script = f"""@echo off
cd /d "{self.install_dir}"
python tigota_elite_dashboard.py
pause
"""
            
            # Salva script
            script_path = self.install_dir / "start_tigota.bat"
            with open(script_path, 'w') as f:
                f.write(startup_script)
            
            # Collegamento nella cartella Startup
            link_path = self.startup_dir / "TIGOTA_Timbratura.bat"
            if self.startup_dir.exists():
                shutil.copy2(script_path, link_path)
                print("  ✓ Collegamento avvio automatico creato")
            
            print("✅ Avvio automatico configurato")
            return True
            
        except Exception as e:
            print(f"❌ Errore configurazione avvio: {e}")
            return False
    
    def create_config_files(self):
        """Crea file di configurazione produzione"""
        print("⚙️ Creazione configurazione produzione...")
        
        try:
            # Configurazione produzione
            prod_config = {
                "app": {
                    "name": "TIGOTÀ Sistema Timbratura",
                    "version": self.version,
                    "environment": "production",
                    "debug": False
                },
                "database": {
                    "path": str(self.data_dir / "database" / "timbrature.db"),
                    "backup_enabled": True,
                    "backup_interval": 3600,
                    "backup_path": str(self.data_dir / "backup")
                },
                "logging": {
                    "level": "INFO",
                    "file": str(self.data_dir / "logs" / "tigota.log"),
                    "max_size": "10MB",
                    "backup_count": 5
                },
                "nfc": {
                    "enabled": True,
                    "port": "AUTO",
                    "timeout": 5000,
                    "retry_attempts": 3
                },
                "ui": {
                    "fullscreen": True,
                    "hide_cursor": True,
                    "auto_return": True,
                    "screensaver_disable": True
                },
                "security": {
                    "admin_password": "tigota2025",
                    "encryption_enabled": True,
                    "backup_encryption": True
                }
            }
            
            # Salva configurazione
            config_path = self.data_dir / "config" / "production.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(prod_config, f, indent=4, ensure_ascii=False)
            
            print("✅ Configurazione produzione creata")
            return True
            
        except Exception as e:
            print(f"❌ Errore creazione configurazione: {e}")
            return False
    
    def create_service_scripts(self):
        """Crea script di servizio"""
        print("🛠️ Creazione script di servizio...")
        
        try:
            # Script start
            start_script = f"""@echo off
title TIGOTÀ Sistema Timbratura
echo Avvio TIGOTÀ Sistema Timbratura...
cd /d "{self.install_dir}"
python tigota_elite_dashboard.py
"""
            
            # Script stop
            stop_script = """@echo off
echo Arresto TIGOTÀ Sistema Timbratura...
taskkill /f /im python.exe /fi "WINDOWTITLE eq TIGOTÀ*"
echo Sistema arrestato.
pause
"""
            
            # Script restart
            restart_script = f"""@echo off
echo Riavvio TIGOTÀ Sistema Timbratura...
call "{self.install_dir}/stop_tigota.bat"
timeout /t 3
call "{self.install_dir}/start_tigota.bat"
"""
            
            # Salva script
            with open(self.install_dir / "start_tigota.bat", 'w') as f:
                f.write(start_script)
            
            with open(self.install_dir / "stop_tigota.bat", 'w') as f:
                f.write(stop_script)
                
            with open(self.install_dir / "restart_tigota.bat", 'w') as f:
                f.write(restart_script)
            
            print("✅ Script di servizio creati")
            return True
            
        except Exception as e:
            print(f"❌ Errore creazione script: {e}")
            return False
    
    def create_desktop_shortcuts(self):
        """Crea collegamenti desktop"""
        print("🖥️ Creazione collegamenti desktop...")
        
        try:
            desktop = Path(os.path.expanduser("~/Desktop"))
            
            # Collegamento app principale
            app_shortcut = f"""@echo off
cd /d "{self.install_dir}"
python tigota_elite_dashboard.py
"""
            
            shortcut_path = desktop / "TIGOTÀ Timbratura.bat"
            with open(shortcut_path, 'w') as f:
                f.write(app_shortcut)
            
            # Collegamento admin
            admin_shortcut = f"""@echo off
cd /d "{self.install_dir}"
echo Modalità Amministratore TIGOTÀ
echo ================================
echo.
echo [1] Avvia Sistema
echo [2] Visualizza Log
echo [3] Backup Database
echo [4] Configurazione
echo [5] Esci
echo.
set /p choice="Scegli opzione (1-5): "

if "%choice%"=="1" python tigota_elite_dashboard.py
if "%choice%"=="2" notepad "{self.data_dir}/logs/tigota.log"
if "%choice%"=="3" xcopy "{self.data_dir}/database" "{self.data_dir}/backup" /s /y
if "%choice%"=="4" notepad "{self.data_dir}/config/production.json"
if "%choice%"=="5" exit

pause
"""
            
            admin_path = desktop / "TIGOTÀ Admin.bat"
            with open(admin_path, 'w') as f:
                f.write(admin_shortcut)
            
            print("✅ Collegamenti desktop creati")
            return True
            
        except Exception as e:
            print(f"❌ Errore creazione collegamenti: {e}")
            return False
    
    def run_installation(self):
        """Esegue installazione completa"""
        print("🎯 TIGOTÀ Sistema Timbratura - Installer Produzione")
        print("=" * 60)
        print(f"Versione: {self.version}")
        print(f"Directory installazione: {self.install_dir}")
        print(f"Directory dati: {self.data_dir}")
        print("=" * 60)
        
        # Verifica privilegi
        if not self.check_admin_rights():
            print("⚠️ ATTENZIONE: Privilegi amministratore consigliati")
            choice = input("Continuare comunque? (s/N): ")
            if choice.lower() != 's':
                print("❌ Installazione annullata")
                return False
        
        # Passaggi installazione
        steps = [
            ("Creazione directory", self.create_directories),
            ("Installazione dipendenze", self.install_dependencies),
            ("Copia file applicazione", self.copy_application_files),
            ("Creazione configurazione", self.create_config_files),
            ("Setup avvio automatico", self.create_startup_script),
            ("Creazione script servizio", self.create_service_scripts),
            ("Creazione collegamenti", self.create_desktop_shortcuts)
        ]
        
        print("\n🔧 Avvio installazione...")
        
        for step_name, step_func in steps:
            print(f"\n📌 {step_name}...")
            if not step_func():
                print(f"❌ Installazione fallita al passaggio: {step_name}")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 INSTALLAZIONE COMPLETATA CON SUCCESSO!")
        print("=" * 60)
        print("\n📋 PROSSIMI PASSI:")
        print("1. Configurare lettore NFC/RFID")
        print("2. Testare il sistema")
        print("3. Formare gli utenti")
        print("4. Avviare in produzione")
        print("\n🖥️ COMANDI UTILI:")
        print(f"• Avvia: {self.install_dir}/start_tigota.bat")
        print(f"• Arresta: {self.install_dir}/stop_tigota.bat")
        print(f"• Admin: Desktop/TIGOTÀ Admin.bat")
        print("\n🆘 SUPPORTO:")
        print("• Email: support@tigota.it")
        print("• Doc: README.md")
        
        return True

def main():
    """Main installer"""
    installer = TigotaInstaller()
    
    try:
        success = installer.run_installation()
        if success:
            input("\nPremi INVIO per uscire...")
        else:
            input("\nInstallazione fallita. Premi INVIO per uscire...")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Installazione interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore inaspettato: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
