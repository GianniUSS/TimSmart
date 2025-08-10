#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOTÀ Professional - Sistema di Timbratura Aziendale
Design professionale per ambienti corporate
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import threading
import time
from nfc_manager import NFCReader, TimbratureManager

class TigotaProfessional:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_professional_window()
        
        # Gestori
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        self.setup_professional_ui()
        self.start_clock()
        self.nfc_reader.start_reading()
        
    def setup_professional_window(self):
        """Configura finestra professionale"""
        self.root.title("TIGOTÀ - Sistema di Timbratura Aziendale")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#F5F7FA')  # Grigio molto chiaro professional
        
        # Bind eventi
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F1>', self.show_admin)
        
    def setup_professional_ui(self):
        """UI professionale moderna"""
        # Container principale
        main_container = tk.Frame(self.root, bg='#F5F7FA')
        main_container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header aziendale elegante
        self.create_professional_header(main_container)
        
        # Corpo principale con design moderno
        self.create_professional_body(main_container)
        
        # Footer aziendale discreto
        self.create_professional_footer(main_container)
        
    def create_professional_header(self, parent):
        """Header aziendale professionale"""
        # Container header con sfondo bianco e bordo sottile
        header_container = tk.Frame(parent, bg='#FFFFFF', height=100)
        header_container.pack(fill='x', pady=(0, 40))
        header_container.pack_propagate(False)
        
        # Linea decorativa superiore TIGOTÀ
        top_line = tk.Frame(header_container, bg='#E91E63', height=4)
        top_line.pack(fill='x')
        
        # Content header
        content_frame = tk.Frame(header_container, bg='#FFFFFF')
        content_frame.pack(expand=True, fill='both', padx=60, pady=20)
        
        # Layout orizzontale: logo a sinistra, info a destra
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Sezione logo sinistra
        logo_frame = tk.Frame(content_frame, bg='#FFFFFF')
        logo_frame.grid(row=0, column=0, sticky='w')
        
        # Logo TIGOTÀ professionale
        logo_label = tk.Label(logo_frame, 
                             text="TIGOTÀ",
                             font=('Segoe UI', 42, 'bold'),
                             bg='#FFFFFF',
                             fg='#E91E63')
        logo_label.pack(side='left')
        
        # Separatore verticale elegante
        separator = tk.Label(logo_frame,
                           text=" | ",
                           font=('Segoe UI', 32, 'normal'),
                           bg='#FFFFFF',
                           fg='#CCCCCC')
        separator.pack(side='left', padx=10)
        
        # Sottotitolo sistema
        subtitle = tk.Label(logo_frame,
                          text="Sistema di Timbratura",
                          font=('Segoe UI', 16, 'normal'),
                          bg='#FFFFFF',
                          fg='#666666')
        subtitle.pack(side='left')
        
        # Sezione info destra
        info_frame = tk.Frame(content_frame, bg='#FFFFFF')
        info_frame.grid(row=0, column=1, sticky='e')
        
        # Status sistema
        status_label = tk.Label(info_frame,
                               text="● SISTEMA OPERATIVO",
                               font=('Segoe UI', 12, 'bold'),
                               bg='#FFFFFF',
                               fg='#4CAF50')
        status_label.pack(anchor='e')
        
        # Versione software
        version_label = tk.Label(info_frame,
                                text="SmartTIM Enterprise v3.0",
                                font=('Segoe UI', 10, 'normal'),
                                bg='#FFFFFF',
                                fg='#999999')
        version_label.pack(anchor='e', pady=(5, 0))
        
    def create_professional_body(self, parent):
        """Corpo principale professionale"""
        # Container corpo con layout moderno
        body_container = tk.Frame(parent, bg='#F5F7FA')
        body_container.pack(expand=True, fill='both')
        
        # Grid layout 70/30 - professionale
        body_container.grid_columnconfigure(0, weight=7)  # 70% datetime
        body_container.grid_columnconfigure(1, weight=3)  # 30% nfc
        body_container.grid_rowconfigure(0, weight=1)
        
        # Sezione datetime principale
        self.create_datetime_professional(body_container)
        
        # Sezione NFC laterale
        self.create_nfc_professional(body_container)
        
    def create_datetime_professional(self, parent):
        """Sezione data/ora professionale"""
        # Card principale con design moderno
        datetime_card = self.create_modern_card(parent, row=0, column=0, padx=(0, 20))
        
        # Content con spaziatura professionale
        content = tk.Frame(datetime_card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=60, pady=50)
        
        # Header della card con status
        header_frame = tk.Frame(content, bg='#FFFFFF')
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Indicatore status elegante
        status_container = tk.Frame(header_frame, bg='#FFFFFF')
        status_container.pack(side='left')
        
        status_indicator = tk.Label(status_container,
                                   text="●",
                                   font=('Arial', 14),
                                   bg='#FFFFFF',
                                   fg='#4CAF50')
        status_indicator.pack(side='left')
        
        status_text = tk.Label(status_container,
                              text="SISTEMA ATTIVO",
                              font=('Segoe UI', 12, 'bold'),
                              bg='#FFFFFF',
                              fg='#4CAF50')
        status_text.pack(side='left', padx=(8, 0))
        
        # Timestamp sistema a destra
        timestamp_label = tk.Label(header_frame,
                                  text="Ultimo aggiornamento: " + datetime.now().strftime("%H:%M:%S"),
                                  font=('Segoe UI', 10, 'normal'),
                                  bg='#FFFFFF',
                                  fg='#999999')
        timestamp_label.pack(side='right')
        
        # Sezione data elegante
        date_container = tk.Frame(content, bg='#FFFFFF')
        date_container.pack(fill='x', pady=(0, 25))
        
        # Label data con tipografia professionale
        self.date_label = tk.Label(date_container,
                                  font=('Segoe UI', 24, 'normal'),
                                  bg='#FFFFFF',
                                  fg='#333333',
                                  justify='left')
        self.date_label.pack(anchor='w')
        
        # Sezione ora prominente
        time_container = tk.Frame(content, bg='#FFFFFF')
        time_container.pack(fill='x', pady=(0, 30))
        
        # Ora con design moderno
        self.time_label = tk.Label(time_container,
                                  font=('Consolas', 64, 'bold'),
                                  bg='#FFFFFF',
                                  fg='#E91E63')
        self.time_label.pack(anchor='w')
        
        # Sottotesto professionale
        subtext_label = tk.Label(content,
                                text="Sistema di rilevazione presenze automatizzato",
                                font=('Segoe UI', 14, 'italic'),
                                bg='#FFFFFF',
                                fg='#777777')
        subtext_label.pack(anchor='w')
        
    def create_nfc_professional(self, parent):
        """Sezione NFC professionale"""
        # Card NFC moderna
        nfc_card = self.create_modern_card(parent, row=0, column=1)
        
        # Content NFC
        nfc_content = tk.Frame(nfc_card, bg='#FFFFFF')
        nfc_content.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Header NFC
        nfc_header = tk.Label(nfc_content,
                             text="ACCESSO BADGE",
                             font=('Segoe UI', 18, 'bold'),
                             bg='#FFFFFF',
                             fg='#333333')
        nfc_header.pack(pady=(0, 20))
        
        # Icona NFC professionale
        nfc_icon_frame = tk.Frame(nfc_content, bg='#F8F9FA', width=120, height=120)
        nfc_icon_frame.pack(pady=(10, 20))
        nfc_icon_frame.pack_propagate(False)
        
        nfc_icon = tk.Label(nfc_icon_frame,
                           text="🏷️",
                           font=('Apple Color Emoji', 48),
                           bg='#F8F9FA')
        nfc_icon.pack(expand=True)
        
        # Istruzioni professionali
        instructions = tk.Label(nfc_content,
                               text="Avvicinare il badge\nal lettore per\nregistrare la presenza",
                               font=('Segoe UI', 12, 'normal'),
                               bg='#FFFFFF',
                               fg='#666666',
                               justify='center')
        instructions.pack(pady=(0, 20))
        
        # Status NFC con design professionale
        self.nfc_status = tk.Label(nfc_content,
                                  text="🟢 Lettore Pronto",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#FFFFFF',
                                  fg='#4CAF50')
        self.nfc_status.pack()
        
    def create_modern_card(self, parent, row, column, padx=10, pady=10):
        """Crea una card moderna con ombra"""
        # Shadow effect
        shadow = tk.Frame(parent, bg='#E0E4E7', height=3)
        shadow.grid(row=row, column=column, sticky='ew', padx=(padx[0]+3 if isinstance(padx, tuple) else padx+3, 
                   padx[1]+3 if isinstance(padx, tuple) else padx+3), 
                   pady=(pady[0]+3 if isinstance(pady, tuple) else pady+3,
                   pady[1] if isinstance(pady, tuple) else pady))
        
        # Main card
        card = tk.Frame(parent, bg='#FFFFFF', relief='flat', bd=0)
        card.grid(row=row, column=column, sticky='nsew', padx=padx, pady=pady)
        
        return card
        
    def create_professional_footer(self, parent):
        """Footer professionale"""
        footer = tk.Frame(parent, bg='#FFFFFF', height=50)
        footer.pack(fill='x', pady=(40, 0))
        footer.pack_propagate(False)
        
        # Linea decorativa superiore
        top_line = tk.Frame(footer, bg='#E91E63', height=2)
        top_line.pack(fill='x')
        
        # Content footer
        footer_content = tk.Frame(footer, bg='#FFFFFF')
        footer_content.pack(expand=True, fill='both', padx=60, pady=15)
        
        # Copyright a sinistra
        copyright_label = tk.Label(footer_content,
                                  text="© 2025 TIGOTÀ - Sistema di Timbratura Aziendale",
                                  font=('Segoe UI', 10, 'normal'),
                                  bg='#FFFFFF',
                                  fg='#999999')
        copyright_label.pack(side='left')
        
        # Info tecnico a destra
        tech_info = tk.Label(footer_content,
                            text="SmartTIM Enterprise | Versione 3.0.1",
                            font=('Segoe UI', 10, 'bold'),
                            bg='#FFFFFF',
                            fg='#E91E63')
        tech_info.pack(side='right')
        
    def start_clock(self):
        """Avvia orologio professionale"""
        self.update_clock()
        
    def update_clock(self):
        """Aggiorna orologio"""
        now = datetime.now()
        
        # Data italiana professionale
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        
        # Ora
        time_str = now.strftime("%H:%M:%S")
        
        # Aggiorna
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
        """Gestisce lettura badge professionale"""
        try:
            # Registra timbratura
            timbratura = self.timbrature_manager.registra_timbratura(badge_id)
            
            # Feedback professionale
            self.show_professional_feedback(timbratura)
            
        except Exception as e:
            print(f"Errore badge: {e}")
            self.show_error_feedback()
            
    def show_professional_feedback(self, timbratura):
        """Feedback professionale"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        # Colore e icona professionale
        if movimento == 'ENTRATA':
            color = '#4CAF50'
            icon = "✓"
            text = f"{icon} INGRESSO REGISTRATO\n{badge_id} - {ora}"
        else:
            color = '#FF9800'
            icon = "⏱"
            text = f"{icon} USCITA REGISTRATA\n{badge_id} - {ora}"
        
        # Aggiorna status NFC
        self.nfc_status.config(text=text, fg=color)
        
        # Ripristina dopo 4 secondi
        self.root.after(4000, lambda: self.nfc_status.config(
            text="🟢 Lettore Pronto", fg='#4CAF50'))
        
    def show_error_feedback(self):
        """Feedback errore professionale"""
        self.nfc_status.config(text="⚠ Errore Lettura Badge", fg='#F44336')
        self.root.after(3000, lambda: self.nfc_status.config(
            text="🟢 Lettore Pronto", fg='#4CAF50'))
        
    def show_admin(self, event=None):
        """Panel admin"""
        print("Pannello amministratore richiesto")
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
        
    def cleanup(self):
        """Cleanup"""
        if hasattr(self, 'nfc_reader'):
            self.nfc_reader.stop_reading()
            
    def run(self):
        """Avvia applicazione"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
            
    def on_closing(self):
        """Chiusura applicazione"""
        self.cleanup()
        self.root.destroy()

def main():
    """Main function"""
    try:
        app = TigotaProfessional()
        app.run()
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
