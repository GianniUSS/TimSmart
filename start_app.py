#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script di avvio per l'App SmartTIM
Esegue controlli prelim    try:
        # Importa e avvia l'app grafica TIGOTA
        from app_timbratura_grafica import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\nApplicazione interrotta dall'utente")
    except Exception as e:
        print(f"Errore nell'avvio dell'applicazione: {e}")
        print("Provo con la versione standard...")
        try:
            from app_timbratura import main as app_standard
            app_standard()
        except Exception as e2:
            print(f"Errore anche con versione standard: {e2}")
            import traceback
            traceback.print_exc()
            sys.exit(1)ia l'applicazione
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Verifica la versione di Python"""
    if sys.version_info < (3, 7):
        print("ERRORE: È richiesto Python 3.7 o superiore")
        print(f"Versione attuale: {sys.version}")
        return False
    return True

def check_dependencies():
    """Verifica e installa le dipendenze se necessarie"""
    required_packages = [
        'Pillow',
        # 'pynfc' commentato per ora dato che richiede hardware specifico
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower())
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Pacchetti mancanti: {missing_packages}")
        print("Installazione dipendenze...")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ])
            for package in missing_packages:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ])
            print("Dipendenze installate con successo!")
        except subprocess.CalledProcessError as e:
            print(f"Errore nell'installazione delle dipendenze: {e}")
            return False
    
    return True

def check_tkinter():
    """Verifica che tkinter sia disponibile"""
    try:
        import tkinter
        return True
    except ImportError:
        print("ERRORE: tkinter non è disponibile")
        print("Su Ubuntu/Debian: sudo apt-get install python3-tk")
        print("Su CentOS/RHEL: sudo yum install tkinter")
        return False

def create_desktop_shortcut():
    """Crea un collegamento sul desktop (Windows)"""
    if sys.platform == 'win32':
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "SmartTIM.lnk")
            target = os.path.join(os.getcwd(), "start_app.py")
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print(f"Collegamento creato: {path}")
        except ImportError:
            print("Per creare il collegamento desktop, installare: pip install winshell pywin32")
        except Exception as e:
            print(f"Errore nella creazione del collegamento: {e}")

def main():
    """Funzione principale di avvio"""
    print("=" * 50)
    print("SmartTIM - Sistema di Timbratura")
    print("Avvio applicazione...")
    print("=" * 50)
    
    # Controlli preliminari
    if not check_python_version():
        sys.exit(1)
    
    if not check_tkinter():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    print("Tutti i controlli superati!")
    print("Avvio dell'applicazione...")
    
    try:
        # Importa e avvia l'app moderna
        from app_modern_timbratura import main as app_main
        app_main()
    except KeyboardInterrupt:
        print("\nApplicazione interrotta dall'utente")
    except Exception as e:
        print(f"Errore nell'avvio dell'applicazione: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
