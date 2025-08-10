#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App per Timbratura - SmartTIM con Design TIGOTA
Applicazione fullscreen con brand TIGOTA per la timbratura dipendenti
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import threading
import time
from nfc_manager import NFCReader, TimbratureManager
from config import COLORS, TEXTS, FONTS, NFC_CONFIG, WINDOW_CONFIG

class AppTimbraturaModerna:
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
        """Definisce la palette di colori TIGOTA"""
        self.colors = COLORS
        
    def setup_ui(self):
        """Configura l'interfaccia utente moderna"""
        # Frame principale con gradiente simulato
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Header moderno con logo TIGOTA
        self.create_modern_header(main_frame)
        
        # Centro con data e orologio elegante
        self.create_modern_center(main_frame)
        
        # Footer moderno con loghi
        self.create_modern_footer(main_frame)
        
    def create_modern_header(self, parent):
        """Crea header moderno con brand TIGOTA"""
        header_frame = tk.Frame(parent, bg=self.colors['background'], height=180)
        header_frame.pack(fill='x', pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Container logo con effetto shadow
        logo_container = tk.Frame(header_frame, bg=self.colors['background'])
        logo_container.pack(expand=True, fill='both', padx=60, pady=20)
        
        # Logo TIGOTA principale
        logo_main = tk.Frame(logo_container, bg=self.colors['card_bg'], 
                           relief='flat', bd=0, padx=40, pady=20)
        logo_main.pack(expand=True, fill='both')
        
        # Effetto shadow simulato
        shadow_frame = tk.Frame(logo_container, bg=self.colors['border'], height=3)
        shadow_frame.pack(fill='x', pady=(0, 0))
        
        # Testo TIGOTA con stile
        tigota_label = tk.Label(logo_main, text="TIGOTÀ", 
                               font=('Segoe UI', 48, 'bold'),
                               bg=self.colors['card_bg'], 
                               fg=self.colors['tigota_pink'])
        tigota_label.pack(pady=(10, 0))
        
        # Sottotitolo
        subtitle_label = tk.Label(logo_main, text="Sistema di Timbratura", 
                                 font=('Segoe UI', 16, 'normal'),
                                 bg=self.colors['card_bg'], 
                                 fg=self.colors['text'])
        subtitle_label.pack(pady=(0, 10))
        
    def create_modern_center(self, parent):
        """Crea sezione centrale moderna"""
        center_frame = tk.Frame(parent, bg=self.colors['background'])
        center_frame.pack(expand=True, fill='both', pady=40)
        
        # Container principale per data/ora
        datetime_container = tk.Frame(center_frame, bg=self.colors['tigota_light'],
                                    relief='flat', bd=0, padx=60, pady=40)
        datetime_container.pack(expand=True, padx=120, pady=40)
        
        # Bordo decorativo rosa TIGOTA
        border_top = tk.Frame(datetime_container, bg=self.colors['tigota_pink'], height=4)
        border_top.pack(fill='x', pady=(0, 20))
        
        # Data moderna
        self.date_label = tk.Label(datetime_container, 
                                  font=FONTS['date'],
                                  bg=self.colors['tigota_light'], 
                                  fg=self.colors['text'])
        self.date_label.pack(pady=(0, 20))
        
        # Ora grande e moderna
        self.time_label = tk.Label(datetime_container, 
                                  font=FONTS['time'],
                                  bg=self.colors['tigota_light'], 
                                  fg=self.colors['tigota_pink'])
        self.time_label.pack(pady=(0, 20))
        
        # Bordo decorativo inferiore
        border_bottom = tk.Frame(datetime_container, bg=self.colors['tigota_pink'], height=4)
        border_bottom.pack(fill='x', pady=(20, 0))
        
        # Area NFC moderna
        self.create_modern_nfc_section(center_frame)
        
    def create_modern_nfc_section(self, parent):
        """Crea sezione NFC moderna"""
        # Posizionamento strategico in basso a destra
        nfc_container = tk.Frame(parent, bg=self.colors['background'])
        nfc_container.pack(side='bottom', anchor='se', padx=40, pady=40)
        
        # Frame NFC con design moderno
        self.nfc_frame = tk.Frame(nfc_container, bg=self.colors['card_bg'], 
                                 relief='flat', bd=0, padx=30, pady=20)
        self.nfc_frame.pack()
        
        # Bordo superiore colorato
        nfc_border = tk.Frame(self.nfc_frame, bg=self.colors['tigota_pink'], height=3)
        nfc_border.pack(fill='x', pady=(0, 15))
        
        # Icona NFC grande
        self.nfc_icon = tk.Label(self.nfc_frame, text="📱", 
                               font=('Segoe UI Emoji', 48, 'normal'),
                               bg=self.colors['card_bg'], 
                               fg=self.colors['tigota_pink'])
        self.nfc_icon.pack(pady=(0, 10))
        
        # Testo istruzione elegante
        self.nfc_text = tk.Label(self.nfc_frame, text=TEXTS['nfc_instruction'], 
                               font=FONTS['nfc_text'],
                               bg=self.colors['card_bg'], 
                               fg=self.colors['text'])
        self.nfc_text.pack(pady=(0, 10))
        
        # Indicatore di stato con colore
        self.nfc_status = tk.Label(self.nfc_frame, text=TEXTS['nfc_active'], 
                                 font=FONTS['nfc_status'],
                                 bg=self.colors['card_bg'], 
                                 fg=self.colors['success'])
        self.nfc_status.pack(pady=(0, 10))
        
        # Effetto shadow per NFC
        nfc_shadow = tk.Frame(nfc_container, bg=self.colors['border'], 
                             height=2, width=200)
        nfc_shadow.pack(pady=(2, 0))
        
    def create_modern_footer(self, parent):
        """Crea footer moderno"""
        footer_frame = tk.Frame(parent, bg=self.colors['background'], height=120)
        footer_frame.pack(fill='x', side='bottom', pady=(0, 20))
        footer_frame.pack_propagate(False)
        
        # Container per elementi footer
        footer_content = tk.Frame(footer_frame, bg=self.colors['background'])
        footer_content.pack(fill='both', expand=True, padx=40)
        
        # Logo software a destra
        software_container = tk.Frame(footer_content, bg=self.colors['card_bg'],
                                     relief='flat', bd=0, padx=25, pady=15)
        software_container.pack(side='right', pady=10)
        
        # Bordo superiore colorato per il logo software
        soft_border = tk.Frame(software_container, bg=self.colors['tigota_pink'], height=2)
        soft_border.pack(fill='x', pady=(0, 10))
        
        # Nome software
        software_label = tk.Label(software_container, 
                                text=TEXTS['software_name'], 
                                font=FONTS['software_name'],
                                bg=self.colors['card_bg'], 
                                fg=self.colors['tigota_pink'])
        software_label.pack()
        
        # Versione software
        version_label = tk.Label(software_container, 
                               text=TEXTS['software_version'], 
                               font=FONTS['software_version'],
                               bg=self.colors['card_bg'], 
                               fg=self.colors['text'])
        version_label.pack()
        
        # Informazioni aggiuntive a sinistra
        info_label = tk.Label(footer_content, 
                            text="Belli, Puliti, Profumati", 
                            font=('Segoe UI', 14, 'italic'),
                            bg=self.colors['background'], 
                            fg=self.colors['text'])
        info_label.pack(side='left', pady=20)
        
    def update_clock(self):
        """Aggiorna data e ora in tempo reale"""
        now = datetime.now()
        
        # Formato data italiana elegante
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
            
            # Mostra feedback visivo moderno
            self.show_modern_feedback(timbratura)
            
        except Exception as e:
            print(f"Errore nella gestione del badge: {e}")
            self.show_error_feedback()
            
    def show_modern_feedback(self, timbratura):
        """Mostra feedback visivo moderno per la timbratura"""
        # Salva stato originale
        old_text = self.nfc_text.cget('text')
        old_color = self.nfc_text.cget('fg')
        old_bg = self.nfc_frame.cget('bg')
        
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        # Colore basato sul movimento
        movement_color = self.colors['success'] if movimento == 'ENTRATA' else self.colors['warning']
        
        # Aggiorna testo con feedback
        feedback_text = f"{TEXTS[movimento.lower()]}\n{badge_id}\n{ora}"
        self.nfc_text.config(text=feedback_text, fg=movement_color)
        
        # Effetto flash sul frame
        self.nfc_frame.config(bg=self.colors['tigota_light'])
        
        # Ripristina dopo il tempo configurato
        self.root.after(NFC_CONFIG['feedback_duration'], 
                       lambda: self.restore_nfc_display(old_text, old_color, old_bg))
        
    def restore_nfc_display(self, old_text, old_color, old_bg):
        """Ripristina il display NFC allo stato originale"""
        self.nfc_text.config(text=old_text, fg=old_color)
        self.nfc_frame.config(bg=old_bg)
        
    def show_error_feedback(self):
        """Mostra feedback per errori"""
        old_text = self.nfc_text.cget('text')
        old_color = self.nfc_text.cget('fg')
        
        self.nfc_text.config(text=TEXTS['nfc_error'], fg=self.colors['error'])
        self.root.after(2000, lambda: self.nfc_text.config(text=old_text, fg=old_color))
        
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
        app = AppTimbraturaModerna()
        app.run()
    except Exception as e:
        print(f"Errore nell'avvio dell'applicazione: {e}")

if __name__ == "__main__":
    main()
