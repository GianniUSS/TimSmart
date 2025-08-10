#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App per Timbratura - SmartTIM
Applicazione fullscreen con colori pastello per la timbratura dipendenti
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import threading
import time
from nfc_manager import NFCReader, TimbratureManager
from config import COLORS, TEXTS, FONTS, NFC_CONFIG, WINDOW_CONFIG

class AppTimbratura:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_colors()
        
        # Inizializza gestori NFC e timbrature
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        self.setup_ui()
        self.update_clock()
        
        # Avvia lettura NFC
        self.nfc_reader.start_reading()
        
    def setup_window(self):
        """Configura la finestra principale"""
        self.root.title(WINDOW_CONFIG['title'])
        if WINDOW_CONFIG['fullscreen']:
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry(WINDOW_CONFIG['geometry'])
            self.root.resizable(WINDOW_CONFIG['resizable'], WINDOW_CONFIG['resizable'])
        
        self.root.configure(bg=COLORS['background'])
        
        # Esc per uscire dalla modalità fullscreen
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
    def setup_colors(self):
        """Definisce la palette di colori pastello"""
        self.colors = COLORS
        
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Frame principale
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header con logo cliente
        self.create_header(main_frame)
        
        # Centro con data e orologio
        self.create_center_section(main_frame)
        
        # Footer con loghi
        self.create_footer(main_frame)
        
    def create_header(self, parent):
        """Crea la sezione header con logo cliente"""
        header_frame = tk.Frame(parent, bg=self.colors['background'], height=150)
        header_frame.pack(fill='x', pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Logo cliente placeholder
        logo_frame = tk.Frame(header_frame, bg=self.colors['card_bg'], 
                             relief='raised', bd=2)
        logo_frame.pack(expand=True, fill='both', padx=50, pady=20)
        
        logo_label = tk.Label(logo_frame, text=TEXTS['logo_cliente'], 
                             font=FONTS['logo_cliente'],
                             bg=self.colors['card_bg'], 
                             fg=self.colors['text'])
        logo_label.pack(expand=True)
        
    def create_center_section(self, parent):
        """Crea la sezione centrale con data e orologio"""
        center_frame = tk.Frame(parent, bg=self.colors['background'])
        center_frame.pack(expand=True, fill='both', pady=30)
        
        # Container per data e ora
        datetime_container = tk.Frame(center_frame, bg=self.colors['primary'],
                                    relief='raised', bd=3)
        datetime_container.pack(expand=True, padx=100, pady=50)
        
        # Data
        self.date_label = tk.Label(datetime_container, 
                                  font=FONTS['date'],
                                  bg=self.colors['primary'], 
                                  fg=self.colors['text'])
        self.date_label.pack(pady=(30, 10))
        
        # Ora
        self.time_label = tk.Label(datetime_container, 
                                  font=FONTS['time'],
                                  bg=self.colors['primary'], 
                                  fg=self.colors['text'])
        self.time_label.pack(pady=(10, 30))
        
        # Area NFC
        self.create_nfc_section(center_frame)
        
    def create_nfc_section(self, parent):
        """Crea la sezione per la lettura NFC"""
        self.nfc_frame = tk.Frame(parent, bg=self.colors['accent'], 
                           relief='raised', bd=3)
        self.nfc_frame.pack(side='bottom', anchor='se', padx=30, pady=30)
        
        # Icona NFC placeholder
        self.nfc_icon = tk.Label(self.nfc_frame, text="📱 NFC", 
                           font=('Arial', 24, 'bold'),
                           bg=self.colors['accent'], 
                           fg=self.colors['text'])
        self.nfc_icon.pack(padx=20, pady=10)
        
        self.nfc_text = tk.Label(self.nfc_frame, text="Avvicina il badge", 
                           font=('Arial', 14),
                           bg=self.colors['accent'], 
                           fg=self.colors['text'])
        self.nfc_text.pack(padx=20, pady=(0, 10))
        
        # Indicatore di stato
        self.nfc_status = tk.Label(self.nfc_frame, text="🟢 Attivo", 
                                 font=('Arial', 12),
                                 bg=self.colors['accent'], 
                                 fg='green')
        self.nfc_status.pack(padx=20, pady=(0, 10))
        
    def create_footer(self, parent):
        """Crea il footer con logo aziendale"""
        footer_frame = tk.Frame(parent, bg=self.colors['background'], height=100)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        # Logo aziendale software (in basso a destra)
        software_logo_frame = tk.Frame(footer_frame, bg=self.colors['secondary'],
                                     relief='raised', bd=2)
        software_logo_frame.pack(side='right', padx=20, pady=10, 
                               ipadx=20, ipady=10)
        
        software_label = tk.Label(software_logo_frame, 
                                text="SmartTIM Software", 
                                font=('Arial', 16, 'bold'),
                                bg=self.colors['secondary'], 
                                fg=self.colors['text'])
        software_label.pack()
        
        version_label = tk.Label(software_logo_frame, 
                               text="v1.0", 
                               font=('Arial', 10),
                               bg=self.colors['secondary'], 
                               fg=self.colors['text'])
        version_label.pack()
        
    def update_clock(self):
        """Aggiorna data e ora in tempo reale"""
        now = datetime.now()
        
        # Formato data italiana
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        
        # Formato ora
        time_str = now.strftime("%H:%M:%S")
        
        self.date_label.config(text=date_str)
        self.time_label.config(text=time_str)
        
        # Aggiorna ogni secondo
        self.root.after(1000, self.update_clock)
        
    def translate_date(self, date_str):
        """Traduce i nomi dei giorni e mesi in italiano"""
        translations = {
            'Monday': 'Lunedì',
            'Tuesday': 'Martedì', 
            'Wednesday': 'Mercoledì',
            'Thursday': 'Giovedì',
            'Friday': 'Venerdì',
            'Saturday': 'Sabato',
            'Sunday': 'Domenica',
            'January': 'Gennaio',
            'February': 'Febbraio',
            'March': 'Marzo',
            'April': 'Aprile',
            'May': 'Maggio',
            'June': 'Giugno',
            'July': 'Luglio',
            'August': 'Agosto',
            'September': 'Settembre',
            'October': 'Ottobre',
            'November': 'Novembre',
            'December': 'Dicembre'
        }
        
        for eng, ita in translations.items():
            date_str = date_str.replace(eng, ita)
            
        return date_str
        
    def toggle_fullscreen(self, event=None):
        """Attiva/disattiva modalità fullscreen"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def on_badge_read(self, badge_id):
        """Callback chiamato quando viene letto un badge NFC"""
        try:
            # Registra la timbratura
            timbratura = self.timbrature_manager.registra_timbratura(badge_id)
            
            # Mostra feedback visivo
            self.show_timbratura_feedback(timbratura)
            
        except Exception as e:
            print(f"Errore nella gestione del badge: {e}")
            self.show_error_feedback()
            
    def show_timbratura_feedback(self, timbratura):
        """Mostra feedback visivo per la timbratura"""
        # Aggiorna il testo NFC temporaneamente
        old_text = self.nfc_text.cget('text')
        old_color = self.nfc_text.cget('fg')
        
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        self.nfc_text.config(
            text=f"{movimento}\n{badge_id}\n{ora}",
            fg='green' if movimento == 'ENTRATA' else 'red'
        )
        
        # Ripristina dopo 3 secondi
        self.root.after(3000, lambda: self.nfc_text.config(text=old_text, fg=old_color))
        
        # Effetto visivo sul frame NFC
        self.animate_nfc_frame()
        
    def show_error_feedback(self):
        """Mostra feedback per errori"""
        old_text = self.nfc_text.cget('text')
        old_color = self.nfc_text.cget('fg')
        
        self.nfc_text.config(text="ERRORE!", fg='red')
        self.root.after(2000, lambda: self.nfc_text.config(text=old_text, fg=old_color))
        
    def animate_nfc_frame(self):
        """Anima il frame NFC per feedback visivo"""
        original_bg = self.nfc_frame.cget('bg')
        
        # Lampeggia verde
        self.nfc_frame.config(bg=self.colors['highlight'])
        self.root.after(300, lambda: self.nfc_frame.config(bg=original_bg))
        
    def simulate_nfc_read(self):
        """Simula la lettura di un badge NFC"""
        # Qui implementerai la logica per la lettura NFC reale
        print("Badge NFC rilevato!")
        # Aggiungi qui la logica per registrare la timbratura
        
    def cleanup(self):
        """Pulizia delle risorse prima della chiusura"""
        if hasattr(self, 'nfc_reader'):
            self.nfc_reader.stop_reading()
        
    def run(self):
        """Avvia l'applicazione"""
        try:
            # Gestisce la chiusura pulita
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
            
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        self.cleanup()
        self.root.destroy()

def main():
    """Funzione principale"""
    try:
        app = AppTimbratura()
        app.run()
    except Exception as e:
        print(f"Errore nell'avvio dell'applicazione: {e}")

if __name__ == "__main__":
    main()
