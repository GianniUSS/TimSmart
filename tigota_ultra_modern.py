#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Timbratura TIGOTÀ - Design Moderno Ultra per Tablet
Interfaccia grafica avanzata con design accattivante per negozi TIGOTÀ
"""

import tkinter as tk
from tkinter import ttk, Canvas
from datetime import datetime
import os
import threading
import time
import math
from nfc_manager import NFCReader, TimbratureManager
from config_ultra_modern import COLORS, TEXTS, FONTS, TABLET_CONFIG, NFC_CONFIG, WINDOW_CONFIG

class TigotaUltraModernApp:
    def __init__(self):
        self.root = tk.Tk()
        self.animation_id = None
        self.pulse_angle = 0
        
        self.setup_window()
        self.setup_managers()
        self.setup_ultra_modern_ui()
        self.start_continuous_animations()
        self.update_clock()
        
    def setup_window(self):
        """Configura finestra tablet"""
        self.root.title(WINDOW_CONFIG['title'])
        self.root.configure(bg=COLORS['background'])
        
        if WINDOW_CONFIG['fullscreen']:
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry(WINDOW_CONFIG['geometry'])
            
        self.root.resizable(False, False)
        self.root.bind('<Escape>', self.toggle_fullscreen)
        
        # Stile cursore per tablet
        if WINDOW_CONFIG.get('hide_cursor', False):
            self.root.config(cursor="none")
            
    def setup_managers(self):
        """Inizializza gestori"""
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        self.nfc_reader.start_reading()
        
    def setup_ultra_modern_ui(self):
        """Setup UI ultra moderna"""
        # Container principale con gradiente di sfondo
        self.main_container = tk.Frame(self.root, bg=COLORS['background'])
        self.main_container.pack(fill='both', expand=True)
        
        # Canvas di sfondo per gradiente
        self.bg_canvas = Canvas(self.main_container, 
                               width=TABLET_CONFIG['screen_width'],
                               height=TABLET_CONFIG['screen_height'],
                               highlightthickness=0)
        self.bg_canvas.pack(fill='both', expand=True)
        
        # Disegna sfondo gradiente
        self.draw_gradient_background()
        
        # Sezioni UI sopra il canvas
        self.create_floating_header()
        self.create_main_dashboard()
        self.create_floating_footer()
        
    def draw_gradient_background(self):
        """Disegna sfondo con gradiente moderno"""
        width = TABLET_CONFIG['screen_width']
        height = TABLET_CONFIG['screen_height']
        
        # Gradiente verticale
        steps = 100
        for i in range(steps):
            y1 = (height * i) // steps
            y2 = (height * (i + 1)) // steps
            
            # Gradiente da bianco a rosa chiarissimo
            ratio = i / steps
            r = int(255 - (255 - 252) * ratio)
            g = int(255 - (255 - 228) * ratio)
            b = int(255 - (255 - 236) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_canvas.create_rectangle(0, y1, width, y2, fill=color, outline='')
            
        # Elementi decorativi di sfondo
        self.draw_background_elements()
        
    def draw_background_elements(self):
        """Disegna elementi decorativi di sfondo"""
        width = TABLET_CONFIG['screen_width']
        height = TABLET_CONFIG['screen_height']
        
        # Cerchi decorativi
        for i in range(5):
            x = (width // 6) * (i + 1)
            y = height - 40
            size = 20 + (i * 5)
            
            self.bg_canvas.create_oval(x - size//2, y - size//2,
                                      x + size//2, y + size//2,
                                      fill=COLORS['tigota_light'], 
                                      outline='', width=0)
            
    def create_floating_header(self):
        """Header flottante moderno"""
        # Container header flottante
        header_container = tk.Frame(self.main_container, bg='')
        header_container.place(x=40, y=30, width=1200, height=120)
        
        # Canvas header con trasparenza simulata
        self.header_canvas = Canvas(header_container, 
                                   width=1200, height=120,
                                   bg=COLORS['background'], 
                                   highlightthickness=0)
        self.header_canvas.pack(fill='both', expand=True)
        
        # Sfondo header con bordi arrotondati simulati
        self.draw_rounded_rect(self.header_canvas, 10, 10, 1190, 110, 20, 
                              fill=COLORS['card_bg'], outline=COLORS['border'])
        
        # Logo TIGOTÀ centrato
        self.header_canvas.create_text(600, 45,
                                      text=TEXTS['logo_principale'],
                                      font=('Segoe UI', 42, 'bold'),
                                      fill=COLORS['tigota_pink'])
        
        # Slogan sotto
        self.header_canvas.create_text(600, 80,
                                      text=TEXTS['slogan'],
                                      font=FONTS['slogan'],
                                      fill=COLORS['text_light'])
        
        # Decorazioni laterali
        self.draw_header_decorations()
        
    def draw_header_decorations(self):
        """Decorazioni header"""
        # Elementi decorativi ai lati del logo
        for side in [-1, 1]:
            x_center = 600 + (side * 250)
            
            # Linee decorative
            for i in range(3):
                y = 30 + (i * 15)
                line_length = 60 - (i * 10)
                
                self.header_canvas.create_line(
                    x_center - line_length//2, y,
                    x_center + line_length//2, y,
                    fill=COLORS['tigota_pink'], width=3)
                    
    def create_main_dashboard(self):
        """Dashboard principale moderna"""
        # Container principale dashboard
        dashboard_container = tk.Frame(self.main_container, bg='')
        dashboard_container.place(x=40, y=180, width=1200, height=400)
        
        # Layout a 2 colonne
        self.create_datetime_card(dashboard_container)
        self.create_nfc_card(dashboard_container)
        
    def create_datetime_card(self, parent):
        """Card data/ora moderna"""
        # Canvas per card data/ora
        datetime_canvas = Canvas(parent, width=700, height=400,
                                bg='', highlightthickness=0)
        datetime_canvas.place(x=0, y=0)
        
        # Sfondo card con ombra
        self.draw_card_with_shadow(datetime_canvas, 10, 10, 690, 390)
        
        # Indicatori status animati in alto
        self.draw_status_row(datetime_canvas)
        
        # Data
        self.date_canvas_id = datetime_canvas.create_text(350, 150,
                                                         text="",
                                                         font=FONTS['date'],
                                                         fill=COLORS['text'])
        
        # Ora grande con effetto
        self.time_canvas_id = datetime_canvas.create_text(350, 220,
                                                         text="",
                                                         font=FONTS['time'],
                                                         fill=COLORS['tigota_pink'])
        
        # Linea decorativa sotto l'ora
        datetime_canvas.create_line(100, 270, 600, 270,
                                   fill=COLORS['tigota_pink'], width=4)
        
        # Piccole info aggiuntive
        datetime_canvas.create_text(350, 320,
                                   text="Sistema di Timbratura Attivo",
                                   font=FONTS['status_text'],
                                   fill=COLORS['text_light'])
        
        self.datetime_canvas = datetime_canvas
        
    def create_nfc_card(self, parent):
        """Card NFC ultra moderna"""
        # Canvas per card NFC
        nfc_canvas = Canvas(parent, width=460, height=400,
                           bg='', highlightthickness=0)
        nfc_canvas.place(x=740, y=0)
        
        # Sfondo card con ombra
        self.draw_card_with_shadow(nfc_canvas, 10, 10, 450, 390)
        
        # Titolo NFC
        nfc_canvas.create_text(230, 50,
                              text=TEXTS['nfc_title'],
                              font=FONTS['nfc_title'],
                              fill=COLORS['tigota_pink'])
        
        # Area NFC circolare moderna
        self.draw_modern_nfc_area(nfc_canvas)
        
        # Istruzioni sotto
        nfc_canvas.create_text(230, 320,
                              text=TEXTS['nfc_subtitle'],
                              font=FONTS['nfc_subtitle'],
                              fill=COLORS['text_light'],
                              width=300)
        
        # Status indicator
        self.nfc_status_id = nfc_canvas.create_text(230, 360,
                                                   text=TEXTS['nfc_active'],
                                                   font=FONTS['status_text'],
                                                   fill=COLORS['nfc_active'])
        
        self.nfc_canvas = nfc_canvas
        
        # Area feedback (inizialmente nascosta)
        self.create_feedback_overlay(parent)
        
    def draw_modern_nfc_area(self, canvas):
        """Area NFC moderna con animazioni"""
        center_x, center_y = 230, 200
        
        # Cerchio base NFC
        self.nfc_base = canvas.create_oval(center_x - 70, center_y - 70,
                                          center_x + 70, center_y + 70,
                                          fill=COLORS['tigota_light'],
                                          outline=COLORS['tigota_pink'], width=4)
        
        # Icona NFC moderna
        canvas.create_text(center_x, center_y - 20,
                          text="📡",
                          font=('Segoe UI Emoji', 32),
                          fill=COLORS['tigota_pink'])
        
        canvas.create_text(center_x, center_y + 15,
                          text="NFC",
                          font=('Segoe UI', 18, 'bold'),
                          fill=COLORS['tigota_pink'])
        
        # Cerchi pulse animati
        self.pulse_circles = []
        for i in range(4):
            circle = canvas.create_oval(center_x - 20, center_y - 20,
                                       center_x + 20, center_y + 20,
                                       outline=COLORS['tigota_pink'], width=2, fill='')
            self.pulse_circles.append(circle)
            canvas.itemconfig(circle, state='hidden')
            
    def create_feedback_overlay(self, parent):
        """Overlay per feedback timbrature"""
        # Canvas overlay (inizialmente nascosto)
        self.feedback_overlay = Canvas(parent, width=460, height=400,
                                      bg='', highlightthickness=0)
        # Non place inizialmente
        
    def draw_card_with_shadow(self, canvas, x1, y1, x2, y2):
        """Disegna card con ombra"""
        # Ombra
        canvas.create_rectangle(x1 + 5, y1 + 5, x2 + 5, y2 + 5,
                               fill=COLORS['shadow'], outline='')
        
        # Card principale
        canvas.create_rectangle(x1, y1, x2, y2,
                               fill=COLORS['card_bg'], 
                               outline=COLORS['border'], width=1)
        
    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Simula rettangolo con bordi arrotondati"""
        # Corpo principale
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)
        
        # Angoli
        canvas.create_oval(x1, y1, x1 + 2*radius, y1 + 2*radius, **kwargs)
        canvas.create_oval(x2 - 2*radius, y1, x2, y1 + 2*radius, **kwargs)
        canvas.create_oval(x1, y2 - 2*radius, x1 + 2*radius, y2, **kwargs)
        canvas.create_oval(x2 - 2*radius, y2 - 2*radius, x2, y2, **kwargs)
        
    def draw_status_row(self, canvas):
        """Riga di indicatori status"""
        statuses = [
            ("Sistema", COLORS['nfc_active']),
            ("NFC", COLORS['tigota_pink']),
            ("Database", COLORS['success'])
        ]
        
        start_x = 50
        for i, (label, color) in enumerate(statuses):
            x = start_x + (i * 150)
            
            # Cerchio status
            canvas.create_oval(x, 50, x + 16, 66, fill=color, outline='')
            
            # Label
            canvas.create_text(x + 30, 58, text=label,
                              font=FONTS['status_text'], fill=COLORS['text'],
                              anchor='w')
                              
    def create_floating_footer(self):
        """Footer flottante"""
        footer_container = tk.Frame(self.main_container, bg='')
        footer_container.place(x=40, y=720, width=1200, height=60)
        
        footer_canvas = Canvas(footer_container, width=1200, height=60,
                              bg='', highlightthickness=0)
        footer_canvas.pack(fill='both', expand=True)
        
        # Sfondo footer
        self.draw_rounded_rect(footer_canvas, 10, 10, 1190, 50, 15,
                              fill=COLORS['card_bg'], outline=COLORS['border'])
        
        # Info software a destra
        footer_canvas.create_text(1100, 30,
                                 text=f"{TEXTS['software_name']} {TEXTS['software_version']}",
                                 font=FONTS['status_text'],
                                 fill=COLORS['tigota_pink'], anchor='e')
        
        # Timestamp ultimo aggiornamento a sinistra
        self.footer_timestamp = footer_canvas.create_text(100, 30,
                                                          text="",
                                                          font=FONTS['status_text'],
                                                          fill=COLORS['text_light'], anchor='w')
        
    def start_continuous_animations(self):
        """Avvia animazioni continue"""
        self.animate_nfc_pulse_continuous()
        self.animate_status_indicators()
        
    def animate_nfc_pulse_continuous(self):
        """Animazione pulse NFC continua"""
        def pulse_step():
            if not hasattr(self, 'pulse_circles'):
                self.root.after(100, pulse_step)
                return
                
            self.pulse_angle += 0.1
            
            for i, circle in enumerate(self.pulse_circles):
                # Calcola posizione e dimensione del pulse
                phase = (self.pulse_angle + i * 0.5) % (2 * math.pi)
                scale = 1 + math.sin(phase) * 1.5
                alpha = (math.sin(phase) + 1) / 2
                
                center_x, center_y = 230, 200
                size = 20 * scale
                
                if alpha > 0.3:  # Mostra solo se abbastanza visibile
                    self.nfc_canvas.coords(circle,
                                          center_x - size, center_y - size,
                                          center_x + size, center_y + size)
                    self.nfc_canvas.itemconfig(circle, state='normal')
                else:
                    self.nfc_canvas.itemconfig(circle, state='hidden')
                    
            self.root.after(50, pulse_step)
            
        pulse_step()
        
    def animate_status_indicators(self):
        """Anima gli indicatori di status"""
        def status_pulse():
            # Animazione indicatori vari
            self.root.after(2000, status_pulse)
            
        status_pulse()
        
    def update_clock(self):
        """Aggiorna orologio e timestamp"""
        now = datetime.now()
        
        # Data italiana
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        
        # Ora
        time_str = now.strftime("%H:%M:%S")
        
        # Aggiorna canvas
        if hasattr(self, 'datetime_canvas'):
            self.datetime_canvas.itemconfig(self.date_canvas_id, text=date_str.upper())
            self.datetime_canvas.itemconfig(self.time_canvas_id, text=time_str)
            
        # Timestamp footer
        timestamp_str = f"Ultimo aggiornamento: {now.strftime('%H:%M:%S')}"
        if hasattr(self, 'footer_timestamp'):
            self.bg_canvas.itemconfig(self.footer_timestamp, text=timestamp_str)
            
        self.root.after(1000, self.update_clock)
        
    def translate_date(self, date_str):
        """Traduce date in italiano"""
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
            timbratura = self.timbrature_manager.registra_timbratura(badge_id)
            self.show_ultra_modern_feedback(timbratura)
        except Exception as e:
            print(f"Errore badge: {e}")
            
    def show_ultra_modern_feedback(self, timbratura):
        """Feedback ultra moderno per timbrature"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        ora = timbratura['ora']
        
        # Mostra overlay feedback
        self.feedback_overlay.place(x=740, y=0)
        
        # Pulisce contenuto precedente
        self.feedback_overlay.delete("all")
        
        # Sfondo overlay
        self.draw_card_with_shadow(self.feedback_overlay, 10, 10, 450, 390)
        
        # Colore movimento
        color = COLORS['success'] if movimento == 'ENTRATA' else COLORS['warning']
        
        # Icona grande
        icon = "✅" if movimento == 'ENTRATA' else "⬅️"
        self.feedback_overlay.create_text(230, 100,
                                         text=icon,
                                         font=('Segoe UI Emoji', 64),
                                         fill=color)
        
        # Testo movimento
        self.feedback_overlay.create_text(230, 170,
                                         text=movimento,
                                         font=FONTS['feedback_large'],
                                         fill=color)
        
        # Badge ID
        self.feedback_overlay.create_text(230, 220,
                                         text=f"Badge: {badge_id}",
                                         font=FONTS['badge_id'],
                                         fill=COLORS['text'])
        
        # Ora
        self.feedback_overlay.create_text(230, 260,
                                         text=ora,
                                         font=FONTS['timestamp'],
                                         fill=COLORS['tigota_pink'])
        
        # Messaggio successo
        self.feedback_overlay.create_text(230, 320,
                                         text=TEXTS['success_msg'],
                                         font=FONTS['feedback_medium'],
                                         fill=COLORS['success'])
        
        # Animazione flash
        self.flash_modern_effect()
        
        # Auto-hide
        self.root.after(TABLET_CONFIG['feedback_duration'], self.hide_modern_feedback)
        
    def flash_modern_effect(self):
        """Effetto flash moderno"""
        # Flash su sfondo gradiente
        original_bg = self.main_container.cget('bg')
        self.main_container.config(bg=COLORS['tigota_light'])
        self.root.after(300, lambda: self.main_container.config(bg=original_bg))
        
    def hide_modern_feedback(self):
        """Nasconde feedback moderno"""
        self.feedback_overlay.place_forget()
        
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
        app = TigotaUltraModernApp()
        app.run()
    except Exception as e:
        print(f"Errore avvio app ultra moderna: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
