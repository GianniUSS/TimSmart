#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher per App Timbratura TIGOTÀ Tablet
Avvio semplificato per deployment su tablet
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import time

def check_dependencies():
    """Verifica dipendenze"""
    try:
        import tkinter
        import json
        from datetime import datetime
        return True
    except ImportError as e:
        messagebox.showerror("Errore Dipendenze", 
                           f"Modulo mancante: {e}\nContattare l'amministratore")
        return False

def check_files():
    """Verifica presenza file necessari"""
    required_files = [
        'tigota_tablet_app.py',
        'nfc_manager.py',
        'config_tablet.py',
        'tigota_tablet_graphics.py'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        messagebox.showerror("File Mancanti", 
                           f"File non trovati:\n{chr(10).join(missing)}")
        return False
    return True

def show_loading_screen():
    """Mostra schermata di caricamento"""
    loading_window = tk.Tk()
    loading_window.title("TIGOTÀ Timbrature")
    loading_window.geometry("400x300")
    loading_window.configure(bg='#E91E63')
    loading_window.resizable(False, False)
    
    # Centra finestra
    loading_window.eval('tk::PlaceWindow . center')
    
    # Logo/Titolo
    title_label = tk.Label(loading_window, 
                          text="TIGOTÀ",
                          font=('Segoe UI', 28, 'bold'),
                          bg='#E91E63',
                          fg='white')
    title_label.pack(pady=(50, 10))
    
    subtitle_label = tk.Label(loading_window,
                             text="Sistema Timbrature",
                             font=('Segoe UI', 16, 'normal'),
                             bg='#E91E63',
                             fg='white')
    subtitle_label.pack(pady=(0, 30))
    
    # Barra di caricamento
    progress_frame = tk.Frame(loading_window, bg='#E91E63')
    progress_frame.pack(pady=20)
    
    progress_bg = tk.Frame(progress_frame, bg='white', height=8, width=300)
    progress_bg.pack()
    
    progress_bar = tk.Frame(progress_bg, bg='#C2185B', height=8, width=0)
    progress_bar.place(x=0, y=0)
    
    status_label = tk.Label(loading_window,
                           text="Avvio in corso...",
                           font=('Segoe UI', 12, 'normal'),
                           bg='#E91E63',
                           fg='white')
    status_label.pack(pady=(20, 0))
    
    # Animazione progresso
    def animate_progress():
        for i in range(101):
            progress_bar.config(width=i * 3)
            if i < 30:
                status_label.config(text="Caricamento moduli...")
            elif i < 60:
                status_label.config(text="Inizializzazione sistema...")
            elif i < 90:
                status_label.config(text="Configurazione tablet...")
            else:
                status_label.config(text="Avvio interfaccia...")
            
            loading_window.update()
            time.sleep(0.02)
    
    # Avvia animazione
    loading_window.after(100, animate_progress)
    
    return loading_window

def launch_tablet_app():
    """Lancia app tablet"""
    try:
        # Cambia directory di lavoro
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Importa e avvia app
        from tigota_tablet_app import TigotaTabletApp
        
        app = TigotaTabletApp()
        app.run()
        
    except Exception as e:
        messagebox.showerror("Errore Avvio", 
                           f"Impossibile avviare l'applicazione:\n{str(e)}")
        return False
    
    return True

def main():
    """Funzione principale del launcher"""
    try:
        # Verifica sistema
        if not check_dependencies():
            return
        
        if not check_files():
            return
        
        # Mostra loading
        loading_window = show_loading_screen()
        
        # Simula caricamento
        loading_window.after(2500, loading_window.destroy)
        loading_window.mainloop()
        
        # Lancia app principale
        launch_tablet_app()
        
    except KeyboardInterrupt:
        print("Launcher interrotto dall'utente")
    except Exception as e:
        messagebox.showerror("Errore Launcher", 
                           f"Errore nel launcher:\n{str(e)}")

if __name__ == "__main__":
    main()
