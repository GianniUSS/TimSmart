#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App per Timbratura - SmartTIM v2.0
Applicazione fullscreen con design moderno per la timbratura dipendenti
"""

import tkinter as tk
from tkinter import ttk, messagebox, Canvas
from datetime import datetime
import os
import threading
import time
import math
from nfc_manager import NFCReader, TimbratureManager
from config import COLORS, TEXTS, FONTS, NFC_CONFIG, WINDOW_CONFIG

class ModernAppTimbratura:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        
        # Inizializza gestori NFC e timbrature
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        self.setup_ui()
        self.update_clock()
        self.animate_elements()
        
        # Avvia lettura NFC
        self.nfc_reader.start_reading()
        
    def setup_window(self):
        """Configura la finestra principale con stile moderno"""
        self.root.title(WINDOW_CONFIG['title'])
        if WINDOW_CONFIG['fullscreen']:
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry(WINDOW_CONFIG['geometry'])
            self.root.resizable(WINDOW_CONFIG['resizable'], WINDOW_CONFIG['resizable'])
        
        self.root.configure(bg=COLORS['background'])
        
        # Controlli keyboard
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Control-q>', self.on_closing)
        
    def setup_styles(self):
        """Configura stili ttk moderni"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Stile per i frame
        style.configure('Modern.TFrame', 
                       background=COLORS['primary'],
                       relief='flat',
                       borderwidth=0)
        
        # Stile per le label
        style.configure('Modern.TLabel',
                       background=COLORS['primary'],
                       foreground=COLORS['text'],
                       font=FONTS['nfc_text'])
        
    def setup_ui(self):
        """Configura l'interfaccia utente moderna"""
        # Frame principale con gradiente
        main_frame = tk.Frame(self.root, bg=COLORS['background'])
        main_frame.pack(fill='both', expand=True)
        
        # Header moderno
        self.create_modern_header(main_frame)
        
        # Centro con animazioni
        self.create_modern_center(main_frame)
        
        # Footer elegante
        self.create_modern_footer(main_frame)
        
    def create_modern_header(self, parent):
        """Crea header moderno con gradiente"""
        header_frame = tk.Frame(parent, bg=COLORS['background'], height=120)
        header_frame.pack(fill='x', pady=(20, 30))
        header_frame.pack_propagate(False)
        
        # Canvas per gradiente
        header_canvas = Canvas(header_frame, height=120, 
                              bg=COLORS['background'], highlightthickness=0)
        header_canvas.pack(fill='both', expand=True, padx=40)
        
        # Crea gradiente
        self.create_gradient(header_canvas, COLORS['gradient_start'], 
                           COLORS['gradient_end'], 120)
        
        # Logo cliente con ombra
        self.logo_text = header_canvas.create_text(
            header_canvas.winfo_reqwidth()//2, 60,
            text=TEXTS['logo_cliente'],
            font=FONTS['logo_cliente'],
            fill=COLORS['text'],
            anchor='center'
        )
        
        # Effetto ombra
        header_canvas.create_text(
            header_canvas.winfo_reqwidth()//2 + 2, 62,
            text=TEXTS['logo_cliente'],
            font=FONTS['logo_cliente'],
            fill=COLORS['primary'],
            anchor='center'
        )
        
        # Riposiziona il testo principale sopra l'ombra
        header_canvas.tag_raise(self.logo_text)
        
    def create_gradient(self, canvas, color1, color2, height):
        """Crea un gradiente su canvas"""
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        for i in range(height):
            ratio = i / height
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, canvas.winfo_reqwidth(), i, fill=color)
    
    def create_modern_center(self, parent):
        """Crea sezione centrale moderna con animazioni"""
        center_frame = tk.Frame(parent, bg=COLORS['background'])
        center_frame.pack(expand=True, fill='both', pady=40)
        
        # Container principale con bordi arrotondati simulati
        datetime_container = tk.Frame(center_frame, bg=COLORS['primary'],
                                    relief='flat', bd=0)
        datetime_container.pack(expand=True, padx=80, pady=60)
        
        # Canvas per bordi arrotondati
        self.center_canvas = Canvas(datetime_container, 
                                   bg=COLORS['primary'], 
                                   highlightthickness=0,
                                   height=300)
        self.center_canvas.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Data con animazione
        self.date_label = tk.Label(datetime_container, 
                                  font=FONTS['date'],
                                  bg=COLORS['primary'], 
                                  fg=COLORS['text'])
        self.date_label.pack(pady=(40, 10))
        
        # Ora con effetti
        self.time_label = tk.Label(datetime_container, 
                                  font=FONTS['time'],
                                  bg=COLORS['primary'], 
                                  fg=COLORS['accent'])
        self.time_label.pack(pady=(10, 40))
        
        # Indicatori di stato animati
        self.create_status_indicators(center_frame)
        
        # Area NFC moderna
        self.create_modern_nfc_section(center_frame)
        
    def create_status_indicators(self, parent):
        """Crea indicatori di stato animati"""
        status_frame = tk.Frame(parent, bg=COLORS['background'])
        status_frame.pack(side='top', pady=20)
        
        # Canvas per indicatori circolari
        self.status_canvas = Canvas(status_frame, width=200, height=50,
                                   bg=COLORS['background'], highlightthickness=0)
        self.status_canvas.pack()
        
        # Indicatori animati
        self.create_animated_indicators()
        
    def create_animated_indicators(self):
        """Crea indicatori circolari animati"""
        # Indicatore sistema attivo
        self.system_indicator = self.status_canvas.create_oval(
            10, 15, 30, 35, 
            fill=COLORS['success'], outline=COLORS['border'], width=2
        )
        
        self.status_canvas.create_text(
            40, 25, text="Sistema Attivo", 
            fill=COLORS['text'], font=FONTS['nfc_status'],
            anchor='w'
        )
        
        # Indicatore NFC
        self.nfc_indicator = self.status_canvas.create_oval(
            120, 15, 140, 35,
            fill=COLORS['accent'], outline=COLORS['border'], width=2
        )
        
        self.status_canvas.create_text(
            150, 25, text="NFC Ready",
            fill=COLORS['text'], font=FONTS['nfc_status'],
            anchor='w'
        )
        
    def create_modern_nfc_section(self, parent):
        """Crea sezione NFC moderna"""
        nfc_container = tk.Frame(parent, bg=COLORS['background'])
        nfc_container.pack(side='bottom', anchor='se', padx=40, pady=40)
        
        # Frame NFC con effetti
        self.nfc_frame = tk.Frame(nfc_container, bg=COLORS['card_bg'],
                                 relief='raised', bd=0)
        self.nfc_frame.pack(padx=10, pady=10)
        
        # Canvas per NFC con animazioni
        self.nfc_canvas = Canvas(self.nfc_frame, width=200, height=150,
                                bg=COLORS['card_bg'], highlightthickness=0)
        self.nfc_canvas.pack(padx=20, pady=20)
        
        # Icona NFC animata
        self.nfc_icon_id = self.nfc_canvas.create_text(
            100, 40, text=TEXTS['nfc_label'],
            font=FONTS['nfc_icon'], fill=COLORS['accent'],
            anchor='center'
        )
        
        # Testo istruzioni
        self.nfc_text_id = self.nfc_canvas.create_text(
            100, 80, text=TEXTS['nfc_instruction'],
            font=FONTS['nfc_text'], fill=COLORS['text'],
            anchor='center'
        )
        
        # Status
        self.nfc_status_id = self.nfc_canvas.create_text(
            100, 110, text=TEXTS['nfc_active'],
            font=FONTS['nfc_status'], fill=COLORS['success'],
            anchor='center'
        )
        
        # Cerchi animati per effetto pulse
        self.nfc_circles = []
        for i in range(3):
            circle = self.nfc_canvas.create_oval(
                80, 20, 120, 60,
                outline=COLORS['accent'], width=2,
                fill='', state='hidden'
            )
            self.nfc_circles.append(circle)
            
    def create_modern_footer(self, parent):
        """Crea footer moderno"""
        footer_frame = tk.Frame(parent, bg=COLORS['background'], height=80)
        footer_frame.pack(fill='x', side='bottom', pady=20)
        footer_frame.pack_propagate(False)
        
        # Canvas footer con gradiente
        footer_canvas = Canvas(footer_frame, height=80,
                              bg=COLORS['background'], highlightthickness=0)
        footer_canvas.pack(fill='both', expand=True, padx=40)
        
        # Logo software moderno
        software_frame = tk.Frame(footer_frame, bg=COLORS['secondary'],
                                 relief='flat', bd=0)
        software_frame.pack(side='right', padx=30, pady=15, ipadx=15, ipady=8)
        
        software_label = tk.Label(software_frame,
                                 text=TEXTS['software_name'],
                                 font=FONTS['software_name'],
                                 bg=COLORS['secondary'],
                                 fg=COLORS['accent'])
        software_label.pack()
        
        version_label = tk.Label(software_frame,
                                text=TEXTS['software_version'],
                                font=FONTS['software_version'],
                                bg=COLORS['secondary'],
                                fg=COLORS['text'])
        version_label.pack()
        
    def animate_elements(self):
        """Avvia animazioni continue"""
        self.animate_nfc_pulse()
        self.animate_indicators()
        
    def animate_nfc_pulse(self):
        """Anima l'effetto pulse dell'NFC"""
        def pulse():
            for i, circle in enumerate(self.nfc_circles):
                self.nfc_canvas.after(i * 500, lambda c=circle: self.pulse_circle(c))
            self.root.after(2000, pulse)
        
        pulse()
        
    def pulse_circle(self, circle):
        """Anima un singolo cerchio pulse"""
        def animate_step(step):
            if step < 20:
                # Espandi
                scale = 1 + (step * 0.1)
                self.nfc_canvas.coords(circle, 
                                      100 - 20*scale, 40 - 20*scale,
                                      100 + 20*scale, 40 + 20*scale)
                alpha = 255 - (step * 12)
                self.nfc_canvas.itemconfig(circle, state='normal')
                self.root.after(50, lambda: animate_step(step + 1))
            else:
                self.nfc_canvas.itemconfig(circle, state='hidden')
                
        animate_step(0)
        
    def animate_indicators(self):
        """Anima gli indicatori di stato"""
        def blink_indicators():
            # Alterna i colori degli indicatori
            current_color = self.status_canvas.itemcget(self.system_indicator, 'fill')
            new_color = COLORS['highlight'] if current_color == COLORS['success'] else COLORS['success']
            self.status_canvas.itemconfig(self.system_indicator, fill=new_color)
            
            self.root.after(1000, blink_indicators)
            
        blink_indicators()
        
    def update_clock(self):
        """Aggiorna data e ora con effetti"""
        now = datetime.now()
        
        # Formato data italiana
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        
        # Formato ora con secondi animati
        time_str = now.strftime("%H:%M:%S")
        
        self.date_label.config(text=date_str)
        
        # Effetto colore per i secondi
        if now.second % 2 == 0:
            self.time_label.config(fg=COLORS['accent'])
        else:
            self.time_label.config(fg=COLORS['highlight'])
            
        self.time_label.config(text=time_str)
        
        # Aggiorna ogni secondo
        self.root.after(1000, self.update_clock)
        
    def translate_date(self, date_str):
        """Traduce i nomi dei giorni e mesi in italiano"""
        translations = {
            'Monday': 'Lunedì', 'Tuesday': 'Martedì', 'Wednesday': 'Mercoledì',
            'Thursday': 'Giovedì', 'Friday': 'Venerdì', 'Saturday': 'Sabato',
            'Sunday': 'Domenica', 'January': 'Gennaio', 'February': 'Febbraio',
            'March': 'Marzo', 'April': 'Aprile', 'May': 'Maggio', 'June': 'Giugno',
            'July': 'Luglio', 'August': 'Agosto', 'September': 'Settembre',
            'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
        }
        
        for eng, ita in translations.items():
            date_str = date_str.replace(eng, ita)
            
        return date_str
        
    def on_badge_read(self, badge_id):
        """Callback per lettura badge con animazioni"""
        try:
            timbratura = self.timbrature_manager.registra_timbratura(badge_id)
            self.show_modern_feedback(timbratura)
        except Exception as e:
            print(f"Errore nella gestione del badge: {e}")
            self.show_error_feedback()
            
    def show_modern_feedback(self, timbratura):
        """Mostra feedback moderno per timbratura"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        # Colori per feedback
        color = COLORS['success'] if movimento == 'ENTRATA' else COLORS['warning']
        
        # Aggiorna NFC canvas
        self.nfc_canvas.itemconfig(self.nfc_text_id,
                                  text=f"{TEXTS[movimento.lower()]}\n{badge_id}\n{ora}",
                                  fill=color)
        
        # Animazione flash
        self.flash_screen(color)
        
        # Ripristina dopo 3 secondi
        self.root.after(3000, self.reset_nfc_display)
        
    def flash_screen(self, color):
        """Effetto flash dello schermo"""
        original_bg = self.root.cget('bg')
        self.root.config(bg=color)
        self.root.after(200, lambda: self.root.config(bg=original_bg))
        
    def reset_nfc_display(self):
        """Ripristina il display NFC"""
        self.nfc_canvas.itemconfig(self.nfc_text_id,
                                  text=TEXTS['nfc_instruction'],
                                  fill=COLORS['text'])
        
    def show_error_feedback(self):
        """Mostra feedback errore moderno"""
        self.nfc_canvas.itemconfig(self.nfc_text_id,
                                  text=TEXTS['nfc_error'],
                                  fill=COLORS['error'])
        self.flash_screen(COLORS['error'])
        self.root.after(2000, self.reset_nfc_display)
        
    def toggle_fullscreen(self, event=None):
        """Attiva/disattiva modalità fullscreen"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def cleanup(self):
        """Pulizia delle risorse"""
        if hasattr(self, 'nfc_reader'):
            self.nfc_reader.stop_reading()
            
    def on_closing(self, event=None):
        """Gestisce la chiusura dell'applicazione"""
        self.cleanup()
        self.root.destroy()
        
    def run(self):
        """Avvia l'applicazione"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()

def main():
    """Funzione principale"""
    try:
        app = ModernAppTimbratura()
        app.run()
    except Exception as e:
        print(f"Errore nell'avvio dell'applicazione: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
