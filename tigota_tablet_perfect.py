#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Timbratura TIGOTÀ - Versione Tablet Ottimizzata
Layout perfetto per tablet touch con gestione spazio ottimizzata
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import threading
import time
from nfc_manager import NFCReader, TimbratureManager
from config_tablet import COLORS, TEXTS, FONTS, NFC_CONFIG, WINDOW_CONFIG, TABLET_CONFIG

class TigotaTabletOptimized:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Gestori
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        self.setup_optimized_ui()
        self.start_clock()
        self.nfc_reader.start_reading()
        
    def setup_window(self):
        """Configura finestra ottimizzata per tablet"""
        self.root.title(WINDOW_CONFIG['title'])
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=COLORS['background'])
        
        # Bind eventi
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F1>', self.show_admin)
        
    def setup_optimized_ui(self):
        """UI ottimizzata con layout perfetto"""
        # Container principale con padding generoso
        main_container = tk.Frame(self.root, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header TIGOTÀ
        self.create_header_optimized(main_container)
        
        # Corpo principale - layout 60/40
        self.create_body_optimized(main_container)
        
        # Footer discreto
        self.create_footer_optimized(main_container)
        
    def create_header_optimized(self, parent):
        """Header TIGOTÀ ottimizzato"""
        # Container header con altezza fissa
        header_container = tk.Frame(parent, bg=COLORS['tigota_light'], height=120)
        header_container.pack(fill='x', pady=(0, 30))
        header_container.pack_propagate(False)
        
        # Content frame centrato
        content_frame = tk.Frame(header_container, bg=COLORS['tigota_light'])
        content_frame.pack(expand=True, fill='both', padx=50, pady=20)
        
        # Logo TIGOTÀ grande e ben visibile
        logo_label = tk.Label(content_frame, 
                             text="TIGOTÀ",
                             font=('Segoe UI', 56, 'bold'),
                             bg=COLORS['tigota_light'],
                             fg=COLORS['tigota_pink'])
        logo_label.pack(expand=True)
        
        # Sottotitolo
        subtitle_label = tk.Label(content_frame,
                                 text="Sistema di Timbratura",
                                 font=('Segoe UI', 18, 'normal'),
                                 bg=COLORS['tigota_light'],
                                 fg=COLORS['text_light'])
        subtitle_label.pack()
        
    def create_body_optimized(self, parent):
        """Corpo principale con data/ora a sinistra e NFC in basso a destra"""
        # Container corpo
        body_container = tk.Frame(parent, bg=COLORS['background'])
        body_container.pack(expand=True, fill='both')
        
        # Grid layout: data/ora occupa tutta la sinistra, NFC in basso a destra
        body_container.grid_columnconfigure(0, weight=7)  # 70% per data/ora
        body_container.grid_columnconfigure(1, weight=3)  # 30% per NFC
        body_container.grid_rowconfigure(0, weight=7)     # 70% altezza superiore
        body_container.grid_rowconfigure(1, weight=3)     # 30% altezza inferiore
        
        # Sezione data/ora (sinistra - spanning entrambe le righe)
        self.create_datetime_optimized(body_container)
        
        # Spazio vuoto in alto a destra
        empty_frame = tk.Frame(body_container, bg=COLORS['background'])
        empty_frame.grid(row=0, column=1, sticky='nsew', padx=(15, 0), pady=10)
        
        # Sezione NFC (basso a destra)
        self.create_nfc_optimized(body_container)
        
    def create_datetime_optimized(self, parent):
        """Sezione data/ora con spazio garantito - spanning entrambe le righe"""
        # Card data/ora con dimensioni generose - occupa entrambe le righe
        datetime_card = tk.Frame(parent, bg=COLORS['card_bg'], relief='flat', bd=0)
        datetime_card.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=(0, 15), pady=10)
        
        # Ombra simulata
        shadow_frame = tk.Frame(parent, bg=COLORS['shadow'], height=5)
        shadow_frame.grid(row=0, column=0, rowspan=2, sticky='sew', padx=(5, 20), pady=(15, 5))
        
        # Content con padding generoso
        content = tk.Frame(datetime_card, bg=COLORS['card_bg'])
        content.pack(expand=True, fill='both', padx=50, pady=40)
        
        # Status indicator compatto
        status_frame = tk.Frame(content, bg=COLORS['card_bg'])
        status_frame.pack(fill='x', pady=(0, 25))
        
        status_dot = tk.Label(status_frame, text="●", 
                             font=('Arial', 16), 
                             fg=COLORS['success'], 
                             bg=COLORS['card_bg'])
        status_dot.pack(side='left')
        
        status_text = tk.Label(status_frame, text="ATTIVO",
                              font=('Segoe UI', 14, 'bold'),
                              fg=COLORS['success'],
                              bg=COLORS['card_bg'])
        status_text.pack(side='left', padx=(10, 0))
        
        # Data con dimensioni controllate
        self.date_label = tk.Label(content,
                                  font=('Segoe UI', 26, 'normal'),  # Font ridotto
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['text'],
                                  wraplength=450,  # Larghezza controllata
                                  justify='center')
        self.date_label.pack(pady=(0, 20))
        
        # Ora prominente
        self.time_label = tk.Label(content,
                                  font=('Consolas', 68, 'bold'),  # Leggermente ridotto
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['tigota_pink'])
        self.time_label.pack(pady=(0, 25))
        
        # Spazio vuoto invece del slogan rimosso
        spacer_label = tk.Label(content,
                               text="",
                               font=('Segoe UI', 16, 'italic'),
                               bg=COLORS['card_bg'],
                               fg=COLORS['text_light'])
        spacer_label.pack()
        
    def create_nfc_optimized(self, parent):
        """Sezione NFC in basso a destra"""
        # Card NFC compatta in basso a destra
        nfc_card = tk.Frame(parent, bg=COLORS['card_bg'], relief='flat', bd=0)
        nfc_card.grid(row=1, column=1, sticky='nsew', padx=(15, 0), pady=10)
        
        # Ombra
        nfc_shadow = tk.Frame(parent, bg=COLORS['shadow'], height=5)
        nfc_shadow.grid(row=1, column=1, sticky='sew', padx=(20, 5), pady=(15, 5))
        
        # Content NFC compatto
        nfc_content = tk.Frame(nfc_card, bg=COLORS['card_bg'])
        nfc_content.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Titolo NFC più piccolo
        nfc_title = tk.Label(nfc_content,
                            text="AVVICINA IL BADGE",
                            font=('Segoe UI', 18, 'bold'),
                            bg=COLORS['card_bg'],
                            fg=COLORS['tigota_pink'],
                            wraplength=180)
        nfc_title.pack(pady=(0, 10))
        
        # Icona NFC più piccola
        nfc_icon = tk.Label(nfc_content,
                           text="📱",
                           font=('Apple Color Emoji', 50),
                           bg=COLORS['card_bg'])
        nfc_icon.pack(pady=10)
        
        # Status NFC
        self.nfc_status = tk.Label(nfc_content,
                                  text="🟢 Sistema Pronto",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['success'])
        self.nfc_status.pack()
        
    def create_footer_optimized(self, parent):
        """Footer discreto"""
        footer = tk.Frame(parent, bg=COLORS['background'], height=60)
        footer.pack(fill='x', pady=(30, 0))
        footer.pack_propagate(False)
        
        # Software info a destra
        software_frame = tk.Frame(footer, bg=COLORS['secondary'])
        software_frame.pack(side='right', padx=20, pady=10, ipadx=15, ipady=5)
        
        software_label = tk.Label(software_frame,
                                 text="SmartTIM v3.0 Tablet",
                                 font=('Segoe UI', 12, 'bold'),
                                 bg=COLORS['secondary'],
                                 fg=COLORS['tigota_pink'])
        software_label.pack()
        
    def start_clock(self):
        """Avvia orologio"""
        self.update_clock()
        
    def update_clock(self):
        """Aggiorna orologio ottimizzato"""
        now = datetime.now()
        
        # Data italiana ottimizzata
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        
        # Ora
        time_str = now.strftime("%H:%M:%S")
        
        # Aggiorna solo se i widget esistono
        if hasattr(self, 'date_label'):
            self.date_label.config(text=date_str.upper())
        if hasattr(self, 'time_label'):
            self.time_label.config(text=time_str)
        
        # Prossimo aggiornamento
        self.root.after(1000, self.update_clock)
        
    def translate_date(self, date_str):
        """Traduzione italiana"""
        translations = {
            'Monday': 'Lunedì', 'Tuesday': 'Martedì', 'Wednesday': 'Mercoledì',
            'Thursday': 'Giovedì', 'Friday': 'Venerdì', 'Saturday': 'Sabato', 'Sunday': 'Domenica',
            'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo', 'April': 'Aprile',
            'May': 'Maggio', 'June': 'Giugno', 'July': 'Luglio', 'August': 'Agosto',
            'September': 'Settembre', 'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
        }
        
        for eng, ita in translations.items():
            date_str = date_str.replace(eng, ita)
        return date_str
        
    def on_badge_read(self, badge_id):
        """Gestisce lettura badge"""
        try:
            # Registra timbratura
            timbratura = self.timbrature_manager.registra_timbratura(badge_id)
            
            # Feedback ottimizzato
            self.show_feedback_optimized(timbratura)
            
        except Exception as e:
            print(f"Errore badge: {e}")
            self.show_error_feedback()
            
    def show_feedback_optimized(self, timbratura):
        """Feedback ottimizzato per tablet"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        # Colore movimento
        color = COLORS['success'] if movimento == 'ENTRATA' else COLORS['warning']
        icon = "🚪➡️" if movimento == 'ENTRATA' else "🚪⬅️"
        
        # Aggiorna status NFC temporaneamente
        feedback_text = f"{icon} {movimento}\n{badge_id} - {ora}"
        self.nfc_status.config(text=feedback_text, fg=color)
        
        # Ripristina dopo 3 secondi
        self.root.after(3000, lambda: self.nfc_status.config(
            text="🟢 Sistema Pronto", fg=COLORS['success']))
        
    def show_error_feedback(self):
        """Feedback errore"""
        self.nfc_status.config(text="❌ Errore Lettura", fg=COLORS['error'])
        self.root.after(2000, lambda: self.nfc_status.config(
            text="🟢 Sistema Pronto", fg=COLORS['success']))
        
    def show_admin(self, event=None):
        """Panel admin"""
        print("Admin panel richiesto")
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
        
    def cleanup(self):
        """Cleanup"""
        if hasattr(self, 'nfc_reader'):
            self.nfc_reader.stop_reading()
            
    def run(self):
        """Avvia app"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
            
    def on_closing(self):
        """Chiusura"""
        self.cleanup()
        self.root.destroy()

def main():
    """Main"""
    try:
        app = TigotaTabletOptimized()
        app.run()
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
