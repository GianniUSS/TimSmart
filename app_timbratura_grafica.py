#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Timbratura TIGOTA - Versione Grafica Avanzata
Design moderno con elementi grafici personalizzati TIGOTA
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import threading
import time
from nfc_manager import NFCReader, TimbratureManager
from config import COLORS, TEXTS, FONTS, NFC_CONFIG, WINDOW_CONFIG
from tigota_graphics import TigotaGraphics

class AppTimbraturaGrafica:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_colors()
        
        # Inizializza gestori NFC e timbrature
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        self.setup_modern_ui()
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
        
        # Bind per controlli
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Button-3>', self.show_admin_menu)  # Click destro per menu admin
        
    def setup_colors(self):
        """Definisce la palette di colori TIGOTA"""
        self.colors = COLORS
        
    def setup_modern_ui(self):
        """Configura l'interfaccia utente ultra-moderna"""
        # Container principale
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header grafico
        self.create_graphic_header(main_container)
        
        # Centro con layout avanzato
        self.create_advanced_center(main_container)
        
        # Footer grafico
        self.create_graphic_footer(main_container)
        
    def create_graphic_header(self, parent):
        """Crea header con grafica TIGOTA personalizzata"""
        header_frame = tk.Frame(parent, bg=self.colors['background'], height=160)
        header_frame.pack(fill='x', pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Logo TIGOTA con grafica personalizzata
        logo_container = tk.Frame(header_frame, bg=self.colors['background'])
        logo_container.pack(expand=True, fill='both', padx=100)
        
        # Crea logo grafico
        self.tigota_logo = TigotaGraphics.create_tigota_logo(logo_container, 600, 120)
        self.tigota_logo.pack(expand=True)
        
        # Bordo decorativo sotto il logo
        border_container = tk.Frame(header_frame, bg=self.colors['background'])
        border_container.pack(fill='x', padx=200, pady=(10, 0))
        
        self.header_border = TigotaGraphics.create_decorative_border(border_container, 800)
        self.header_border.pack()
        
    def create_advanced_center(self, parent):
        """Crea sezione centrale con layout avanzato"""
        center_frame = tk.Frame(parent, bg=self.colors['background'])
        center_frame.pack(expand=True, fill='both', pady=30)
        
        # Grid layout per organizzazione migliore
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=0)
        
        # Sezione data/ora principale
        datetime_section = tk.Frame(center_frame, bg=self.colors['background'])
        datetime_section.grid(row=0, column=0, sticky='nsew', padx=50)
        
        self.create_datetime_display(datetime_section)
        
        # Sezione NFC laterale
        nfc_section = tk.Frame(center_frame, bg=self.colors['background'])
        nfc_section.grid(row=0, column=1, sticky='nse', padx=50)
        
        self.create_advanced_nfc_section(nfc_section)
        
    def create_datetime_display(self, parent):
        """Crea display data/ora avanzato"""
        # Container principale per data/ora
        datetime_container = tk.Frame(parent, bg=self.colors['card_bg'], 
                                     relief='flat', bd=0)
        datetime_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Padding interno
        datetime_inner = tk.Frame(datetime_container, bg=self.colors['card_bg'])
        datetime_inner.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Bordo superiore decorativo
        top_border_container = tk.Frame(datetime_inner, bg=self.colors['card_bg'])
        top_border_container.pack(fill='x', pady=(0, 30))
        
        self.datetime_border = TigotaGraphics.create_decorative_border(
            top_border_container, 600, COLORS['tigota_pink'])
        self.datetime_border.pack()
        
        # Data elegante
        date_container = tk.Frame(datetime_inner, bg=self.colors['card_bg'])
        date_container.pack(fill='x', pady=(0, 20))
        
        self.date_label = tk.Label(date_container, 
                                  font=FONTS['date'],
                                  bg=self.colors['card_bg'], 
                                  fg=self.colors['text'],
                                  justify='center')
        self.date_label.pack()
        
        # Ora prominente
        time_container = tk.Frame(datetime_inner, bg=self.colors['card_bg'])
        time_container.pack(fill='x', pady=20)
        
        self.time_label = tk.Label(time_container, 
                                  font=FONTS['time'],
                                  bg=self.colors['card_bg'], 
                                  fg=self.colors['tigota_pink'],
                                  justify='center')
        self.time_label.pack()
        
        # Indicatore digitale
        digital_indicator = tk.Label(datetime_inner, 
                                   text="• SISTEMA ATTIVO •", 
                                   font=('Consolas', 12, 'bold'),
                                   bg=self.colors['card_bg'], 
                                   fg=self.colors['success'])
        digital_indicator.pack(pady=(20, 0))
        
        # Bordo inferiore decorativo
        bottom_border_container = tk.Frame(datetime_inner, bg=self.colors['card_bg'])
        bottom_border_container.pack(fill='x', pady=(30, 0))
        
        self.datetime_border_bottom = TigotaGraphics.create_decorative_border(
            bottom_border_container, 600, COLORS['tigota_pink'])
        self.datetime_border_bottom.pack()
        
    def create_advanced_nfc_section(self, parent):
        """Crea sezione NFC avanzata"""
        # Container NFC principale
        nfc_main_container = tk.Frame(parent, bg=self.colors['card_bg'], 
                                     relief='flat', bd=0, width=300)
        nfc_main_container.pack(pady=20, padx=20)
        nfc_main_container.pack_propagate(False)
        
        # Padding interno
        self.nfc_container = tk.Frame(nfc_main_container, bg=self.colors['card_bg'])
        self.nfc_container.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Icona NFC grafica personalizzata
        icon_container = tk.Frame(self.nfc_container, bg=self.colors['card_bg'])
        icon_container.pack(pady=(0, 20))
        
        self.nfc_icon_canvas = TigotaGraphics.create_nfc_icon(icon_container, 100)
        self.nfc_icon_canvas.pack()
        
        # Titolo sezione
        nfc_title = tk.Label(self.nfc_container, text="NFC READER", 
                           font=('Segoe UI', 16, 'bold'),
                           bg=self.colors['card_bg'], 
                           fg=self.colors['tigota_pink'])
        nfc_title.pack(pady=(0, 10))
        
        # Testo istruzione
        self.nfc_text = tk.Label(self.nfc_container, text=TEXTS['nfc_instruction'], 
                               font=FONTS['nfc_text'],
                               bg=self.colors['card_bg'], 
                               fg=self.colors['text'],
                               wraplength=200, justify='center')
        self.nfc_text.pack(pady=(0, 15))
        
        # Indicatore di stato grafico
        status_container = tk.Frame(self.nfc_container, bg=self.colors['card_bg'])
        status_container.pack()
        
        self.status_indicator = TigotaGraphics.create_status_indicator(
            status_container, "tigota", 16)
        self.status_indicator.pack()
        
        # Area feedback timbrature
        self.feedback_container = tk.Frame(self.nfc_container, bg=self.colors['card_bg'])
        self.feedback_container.pack(fill='x', pady=(20, 0))
        
        # Inizialmente nascosto
        self.feedback_container.pack_forget()
        
    def create_graphic_footer(self, parent):
        """Crea footer con elementi grafici"""
        footer_frame = tk.Frame(parent, bg=self.colors['background'], height=100)
        footer_frame.pack(fill='x', side='bottom', pady=(30, 0))
        footer_frame.pack_propagate(False)
        
        # Container footer
        footer_content = tk.Frame(footer_frame, bg=self.colors['background'])
        footer_content.pack(fill='both', expand=True, padx=40)
        
        # Slogan TIGOTA a sinistra
        slogan_container = tk.Frame(footer_content, bg=self.colors['background'])
        slogan_container.pack(side='left', pady=20)
        
        slogan_label = tk.Label(slogan_container, 
                              text="Belli, Puliti, Profumati", 
                              font=('Segoe UI', 18, 'italic'),
                              bg=self.colors['background'], 
                              fg=self.colors['tigota_pink'])
        slogan_label.pack()
        
        # Info software a destra
        software_container = tk.Frame(footer_content, bg=self.colors['card_bg'],
                                     relief='flat', bd=0, padx=30, pady=15)
        software_container.pack(side='right', pady=20)
        
        # Bordo superiore per software
        soft_border_container = tk.Frame(software_container, bg=self.colors['card_bg'])
        soft_border_container.pack(fill='x', pady=(0, 10))
        
        self.software_border = TigotaGraphics.create_decorative_border(
            soft_border_container, 200, COLORS['tigota_pink'])
        self.software_border.pack()
        
        # Nome e versione software
        software_label = tk.Label(software_container, 
                                text=TEXTS['software_name'], 
                                font=FONTS['software_name'],
                                bg=self.colors['card_bg'], 
                                fg=self.colors['tigota_pink'])
        software_label.pack()
        
        version_label = tk.Label(software_container, 
                               text=TEXTS['software_version'], 
                               font=FONTS['software_version'],
                               bg=self.colors['card_bg'], 
                               fg=self.colors['text'])
        version_label.pack()
        
    def update_clock(self):
        """Aggiorna data e ora con animazioni"""
        now = datetime.now()
        
        # Formato data italiana
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        
        # Formato ora
        time_str = now.strftime("%H:%M:%S")
        
        # Aggiorna labels
        self.date_label.config(text=date_str.upper())
        self.time_label.config(text=time_str)
        
        # Aggiorna ogni secondo
        self.root.after(1000, self.update_clock)
        
    def translate_date(self, date_str):
        """Traduce i nomi dei giorni e mesi in italiano"""
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
        """Gestisce la lettura del badge con feedback avanzato"""
        try:
            # Registra timbratura
            timbratura = self.timbrature_manager.registra_timbratura(badge_id)
            
            # Feedback visivo avanzato
            self.show_advanced_feedback(timbratura)
            
        except Exception as e:
            print(f"Errore gestione badge: {e}")
            self.show_error_feedback()
            
    def show_advanced_feedback(self, timbratura):
        """Mostra feedback visivo avanzato"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        # Mostra area feedback
        self.feedback_container.pack(fill='x', pady=(20, 0))
        
        # Pulisce feedback precedente
        for widget in self.feedback_container.winfo_children():
            widget.destroy()
        
        # Colore movimento
        color = self.colors['success'] if movimento == 'ENTRATA' else self.colors['warning']
        
        # Icona movimento
        icon_text = "🚪➡️" if movimento == 'ENTRATA' else "🚪⬅️"
        movement_icon = tk.Label(self.feedback_container, text=icon_text, 
                               font=('Segoe UI Emoji', 24, 'normal'),
                               bg=self.colors['card_bg'], fg=color)
        movement_icon.pack()
        
        # Testo movimento
        movement_label = tk.Label(self.feedback_container, text=movimento, 
                                font=('Segoe UI', 14, 'bold'),
                                bg=self.colors['card_bg'], fg=color)
        movement_label.pack(pady=(5, 0))
        
        # Badge ID
        badge_label = tk.Label(self.feedback_container, text=badge_id, 
                             font=('Consolas', 12, 'normal'),
                             bg=self.colors['card_bg'], fg=self.colors['text'])
        badge_label.pack()
        
        # Ora
        time_label = tk.Label(self.feedback_container, text=ora, 
                            font=('Consolas', 12, 'bold'),
                            bg=self.colors['card_bg'], fg=self.colors['tigota_pink'])
        time_label.pack()
        
        # Effetto flash su contenitore NFC
        self.flash_nfc_container(color)
        
        # Nasconde feedback dopo timeout
        self.root.after(NFC_CONFIG['feedback_duration'], self.hide_feedback)
        
    def flash_nfc_container(self, color):
        """Effetto flash sul container NFC"""
        original_bg = self.nfc_container.cget('bg')
        
        # Flash colorato
        self.nfc_container.config(bg=self.colors['tigota_light'])
        self.root.after(200, lambda: self.nfc_container.config(bg=original_bg))
        
    def hide_feedback(self):
        """Nasconde l'area feedback"""
        self.feedback_container.pack_forget()
        
    def show_error_feedback(self):
        """Mostra feedback di errore"""
        # Implementazione simile ma per errori
        pass
        
    def show_admin_menu(self, event=None):
        """Mostra menu amministratore (click destro)"""
        admin_menu = tk.Menu(self.root, tearoff=0)
        admin_menu.add_command(label="📊 Visualizza Timbrature", command=self.show_timbrature)
        admin_menu.add_command(label="⚙️ Impostazioni", command=self.show_settings)
        admin_menu.add_separator()
        admin_menu.add_command(label="🚪 Esci", command=self.on_closing)
        
        try:
            admin_menu.tk_popup(event.x_root, event.y_root)
        finally:
            admin_menu.grab_release()
            
    def show_timbrature(self):
        """Mostra finestra timbrature"""
        messagebox.showinfo("Timbrature", "Funzionalità in sviluppo")
        
    def show_settings(self):
        """Mostra finestra impostazioni"""
        messagebox.showinfo("Impostazioni", "Funzionalità in sviluppo")
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def cleanup(self):
        """Pulizia risorse"""
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
        """Gestisce chiusura"""
        self.cleanup()
        self.root.destroy()

def main():
    """Funzione principale"""
    try:
        app = AppTimbraturaGrafica()
        app.run()
    except Exception as e:
        print(f"Errore avvio applicazione: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
