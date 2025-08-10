#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOTÀ Dashboard con Orologio Analogico
Design fedele all'immagine tablet moderna
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import math
import os
import threading
import time
from nfc_manager import NFCReader, TimbratureManager

class TigotaAnalogDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Gestori
        self.timbrature_manager = TimbratureManager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)
        
        self.setup_dashboard()
        self.start_clock()
        self.nfc_reader.start_reading()
        
    def setup_window(self):
        """Configura finestra"""
        self.root.title("TIGOTÀ - Dashboard Moderna")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#E8EBF0')  # Grigio chiaro come nell'immagine
        
        # Bind eventi
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F1>', self.show_admin)
        
    def setup_dashboard(self):
        """Setup dashboard simile all'immagine"""
        # Container principale
        main_container = tk.Frame(self.root, bg='#E8EBF0')
        main_container.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Header verde come nell'immagine
        self.create_header_bar(main_container)
        
        # Grid dashboard 3x2 come nell'immagine
        self.create_main_grid(main_container)
        
    def create_header_bar(self, parent):
        """Header verde come nell'immagine"""
        # Barra verde superiore
        header_bar = tk.Frame(parent, bg='#4CAF50', height=60)
        header_bar.pack(fill='x', pady=(0, 20))
        header_bar.pack_propagate(False)
        
        # Content header
        header_content = tk.Frame(header_bar, bg='#4CAF50')
        header_content.pack(expand=True, fill='both', padx=40, pady=15)
        
        # Logo e titolo sinistra
        left_frame = tk.Frame(header_content, bg='#4CAF50')
        left_frame.pack(side='left', fill='y')
        
        # Logo TIGOTÀ
        logo_label = tk.Label(left_frame,
                             text="TIGOTÀ",
                             font=('Segoe UI', 24, 'bold'),
                             bg='#4CAF50',
                             fg='#FFFFFF')
        logo_label.pack(side='left')
        
        # Separatore
        sep_label = tk.Label(left_frame,
                           text="  |  ",
                           font=('Segoe UI', 18, 'normal'),
                           bg='#4CAF50',
                           fg='#FFFFFF')
        sep_label.pack(side='left')
        
        # Titolo sistema
        title_label = tk.Label(left_frame,
                              text="Sistema di Timbratura",
                              font=('Segoe UI', 14, 'normal'),
                              bg='#4CAF50',
                              fg='#FFFFFF')
        title_label.pack(side='left', pady=2)
        
        # Info destra
        right_frame = tk.Frame(header_content, bg='#4CAF50')
        right_frame.pack(side='right', fill='y')
        
        # Data corrente
        self.header_date = tk.Label(right_frame,
                                   text="",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg='#4CAF50',
                                   fg='#FFFFFF')
        self.header_date.pack(side='right', pady=2)
        
        # Status
        status_label = tk.Label(right_frame,
                               text="● Online  ",
                               font=('Segoe UI', 11, 'normal'),
                               bg='#4CAF50',
                               fg='#FFFFFF')
        status_label.pack(side='right', padx=(0, 20), pady=2)
        
    def create_main_grid(self, parent):
        """Grid principale 3x2"""
        # Container grid
        grid_container = tk.Frame(parent, bg='#E8EBF0')
        grid_container.pack(expand=True, fill='both')
        
        # Configurazione grid 3 colonne, 2 righe
        for i in range(3):
            grid_container.grid_columnconfigure(i, weight=1)
        for i in range(2):
            grid_container.grid_rowconfigure(i, weight=1)
        
        # Card 1: Dipendenti (top-left)
        self.create_employee_card(grid_container, 0, 0)
        
        # Card 2: Orologio Analogico (top-center) - PRINCIPALE
        self.create_analog_clock_card(grid_container, 0, 1)
        
        # Card 3: NFC Badge (top-right)
        self.create_badge_card(grid_container, 0, 2)
        
        # Card 4: Timbrature (bottom-left)
        self.create_timbrature_card(grid_container, 1, 0)
        
        # Card 5: Info Sistema (bottom-center)
        self.create_system_card(grid_container, 1, 1)
        
        # Card 6: Statistiche (bottom-right)
        self.create_stats_card(grid_container, 1, 2)
        
    def create_employee_card(self, parent, row, col):
        """Card dipendenti"""
        card = self.create_card(parent, row, col, "👥", "Dipendenti", "#2196F3")
        
        # Content
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=20, pady=15)
        
        # Numero dipendenti
        count_label = tk.Label(content,
                              text="24",
                              font=('Segoe UI', 36, 'bold'),
                              bg='#FFFFFF',
                              fg='#2196F3')
        count_label.pack(expand=True)
        
        # Sottotesto
        sub_label = tk.Label(content,
                            text="Totali",
                            font=('Segoe UI', 12, 'normal'),
                            bg='#FFFFFF',
                            fg='#666666')
        sub_label.pack()
        
    def create_analog_clock_card(self, parent, row, col):
        """Card orologio analogico - PRINCIPALE"""
        card = self.create_card(parent, row, col, "🕐", "Ora Corrente", "#E91E63", large=True)
        
        # Content
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Canvas per orologio analogico
        self.clock_canvas = tk.Canvas(content, 
                                     width=200, 
                                     height=200, 
                                     bg='#FFFFFF', 
                                     highlightthickness=0)
        self.clock_canvas.pack(expand=True, pady=(10, 0))
        
        # Ora digitale sotto l'orologio
        self.digital_time = tk.Label(content,
                                    font=('Consolas', 20, 'bold'),
                                    bg='#FFFFFF',
                                    fg='#E91E63')
        self.digital_time.pack(pady=(10, 0))
        
        # Data
        self.digital_date = tk.Label(content,
                                    font=('Segoe UI', 12, 'normal'),
                                    bg='#FFFFFF',
                                    fg='#666666')
        self.digital_date.pack()
        
    def create_badge_card(self, parent, row, col):
        """Card badge NFC"""
        card = self.create_card(parent, row, col, "🏷️", "Badge Access", "#FF9800")
        
        # Content
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=20, pady=15)
        
        # Icona NFC grande
        nfc_icon = tk.Label(content,
                           text="📱",
                           font=('Apple Color Emoji', 32),
                           bg='#FFFFFF')
        nfc_icon.pack(expand=True)
        
        # Status
        self.nfc_status = tk.Label(content,
                                  text="Pronto",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#FFFFFF',
                                  fg='#4CAF50')
        self.nfc_status.pack()
        
    def create_timbrature_card(self, parent, row, col):
        """Card timbrature"""
        card = self.create_card(parent, row, col, "📋", "Timbrature", "#9C27B0")
        
        # Content
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=20, pady=15)
        
        # Numero timbrature oggi
        self.timb_count = tk.Label(content,
                                  text="0",
                                  font=('Segoe UI', 36, 'bold'),
                                  bg='#FFFFFF',
                                  fg='#9C27B0')
        self.timb_count.pack(expand=True)
        
        # Sottotesto
        sub_label = tk.Label(content,
                            text="Oggi",
                            font=('Segoe UI', 12, 'normal'),
                            bg='#FFFFFF',
                            fg='#666666')
        sub_label.pack()
        
    def create_system_card(self, parent, row, col):
        """Card sistema"""
        card = self.create_card(parent, row, col, "⚙️", "Sistema", "#607D8B")
        
        # Content
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=20, pady=15)
        
        # Status sistema
        status_label = tk.Label(content,
                               text="Operativo",
                               font=('Segoe UI', 16, 'bold'),
                               bg='#FFFFFF',
                               fg='#4CAF50')
        status_label.pack(expand=True)
        
        # Versione
        version_label = tk.Label(content,
                                text="v3.0",
                                font=('Segoe UI', 12, 'normal'),
                                bg='#FFFFFF',
                                fg='#666666')
        version_label.pack()
        
    def create_stats_card(self, parent, row, col):
        """Card statistiche"""
        card = self.create_card(parent, row, col, "📊", "Report", "#795548")
        
        # Content
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=20, pady=15)
        
        # Ultima timbratura
        self.last_action = tk.Label(content,
                                   text="--:--",
                                   font=('Segoe UI', 20, 'bold'),
                                   bg='#FFFFFF',
                                   fg='#795548')
        self.last_action.pack(expand=True)
        
        # Sottotesto
        sub_label = tk.Label(content,
                            text="Ultima",
                            font=('Segoe UI', 12, 'normal'),
                            bg='#FFFFFF',
                            fg='#666666')
        sub_label.pack()
        
    def create_card(self, parent, row, col, icon, title, color, large=False):
        """Crea card moderna"""
        # Padding maggiore per card grande
        padx = 15 if large else 10
        pady = 15 if large else 10
        
        # Shadow
        shadow = tk.Frame(parent, bg='#D0D4DA', height=3)
        shadow.grid(row=row, column=col, sticky='nsew', 
                   padx=(padx+3, padx+3), pady=(pady+3, pady))
        
        # Main card
        card = tk.Frame(parent, bg='#FFFFFF', relief='flat', bd=0)
        card.grid(row=row, column=col, sticky='nsew', padx=padx, pady=pady)
        
        # Header colorato
        header = tk.Frame(card, bg=color, height=40)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header, bg=color)
        header_content.pack(expand=True, fill='both', padx=15, pady=8)
        
        # Icona
        icon_label = tk.Label(header_content,
                             text=icon,
                             font=('Apple Color Emoji', 16),
                             bg=color)
        icon_label.pack(side='left')
        
        # Titolo
        title_label = tk.Label(header_content,
                              text=title,
                              font=('Segoe UI', 12, 'bold'),
                              bg=color,
                              fg='#FFFFFF')
        title_label.pack(side='left', padx=(8, 0))
        
        return card
        
    def draw_analog_clock(self):
        """Disegna orologio analogico"""
        # Pulisci canvas
        self.clock_canvas.delete("all")
        
        # Dimensioni
        width = 200
        height = 200
        center_x = width // 2
        center_y = height // 2
        radius = 80
        
        # Cerchio esterno
        self.clock_canvas.create_oval(center_x - radius, center_y - radius,
                                     center_x + radius, center_y + radius,
                                     outline='#E91E63', width=3, fill='#FAFAFA')
        
        # Ore (12, 3, 6, 9)
        for hour in [12, 3, 6, 9]:
            angle = math.radians((hour * 30) - 90)
            x1 = center_x + (radius - 15) * math.cos(angle)
            y1 = center_y + (radius - 15) * math.sin(angle)
            x2 = center_x + (radius - 5) * math.cos(angle)
            y2 = center_y + (radius - 5) * math.sin(angle)
            self.clock_canvas.create_line(x1, y1, x2, y2, fill='#E91E63', width=3)
        
        # Tacche ore minori
        for hour in range(1, 13):
            if hour not in [12, 3, 6, 9]:
                angle = math.radians((hour * 30) - 90)
                x1 = center_x + (radius - 10) * math.cos(angle)
                y1 = center_y + (radius - 10) * math.sin(angle)
                x2 = center_x + (radius - 5) * math.cos(angle)
                y2 = center_y + (radius - 5) * math.sin(angle)
                self.clock_canvas.create_line(x1, y1, x2, y2, fill='#CCCCCC', width=2)
        
        # Ora corrente
        now = datetime.now()
        hours = now.hour % 12
        minutes = now.minute
        seconds = now.second
        
        # Lancetta ore
        hour_angle = math.radians(((hours + minutes/60) * 30) - 90)
        hour_x = center_x + 40 * math.cos(hour_angle)
        hour_y = center_y + 40 * math.sin(hour_angle)
        self.clock_canvas.create_line(center_x, center_y, hour_x, hour_y, 
                                     fill='#E91E63', width=6, capstyle='round')
        
        # Lancetta minuti
        minute_angle = math.radians((minutes * 6) - 90)
        minute_x = center_x + 60 * math.cos(minute_angle)
        minute_y = center_y + 60 * math.sin(minute_angle)
        self.clock_canvas.create_line(center_x, center_y, minute_x, minute_y, 
                                     fill='#E91E63', width=4, capstyle='round')
        
        # Lancetta secondi
        second_angle = math.radians((seconds * 6) - 90)
        second_x = center_x + 70 * math.cos(second_angle)
        second_y = center_y + 70 * math.sin(second_angle)
        self.clock_canvas.create_line(center_x, center_y, second_x, second_y, 
                                     fill='#FF5722', width=2, capstyle='round')
        
        # Centro
        self.clock_canvas.create_oval(center_x - 6, center_y - 6,
                                     center_x + 6, center_y + 6,
                                     fill='#E91E63', outline='#E91E63')
        
    def start_clock(self):
        """Avvia orologio"""
        self.update_clock()
        
    def update_clock(self):
        """Aggiorna orologio analogico e digitale"""
        now = datetime.now()
        
        # Disegna orologio analogico
        if hasattr(self, 'clock_canvas'):
            self.draw_analog_clock()
        
        # Aggiorna ora digitale
        time_str = now.strftime("%H:%M:%S")
        if hasattr(self, 'digital_time'):
            self.digital_time.config(text=time_str)
        
        # Aggiorna data
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        if hasattr(self, 'digital_date'):
            self.digital_date.config(text=date_str.title())
        
        # Aggiorna header
        header_date_str = now.strftime("%d/%m/%Y - %H:%M")
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
            
            # Feedback
            self.show_feedback(timbratura)
            
            # Aggiorna contatori
            self.update_counters()
            
        except Exception as e:
            print(f"Errore badge: {e}")
            self.show_error()
            
    def show_feedback(self, timbratura):
        """Mostra feedback"""
        movimento = timbratura['tipo_movimento']
        ora = timbratura['ora']
        
        # Aggiorna NFC status
        if movimento == 'ENTRATA':
            self.nfc_status.config(text="✅ Entrata", fg='#4CAF50')
        else:
            self.nfc_status.config(text="🚪 Uscita", fg='#FF9800')
        
        # Aggiorna ultima azione
        self.last_action.config(text=ora.split()[1])  # Solo ora
        
        # Ripristina dopo 3 secondi
        self.root.after(3000, lambda: self.nfc_status.config(
            text="Pronto", fg='#4CAF50'))
        
    def show_error(self):
        """Mostra errore"""
        self.nfc_status.config(text="❌ Errore", fg='#F44336')
        self.root.after(2000, lambda: self.nfc_status.config(
            text="Pronto", fg='#4CAF50'))
        
    def update_counters(self):
        """Aggiorna contatori"""
        # Incrementa timbrature oggi
        count = getattr(self, '_daily_count', 0) + 1
        self._daily_count = count
        self.timb_count.config(text=str(count))
        
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
    """Main function"""
    try:
        app = TigotaAnalogDashboard()
        app.run()
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
