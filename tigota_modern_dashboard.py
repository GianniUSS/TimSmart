#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOTÀ Modern Dashboard - Sistema di Timbratura
Design ispirato a interfacce tablet moderne e pulite
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import threading
import time
from nfc_manager import NFCReader, TimbratureManager

class TigotaModernDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_modern_window()
        
        # Gestori
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        self.setup_modern_dashboard()
        self.start_clock()
        self.nfc_reader.start_reading()
        
    def setup_modern_window(self):
        """Configura finestra moderna"""
        self.root.title("TIGOTÀ - Dashboard Timbratura")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#F0F2F5')  # Grigio molto chiaro moderno
        
        # Bind eventi
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F1>', self.show_admin)
        
    def setup_modern_dashboard(self):
        """Setup dashboard moderna"""
        # Container principale senza padding eccessivi
        main_container = tk.Frame(self.root, bg='#F0F2F5')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header moderno
        self.create_modern_header(main_container)
        
        # Dashboard principale
        self.create_dashboard_grid(main_container)
        
    def create_modern_header(self, parent):
        """Header moderno minimalista"""
        # Header container
        header = tk.Frame(parent, bg='#FFFFFF', height=70)
        header.pack(fill='x', pady=(0, 20))
        header.pack_propagate(False)
        
        # Content header con layout orizzontale
        header_content = tk.Frame(header, bg='#FFFFFF')
        header_content.pack(expand=True, fill='both', padx=30, pady=15)
        
        # Logo TIGOTÀ a sinistra
        logo_frame = tk.Frame(header_content, bg='#FFFFFF')
        logo_frame.pack(side='left', fill='y')
        
        logo_label = tk.Label(logo_frame,
                             text="TIGOTÀ",
                             font=('Segoe UI', 28, 'bold'),
                             bg='#FFFFFF',
                             fg='#E91E63')
        logo_label.pack(side='left', pady=5)
        
        # Separatore
        sep_label = tk.Label(logo_frame,
                           text="  |  ",
                           font=('Segoe UI', 20, 'normal'),
                           bg='#FFFFFF',
                           fg='#DDDDDD')
        sep_label.pack(side='left', pady=8)
        
        # Titolo sistema
        title_label = tk.Label(logo_frame,
                              text="Sistema Timbratura",
                              font=('Segoe UI', 16, 'normal'),
                              bg='#FFFFFF',
                              fg='#666666')
        title_label.pack(side='left', pady=8)
        
        # Status e info a destra
        info_frame = tk.Frame(header_content, bg='#FFFFFF')
        info_frame.pack(side='right', fill='y')
        
        # Status indicator
        status_label = tk.Label(info_frame,
                               text="🟢 Online",
                               font=('Segoe UI', 12, 'bold'),
                               bg='#FFFFFF',
                               fg='#4CAF50')
        status_label.pack(side='right', pady=5)
        
        # Data corrente piccola
        self.header_date = tk.Label(info_frame,
                                   text="",
                                   font=('Segoe UI', 11, 'normal'),
                                   bg='#FFFFFF',
                                   fg='#999999')
        self.header_date.pack(side='right', padx=(0, 20), pady=5)
        
    def create_dashboard_grid(self, parent):
        """Dashboard con layout a griglia moderno"""
        # Container dashboard
        dashboard = tk.Frame(parent, bg='#F0F2F5')
        dashboard.pack(expand=True, fill='both')
        
        # Grid 2x2 con proporzioni diverse
        dashboard.grid_columnconfigure(0, weight=2)  # Sinistra più grande
        dashboard.grid_columnconfigure(1, weight=1)  # Destra più piccola
        dashboard.grid_rowconfigure(0, weight=2)     # Sopra più grande
        dashboard.grid_rowconfigure(1, weight=1)     # Sotto più piccolo
        
        # Card principale - Orologio (top-left)
        self.create_clock_card(dashboard)
        
        # Card NFC (top-right)
        self.create_nfc_card(dashboard)
        
        # Card Info (bottom-left)
        self.create_info_card(dashboard)
        
        # Card Statistiche (bottom-right)
        self.create_stats_card(dashboard)
        
    def create_clock_card(self, parent):
        """Card orologio principale"""
        # Card container
        clock_card = self.create_card(parent, row=0, column=0, padx=(0, 10), pady=(0, 10))
        
        # Content
        content = tk.Frame(clock_card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=40, pady=30)
        
        # Header card
        header_frame = tk.Frame(content, bg='#FFFFFF')
        header_frame.pack(fill='x', pady=(0, 20))
        
        card_title = tk.Label(header_frame,
                             text="Ora Corrente",
                             font=('Segoe UI', 18, 'bold'),
                             bg='#FFFFFF',
                             fg='#333333')
        card_title.pack(side='left')
        
        # Status indicator
        status_dot = tk.Label(header_frame,
                             text="●",
                             font=('Arial', 12),
                             bg='#FFFFFF',
                             fg='#4CAF50')
        status_dot.pack(side='right')
        
        # Orologio grande centrale
        clock_container = tk.Frame(content, bg='#FFFFFF')
        clock_container.pack(expand=True, fill='both')
        
        # Ora principale
        self.main_time = tk.Label(clock_container,
                                 font=('Consolas', 72, 'bold'),
                                 bg='#FFFFFF',
                                 fg='#E91E63')
        self.main_time.pack(expand=True)
        
        # Data sotto l'ora
        self.main_date = tk.Label(clock_container,
                                 font=('Segoe UI', 20, 'normal'),
                                 bg='#FFFFFF',
                                 fg='#666666')
        self.main_date.pack(pady=(10, 0))
        
    def create_nfc_card(self, parent):
        """Card NFC moderna"""
        # Card container
        nfc_card = self.create_card(parent, row=0, column=1, padx=(10, 0), pady=(0, 10))
        
        # Content
        content = tk.Frame(nfc_card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=30, pady=25)
        
        # Header
        header_frame = tk.Frame(content, bg='#FFFFFF')
        header_frame.pack(fill='x', pady=(0, 15))
        
        nfc_title = tk.Label(header_frame,
                            text="Badge Access",
                            font=('Segoe UI', 16, 'bold'),
                            bg='#FFFFFF',
                            fg='#333333')
        nfc_title.pack()
        
        # Icona NFC grande
        icon_frame = tk.Frame(content, bg='#F8F9FA', width=100, height=100)
        icon_frame.pack(pady=20)
        icon_frame.pack_propagate(False)
        
        nfc_icon = tk.Label(icon_frame,
                           text="🏷️",
                           font=('Apple Color Emoji', 40),
                           bg='#F8F9FA')
        nfc_icon.pack(expand=True)
        
        # Istruzioni
        instructions = tk.Label(content,
                               text="Avvicina il badge\nal sensore NFC",
                               font=('Segoe UI', 12, 'normal'),
                               bg='#FFFFFF',
                               fg='#666666',
                               justify='center')
        instructions.pack(pady=(10, 15))
        
        # Status NFC
        self.nfc_status = tk.Label(content,
                                  text="🟢 Pronto",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#FFFFFF',
                                  fg='#4CAF50')
        self.nfc_status.pack()
        
    def create_info_card(self, parent):
        """Card informazioni"""
        # Card container
        info_card = self.create_card(parent, row=1, column=0, padx=(0, 10), pady=(10, 0))
        
        # Content
        content = tk.Frame(info_card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=30, pady=20)
        
        # Header
        info_title = tk.Label(content,
                             text="Informazioni Sistema",
                             font=('Segoe UI', 14, 'bold'),
                             bg='#FFFFFF',
                             fg='#333333')
        info_title.pack(anchor='w', pady=(0, 15))
        
        # Info grid
        info_frame = tk.Frame(content, bg='#FFFFFF')
        info_frame.pack(fill='x')
        
        # Ultima timbratura
        last_label = tk.Label(info_frame,
                             text="Ultima timbratura:",
                             font=('Segoe UI', 10, 'normal'),
                             bg='#FFFFFF',
                             fg='#666666')
        last_label.pack(anchor='w')
        
        self.last_time = tk.Label(info_frame,
                                 text="Nessuna timbratura oggi",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg='#FFFFFF',
                                 fg='#333333')
        self.last_time.pack(anchor='w', pady=(2, 10))
        
        # Versione software
        version_label = tk.Label(info_frame,
                                text="Software:",
                                font=('Segoe UI', 10, 'normal'),
                                bg='#FFFFFF',
                                fg='#666666')
        version_label.pack(anchor='w')
        
        version_value = tk.Label(info_frame,
                                text="SmartTIM v3.0 Dashboard",
                                font=('Segoe UI', 10, 'bold'),
                                bg='#FFFFFF',
                                fg='#E91E63')
        version_value.pack(anchor='w')
        
    def create_stats_card(self, parent):
        """Card statistiche"""
        # Card container
        stats_card = self.create_card(parent, row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        # Content
        content = tk.Frame(stats_card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=25, pady=20)
        
        # Header
        stats_title = tk.Label(content,
                              text="Oggi",
                              font=('Segoe UI', 14, 'bold'),
                              bg='#FFFFFF',
                              fg='#333333')
        stats_title.pack(anchor='w', pady=(0, 15))
        
        # Stats
        stats_frame = tk.Frame(content, bg='#FFFFFF')
        stats_frame.pack(fill='x')
        
        # Timbrature oggi
        timb_label = tk.Label(stats_frame,
                             text="Timbrature:",
                             font=('Segoe UI', 10, 'normal'),
                             bg='#FFFFFF',
                             fg='#666666')
        timb_label.pack(anchor='w')
        
        self.timb_count = tk.Label(stats_frame,
                                  text="0",
                                  font=('Segoe UI', 18, 'bold'),
                                  bg='#FFFFFF',
                                  fg='#4CAF50')
        self.timb_count.pack(anchor='w', pady=(2, 10))
        
        # Status
        status_label = tk.Label(stats_frame,
                               text="Sistema:",
                               font=('Segoe UI', 10, 'normal'),
                               bg='#FFFFFF',
                               fg='#666666')
        status_label.pack(anchor='w')
        
        status_value = tk.Label(stats_frame,
                               text="Operativo",
                               font=('Segoe UI', 10, 'bold'),
                               bg='#FFFFFF',
                               fg='#4CAF50')
        status_value.pack(anchor='w')
        
    def create_card(self, parent, row, column, padx=5, pady=5):
        """Crea una card moderna con ombra leggera"""
        # Shadow
        shadow = tk.Frame(parent, bg='#E0E4E8', height=2)
        shadow.grid(row=row, column=column, sticky='ew', 
                   padx=(padx[0]+2 if isinstance(padx, tuple) else padx+2,
                        padx[1]+2 if isinstance(padx, tuple) else padx+2),
                   pady=(pady[0]+2 if isinstance(pady, tuple) else pady+2,
                        pady[1] if isinstance(pady, tuple) else pady))
        
        # Main card
        card = tk.Frame(parent, bg='#FFFFFF', relief='flat', bd=0)
        card.grid(row=row, column=column, sticky='nsew', padx=padx, pady=pady)
        
        return card
        
    def start_clock(self):
        """Avvia orologio"""
        self.update_clock()
        
    def update_clock(self):
        """Aggiorna tutti gli orologi"""
        now = datetime.now()
        
        # Formati
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        header_date_str = now.strftime("%d/%m/%Y")
        
        # Aggiorna widgets
        if hasattr(self, 'main_time'):
            self.main_time.config(text=time_str)
        if hasattr(self, 'main_date'):
            self.main_date.config(text=date_str.title())
        if hasattr(self, 'header_date'):
            self.header_date.config(text=header_date_str)
        
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
            
            # Feedback moderno
            self.show_modern_feedback(timbratura)
            
            # Aggiorna statistiche
            self.update_stats()
            
        except Exception as e:
            print(f"Errore badge: {e}")
            self.show_error_feedback()
            
    def show_modern_feedback(self, timbratura):
        """Feedback moderno"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        if movimento == 'ENTRATA':
            icon = "✅"
            color = '#4CAF50'
            text = f"{icon} Ingresso\n{badge_id}"
        else:
            icon = "🚪"
            color = '#FF9800'
            text = f"{icon} Uscita\n{badge_id}"
        
        # Aggiorna NFC status
        self.nfc_status.config(text=text, fg=color)
        
        # Aggiorna ultima timbratura
        self.last_time.config(text=f"{movimento} - {ora}")
        
        # Ripristina dopo 4 secondi
        self.root.after(4000, lambda: self.nfc_status.config(
            text="🟢 Pronto", fg='#4CAF50'))
        
    def show_error_feedback(self):
        """Feedback errore"""
        self.nfc_status.config(text="❌ Errore", fg='#F44336')
        self.root.after(3000, lambda: self.nfc_status.config(
            text="🟢 Pronto", fg='#4CAF50'))
        
    def update_stats(self):
        """Aggiorna statistiche"""
        # Conta timbrature di oggi (simulato)
        count = getattr(self, '_daily_count', 0) + 1
        self._daily_count = count
        self.timb_count.config(text=str(count))
        
    def show_admin(self, event=None):
        """Panel admin"""
        print("Dashboard admin richiesto")
        
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
    """Main function"""
    try:
        app = TigotaModernDashboard()
        app.run()
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
