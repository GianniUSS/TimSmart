#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Timbratura TIGOTÀ - Versione Tablet Touch
Interfaccia ottimizzata per tablet touch nei negozi TIGOTÀ
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import threading
import time
import math
from nfc_manager import NFCReader, TimbratureManager
from config_tablet import COLORS, TEXTS, FONTS, NFC_CONFIG, WINDOW_CONFIG, TABLET_CONFIG
from tigota_tablet_graphics import TigotaTabletGraphics

class TigotaTabletApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Inizializza gestori
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        # Stato applicazione
        self.current_screen = "home"
        self.last_activity = time.time()
        self.feedback_popup = None
        
        self.setup_tablet_ui()
        self.start_systems()
        
    def setup_window(self):
        """Configura finestra per tablet"""
        self.root.title(WINDOW_CONFIG['title'])
        
        if WINDOW_CONFIG['fullscreen']:
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry(WINDOW_CONFIG['geometry'])
            self.root.resizable(False, False)
        
        self.root.configure(bg=COLORS['background'])
        
        # Hide cursor su tablet
        if WINDOW_CONFIG.get('hide_cursor', False):
            self.root.configure(cursor="none")
        
        # Bind eventi
        self.root.bind('<Button-1>', self.on_touch)
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F1>', self.show_admin_panel)
        
    def setup_tablet_ui(self):
        """Configura UI ottimizzata per tablet"""
        # Container principale
        self.main_container = tk.Frame(self.root, bg=COLORS['background'])
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Layout principale
        self.create_tablet_header()
        self.create_tablet_main_area()
        self.create_tablet_footer()
        
    def create_tablet_header(self):
        """Crea header moderno per tablet"""
        header_height = 140
        
        # Shadow container per header
        header_shadow, self.header_frame = TigotaTabletGraphics.create_modern_card(
            self.main_container, TABLET_CONFIG['screen_width']-40, header_height,
            COLORS['card_bg'], 6)
        header_shadow.pack(fill='x', pady=(0, 20))
        
        # Logo TIGOTÀ moderno
        logo_container = tk.Frame(self.header_frame, bg=COLORS['card_bg'])
        logo_container.pack(expand=True, fill='both', pady=10)
        
        self.logo_canvas = TigotaTabletGraphics.create_tigota_logo_modern(
            logo_container, 600, 120)
        self.logo_canvas.pack(expand=True)
        
    def create_tablet_main_area(self):
        """Crea area principale con layout tablet"""
        main_height = TABLET_CONFIG['screen_height'] - 300  # Header + Footer
        
        # Container principale
        main_area = tk.Frame(self.main_container, bg=COLORS['background'])
        main_area.pack(expand=True, fill='both', pady=15)
        
        # Layout a due colonne per tablet con più spazio per la data
        main_area.grid_columnconfigure(0, weight=3)  # Colonna sinistra più grande
        main_area.grid_columnconfigure(1, weight=2)  # Colonna destra
        main_area.grid_rowconfigure(0, weight=1)
        
        # Sezione data/ora (sinistra)
        self.create_datetime_section(main_area)
        
        # Sezione NFC (destra)
        self.create_nfc_section_tablet(main_area)
        
    def create_datetime_section(self, parent):
        """Crea sezione data/ora per tablet"""
        # Card per data/ora con dimensioni maggiori
        datetime_shadow, datetime_frame = TigotaTabletGraphics.create_modern_card(
            parent, 600, 320, COLORS['card_bg'], 8)  # Aumentato larghezza e altezza
        datetime_shadow.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        
        # Contenuto data/ora
        content_frame = tk.Frame(datetime_frame, bg=COLORS['card_bg'])
        content_frame.pack(expand=True, fill='both', padx=30, pady=25)  # Ridotto padding
        
        # Indicatore sistema
        status_frame = tk.Frame(content_frame, bg=COLORS['card_bg'])
        status_frame.pack(fill='x', pady=(0, 15))
        
        self.system_status = TigotaTabletGraphics.create_status_indicator_modern(
            status_frame, "active", 25)
        self.system_status.pack(anchor='w')
        
        # Data moderna con wraplength per evitare troncamenti
        self.date_label = tk.Label(content_frame,
                                  font=FONTS['date'],
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['text'],
                                  justify='center',
                                  wraplength=550)  # Aggiunto wraplength
        self.date_label.pack(pady=(0, 15))
        
        # Ora prominente
        self.time_label = tk.Label(content_frame,
                                  font=FONTS['time'],
                                  bg=COLORS['card_bg'],
                                  fg=COLORS['tigota_pink'],
                                  justify='center')
        self.time_label.pack(pady=(0, 15))
        
        # Slogan TIGOTÀ
        slogan_label = tk.Label(content_frame, text=TEXTS['slogan'],
                               font=FONTS['slogan'],
                               bg=COLORS['card_bg'],
                               fg=COLORS['text_light'],
                               justify='center',
                               wraplength=550)  # Aggiunto wraplength
        slogan_label.pack()
        
    def create_nfc_section_tablet(self, parent):
        """Crea sezione NFC ottimizzata per tablet"""
        # Card NFC
        nfc_shadow, self.nfc_frame = TigotaTabletGraphics.create_modern_card(
            parent, 350, 300, COLORS['card_bg'], 8)
        nfc_shadow.grid(row=0, column=1, sticky='nsew')
        
        # Contenuto NFC
        nfc_content = tk.Frame(self.nfc_frame, bg=COLORS['card_bg'])
        nfc_content.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Titolo NFC
        nfc_title = tk.Label(nfc_content, text=TEXTS['nfc_title'],
                           font=FONTS['nfc_title'],
                           bg=COLORS['card_bg'],
                           fg=COLORS['tigota_pink'])
        nfc_title.pack(pady=(0, 10))
        
        # Zona NFC touch
        nfc_zone_container = tk.Frame(nfc_content, bg=COLORS['card_bg'])
        nfc_zone_container.pack(expand=True, pady=20)
        
        self.nfc_zone = TigotaTabletGraphics.create_nfc_zone_modern(
            nfc_zone_container, 180)
        self.nfc_zone.pack()
        
        # Bind touch sulla zona NFC
        self.nfc_zone.bind('<Button-1>', self.simulate_nfc_touch)
        
        # Istruzioni
        self.nfc_instruction = tk.Label(nfc_content, text=TEXTS['nfc_subtitle'],
                                      font=('Segoe UI', 12, 'normal'),
                                      bg=COLORS['card_bg'],
                                      fg=COLORS['text_light'],
                                      wraplength=280, justify='center')
        self.nfc_instruction.pack(pady=(10, 0))
        
        # Status NFC
        self.nfc_status_label = tk.Label(nfc_content, text=TEXTS['nfc_active'],
                                       font=('Segoe UI', 14, 'bold'),
                                       bg=COLORS['card_bg'],
                                       fg=COLORS['nfc_active'])
        self.nfc_status_label.pack(pady=(10, 0))
        
    def create_tablet_footer(self):
        """Crea footer per tablet"""
        footer_height = 80
        
        # Footer shadow
        footer_shadow, footer_frame = TigotaTabletGraphics.create_modern_card(
            self.main_container, TABLET_CONFIG['screen_width']-40, footer_height,
            COLORS['card_bg'], 4)
        footer_shadow.pack(fill='x', pady=(20, 0))
        
        # Contenuto footer
        footer_content = tk.Frame(footer_frame, bg=COLORS['card_bg'])
        footer_content.pack(expand=True, fill='both', padx=30, pady=15)
        
        # Informazioni software (sinistra)
        info_frame = tk.Frame(footer_content, bg=COLORS['card_bg'])
        info_frame.pack(side='left', anchor='w')
        
        software_label = tk.Label(info_frame, text=TEXTS['software_name'],
                                 font=('Segoe UI', 16, 'bold'),
                                 bg=COLORS['card_bg'],
                                 fg=COLORS['tigota_pink'])
        software_label.pack(anchor='w')
        
        version_label = tk.Label(info_frame, text=TEXTS['software_version'],
                               font=('Segoe UI', 12, 'normal'),
                               bg=COLORS['card_bg'],
                               fg=COLORS['text_light'])
        version_label.pack(anchor='w')
        
        # Pulsante admin (destra)
        admin_container, self.admin_button = TigotaTabletGraphics.create_touch_button(
            footer_content, "⚙️ Admin", self.show_admin_panel,
            COLORS['text_light'], 120, 40)
        admin_container.pack(side='right', anchor='e')
        
    def start_systems(self):
        """Avvia tutti i sistemi"""
        self.update_clock()
        self.animate_nfc_zone()
        self.check_auto_return()
        self.nfc_reader.start_reading()
        
    def update_clock(self):
        """Aggiorna orologio con animazioni"""
        now = datetime.now()
        
        # Data italiana
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        
        # Ora
        time_str = now.strftime("%H:%M:%S")
        
        self.date_label.config(text=date_str.upper())
        self.time_label.config(text=time_str)
        
        # Aggiorna ogni secondo
        self.root.after(1000, self.update_clock)
        
    def animate_nfc_zone(self):
        """Anima la zona NFC"""
        # Implementa animazione pulse sulla zona NFC
        # (animazione semplificata per ora)
        self.root.after(2000, self.animate_nfc_zone)
        
    def check_auto_return(self):
        """Controlla ritorno automatico alla home"""
        if time.time() - self.last_activity > TABLET_CONFIG['auto_return_home'] / 1000:
            self.return_to_home()
        
        self.root.after(5000, self.check_auto_return)
        
    def on_touch(self, event=None):
        """Gestisce eventi touch"""
        self.last_activity = time.time()
        
    def simulate_nfc_touch(self, event=None):
        """Simula touch sulla zona NFC (per test)"""
        if NFC_CONFIG['simulation_mode']:
            # Simula lettura badge per test
            test_badges = ["EMP001", "EMP002", "EMP003", "ADM001"]
            import random
            badge_id = random.choice(test_badges)
            self.on_badge_read(badge_id)
        
    def on_badge_read(self, badge_id):
        """Gestisce lettura badge NFC"""
        try:
            # Aggiorna status
            self.nfc_status_label.config(text=TEXTS['nfc_reading'],
                                       fg=COLORS['warning'])
            
            # Registra timbratura
            timbratura = self.timbrature_manager.registra_timbratura(badge_id)
            
            # Mostra feedback
            self.show_tablet_feedback(timbratura)
            
            # Ripristina status dopo delay
            self.root.after(2000, self.reset_nfc_status)
            
        except Exception as e:
            print(f"Errore timbratura: {e}")
            self.show_error_feedback()
            
    def show_tablet_feedback(self, timbratura):
        """Mostra feedback ottimizzato per tablet"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        timestamp = timbratura['ora']
        
        # Chiude popup precedente se esiste
        if self.feedback_popup:
            try:
                self.feedback_popup.destroy()
            except:
                pass
        
        # Crea nuovo popup
        self.feedback_popup = TigotaTabletGraphics.create_feedback_popup(
            self.root, movimento, badge_id, timestamp)
        
        # Auto-chiudi popup
        self.root.after(TABLET_CONFIG['feedback_duration'], self.close_feedback_popup)
        
    def close_feedback_popup(self):
        """Chiude popup feedback"""
        if self.feedback_popup:
            try:
                self.feedback_popup.destroy()
                self.feedback_popup = None
            except:
                pass
                
    def show_error_feedback(self):
        """Mostra feedback errore"""
        self.nfc_status_label.config(text=TEXTS['nfc_error'],
                                   fg=COLORS['error'])
        self.root.after(3000, self.reset_nfc_status)
        
    def reset_nfc_status(self):
        """Ripristina status NFC"""
        self.nfc_status_label.config(text=TEXTS['nfc_active'],
                                   fg=COLORS['nfc_active'])
        
    def show_admin_panel(self, event=None):
        """Mostra pannello amministratore"""
        # TODO: Implementare pannello admin
        print("Admin panel richiesto")
        
    def return_to_home(self):
        """Ritorna alla schermata home"""
        self.current_screen = "home"
        self.last_activity = time.time()
        
    def translate_date(self, date_str):
        """Traduce data in italiano"""
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
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def cleanup(self):
        """Pulizia risorse"""
        if hasattr(self, 'nfc_reader'):
            self.nfc_reader.stop_reading()
        if self.feedback_popup:
            try:
                self.feedback_popup.destroy()
            except:
                pass
                
    def run(self):
        """Avvia applicazione"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
            
    def on_closing(self):
        """Gestisce chiusura"""
        self.cleanup()
        self.root.destroy()

def main():
    """Funzione principale"""
    try:
        app = TigotaTabletApp()
        app.run()
    except Exception as e:
        print(f"Errore avvio app tablet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
