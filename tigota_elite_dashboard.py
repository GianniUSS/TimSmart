#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOTÀ Elite Dashboard - Sistema di Timbratura Premium con SQLite
Design ultra-professionale con animazioni fluide e database robusto
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import math
import os
import threading
import time
import configparser
import winsound  # Per suoni Windows
try:
    import pygame  # Per audio più robusto negli EXE
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
from nfc_manager import NFCReader
from database_sqlite import get_database_manager, close_database

class TigotaEliteDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_elite_window()

        # Carica configurazione negozio
        self.load_store_config()

        # Gestori (SQLite database robusto) - con retry
        self.database_manager = None
        self.init_database_manager()
        self.nfc_reader = NFCReader(callback=self.on_badge_read)

        # Variabili per animazioni
        self.pulse_state = 0
        self.notification_queue = []

        self.setup_elite_dashboard()
        self.start_animations()

    def load_store_config(self):
        """Carica configurazione negozio da config.ini se presente"""
        try:
            cfg = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
            self.store_config = {}
            if os.path.exists(config_path):
                cfg.read(config_path, encoding='utf-8')
                if 'STORE' in cfg:
                    self.store_config = dict(cfg['STORE'])
        except Exception as e:
            print(f"⚠️ Errore lettura config: {e}")
            self.store_config = {}

    def get_store_display_text(self):
        """Ritorna testo display del negozio"""
        if hasattr(self, 'store_config') and self.store_config:
            code = self.store_config.get('code') or self.store_config.get('id')
            name = self.store_config.get('name') or self.store_config.get('negozio')
            city = self.store_config.get('city') or self.store_config.get('citta')
            parts = [p for p in [name, city, code] if p]
            return " • ".join(parts)
        return ""

    def init_database_manager(self):
        """Inizializza database manager con retry semplice"""
        try:
            self.database_manager = get_database_manager()
        except Exception as e:
            print(f"⚠️ DB non pronto: {e}")
            self.database_manager = None
            # Riprova tra 1 secondo
            if hasattr(self, 'root'):
                self.root.after(1000, self.retry_database_init)

    def retry_database_init(self):
        """Riprova inizializzazione DB"""
        if not getattr(self, 'database_manager', None):
            self.init_database_manager()
        
    def setup_elite_window(self):
        """Configura finestra elite con rilevamento tablet"""
        self.root.title("TIGOTÀ Elite Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#E8EDF2')  # Grigio più sofisticato
        
        # DETECT RISOLUZIONE per ottimizzazioni automatiche
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Ottimizzazioni automatiche per tablet (risoluzione tipica 1024x768, 1280x800, etc.)
        self.is_tablet_resolution = screen_height <= 900 or (screen_width <= 1366 and screen_height <= 768)
        
        if self.is_tablet_resolution:
            print(f"📱 MODALITÀ TABLET RILEVATA: {screen_width}x{screen_height}")
        else:
            print(f"🖥️ MODALITÀ DESKTOP: {screen_width}x{screen_height}")
        
        # Bind eventi
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F1>', self.show_admin)
        self.root.bind('<F5>', self.refresh_dashboard)
        
        # SUPPORTO LETTORE USB ID CARD (modalità tastiera)
        self.badge_input_buffer = ""
        self.root.bind('<Key>', self.on_keyboard_input)
        self.root.focus_set()  # Assicura che l'app riceva gli eventi tastiera
        
    # Nota: l'aggiornamento periodico verrà avviato dopo la creazione della UI
        
    def setup_elite_dashboard(self):
        """Setup dashboard elite"""
        # STRATEGIA LAYOUT OTTIMIZZATA PER TABLET
        if self.is_tablet_resolution:
            # Per tablet: padding ridotti per massimizzare spazio
            main_container = tk.Frame(self.root, bg='#E8EDF2')
            main_container.pack(fill='both', expand=True, padx=10, pady=5)
        else:
            # Per desktop: padding normali
            main_container = tk.Frame(self.root, bg='#E8EDF2')
            main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Status bar PRIMA (sempre visibile in fondo)
        self.create_status_bar(main_container)

        # Header premium con gradiente
        self.create_premium_header(main_container)

        # Grid dashboard raffinato
        self.create_premium_grid(main_container)

        # Avvia aggiornamento automatico dati reali ogni 30 secondi, ora che la UI è pronta
        self.schedule_real_data_update()
        
    def create_premium_header(self, parent):
        """Header premium con gradiente"""
        # Container header con altezza maggiore
        header_container = tk.Frame(parent, bg='#E8EDF2')
        header_container.pack(fill='x', pady=(0, 25))
        
        # Header principale con gradiente simulato
        header_main = tk.Frame(header_container, bg='#1E88E5', height=80)
        header_main.pack(fill='x')
        header_main.pack_propagate(False)
        
        # Gradiente simulato con frame sovrapposti
        for i in range(5):
            shade = 30 + (i * 10)  # Da più scuro a più chiaro
            color = f"#{shade:02x}{120 + i*10:02x}{229:02x}"
            gradient_frame = tk.Frame(header_main, bg=color, height=16)
            gradient_frame.pack(fill='x')
        
        # Content header sovrapposto
        header_content = tk.Frame(header_container, bg='#1E88E5')
        header_content.place(x=0, y=0, relwidth=1, height=80)
        
        # Layout header con più dettagli
        content_frame = tk.Frame(header_content, bg='#1E88E5')
        content_frame.pack(expand=True, fill='both', padx=50, pady=20)
        
        # Sinistra: Logo + info
        left_section = tk.Frame(content_frame, bg='#1E88E5')
        left_section.pack(side='left', fill='y')
        
        # Logo TIGOTÀ con ombra
        logo_shadow = tk.Label(left_section,
                              text="TIGOTÀ",
                              font=('Segoe UI', 30, 'bold'),
                              bg='#1E88E5',
                              fg='#0D47A1')  # Ombra scura
        logo_shadow.place(x=2, y=2)
        
        logo_main = tk.Label(left_section,
                            text="TIGOTÀ",
                            font=('Segoe UI', 30, 'bold'),
                            bg='#1E88E5',
                            fg='#FFFFFF')
        logo_main.pack(side='left')
        
        # Separatore elegante
        separator = tk.Label(left_section,
                           text="  ◆  ",
                           font=('Segoe UI', 20, 'normal'),
                           bg='#1E88E5',
                           fg='#BBDEFB')
        separator.pack(side='left', padx=10)
        
        # Info sistema
        info_frame = tk.Frame(left_section, bg='#1E88E5')
        info_frame.pack(side='left', fill='y')
        
        system_title = tk.Label(info_frame,
                               text="Sistema di Timbratura Aziendale",
                               font=('Segoe UI', 14, 'bold'),
                               bg='#1E88E5',
                               fg='#FFFFFF')
        system_title.pack(anchor='w')
        
        # Destra: Sezione controlli e info negozio
        right_section = tk.Frame(content_frame, bg='#1E88E5')
        right_section.pack(side='right', fill='y')
        
        # Container per icone di gestione
        controls_frame = tk.Frame(right_section, bg='#1E88E5')
        controls_frame.pack(side='right', fill='y', padx=(0, 20))
        
        # Icona gestione badge-NFC (professionale)
        self.create_badge_management_icon(controls_frame)
        
        # Info negozio (se presente)
        store_text = self.get_store_display_text()
        if store_text:
            store_label = tk.Label(right_section,
                                  text=store_text,
                                  font=('Segoe UI', 16, 'bold'),
                                  bg='#1E88E5',
                                  fg='#FFFFFF')
            store_label.pack(anchor='e', padx=(20, 0))
        
    def create_premium_grid(self, parent):
        """Grid premium con card avanzate"""
        # Container grid con margini eleganti
        grid_container = tk.Frame(parent, bg='#E8EDF2')
        grid_container.pack(expand=True, fill='both', pady=(10, 15))
        
        # Grid 3x2 ottimizzato
        for i in range(3):
            grid_container.grid_columnconfigure(i, weight=1, minsize=300)
        for i in range(2):
            grid_container.grid_rowconfigure(i, weight=1, minsize=180)
        
        # Card premium con design migliorato - LAYOUT FINALE 2 CARD CON ALTEZZA UGUALE
        self.create_clock_premium_card(grid_container, 0, 0, large=True)  # Orologio grande - 2 colonne e 2 righe (0,0 span 2x2)
        self.create_nfc_premium_card(grid_container, 0, 2, large=True)    # NFC a destra - stessa altezza (colonna 2, span 2 righe)
        
    def create_clock_premium_card(self, parent, row, col, large=False):
        """Card orologio premium con dettagli extra - ora supporta spanning completo"""
        # Se large=True, occupa 2 colonne E 2 righe (colspan=2, rowspan=2)
        colspan = 2 if large else 1
        rowspan = 2 if large else 1
        card = self.create_premium_card(parent, row, col, "🕐", "Orologio Centrale", "#E91E63", 
                                       large=large, colspan=colspan, rowspan=rowspan)
        
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=10, pady=8)  # Padding minimizzato per massimo spazio
        
        # Canvas orologio MEGA GRANDE per massima visibilità
        canvas_size = 480 if large else 320  # Aumentato ulteriormente per visibilità perfetta
        self.premium_clock_canvas = tk.Canvas(content, 
                                             width=canvas_size, 
                                             height=canvas_size, 
                                             bg='#FFFFFF', 
                                             highlightthickness=0)
        self.premium_clock_canvas.pack(expand=True, pady=(0, 2))  # Padding ultra minimo
        
        # Ora digitale con secondi animati - MASSIMIZZATA
        time_frame = tk.Frame(content, bg='#FFFFFF')
        time_frame.pack(fill='x')
        
        # Font dinamico MASSIMIZZATO per occupare tutto lo spazio
        font_size = 70 if large else 50  # Aumentato da 55 a 70 per tablet
        self.premium_time = tk.Label(time_frame,
                                    font=('Consolas', font_size, 'bold'),
                                    bg='#FFFFFF',
                                    fg='#E91E63')
        self.premium_time.pack()
        
        # Data MASSIMIZZATA per visibilità estrema
        self.premium_date = tk.Label(time_frame,
                                    font=('Segoe UI', 32, 'bold'),  # Aumentato da 24 a 32
                                    bg='#FFFFFF',
                                    fg='#666666')
        self.premium_date.pack(pady=(0, 0))  # Padding azzerato
        
        # Timezone OTTIMIZZATO
        timezone_label = tk.Label(time_frame,
                                 text="UTC+1 (CEST)",
                                 font=('Segoe UI', 20, 'italic'),  # Aumentato da 16 a 20
                                 bg='#FFFFFF',
                                 fg='#999999')
        timezone_label.pack()
        
    def create_nfc_premium_card(self, parent, row, col, large=False):
        """Card NFC premium con selettori tipo timbratura - ora supporta spanning verticale"""
        # Se large=True, occupa 2 righe (rowspan=2)
        rowspan = 2 if large else 1
        card = self.create_premium_card(parent, row, col, "🏷️", "Sistema Timbratura", "#FF9800", 
                                       large=large, rowspan=rowspan)
        
        content = tk.Frame(card, bg='#FFFFFF')
        content.pack(expand=True, fill='both', padx=15, pady=10)  # Ridotto padding per tablet
        
        # Selettori tipo timbratura
        self.create_timbratura_selectors(content)
        
        # Container per status e icona badge
        bottom_frame = tk.Frame(content, bg='#FFFFFF')
        bottom_frame.pack(fill='x', pady=(3, 0))  # Ridotto padding verticale
        
        # Status con dettagli (sinistra)
        status_frame = tk.Frame(bottom_frame, bg='#FFFFFF')
        status_frame.pack(side='left', fill='x', expand=True)
        
        self.nfc_status_premium = tk.Label(status_frame,
                                          text="🟢 Lettore Attivo",
                                          font=('Segoe UI', 14, 'bold'),  # Font più grande per tablet
                                          bg='#FFFFFF',
                                          fg='#4CAF50')
        self.nfc_status_premium.pack()
        
        # Ultima lettura
        self.last_read_label = tk.Label(status_frame,
                                       text="Ultima lettura: --:--",
                                       font=('Segoe UI', 11, 'normal'),  # Font più grande per tablet
                                       bg='#FFFFFF',
                                       fg='#666666')
        self.last_read_label.pack()
        
        # Icona badge NFC in basso a destra - LAYOUT MIGLIORATO
        badge_icon_frame = tk.Frame(bottom_frame, bg='#FFFFFF')
        badge_icon_frame.pack(side='right', anchor='e', padx=(10, 0))  # Più spazio a sinistra
        
        # Carica immagine badge personalizzata o usa emoji di fallback
        self.nfc_badge_icon = self.create_badge_icon(badge_icon_frame)
        self.nfc_badge_icon.pack()
        
        # Freccia a destra sotto l'icona badge - PERFETTO PER TABLET
        self.arrow_badge = tk.Label(badge_icon_frame,
                                   text="→",  # Freccia classica
                                   font=('Arial', 40, 'bold'),  # Font ottimale per tablet
                                   bg='#FFFFFF',
                                   fg='#FF4500')  # Arancione brillante per visibilità
        self.arrow_badge.pack(pady=(5, 0))  # Più spazio sopra la freccia
        
    def create_badge_icon(self, parent):
        """Crea icona badge - carica immagine personalizzata o usa emoji fallback"""
        try:
            # Lista dei possibili nomi file per l'immagine badge
            badge_image_names = [
                'logo_nfc.jpg', 'logo_nfc.png', 'logo_nfc.jpeg',  # Il tuo file specifico
                'badge_icon.png', 'badge.png', 'nfc_badge.png', 
                'badge_icon.jpg', 'badge.jpg', 'nfc_badge.jpg',
                'badge_icon.jpeg', 'badge.jpeg', 'nfc_badge.jpeg',
                'badge_icon.gif', 'badge.gif', 'nfc_badge.gif'
            ]
            
            # Cerca l'immagine nella directory corrente e nella cartella immagini
            badge_image_path = None
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Cartelle dove cercare l'immagine
            search_directories = [
                current_dir,  # Directory corrente
                os.path.join(current_dir, 'immagini'),  # Cartella immagini
                os.path.join(current_dir, 'images'),   # Cartella images
                os.path.join(current_dir, 'assets')    # Cartella assets
            ]
            
            # Cerca l'immagine in tutte le directory
            for search_dir in search_directories:
                if os.path.exists(search_dir):
                    for image_name in badge_image_names:
                        full_path = os.path.join(search_dir, image_name)
                        if os.path.exists(full_path):
                            badge_image_path = full_path
                            print(f"✅ Trovata immagine badge: {image_name} in {search_dir}")
                            break
                    if badge_image_path:
                        break
            
            if badge_image_path:
                # Carica e ridimensiona l'immagine
                from PIL import Image, ImageTk
                
                # Apri l'immagine
                pil_image = Image.open(badge_image_path)
                
                # Ridimensiona OTTIMIZZATO per tablet (max 200x200 pixel - bilanciato per spazio)
                size = (200, 200)  # Ridotto da 280 a 200 per lasciare spazio verticale
                pil_image.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Converti per tkinter
                tk_image = ImageTk.PhotoImage(pil_image)
                
                # Crea label con immagine
                badge_label = tk.Label(parent, image=tk_image, bg='#FFFFFF')
                badge_label.image = tk_image  # Mantieni riferimento per evitare garbage collection
                
                print(f"✅ Immagine badge caricata: {badge_image_path}")
                return badge_label
                
            else:
                print("⚠️ Nessuna immagine badge trovata, uso emoji fallback")
                raise FileNotFoundError("Badge image not found")
                
        except Exception as e:
            print(f"⚠️ Errore caricamento immagine badge: {e}")
            print("📟 Uso emoji fallback")
            
            # Fallback: usa emoji come prima
            badge_label = tk.Label(parent,
                                 text="📟",  # Emoji fallback
                                 font=('Apple Color Emoji', 32),
                                 bg='#FFFFFF')
            return badge_label

    def create_premium_card(self, parent, row, col, icon, title, color, large=False, rowspan=1, colspan=1):
        """Crea card premium con effetti avanzati - supporta spanning verticale e orizzontale"""
        # Padding dinamico
        base_padx, base_pady = (12, 12) if large else (8, 8)
        
        # Ombra multipla per effetto depth
        for i in range(3):
            shadow_alpha = 50 + (i * 30)
            shadow_color = f"#{shadow_alpha:02x}{shadow_alpha:02x}{shadow_alpha:02x}"
            shadow = tk.Frame(parent, bg=shadow_color, height=1+i)
            shadow.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky='nsew', 
                       padx=(base_padx+3+i, base_padx+3+i), 
                       pady=(base_pady+3+i, base_pady+i))
        
        # Card principale con rowspan e colspan
        card = tk.Frame(parent, bg='#FFFFFF', relief='flat', bd=0)
        card.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan, sticky='nsew', padx=base_padx, pady=base_pady)
        
        # Header con gradiente simulato
        header = tk.Frame(card, bg=color, height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Gradiente header (simulato)
        for i in range(3):
            # Crea sfumature del colore principale
            if color == "#2196F3":
                gradient_colors = ["#1976D2", "#1E88E5", "#2196F3"]
            elif color == "#E91E63":
                gradient_colors = ["#C2185B", "#D81B60", "#E91E63"]
            elif color == "#FF9800":
                gradient_colors = ["#F57C00", "#FB8C00", "#FF9800"]
            elif color == "#9C27B0":
                gradient_colors = ["#7B1FA2", "#8E24AA", "#9C27B0"]
            elif color == "#607D8B":
                gradient_colors = ["#455A64", "#546E7A", "#607D8B"]
            else:
                gradient_colors = ["#5D4037", "#6D4C41", "#795548"]
            
            grad_frame = tk.Frame(header, bg=gradient_colors[i], height=17)
            grad_frame.pack(fill='x')
        
        # Header content sovrapposto
        header_content = tk.Frame(card, bg=color)
        header_content.place(x=0, y=0, relwidth=1, height=50)
        
        header_inner = tk.Frame(header_content, bg=color)
        header_inner.pack(expand=True, fill='both', padx=20, pady=12)
        
        # Icona con effetto glow
        icon_shadow = tk.Label(header_inner,
                              text=icon,
                              font=('Apple Color Emoji', 18),
                              bg=color,
                              fg='#000000')
        icon_shadow.place(x=1, y=1)
        
        icon_main = tk.Label(header_inner,
                            text=icon,
                            font=('Apple Color Emoji', 18),
                            bg=color)
        icon_main.pack(side='left')
        
        # Titolo con typography migliorata
        title_label = tk.Label(header_inner,
                              text=title,
                              font=('Segoe UI', 12, 'bold'),
                              bg=color,
                              fg='#FFFFFF')
        title_label.pack(side='left', padx=(10, 0))
        
        # Indicatore status
        status_dot = tk.Label(header_inner,
                             text="●",
                             font=('Arial', 8),
                             bg=color,
                             fg='#FFFFFF')
        status_dot.pack(side='right')
        
        return card
        
    def create_status_bar(self, parent):
        """Status bar inferiore premium - SEMPRE VISIBILE su tablet"""
        # OTTIMIZZAZIONE TABLET: Status bar ultra-compatta
        if self.is_tablet_resolution:
            status_bar = tk.Frame(parent, bg='#CFD8DC', height=35)  # Altezza fissa ridotta
            status_bar.pack(fill='x', pady=(2, 2), side='bottom')  # Padding minimali
            status_bar.pack_propagate(False)  # Mantieni altezza fissa
            
            # Content status bar ULTRA-COMPATTO per tablet
            status_content = tk.Frame(status_bar, bg='#CFD8DC')
            status_content.pack(expand=True, fill='both', padx=10, pady=2)  # Padding minimi
            
            # Solo info essenziali per tablet
            left_status = tk.Label(status_content,
                                  text="© 2025 TIGOTÀ Elite",  # Testo ancora più corto
                                  font=('Segoe UI', 8, 'normal'),  # Font ancora più piccolo
                                  bg='#CFD8DC',
                                  fg='#37474F')
            left_status.pack(side='left')
            
            # Centro: Notifiche compatte
            self.notification_label = tk.Label(status_content,
                                              text="",
                                              font=('Segoe UI', 8, 'italic'),
                                              bg='#CFD8DC',
                                              fg='#E91E63')
            self.notification_label.pack(side='left', padx=(15, 0))
            
            # Solo stato DB per tablet
            tech_status = tk.Label(status_content,
                                  text="🗄️ DB OK",  # Solo essenziale
                                  font=('Segoe UI', 8, 'normal'),
                                  bg='#CFD8DC',
                                  fg='#37474F')
            tech_status.pack(side='right')
        else:
            # Layout normale per desktop
            status_bar = tk.Frame(parent, bg='#CFD8DC')  
            status_bar.pack(fill='x', pady=(8, 5), side='bottom')  # Padding ridotto per tablet
            
            # Content status bar COMPATTO
            status_content = tk.Frame(status_bar, bg='#CFD8DC')
            status_content.pack(expand=True, fill='both', padx=20, pady=6)  # Padding ridotto
            
            # Sinistra: Copyright COMPATTO
            left_status = tk.Label(status_content,
                                  text="© 2025 TIGOTÀ | Sistema Timbratura Elite",  # Testo accorciato
                                  font=('Segoe UI', 10, 'normal'),  # Font ridotto per spazio
                                  bg='#CFD8DC',
                                  fg='#37474F')
            left_status.pack(side='left')
            
            # Centro: Notifiche COMPATTE
            self.notification_label = tk.Label(status_content,
                                              text="",
                                              font=('Segoe UI', 10, 'italic'),  # Font ridotto
                                              bg='#CFD8DC',
                                              fg='#E91E63')
            self.notification_label.pack(side='left', padx=(30, 0))  # Padding ridotto
            
            # Destra: Info tecniche COMPATTE
            tech_status = tk.Label(status_content,
                                  text="🔒 Sicuro | 🗄️ DB OK | 📡 Sync",  # Testo accorciato
                                  font=('Segoe UI', 10, 'normal'),  # Font ridotto
                                  bg='#CFD8DC',
                                  fg='#37474F')
            tech_status.pack(side='right')
        
    def create_badge_management_icon(self, parent):
        """Crea icona professionale per gestione abbinamento badge-NFC"""
        # Container principale con effetti hover
        icon_container = tk.Frame(parent, bg='#1E88E5', cursor='hand2')
        icon_container.pack(side='right', padx=(10, 0))
        
        # Frame interno con bordo elegante
        icon_frame = tk.Frame(icon_container, 
                             bg='#0D47A1', 
                             relief='raised', 
                             bd=1,
                             width=50, 
                             height=50)
        icon_frame.pack_propagate(False)
        icon_frame.pack(padx=2, pady=2)
        
        # Icona principale - simbolo professionale per configurazione badge
        icon_label = tk.Label(icon_frame,
                             text="⚙️",  # Icona ingranaggio per configurazione
                             font=('Segoe UI Emoji', 20),
                             bg='#0D47A1',
                             fg='#FFFFFF')
        icon_label.pack(expand=True)
        
        # Badge piccolo indicatore
        badge_indicator = tk.Label(icon_frame,
                                  text="🏷️",
                                  font=('Segoe UI Emoji', 12),
                                  bg='#0D47A1',
                                  fg='#FFD700')  # Oro per distinguere
        badge_indicator.place(x=32, y=32)
        
        # Tooltip al passaggio del mouse
        def show_tooltip(event):
            # Cambia colore per feedback hover
            icon_frame.configure(bg='#1565C0')
            icon_label.configure(bg='#1565C0')
            badge_indicator.configure(bg='#1565C0')
            
        def hide_tooltip(event):
            # Ripristina colore originale
            icon_frame.configure(bg='#0D47A1')
            icon_label.configure(bg='#0D47A1')
            badge_indicator.configure(bg='#0D47A1')
        
        def open_badge_management(event):
            """Apre finestra gestione badge-NFC"""
            self.show_badge_management_window()
        
        # Bind eventi per tutti i componenti
        for widget in [icon_container, icon_frame, icon_label, badge_indicator]:
            widget.bind('<Enter>', show_tooltip)
            widget.bind('<Leave>', hide_tooltip)
            widget.bind('<Button-1>', open_badge_management)
            widget.configure(cursor='hand2')
        
        # Salva riferimento per aggiornamenti
        self.badge_management_icon = {
            'container': icon_container,
            'frame': icon_frame,
            'icon': icon_label,
            'badge': badge_indicator
        }
        
    def show_badge_management_window(self):
        """Finestra professionale per gestione abbinamento badge-NFC"""
        # Crea finestra modal professionale
        window = tk.Toplevel(self.root)
        window.title("Gestione Abbinamento Badge-NFC | TIGOTÀ Elite")
        window.configure(bg='#F5F5F5')
        window.resizable(False, False)
        
        # Dimensioni e posizionamento centrato
        window_width = 800
        window_height = 600
        
        # Calcola posizione centrale
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        window.attributes('-topmost', True)
        window.grab_set()  # Modal
        
        # Header professionale
        header_frame = tk.Frame(window, bg='#1E88E5', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#1E88E5')
        header_content.pack(expand=True, fill='both', padx=30, pady=20)
        
        # Titolo e icona
        title_frame = tk.Frame(header_content, bg='#1E88E5')
        title_frame.pack(fill='x')
        
        title_icon = tk.Label(title_frame,
                             text="⚙️🏷️",
                             font=('Segoe UI Emoji', 24),
                             bg='#1E88E5',
                             fg='#FFFFFF')
        title_icon.pack(side='left')
        
        title_label = tk.Label(title_frame,
                              text="Gestione Abbinamento Badge-NFC",
                              font=('Segoe UI', 18, 'bold'),
                              bg='#1E88E5',
                              fg='#FFFFFF')
        title_label.pack(side='left', padx=(15, 0))
        
        # Sottotitolo
        subtitle_label = tk.Label(header_content,
                                 text="Associa codici badge ai valori NFC per il riconoscimento automatico",
                                 font=('Segoe UI', 12),
                                 bg='#1E88E5',
                                 fg='#BBDEFB')
        subtitle_label.pack(anchor='w', pady=(5, 0))
        
        # Content area principale
        main_content = tk.Frame(window, bg='#F5F5F5')
        main_content.pack(expand=True, fill='both', padx=30, pady=20)
        
        # Sezione nuovo abbinamento
        self.create_new_pairing_section(main_content)
        
        # Separatore elegante - NASCOSTO
        # separator = tk.Frame(main_content, bg='#E0E0E0', height=2)
        # separator.pack(fill='x', pady=20)
        
        # Sezione lista abbinamenti esistenti - NASCOSTA su richiesta utente
        # self.create_existing_pairings_section(main_content, window)
        
        # Footer con pulsanti
        footer_frame = tk.Frame(window, bg='#F5F5F5')
        footer_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # Pulsante chiudi
        close_button = tk.Button(footer_frame,
                                text="✖️ Chiudi",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#757575',
                                fg='#FFFFFF',
                                relief='flat',
                                padx=20,
                                pady=8,
                                cursor='hand2',
                                command=window.destroy)
        close_button.pack(side='right')
        
        # Salva riferimento finestra
        self.badge_management_window = window
        
    def create_new_pairing_section(self, parent):
        """Sezione per creare nuovo abbinamento badge-NFC"""
        # Titolo sezione
        section_title = tk.Label(parent,
                                text="➕ Nuovo Abbinamento",
                                font=('Segoe UI', 16, 'bold'),
                                bg='#F5F5F5',
                                fg='#1E88E5')
        section_title.pack(anchor='w', pady=(0, 15))
        
        # Frame principale per form
        form_frame = tk.Frame(parent, bg='#FFFFFF', relief='solid', bd=1)
        form_frame.pack(fill='x', pady=(0, 10))
        
        form_content = tk.Frame(form_frame, bg='#FFFFFF')
        form_content.pack(fill='x', padx=25, pady=20)
        
        # Prima riga: Badge ID
        row1 = tk.Frame(form_content, bg='#FFFFFF')
        row1.pack(fill='x', pady=(0, 15))
        
        badge_label = tk.Label(row1,
                              text="Codice Badge:",
                              font=('Segoe UI', 14, 'bold'),  # Font più grande
                              bg='#FFFFFF',
                              fg='#333333',
                              width=12)  # Larghezza fissa per allineamento
        badge_label.pack(side='left')
        
        self.badge_entry = tk.Entry(row1,
                                   font=('Consolas', 14, 'bold'),  # Font più grande
                                   width=25,  # Campo più largo
                                   relief='solid',
                                   bd=2,  # Bordo più spesso
                                   bg='#F8F9FA',  # Sfondo leggermente diverso per indicare tocco
                                   fg='#333333',
                                   insertbackground='#333333',  # Cursore visibile
                                   cursor='hand2')  # Cursore a mano per indicare che è cliccabile
        self.badge_entry.pack(side='left', padx=(10, 0), ipady=8)  # Padding verticale interno
        
        # BINDING per aprire tastierino al tocco del campo - CON CONTROLLO ANTI-LOOP
        def open_badge_keypad(event=None):
            # Non aprire se stiamo aggiornando programmaticamente
            if getattr(self, '_programmatic_update', False):
                return
            # Non aprire se il campo ha già un valore valido (non è il placeholder)
            current_val = self.badge_entry.get()
            if current_val and current_val != "👆 Tocca per tastierino" and len(current_val.strip()) > 0:
                # Se l'utente clicca su un campo già compilato, seleziona tutto per facilitare la modifica
                self.badge_entry.select_range(0, tk.END)
                return
            self.show_numeric_keypad('badge')
        
        self.badge_entry.bind('<Button-1>', open_badge_keypad)
        
        # Tooltip visivo per far capire che il campo è toccabile
        self.badge_entry.insert(0, "👆 Tocca per tastierino")
        self.badge_entry.bind('<Enter>', lambda e: self.badge_entry.configure(bg='#E3F2FD'))
        self.badge_entry.bind('<Leave>', lambda e: self.badge_entry.configure(bg='#F8F9FA'))
        
        # Pulsante tastierino numerico - NUOVO per tablet touch
        keypad_btn = tk.Button(row1,
                              text="🔢",
                              font=('Segoe UI Emoji', 12),
                              bg='#2196F3',
                              fg='#FFFFFF',
                              relief='flat',
                              width=3,
                              pady=5,
                              cursor='hand2',
                              command=lambda: self.show_numeric_keypad('badge'))
        keypad_btn.pack(side='left', padx=(5, 0))
        
        # Seconda riga: Valore NFC
        row2 = tk.Frame(form_content, bg='#FFFFFF')
        row2.pack(fill='x', pady=(0, 15))
        
        nfc_label = tk.Label(row2,
                            text="Valore NFC:",
                            font=('Segoe UI', 14, 'bold'),  # Font più grande
                            bg='#FFFFFF',
                            fg='#333333',
                            width=12)  # Larghezza fissa per allineamento
        nfc_label.pack(side='left')
        
        # Campo NFC - SOLO LETTURA TRAMITE LETTORE HARDWARE NFC - NESSUN TASTIERINO
        self.nfc_entry = tk.Entry(row2,
                                 font=('Consolas', 14, 'bold'),  # Font più grande
                                 width=25,  # Campo più largo
                                 relief='solid',
                                 bd=2,  # Bordo più spesso
                                 bg='#F0F8FF',  # Sfondo azzurro per indicare lettura hardware
                                 fg='#333333',
                                 state='readonly',  # SOLO LETTURA - non modificabile
                                 cursor='arrow')  # Cursore normale, non cliccabile
        self.nfc_entry.pack(side='left', padx=(10, 0), ipady=8)  # Padding verticale interno
        
        # NESSUN BINDING PER TASTIERINO - Il campo NFC viene popolato solo dal lettore hardware
        # Inserisce testo esplicativo
        self.nfc_entry.config(state='normal')
        self.nfc_entry.insert(0, "🔵 Avvicina NFC al lettore")
        self.nfc_entry.configure(fg='#666666')
        self.nfc_entry.config(state='readonly')
        
        # Solo hover per feedback visivo che il campo riceve dati dal lettore
        self.nfc_entry.bind('<Enter>', lambda e: self.nfc_entry.configure(bg='#E8F5E8'))
        self.nfc_entry.bind('<Leave>', lambda e: self.nfc_entry.configure(bg='#F0F8FF'))
        
        # Terza riga: Nome/Descrizione
        row3 = tk.Frame(form_content, bg='#FFFFFF')
        row3.pack(fill='x', pady=(0, 20))
        
        name_label = tk.Label(row3,
                             text="Nome/Desc:",
                             font=('Segoe UI', 14, 'bold'),  # Font più grande
                             bg='#FFFFFF',
                             fg='#333333',
                             width=12)  # Larghezza fissa per allineamento
        name_label.pack(side='left')
        
        self.name_entry = tk.Entry(row3,
                                  font=('Segoe UI', 14, 'bold'),  # Font più grande
                                  width=35,  # Campo più largo
                                  relief='solid',
                                  bd=2,  # Bordo più spesso
                                  bg='#F8F9FA',  # Sfondo leggermente diverso per indicare tocco
                                  fg='#333333',
                                  insertbackground='#333333',  # Cursore visibile
                                  cursor='hand2')  # Cursore a mano per indicare che è cliccabile
        self.name_entry.pack(side='left', padx=(10, 0), ipady=8)  # Padding verticale interno
        
        # BINDING per aprire tastierino al tocco del campo NOME - CON CONTROLLO ANTI-LOOP
        def open_name_keypad(event=None):
            # Non aprire se stiamo aggiornando programmaticamente
            if getattr(self, '_programmatic_update', False):
                return
            # Non aprire se il campo ha già un valore valido (non è il placeholder)
            current_val = self.name_entry.get()
            if current_val and current_val != "👆 Tocca per tastierino" and len(current_val.strip()) > 0:
                # Se l'utente clicca su un campo già compilato, seleziona tutto per facilitare la modifica
                self.name_entry.select_range(0, tk.END)
                return
            self.show_numeric_keypad('name')
        
        self.name_entry.bind('<Button-1>', open_name_keypad)
        
        # Tooltip visivo per far capire che il campo è toccabile
        self.name_entry.insert(0, "👆 Tocca per tastierino")
        self.name_entry.bind('<Enter>', lambda e: self.name_entry.configure(bg='#E8F5E8'))
        self.name_entry.bind('<Leave>', lambda e: self.name_entry.configure(bg='#F8F9FA'))
        
        # Pulsante tastierino alfanumerico per NOME
        name_keypad_btn = tk.Button(row3,
                                   text="⌨️",
                                   font=('Segoe UI Emoji', 12),
                                   bg='#4CAF50',
                                   fg='#FFFFFF',
                                   relief='flat',
                                   width=3,
                                   pady=5,
                                   cursor='hand2',
                                   command=lambda: self.show_numeric_keypad('name'))
        name_keypad_btn.pack(side='left', padx=(5, 0))
        
        # Pulsante salva
        save_btn = tk.Button(form_content,
                            text="💾 Salva Abbinamento",
                            font=('Segoe UI', 12, 'bold'),
                            bg='#1E88E5',
                            fg='#FFFFFF',
                            relief='flat',
                            padx=25,
                            pady=10,
                            cursor='hand2',
                            command=self.save_badge_pairing)
        save_btn.pack(anchor='e')
        
    def create_existing_pairings_section(self, parent, window):
        """Sezione per visualizzare abbinamenti esistenti"""
        # Titolo sezione
        section_title = tk.Label(parent,
                                text="📋 Abbinamenti Esistenti",
                                font=('Segoe UI', 16, 'bold'),
                                bg='#F5F5F5',
                                fg='#1E88E5')
        section_title.pack(anchor='w', pady=(0, 15))
        
        # Container con scrollbar
        list_container = tk.Frame(parent, bg='#FFFFFF', relief='solid', bd=1)
        list_container.pack(fill='both', expand=True)
        
        # Canvas per scrolling
        canvas = tk.Canvas(list_container, bg='#FFFFFF', highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header della lista
        header_frame = tk.Frame(scrollable_frame, bg='#E3F2FD')
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        tk.Label(header_frame, text="Codice Badge", font=('Segoe UI', 10, 'bold'), 
                bg='#E3F2FD', fg='#1565C0', width=15).pack(side='left', padx=5)
        tk.Label(header_frame, text="Valore NFC", font=('Segoe UI', 10, 'bold'), 
                bg='#E3F2FD', fg='#1565C0', width=20).pack(side='left', padx=5)
        tk.Label(header_frame, text="Nome/Descrizione", font=('Segoe UI', 10, 'bold'), 
                bg='#E3F2FD', fg='#1565C0', width=25).pack(side='left', padx=5)
        tk.Label(header_frame, text="Azioni", font=('Segoe UI', 10, 'bold'), 
                bg='#E3F2FD', fg='#1565C0', width=10).pack(side='left', padx=5)
        
        # Carica abbinamenti esistenti
        self.load_existing_pairings(scrollable_frame)
        
        # Salva riferimenti
        self.pairings_canvas = canvas
        self.pairings_scrollable_frame = scrollable_frame
        
    def start_badge_scan(self):
        """Avvia scansione badge in modalità learn"""
        try:
            # Pulisce campo e prepara per input
            self.badge_entry.delete(0, tk.END)
            self.badge_entry.configure(bg='#FFF3E0')  # Sfondo arancione chiaro
            self.badge_entry.insert(0, "Avvicina badge...")
            
            # Abilita modalità learn per prossima lettura
            self.badge_learn_mode = True
            
            # Messaggio di feedback
            self.show_notification("🔍 Modalità apprendimento badge attiva - Avvicina il badge")
            
            # Auto-reset dopo 30 secondi
            self.root.after(30000, self.reset_badge_learn_mode)
            
        except Exception as e:
            print(f"❌ Errore avvio scansione badge: {e}")
            
    def start_nfc_read(self):
        """Avvia lettura NFC in modalità learn - Solo lettore hardware"""
        try:
            # Pulisce campo e prepara per input dal lettore hardware
            self.nfc_entry.config(state='normal')
            self.nfc_entry.delete(0, tk.END)
            self.nfc_entry.configure(bg='#E8F5E8')  # Sfondo verde chiaro
            self.nfc_entry.insert(0, "📡 Lettura NFC attiva...")
            self.nfc_entry.config(state='readonly')
            
            # Abilita modalità learn per prossima lettura
            self.nfc_learn_mode = True
            
            # Messaggio di feedback
            self.show_notification("📡 Modalità lettura NFC attiva - Avvicina il badge al lettore hardware")
            
            # Auto-reset dopo 30 secondi
            self.root.after(30000, self.reset_nfc_learn_mode)
            
        except Exception as e:
            print(f"❌ Errore avvio lettura NFC: {e}")
            
    def reset_badge_learn_mode(self):
        """Reset modalità apprendimento badge"""
        if hasattr(self, 'badge_learn_mode'):
            self.badge_learn_mode = False
            if hasattr(self, 'badge_entry'):
                self.badge_entry.configure(bg='#FFFFFF')
                if self.badge_entry.get() == "Avvicina badge...":
                    self.badge_entry.delete(0, tk.END)
                    
    def reset_nfc_learn_mode(self):
        """Reset modalità lettura NFC"""
        if hasattr(self, 'nfc_learn_mode'):
            self.nfc_learn_mode = False
            if hasattr(self, 'nfc_entry'):
                self.nfc_entry.config(state='normal')
                self.nfc_entry.configure(bg='#F0F8FF')
                if self.nfc_entry.get() in ["📡 Lettura NFC attiva...", "Lettura NFC..."]:
                    self.nfc_entry.delete(0, tk.END)
                    self.nfc_entry.insert(0, "🔵 Avvicina NFC al lettore")
                    self.nfc_entry.configure(fg='#666666')
                self.nfc_entry.config(state='readonly')
                    
    def save_badge_pairing(self):
        """Salva nuovo abbinamento badge-NFC"""
        try:
            badge_code = self.badge_entry.get().strip()
            nfc_value = self.nfc_entry.get().strip()
            name_desc = self.name_entry.get().strip()
            
            # Validazione
            if not badge_code or badge_code == "Avvicina badge...":
                self.show_notification("⚠️ Inserire codice badge valido")
                return
                
            if not nfc_value or nfc_value == "Lettura NFC...":
                self.show_notification("⚠️ Inserire valore NFC valido")
                return
                
            if not name_desc:
                name_desc = f"Badge {badge_code}"
            
            # Salva nel database (se supportato)
            success = False
            if hasattr(self, 'database_manager') and self.database_manager:
                try:
                    success = self.database_manager.save_badge_pairing(
                        badge_code=badge_code,
                        nfc_value=nfc_value,
                        description=name_desc
                    )
                except AttributeError:
                    print("⚠️ Metodo save_badge_pairing non implementato nel database")
                    # TEMPORANEO: simula successo per demo
                    success = True
                    print(f"📝 DEMO: Abbinamento salvato -> {badge_code} : {nfc_value} ({name_desc})")
                
            if success:
                # Reset form
                self.badge_entry.delete(0, tk.END)
                self.badge_entry.configure(bg='#FFFFFF')
                self.nfc_entry.delete(0, tk.END)
                self.nfc_entry.configure(bg='#FFFFFF')
                self.name_entry.delete(0, tk.END)
                
                # Aggiorna lista
                self.refresh_pairings_list()
                
                # Feedback successo
                self.show_notification(f"✅ Abbinamento salvato: {badge_code} → {nfc_value}")
            else:
                self.show_notification("❌ Errore salvataggio abbinamento")
                
        except Exception as e:
            print(f"❌ Errore salvataggio abbinamento: {e}")
            self.show_notification("❌ Errore durante il salvataggio")
            
    def load_existing_pairings(self, parent):
        """Carica e visualizza abbinamenti esistenti"""
        try:
            # TEMPORANEO: Database potrebbe non avere ancora il metodo get_badge_pairings
            if hasattr(self, 'database_manager') and self.database_manager:
                try:
                    pairings = self.database_manager.get_badge_pairings()
                except AttributeError:
                    print("⚠️ Metodo get_badge_pairings non implementato nel database")
                    pairings = []
            else:
                pairings = []  # Fallback se database non disponibile
            
            # Esempio di abbinamenti di default se il database è vuoto o non supportato
            if not pairings:
                pairings = [
                    {'badge_code': '0123456789', 'nfc_value': 'A1B2C3D4E5F6', 'description': 'Badge Demo Amministratore'},
                    {'badge_code': '9876543210', 'nfc_value': 'F6E5D4C3B2A1', 'description': 'Badge Demo Dipendente'},
                    {'badge_code': '1122334455', 'nfc_value': 'BC12331313AB', 'description': 'PICCOLI GIOVANNI'}
                ]
            
            # Visualizza ogni abbinamento
            for i, pairing in enumerate(pairings):
                self.create_pairing_row(parent, pairing, i)
                
        except Exception as e:
            print(f"❌ Errore caricamento abbinamenti: {e}")
            # Mostra riga di errore
            error_frame = tk.Frame(parent, bg='#FFEBEE')
            error_frame.pack(fill='x', padx=10, pady=5)
            
            error_label = tk.Label(error_frame,
                                  text="⚠️ Database in fase di configurazione - Usando dati demo",
                                  font=('Segoe UI', 10),
                                  bg='#FFEBEE',
                                  fg='#FF9800')
            error_label.pack(pady=10)
            
    def create_pairing_row(self, parent, pairing, index):
        """Crea riga per singolo abbinamento"""
        # Colore alternato per le righe
        bg_color = '#FAFAFA' if index % 2 == 0 else '#FFFFFF'
        
        row_frame = tk.Frame(parent, bg=bg_color, relief='solid', bd=1)
        row_frame.pack(fill='x', padx=10, pady=2)
        
        # Contenuto riga
        content_frame = tk.Frame(row_frame, bg=bg_color)
        content_frame.pack(fill='x', padx=10, pady=8)
        
        # Badge code
        badge_label = tk.Label(content_frame,
                              text=pairing.get('badge_code', 'N/A'),
                              font=('Consolas', 10, 'bold'),
                              bg=bg_color,
                              fg='#1565C0',
                              width=15)
        badge_label.pack(side='left', padx=5)
        
        # NFC value
        nfc_label = tk.Label(content_frame,
                            text=pairing.get('nfc_value', 'N/A'),
                            font=('Consolas', 10),
                            bg=bg_color,
                            fg='#333333',
                            width=20)
        nfc_label.pack(side='left', padx=5)
        
        # Description
        desc_label = tk.Label(content_frame,
                             text=pairing.get('description', 'N/A'),
                             font=('Segoe UI', 10),
                             bg=bg_color,
                             fg='#333333',
                             width=25,
                             anchor='w')
        desc_label.pack(side='left', padx=5)
        
        # Pulsanti azioni
        actions_frame = tk.Frame(content_frame, bg=bg_color)
        actions_frame.pack(side='left', padx=5)
        
        # Pulsante elimina
        delete_btn = tk.Button(actions_frame,
                              text="🗑️",
                              font=('Segoe UI Emoji', 10),
                              bg='#F44336',
                              fg='#FFFFFF',
                              relief='flat',
                              width=3,
                              cursor='hand2',
                              command=lambda: self.delete_pairing(pairing))
        delete_btn.pack(side='left', padx=2)
        
        # Pulsante modifica
        edit_btn = tk.Button(actions_frame,
                            text="✏️",
                            font=('Segoe UI Emoji', 10),
                            bg='#FF9800',
                            fg='#FFFFFF',
                            relief='flat',
                            width=3,
                            cursor='hand2',
                            command=lambda: self.edit_pairing(pairing))
        edit_btn.pack(side='left', padx=2)
        
    def refresh_pairings_list(self):
        """Aggiorna lista abbinamenti"""
        try:
            # Pulisce frame esistente
            for widget in self.pairings_scrollable_frame.winfo_children():
                if widget.winfo_class() != 'Frame' or 'header' not in str(widget):
                    widget.destroy()
            
            # Ricarica abbinamenti
            self.load_existing_pairings(self.pairings_scrollable_frame)
            
        except Exception as e:
            print(f"❌ Errore refresh lista: {e}")
            
    def delete_pairing(self, pairing):
        """Elimina abbinamento"""
        try:
            # Conferma eliminazione
            import tkinter.messagebox as msgbox
            
            result = msgbox.askyesno(
                "Conferma Eliminazione",
                f"Eliminare l'abbinamento?\n\nBadge: {pairing.get('badge_code')}\nNFC: {pairing.get('nfc_value')}",
                icon='warning'
            )
            
            if result:
                if hasattr(self, 'database_manager') and self.database_manager:
                    success = self.database_manager.delete_badge_pairing(pairing.get('badge_code'))
                    
                    if success:
                        self.refresh_pairings_list()
                        self.show_notification(f"✅ Abbinamento eliminato: {pairing.get('badge_code')}")
                    else:
                        self.show_notification("❌ Errore eliminazione abbinamento")
                else:
                    self.show_notification("❌ Database non disponibile")
                    
        except Exception as e:
            print(f"❌ Errore eliminazione: {e}")
            
    def edit_pairing(self, pairing):
        """Modifica abbinamento esistente"""
        try:
            # Popola i campi del form con i dati esistenti
            self.badge_entry.delete(0, tk.END)
            self.badge_entry.insert(0, pairing.get('badge_code', ''))
            
            self.nfc_entry.delete(0, tk.END)
            self.nfc_entry.insert(0, pairing.get('nfc_value', ''))
            
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, pairing.get('description', ''))
            
            # Feedback
            self.show_notification(f"📝 Modifica abbinamento: {pairing.get('badge_code')}")
            
        except Exception as e:
            print(f"❌ Errore modifica: {e}")
            
    def show_numeric_keypad(self, field_type):
        """Mostra tastierino professionale per tablet touch - BADGE NUMERICO / NOME ALFANUMERICO"""
        try:
            # GESTISCE BADGE (numerico) e NOME (alfanumerico) - Il campo NFC usa esclusivamente il lettore hardware
            if field_type not in ['badge', 'name']:
                print("⚠️ Tastierino disponibile solo per badge e nome - NFC usa lettore hardware")
                return
                
            # Crea finestra tastierino modal
            keypad_window = tk.Toplevel(self.root)
            keypad_window.configure(bg='#F5F5F5')
            keypad_window.resizable(False, False)
            
            # Dimensioni e configurazione in base al tipo
            if field_type == 'badge':
                window_width = 500
                window_height = 750
                title_text = "Inserisci Codice Badge Numerico"
                keypad_window.title("Tastierino Badge | TIGOTÀ Elite")
            else:  # name
                window_width = 1300  # Finestra molto più larga
                window_height = 1000   # Altezza aumentata per dare più spazio al pulsante
                title_text = "Inserisci Nome/Descrizione"
                keypad_window.title("Tastierino Nome | TIGOTÀ Elite")
            
            # Centra finestra
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            keypad_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            keypad_window.attributes('-topmost', True)
            keypad_window.grab_set()  # Modal
            
            # Header del tastierino
            header_frame = tk.Frame(keypad_window, bg='#1E88E5', height=60)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            header_content = tk.Frame(header_frame, bg='#1E88E5')
            header_content.pack(expand=True, fill='both', padx=20, pady=15)
            
            # Icona e titolo
            if field_type == 'badge':
                icon_text = "🔢"
            else:  # name
                icon_text = "✏️"
                
            icon_label = tk.Label(header_content,
                                 text=icon_text,
                                 font=('Segoe UI Emoji', 20),
                                 bg='#1E88E5',
                                 fg='#FFFFFF')
            icon_label.pack(side='left')
            
            title_label = tk.Label(header_content,
                                  text=title_text,
                                  font=('Segoe UI', 14, 'bold'),
                                  bg='#1E88E5',
                                  fg='#FFFFFF')
            title_label.pack(side='left', padx=(10, 0))
            
            # Area display input
            display_frame = tk.Frame(keypad_window, bg='#F5F5F5')
            display_frame.pack(fill='x', padx=20, pady=15)
            
            # Entry display con valore corrente
            self.keypad_display = tk.Entry(display_frame,
                                          font=('Consolas', 16, 'bold'),
                                          relief='solid',
                                          bd=2,
                                          justify='center',
                                          state='readonly')
            self.keypad_display.pack(fill='x', ipady=10)
            
            # Ottieni valore corrente dal campo appropriato
            if field_type == 'badge':
                current_value = self.badge_entry.get()
            else:  # name
                current_value = self.name_entry.get()
                
            # Pulisce valori placeholder e messaggi di sistema
            if current_value in ["👆 Tocca per tastierino"]:
                current_value = ""
                
            # Imposta valore corrente
            self.keypad_display.config(state='normal')
            self.keypad_display.delete(0, tk.END)
            self.keypad_display.insert(0, current_value)
            self.keypad_display.config(state='readonly')
            
            # Area tastierino
            keypad_frame = tk.Frame(keypad_window, bg='#F5F5F5')
            keypad_frame.pack(expand=True, fill='both', padx=20, pady=(0, 15))
            
            # Crea layout tastierino in base al tipo
            if field_type == 'badge':
                self.create_numeric_keypad(keypad_frame, keypad_window, field_type)
            else:  # name
                self.create_full_alphanumeric_keypad(keypad_frame, keypad_window, field_type)
                
        except Exception as e:
            print(f"❌ Errore tastierino: {e}")
            
    def create_numeric_keypad(self, parent, window, field_type):
        """Crea tastierino numerico per badge"""
        # Layout numerico 3x4 + controlli
        buttons_frame = tk.Frame(parent, bg='#F5F5F5')
        buttons_frame.pack(expand=True, pady=10)
        
        # Numeri 1-9
        for i in range(1, 10):
            row = (i - 1) // 3
            col = (i - 1) % 3
            
            btn = tk.Button(buttons_frame,
                           text=str(i),
                           font=('Arial', 18, 'bold'),
                           bg='#FFFFFF',
                           fg='#333333',
                           relief='solid',
                           bd=1,
                           width=4,
                           height=2,
                           cursor='hand2',
                           command=lambda num=i: self.keypad_input(str(num)))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Configura peso grid
            buttons_frame.grid_rowconfigure(row, weight=1)
            buttons_frame.grid_columnconfigure(col, weight=1)
        
        # Riga finale: Cancella, 0, Backspace
        # Cancella tutto
        clear_btn = tk.Button(buttons_frame,
                             text="C",
                             font=('Arial', 16, 'bold'),
                             bg='#F44336',
                             fg='#FFFFFF',
                             relief='solid',
                             bd=1,
                             width=4,
                             height=2,
                             cursor='hand2',
                             command=self.keypad_clear)
        clear_btn.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')
        
        # Zero
        zero_btn = tk.Button(buttons_frame,
                            text="0",
                            font=('Arial', 18, 'bold'),
                            bg='#FFFFFF',
                            fg='#333333',
                            relief='solid',
                            bd=1,
                            width=4,
                            height=2,
                            cursor='hand2',
                            command=lambda: self.keypad_input("0"))
        zero_btn.grid(row=3, column=1, padx=5, pady=5, sticky='nsew')
        
        # Backspace
        back_btn = tk.Button(buttons_frame,
                            text="⌫",
                            font=('Arial', 16, 'bold'),
                            bg='#FF9800',
                            fg='#FFFFFF',
                            relief='solid',
                            bd=1,
                            width=4,
                            height=2,
                            cursor='hand2',
                            command=self.keypad_backspace)
        back_btn.grid(row=3, column=2, padx=5, pady=5, sticky='nsew')
        
        # Configura peso ultima riga
        buttons_frame.grid_rowconfigure(3, weight=1)
        
        # PULSANTE CONFERMA SUPER LEGGIBILE E IMPOSSIBILE DA PERDERE
        confirm_frame = tk.Frame(parent, bg='#F5F5F5')
        confirm_frame.pack(fill='x', pady=(25, 15), padx=15)  # Ancora più spazio
        
        # Etichetta molto evidente
        confirm_label = tk.Label(confirm_frame,
                                text="👇 TOCCA QUI PER CONFERMARE 👇",
                                font=('Arial', 16, 'bold'),  # Font più grande
                                bg='#F5F5F5',
                                fg='#1976D2')  # Blu più scuro per contrasto
        confirm_label.pack(pady=(0, 10))
        
        # Pulsante conferma GIGANTE con massimo contrasto
        big_confirm_btn = tk.Button(confirm_frame,
                                   text="✅ CONFERMA",
                                   font=('Arial', 28, 'bold'),  # Font ENORME
                                   bg='#4CAF50',  # Verde brillante
                                   fg='#FFFFFF',  # Bianco puro
                                   activebackground='#45a049',  # Verde più scuro quando premuto
                                   activeforeground='#FFFFFF',
                                   relief='raised',  # Effetto 3D molto evidente
                                   bd=8,  # Bordo MOLTO spesso
                                   width=18,  # Larghezza ottimale
                                   height=4,  # Altezza maggiore
                                   cursor='hand2',
                                   highlightthickness=0,
                                   command=lambda: self.keypad_confirm(window, field_type))
        big_confirm_btn.pack(pady=20, padx=10, fill='x')  # Molto spazio e fill completo
        
        # Pulsanti azione (più piccoli ora)
        self.create_keypad_action_buttons(parent, window, field_type)
        
    def create_alphanumeric_keypad(self, parent, window, field_type):
        """Crea tastierino alfanumerico per NFC"""
        # Container principale
        keypad_container = tk.Frame(parent, bg='#F5F5F5')
        keypad_container.pack(expand=True, pady=10)
        
        # Prima sezione: Numeri 0-9
        numbers_frame = tk.Frame(keypad_container, bg='#F5F5F5')
        numbers_frame.pack(pady=(0, 10))
        
        numbers_label = tk.Label(numbers_frame,
                                text="Numeri:",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#F5F5F5',
                                fg='#333333')
        numbers_label.pack()
        
        num_buttons_frame = tk.Frame(numbers_frame, bg='#F5F5F5')
        num_buttons_frame.pack(pady=5)
        
        # Numeri in 2 righe (0-4, 5-9)
        for i in range(10):
            row = i // 5
            col = i % 5
            
            btn = tk.Button(num_buttons_frame,
                           text=str(i),
                           font=('Arial', 14, 'bold'),
                           bg='#E3F2FD',
                           fg='#1565C0',
                           relief='solid',
                           bd=1,
                           width=3,
                           height=2,
                           cursor='hand2',
                           command=lambda num=i: self.keypad_input(str(num)))
            btn.grid(row=row, column=col, padx=2, pady=2)
        
        # Seconda sezione: Lettere A-F (comuni per codici hex)
        letters_frame = tk.Frame(keypad_container, bg='#F5F5F5')
        letters_frame.pack(pady=(0, 10))
        
        letters_label = tk.Label(letters_frame,
                                text="Lettere (A-F):",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#F5F5F5',
                                fg='#333333')
        letters_label.pack()
        
        letters_buttons_frame = tk.Frame(letters_frame, bg='#F5F5F5')
        letters_buttons_frame.pack(pady=5)
        
        hex_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        for i, letter in enumerate(hex_letters):
            btn = tk.Button(letters_buttons_frame,
                           text=letter,
                           font=('Arial', 14, 'bold'),
                           bg='#E8F5E8',
                           fg='#2E7D32',
                           relief='solid',
                           bd=1,
                           width=3,
                           height=2,
                           cursor='hand2',
                           command=lambda l=letter: self.keypad_input(l))
            btn.grid(row=0, column=i, padx=2, pady=2)
        
        # Controlli
        controls_frame = tk.Frame(keypad_container, bg='#F5F5F5')
        controls_frame.pack(pady=10)
        
        # Cancella tutto
        clear_btn = tk.Button(controls_frame,
                             text="Cancella Tutto",
                             font=('Arial', 12, 'bold'),
                             bg='#F44336',
                             fg='#FFFFFF',
                             relief='solid',
                             bd=1,
                             padx=20,
                             pady=8,
                             cursor='hand2',
                             command=self.keypad_clear)
        clear_btn.pack(side='left', padx=5)
        
        # Backspace
        back_btn = tk.Button(controls_frame,
                            text="⌫ Cancella",
                            font=('Arial', 12, 'bold'),
                            bg='#FF9800',
                            fg='#FFFFFF',
                            relief='solid',
                            bd=1,
                            padx=20,
                            pady=8,
                            cursor='hand2',
                            command=self.keypad_backspace)
        back_btn.pack(side='left', padx=5)
        
        # PULSANTE CONFERMA SUPER LEGGIBILE per NFC
        confirm_frame_nfc = tk.Frame(keypad_container, bg='#F5F5F5')
        confirm_frame_nfc.pack(pady=(35, 20), padx=15, fill='x')  # Ancora più spazio
        
        # Etichetta esplicativa molto evidente per NFC
        confirm_label_nfc = tk.Label(confirm_frame_nfc,
                                    text="👇 TOCCA QUI PER CONFERMARE 👇",
                                    font=('Arial', 16, 'bold'),  # Font più grande
                                    bg='#F5F5F5',
                                    fg='#1976D2')  # Blu più scuro per contrasto
        confirm_label_nfc.pack(pady=(0, 10))
        
        # Pulsante conferma GIGANTE con massimo contrasto per NFC
        big_confirm_btn_nfc = tk.Button(confirm_frame_nfc,
                                       text="✅ CONFERMA",
                                       font=('Arial', 28, 'bold'),  # Font ENORME
                                       bg='#4CAF50',  # Verde brillante
                                       fg='#FFFFFF',  # Bianco puro
                                       activebackground='#45a049',  # Verde più scuro quando premuto
                                       activeforeground='#FFFFFF',
                                       relief='raised',  # Effetto 3D molto evidente
                                       bd=8,  # Bordo MOLTO spesso
                                       width=18,  # Larghezza ottimale
                                       height=4,  # Altezza maggiore
                                       cursor='hand2',
                                       highlightthickness=0,
                                       command=lambda: self.keypad_confirm(window, field_type))
        big_confirm_btn_nfc.pack(pady=20, padx=10, fill='x')  # Molto spazio e fill completo
        
        # Pulsanti azione (più piccoli ora)
        self.create_keypad_action_buttons(parent, window, field_type)
        
    def create_full_alphanumeric_keypad(self, parent, window, field_type):
        """Crea tastierino alfanumerico completo per nome/descrizione"""
        # Container principale SEMPLICE senza scroll
        keypad_container = tk.Frame(parent, bg='#F5F5F5')
        keypad_container.pack(expand=True, fill='both', pady=10, padx=20)
        
        # Prima sezione: Lettere A-Z
        letters_frame = tk.Frame(keypad_container, bg='#F5F5F5')
        letters_frame.pack(pady=(0, 10))
        
        letters_label = tk.Label(letters_frame,
                                text="Lettere:",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#F5F5F5',
                                fg='#333333')
        letters_label.pack()
        
        letters_buttons_frame = tk.Frame(letters_frame, bg='#F5F5F5')
        letters_buttons_frame.pack(pady=5)
        
        # Lettere in 3 righe QWERTY-like CON TASTI INGRANDITI
        qwerty_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]
        
        for row_index, row_letters in enumerate(qwerty_rows):
            row_frame = tk.Frame(letters_buttons_frame, bg='#F5F5F5')
            row_frame.pack(pady=5)  # Più spazio tra righe
            
            for letter in row_letters:
                btn = tk.Button(row_frame,
                               text=letter,
                               font=('Arial', 16, 'bold'),  # Font ingrandito
                               bg='#E3F2FD',
                               fg='#1565C0',
                               relief='solid',
                               bd=1,
                               width=4,  # Larghezza aumentata
                               height=2,  # Altezza mantenuta
                               cursor='hand2',
                               command=lambda l=letter: self.keypad_input(l))
                btn.pack(side='left', padx=3, pady=3)  # Spazio leggermente aumentato
        
        # Seconda sezione: Numeri 0-9
        numbers_frame = tk.Frame(keypad_container, bg='#F5F5F5')
        numbers_frame.pack(pady=(0, 10))
        
        numbers_label = tk.Label(numbers_frame,
                                text="Numeri:",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#F5F5F5',
                                fg='#333333')
        numbers_label.pack()
        
        num_buttons_frame = tk.Frame(numbers_frame, bg='#F5F5F5')
        num_buttons_frame.pack(pady=5)
        
        # Numeri in 1 riga (0-9) DIMENSIONI AUMENTATE
        for i in range(10):
            btn = tk.Button(num_buttons_frame,
                           text=str(i),
                           font=('Arial', 16, 'bold'),  # Font ingrandito
                           bg='#E8F5E8',
                           fg='#2E7D32',
                           relief='solid',
                           bd=1,
                           width=4,  # Larghezza aumentata
                           height=2,  # Altezza mantenuta
                           cursor='hand2',
                           command=lambda num=i: self.keypad_input(str(num)))
            btn.pack(side='left', padx=3, pady=3)  # Spazio leggermente aumentato
        
        # Terza sezione: Caratteri speciali
        special_frame = tk.Frame(keypad_container, bg='#F5F5F5')
        special_frame.pack(pady=(0, 10))
        
        special_label = tk.Label(special_frame,
                                text="Caratteri speciali:",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#F5F5F5',
                                fg='#333333')
        special_label.pack()
        
        special_buttons_frame = tk.Frame(special_frame, bg='#F5F5F5')
        special_buttons_frame.pack(pady=5)
        
        special_chars = [' ', '.', ',', '-', '_', '(', ')', '@', '!', '?']
        for char in special_chars:
            display_char = 'SPAZIO' if char == ' ' else char
            # Stile speciale per il tasto SPAZIO per renderlo più leggibile
            if char == ' ':
                btn = tk.Button(special_buttons_frame,
                               text=display_char,
                               font=('Arial', 16, 'bold'),  # Font ingrandito
                               bg='#4CAF50',  # Verde per maggiore contrasto
                               fg='#FFFFFF',  # Testo bianco per massima leggibilità
                               relief='solid',
                               bd=2,  # Bordo più spesso
                               width=7,  # Più largo per essere più visibile
                               height=2,  # Altezza mantenuta
                               cursor='hand2',
                               command=lambda c=char: self.keypad_input(c))
            else:
                btn = tk.Button(special_buttons_frame,
                               text=display_char,
                               font=('Arial', 14, 'bold'),  # Font leggermente ingrandito
                               bg='#FFF3E0',
                               fg='#E65100',
                               relief='solid',
                               bd=1,
                               width=4,  # Larghezza aumentata
                               height=2,  # Altezza mantenuta
                               cursor='hand2',
                               command=lambda c=char: self.keypad_input(c))
            btn.pack(side='left', padx=3, pady=3)  # Spazio leggermente aumentato
        
        # Controlli
        controls_frame = tk.Frame(keypad_container, bg='#F5F5F5')
        controls_frame.pack(pady=15)
        
        # Cancella tutto RIDOTTO
        clear_btn = tk.Button(controls_frame,
                             text="🗑️ Cancella Tutto",
                             font=('Arial', 12, 'bold'),  # Font ridotto
                             bg='#F44336',
                             fg='#FFFFFF',
                             relief='solid',
                             bd=1,  # Bordo ridotto
                             padx=15,  # Padding ridotto
                             pady=8,   # Padding ridotto
                             cursor='hand2',
                             command=self.keypad_clear)
        clear_btn.pack(side='left', padx=10)  # Spazio ridotto
        
        # Backspace RIDOTTO
        back_btn = tk.Button(controls_frame,
                            text="⌫ Cancella",
                            font=('Arial', 12, 'bold'),  # Font ridotto
                            bg='#FF9800',
                            fg='#FFFFFF',
                            relief='solid',
                            bd=1,  # Bordo ridotto
                            padx=15,  # Padding ridotto
                            pady=8,   # Padding ridotto
                            cursor='hand2',
                            command=self.keypad_backspace)
        back_btn.pack(side='left', padx=10)  # Spazio ridotto
        
        # Maiuscole/Minuscole toggle RIDOTTO
        caps_btn = tk.Button(controls_frame,
                            text="🔠 Maiusc",
                            font=('Arial', 12, 'bold'),  # Font ridotto
                            bg='#9C27B0',
                            fg='#FFFFFF',
                            relief='solid',
                            bd=1,  # Bordo ridotto
                            padx=15,  # Padding ridotto
                            pady=8,   # Padding ridotto
                            cursor='hand2',
                            command=self.toggle_caps)
        caps_btn.pack(side='left', padx=10)  # Spazio ridotto
        
        # PULSANTE CONFERMA SUPER LEGGIBILE per NOME
        confirm_frame_name = tk.Frame(keypad_container, bg='#F5F5F5')
        confirm_frame_name.pack(pady=(35, 20), padx=15, fill='x')

        # Etichetta esplicativa molto evidente per NOME
        confirm_label_name = tk.Label(
            confirm_frame_name,
            text="TOCCA QUI PER CONFERMARE",
            font=('Segoe UI', 18, 'bold'),
            bg='#F5F5F5',
            fg='#D32F2F'
        )
        confirm_label_name.pack(pady=(0, 8))

        # Pulsante CONFERMA con font ridotto per stare nella finestra
        big_confirm_btn_name = tk.Button(
            confirm_frame_name,
            text="CONFERMA",
            font=('Segoe UI', 24, 'bold'),  # Font ridotto
            bg='#D32F2F', fg='#FFFFFF',
            activebackground='#B71C1C', activeforeground='#FFFFFF',
            relief='raised', bd=8,
            padx=30, pady=12,  # Padding ridotto
            cursor='hand2', highlightthickness=0,
            command=lambda: self.keypad_confirm(window, field_type)
        )
        big_confirm_btn_name.pack(pady=8, padx=10)
        # Rimosso pulsante di conferma duplicato in fondo per evitare tagli e overflow verticale
        
        # NOTA: Rimosso il pulsante "Annulla" per evitare confusione
        # Gli utenti possono chiudere la finestra con la X in alto a destra
        
    def toggle_caps(self):
        """Toggle maiuscole/minuscole - implementazione semplificata"""
        # Questa funzione può essere espansa per cambiare lo stato delle lettere
        self.show_notification("💡 Usa le lettere maiuscole direttamente dal tastierino")
        
    def create_keypad_action_buttons(self, parent, window, field_type):
        """Crea pulsanti azione del tastierino - ora più piccoli"""
        # Footer con pulsanti azione più discreti
        footer_frame = tk.Frame(parent, bg='#F5F5F5')
        footer_frame.pack(fill='x', pady=(10, 0))
        
        # Solo pulsante Annulla (più piccolo)
        cancel_btn = tk.Button(footer_frame,
                              text="❌ Annulla",
                              font=('Segoe UI', 10),  # Font più piccolo
                              bg='#757575',
                              fg='#FFFFFF',
                              relief='flat',
                              padx=15,  # Padding ridotto
                              pady=6,   # Padding ridotto
                              cursor='hand2',
                              command=window.destroy)
        cancel_btn.pack(side='right')  # Solo a destra
        
    def keypad_input(self, char):
        """Gestisce input dal tastierino"""
        try:
            self.keypad_display.config(state='normal')
            current = self.keypad_display.get()
            self.keypad_display.delete(0, tk.END)
            self.keypad_display.insert(0, current + char)
            self.keypad_display.config(state='readonly')
        except Exception as e:
            print(f"❌ Errore input tastierino: {e}")
            
    def keypad_clear(self):
        """Cancella tutto il contenuto"""
        try:
            self.keypad_display.config(state='normal')
            self.keypad_display.delete(0, tk.END)
            self.keypad_display.config(state='readonly')
        except Exception as e:
            print(f"❌ Errore clear tastierino: {e}")
            
    def keypad_backspace(self):
        """Cancella ultimo carattere"""
        try:
            self.keypad_display.config(state='normal')
            current = self.keypad_display.get()
            if current:
                self.keypad_display.delete(0, tk.END)
                self.keypad_display.insert(0, current[:-1])
            self.keypad_display.config(state='readonly')
        except Exception as e:
            print(f"❌ Errore backspace tastierino: {e}")
            
    def keypad_confirm(self, window, field_type):
        """Conferma input del tastierino - BADGE (numerico) e NOME (alfanumerico)"""
        try:
            value = self.keypad_display.get()
            
            # Gestisce badge e nome - NFC usa esclusivamente lettore hardware
            if field_type not in ['badge', 'name']:
                print("⚠️ Conferma tastierino disponibile solo per badge e nome")
                window.destroy()
                return
            
            # Imposta flag per evitare apertura automatica durante inserimento programmato
            self._programmatic_update = True
            
            # Applica valore al campo appropriato
            if field_type == 'badge':
                self.badge_entry.delete(0, tk.END)
                self.badge_entry.insert(0, value)
                self.badge_entry.configure(bg='#E8F5E8')  # Verde successo
                feedback_msg = f"✅ Codice badge inserito: {value}"
            else:  # name
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, value)
                self.name_entry.configure(bg='#E8F5E8')  # Verde successo
                feedback_msg = f"✅ Nome inserito: {value}"
                
            # Chiudi tastierino
            window.destroy()
            
            # Reset flag dopo un breve delay
            self.root.after(100, lambda: setattr(self, '_programmatic_update', False))
            
            # Feedback
            self.show_notification(feedback_msg)
            
        except Exception as e:
            print(f"❌ Errore conferma tastierino: {e}")
            # Assicurati di resettare il flag anche in caso di errore
            self._programmatic_update = False
            window.destroy()
        
    def draw_premium_analog_clock(self):
        """Disegna orologio analogico premium - dimensioni dinamiche"""
        canvas = self.premium_clock_canvas
        canvas.delete("all")
        
        # Dimensioni dinamiche basate sulla size del canvas
        width = int(canvas['width'])
        height = int(canvas['height'])
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 20  # Margine di 20px
        
        # Cerchio esterno con gradiente simulato
        for i in range(5):
            r = radius - i
            alpha = 255 - (i * 30)
            color = f"#{alpha//10:01x}{alpha//10:01x}{alpha//10:01x}"
            canvas.create_oval(center_x - r, center_y - r,
                             center_x + r, center_y + r,
                             outline=color, width=1)
        
        # Cerchio principale pulito e leggibile
        canvas.create_oval(center_x - radius, center_y - radius,
                          center_x + radius, center_y + radius,
                          outline='#E91E63', width=4, fill='#FAFAFA')
        
        # Numeri ore LEGGIBILI - dimensioni equilibrate per chiarezza
        number_offset = radius * 0.25  # Offset standard per posizionamento corretto
        font_size = max(16, int(radius // 8))  # Font proporzionato e leggibile
        for hour in range(1, 13):
            angle = math.radians((hour * 30) - 90)
            x = center_x + (radius - number_offset) * math.cos(angle)
            y = center_y + (radius - number_offset) * math.sin(angle)
            
            # Ombra sottile per contrasto
            canvas.create_text(x+1, y+1, text=str(hour), 
                             font=('Segoe UI', font_size, 'bold'), 
                             fill='#CCCCCC')
            # Numero principale ben leggibile
            canvas.create_text(x, y, text=str(hour), 
                             font=('Segoe UI', font_size, 'bold'), 
                             fill='#333333')
        
        # Tacche minuti - proporzionali
        tick_length = radius * 0.08  # 8% del raggio per lunghezza tacche
        for minute in range(60):
            if minute % 5 != 0:  # Solo tacche minori
                angle = math.radians((minute * 6) - 90)
                x1 = center_x + (radius - tick_length) * math.cos(angle)
                y1 = center_y + (radius - tick_length) * math.sin(angle)
                x2 = center_x + (radius - tick_length/2) * math.cos(angle)
                y2 = center_y + (radius - tick_length/2) * math.sin(angle)
                canvas.create_line(x1, y1, x2, y2, fill='#DDDDDD', width=1)
        
        # Ora corrente
        now = datetime.now()
        hours = now.hour % 12
        minutes = now.minute
        seconds = now.second
        
        # Lancette EQUILIBRATE per leggibilità ottimale
        hour_length = radius * 0.5   # 50% del raggio
        minute_length = radius * 0.7 # 70% del raggio
        second_length = radius * 0.8 # 80% del raggio
        
        # Lancetta ore con spessore appropriato
        hour_angle = math.radians(((hours + minutes/60) * 30) - 90)
        hour_x = center_x + hour_length * math.cos(hour_angle)
        hour_y = center_y + hour_length * math.sin(hour_angle)
        
        # Ombra lancetta ore
        canvas.create_line(center_x+2, center_y+2, hour_x+2, hour_y+2, 
                          fill='#CCCCCC', width=max(6, radius//20), capstyle='round')
        canvas.create_line(center_x, center_y, hour_x, hour_y, 
                          fill='#E91E63', width=max(5, radius//25), capstyle='round')
        
        # Lancetta minuti con spessore appropriato
        minute_angle = math.radians((minutes * 6) - 90)
        minute_x = center_x + minute_length * math.cos(minute_angle)
        minute_y = center_y + minute_length * math.sin(minute_angle)
        
        # Ombra lancetta minuti
        canvas.create_line(center_x+2, center_y+2, minute_x+2, minute_y+2, 
                          fill='#CCCCCC', width=max(4, radius//30), capstyle='round')
        canvas.create_line(center_x, center_y, minute_x, minute_y, 
                          fill='#E91E63', width=max(3, radius//35), capstyle='round')
        
        # Lancetta secondi equilibrata
        second_angle = math.radians((seconds * 6) - 90)
        second_x = center_x + second_length * math.cos(second_angle)
        second_y = center_y + second_length * math.sin(second_angle)
        
        canvas.create_line(center_x, center_y, second_x, second_y, 
                          fill='#FF5722', width=max(2, radius//50), capstyle='round')
        
        # Centro appropriato e ben visibile
        center_size = max(8, radius//20)  # Centro proporzionato
        canvas.create_oval(center_x - center_size, center_y - center_size,
                          center_x + center_size, center_y + center_size,
                          fill='#FFFFFF', outline='#E91E63', width=3)
        canvas.create_oval(center_x - center_size//2, center_y - center_size//2,
                          center_x + center_size//2, center_y + center_size//2,
                          fill='#E91E63', outline='#E91E63')
        
    def start_animations(self):
        """Avvia animazioni e aggiornamenti"""
        self.update_clock_premium()
        self.animate_pulse()
        self.update_uptime()
        
    def update_clock_premium(self):
        """Aggiorna orologio premium"""
        now = datetime.now()
        
        # Disegna orologio analogico
        if hasattr(self, 'premium_clock_canvas'):
            self.draw_premium_analog_clock()
        
        # Aggiorna ora digitale
        time_str = now.strftime("%H:%M:%S")
        if hasattr(self, 'premium_time'):
            self.premium_time.config(text=time_str)
        
        # Aggiorna data
        date_str = now.strftime("%A, %d %B %Y")
        date_str = self.translate_date(date_str)
        if hasattr(self, 'premium_date'):
            self.premium_date.config(text=date_str.title())
        
        # Prossimo aggiornamento
        self.root.after(1000, self.update_clock_premium)
        
    def animate_pulse(self):
        """Animazione pulse per indicatori live"""
        self.pulse_state = (self.pulse_state + 1) % 20
        
        # Pulse NFC badge icon - ANIMAZIONE DISABILITATA
        # L'icona badge rimane statica come richiesto dall'utente
        
        # Prossima animazione
        self.root.after(100, self.animate_pulse)
        
    def update_uptime(self):
        """Aggiorna uptime sistema"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
        
        uptime = datetime.now() - self.start_time
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60
        
        uptime_str = f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
        if hasattr(self, 'uptime_label'):
            self.uptime_label.config(text=uptime_str)
        
        # Prossimo aggiornamento uptime
        self.root.after(1000, self.update_uptime)
        
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
        """Gestisce lettura badge premium con tipo timbratura selezionato + modalità apprendimento"""
        try:
            # MODALITÀ APPRENDIMENTO BADGE
            if hasattr(self, 'badge_learn_mode') and self.badge_learn_mode:
                if hasattr(self, 'badge_entry'):
                    self.badge_entry.delete(0, tk.END)
                    self.badge_entry.insert(0, str(badge_id))
                    self.badge_entry.configure(bg='#E8F5E8')  # Verde successo
                    self.badge_learn_mode = False
                    self.show_notification(f"✅ Badge acquisito: {badge_id}")
                return
            
            # MODALITÀ APPRENDIMENTO NFC - Solo da lettore hardware
            if hasattr(self, 'nfc_learn_mode') and self.nfc_learn_mode:
                if hasattr(self, 'nfc_entry'):
                    self.nfc_entry.config(state='normal')
                    self.nfc_entry.delete(0, tk.END)
                    self.nfc_entry.insert(0, str(badge_id))
                    self.nfc_entry.configure(bg='#E8F5E8')  # Verde successo
                    self.nfc_entry.config(state='readonly')
                    self.nfc_learn_mode = False
                    self.show_notification(f"✅ Valore NFC acquisito da lettore: {badge_id}")
                return
            
            # MODALITÀ NORMALE - Timbratura
            # Riproduce suono di conferma
            self.play_badge_sound()
            
            # Ottieni tipo timbratura selezionato
            tipo_selezionato = getattr(self, 'timbratura_type', tk.StringVar(value="inizio_giornata")).get()
            
            # Mappa tipi per database (compatibilità)
            tipo_db_map = {
                'inizio_giornata': 'entrata',
                'fine_giornata': 'uscita', 
                'inizio_pausa': 'pausa_inizio',
                'fine_pausa': 'pausa_fine'
            }
            
            tipo_movimento = tipo_db_map.get(tipo_selezionato, 'entrata')
            
            # Messaggio e colore per tipo
            tipo_config = {
                'inizio_giornata': {'msg': 'Buona giornata!', 'color': '#4CAF50'},
                'fine_giornata': {'msg': 'Arrivederci!', 'color': '#F44336'},
                'inizio_pausa': {'msg': 'Buona pausa!', 'color': '#FF9800'},
                'fine_pausa': {'msg': 'Bentornato!', 'color': '#2196F3'}
            }
            
            config = tipo_config.get(tipo_selezionato, {'msg': 'Timbratura registrata', 'color': '#4CAF50'})
            
            # Salva timbratura nel database SQLite
            success = self.database_manager.save_timbratura(
                badge_id=badge_id,
                tipo=tipo_movimento,
                nome="",  # Da integrare con anagrafica
                cognome=""
            )
            
            if success:
                # Feedback premium di successo
                self.show_premium_feedback({
                    'badge_id': badge_id,
                    'tipo_movimento': tipo_selezionato,
                    'messaggio': config['msg'],
                    'colore': config['color'],
                    'timestamp': datetime.now()
                })
                
                # Aggiorna contatori dashboard
                self.update_premium_counters()
                
                # Notifica nella status bar
                self.show_notification(f"✅ Badge {badge_id} - {tipo_movimento.upper()}")
            else:
                # Errore nel salvataggio
                self.show_premium_error("Errore salvataggio timbratura")
            
        except Exception as e:
            print(f"❌ Errore gestione badge: {e}")
            print(f"❌ Badge ID ricevuto: '{badge_id}'")
            print(f"❌ Tipo errore: {type(e).__name__}")
            self.show_premium_error("Errore sistema")
            
    def show_premium_feedback(self, timbratura):
        """Feedback premium con animazioni per tutti i tipi"""
        movimento = timbratura['tipo_movimento']
        badge_id = timbratura['badge_id']
        messaggio = timbratura.get('messaggio', 'Timbratura registrata')
        colore = timbratura.get('colore', '#4CAF50')
        timestamp = timbratura.get('timestamp', datetime.now())
        ora = timestamp.strftime('%d/%m/%Y %H:%M:%S')

        # Configurazione per tipi movimento con nuove icone
        movimento_config = {
            'entrata': {'text': '▶️ Entrata Registrata', 'color': '#2E7D32'},
            'uscita': {'text': '◀️ Uscita Registrata', 'color': '#D32F2F'},
            'inizio_giornata': {'text': '▶️ Inizio Giornata', 'color': '#2E7D32'},
            'fine_giornata': {'text': '◀️ Fine Giornata', 'color': '#D32F2F'},
            'inizio_pausa': {'text': '⏸️ Inizio Pausa', 'color': '#FF9800'},
            'fine_pausa': {'text': '▶️ Fine Pausa', 'color': '#2196F3'}
        }

        config = movimento_config.get(movimento, {'text': f'✅ {movimento.title()}', 'color': colore})

        # Aggiorna NFC status
        self.nfc_status_premium.config(text=config['text'], fg=config['color'])

        # Aggiorna ultima lettura
        self.last_read_label.config(text=f"Ultima lettura: {ora.split()[1]}")

        # Ripristina dopo 4 secondi
        self.root.after(4000, lambda: self.nfc_status_premium.config(
            text="🟢 Lettore Attivo", fg='#4CAF50'))
        
    def show_premium_error(self, message="Errore Lettura"):
        """Errore premium con messaggio personalizzato"""
        self.nfc_status_premium.config(text=f"❌ {message}", fg='#F44336')
        self.show_notification(f"Errore: {message}")
        
        self.root.after(3000, lambda: self.nfc_status_premium.config(
            text="🟢 Lettore Attivo", fg='#4CAF50'))
        
    def update_premium_counters(self):
        """Aggiorna contatori premium con dati SQLite reali"""
        try:
            # Ottieni statistiche reali dal database SQLite
            stats = self.database_manager.get_database_stats()
            timbrature_oggi = stats.get('timbrature_today', 0)
            total_timbrature = stats.get('total_timbrature', 0)
            unique_badges = stats.get('unique_badges', 0)
            
            # Ottieni timbrature di oggi per calcolare entrate/uscite
            timbrature_today = self.database_manager.get_timbrature_today()
            
            entrate = sum(1 for t in timbrature_today if t.get('tipo') == 'entrata')
            uscite = sum(1 for t in timbrature_today if t.get('tipo') == 'uscita')
            
            # Aggiorna labels se esistono
            if hasattr(self, 'entrate_label_premium'):
                self.entrate_label_premium.config(text=f"Entrate: {entrate}")
            if hasattr(self, 'uscite_label_premium'):
                self.uscite_label_premium.config(text=f"Uscite: {uscite}")
            if hasattr(self, 'badge_unique_label'):
                self.badge_unique_label.config(text=f"Badge unici: {unique_badges}")
                
        except Exception as e:
            print(f"Errore aggiornamento contatori: {e}")
            # Fallback a contatori statici in caso di errore
            count = getattr(self, '_daily_count', 0) + 1
            self._daily_count = count
        
    def show_notification(self, message):
        """Mostra notifica nella status bar"""
        if hasattr(self, 'notification_label'):
            self.notification_label.config(text=f"🔔 {message}")
            # Rimuovi dopo 5 secondi
            self.root.after(5000, lambda: self.notification_label.config(text=""))
        else:
            # Se la label non esiste ancora, stampa il messaggio
            print(f"📢 {message}")
        
    def refresh_dashboard(self, event=None):
        """Refresh dashboard"""
        self.show_notification("Dashboard aggiornata")
        
    def simulate_nfc_badge(self, event=None):
        """SIMULAZIONE DISABILITATA - MODALITÀ PRODUZIONE"""
        print("⚠️ SIMULAZIONE DISABILITATA - Sistema in modalità produzione")
        self.show_notification("⚠️ SOLO LETTORE NFC HARDWARE - Avvicina badge reale")
    
    def show_admin(self, event=None):
        """Panel admin premium"""
        self.show_notification("Accesso amministratore richiesto")
    
    def on_keyboard_input(self, event):
        """
        Gestisce input da lettore USB ID Card (modalità tastiera)
        Il lettore digita l'ID badge seguito da ENTER
        """
        try:
            char = event.char
            
            # Ignora tasti speciali e funzione
            if not char or ord(char) < 32:
                # ENTER premuto - processa il badge
                if event.keysym == 'Return' and self.badge_input_buffer:
                    badge_id = self.badge_input_buffer.strip()
                    if len(badge_id) >= 4:  # ID badge valido
                        print(f"🔌 Badge USB ricevuto: {badge_id}")
                        # Processa il badge come lettura NFC
                        self.on_badge_read(badge_id)
                    
                    # Reset buffer
                    self.badge_input_buffer = ""
                return
            
            # Accumula caratteri dell'ID badge
            self.badge_input_buffer += char
            
            # Limite sicurezza
            if len(self.badge_input_buffer) > 50:
                self.badge_input_buffer = self.badge_input_buffer[-50:]
                
            # Auto-processo se il lettore non invia ENTER (alcuni modelli)
            # Attesa 100ms per caratteri aggiuntivi
            self.root.after(100, self._check_badge_complete)
            
        except Exception as e:
            print(f"❌ Errore input tastiera: {e}")
    
    def _check_badge_complete(self):
        """Controlla se l'input del badge è completo (senza ENTER esplicito)"""
        try:
            # Se il buffer contiene un ID valido e non ci sono nuovi input
            if (len(self.badge_input_buffer) >= 8 and 
                len(self.badge_input_buffer) <= 20):
                
                badge_id = self.badge_input_buffer.strip()
                print(f"🔌 Badge USB completato: {badge_id}")
                self.on_badge_read(badge_id)
                self.badge_input_buffer = ""
                
        except Exception as e:
            print(f"❌ Errore controllo badge: {e}")
    
    def play_badge_sound(self):
        """Riproduce un suono di conferma per il badge rilevato"""
        self.play_sound('success')
        
        # Approccio multiplo con focus su compatibilità EXE + feedback visivo
        sound_played = False
        
        # Metodo 1: winsound.Beep - il più diretto e compatibile
        try:
            winsound.Beep(1000, 300)  # 1000Hz per 300ms
            print("✅ winsound.Beep riprodotto")
            sound_played = True
        except Exception as e:
            print(f"❌ winsound.Beep fallito: {e}")
        
        # Metodo 2: Multipli beep per enfasi
        if not sound_played:
            try:
                for i in range(3):
                    winsound.Beep(800 + i*200, 100)
                print("✅ Beep multipli riprodotti")
                sound_played = True
            except Exception as e:
                print(f"❌ Beep multipli falliti: {e}")
        
        # Metodo 3: MessageBeep di sistema
        if not sound_played:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                print("✅ MessageBeep riprodotto")
                sound_played = True
            except Exception as e:
                print(f"❌ MessageBeep fallito: {e}")
        
        # Metodo 4: PowerShell beep (molto compatibile con EXE)
        if not sound_played:
            try:
                import subprocess
                subprocess.run(["powershell", "-c", "[console]::beep(1000,300)"], 
                             capture_output=True, timeout=2)
                print("✅ PowerShell beep riprodotto")
                sound_played = True
            except Exception as e:
                print(f"❌ PowerShell beep fallito: {e}")
        
        # NUOVO: Metodo 5 - Notifica Windows (sempre visibile)
        if not sound_played:
            try:
                import subprocess
                subprocess.run([
                    "powershell", "-c", 
                    "Add-Type -AssemblyName System.Windows.Forms; " +
                    "[System.Windows.Forms.MessageBox]::Show('✅ TIMBRATURA REGISTRATA!', 'TIGOTÀ', 'OK', 'Information')"
                ], capture_output=True, timeout=3)
                print("✅ Notifica Windows mostrata")
                sound_played = True
            except Exception as e:
                print(f"❌ Notifica Windows fallita: {e}")
        
        # NUOVO: Metodo 6 - Flash della finestra per attirare attenzione
        try:
            # Flash della finestra principale
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            # Cambio colore temporaneo dello sfondo
            original_bg = self.root.cget('bg')
            self.root.configure(bg='#00FF00')  # Verde brillante
            self.root.after(200, lambda: self.root.configure(bg=original_bg))
            
            print("✅ Feedback visivo attivato")
        except Exception as e:
            print(f"❌ Feedback visivo fallito: {e}")
        
        # Metodo 7: ASCII bell come ultimo tentativo
        if not sound_played:
            try:
                print("\a\a\a")  # Triple ASCII bell
                print("✅ ASCII bell triplo riprodotto")
                sound_played = True
            except:
                pass
        
        if sound_played:
            print("✅ Suono riprodotto con successo")
        else:
            print("⚠️ Audio non disponibile - usando solo feedback visivo")
            
        # SEMPRE attivo: Feedback visivo aggiuntivo nella UI
        self.show_audio_feedback_visual()
    
    def show_audio_feedback_visual(self):
        """Mostra feedback visivo prominente quando l'audio non funziona"""
        try:
            # Crea un overlay temporaneo verde brillante
            overlay = tk.Toplevel(self.root)
            overlay.title("TIMBRATURA CONFERMATA")
            overlay.configure(bg='#00FF00')
            
            # Calcola dimensioni e posizione per centrare il popup
            popup_width = 600
            popup_height = 400
            
            # Forza l'aggiornamento della geometria della finestra principale
            self.root.update_idletasks()
            
            # Ottieni dimensioni dello schermo
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calcola posizione centrale precisa
            x = (screen_width - popup_width) // 2
            y = (screen_height - popup_height) // 2
            
            # Assicurati che la finestra non vada fuori schermo
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            
            overlay.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
            overlay.attributes('-topmost', True)
            overlay.resizable(False, False)
            
            # Centra il popup rispetto alla finestra principale se disponibile
            try:
                # Ottieni posizione e dimensione della finestra principale
                main_x = self.root.winfo_x()
                main_y = self.root.winfo_y()
                main_width = self.root.winfo_width()
                main_height = self.root.winfo_height()
                
                # Calcola centro della finestra principale
                center_x = main_x + (main_width // 2) - (popup_width // 2)
                center_y = main_y + (main_height // 2) - (popup_height // 2)
                
                # Usa il centro della finestra principale se disponibile
                if center_x > 0 and center_y > 0:
                    overlay.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
            except:
                # Fallback al centro dello schermo
                pass
            
            # Container principale con padding
            main_frame = tk.Frame(overlay, bg='#00FF00', padx=40, pady=40)
            main_frame.pack(expand=True, fill='both')
            
            # Messaggio di conferma molto grande
            confirm_label = tk.Label(
                main_frame,
                text="✅ TIMBRATURA\nREGISTRATA!",
                font=('Arial', 36, 'bold'),
                bg='#00FF00',
                fg='#000000',
                justify='center'
            )
            confirm_label.pack(expand=True)
            
            # Messaggio informativo
            info_label = tk.Label(
                main_frame,
                text="Operazione completata con successo",
                font=('Arial', 16),
                bg='#00FF00',
                fg='#333333'
            )
            info_label.pack(pady=(10, 0))
            
            # Chiudi automaticamente dopo 2 secondi (un po' più tempo per leggere)
            overlay.after(2000, overlay.destroy)
            
            # Flash dell'interfaccia principale
            original_colors = {}
            for widget_name in ['status_label', 'time_label', 'date_label']:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    original_colors[widget_name] = widget.cget('bg')
                    widget.configure(bg='#FFFF00')  # Giallo brillante
            
            # Ripristina colori dopo 500ms
            def restore_colors():
                for widget_name, original_bg in original_colors.items():
                    if hasattr(self, widget_name):
                        widget = getattr(self, widget_name)
                        widget.configure(bg=original_bg)
            
            self.root.after(500, restore_colors)
            
            print("✅ Feedback visivo prominente attivato")
            
        except Exception as e:
            print(f"❌ Errore feedback visivo: {e}")
    
    def play_sound(self, sound_type='default', volume_level=0.7):
        """
        Sistema audio enterprise - Suoni distintivi per diverse azioni
        
        Tipi disponibili:
        - 'selection': Suono selezione pulsante (soft click)
        - 'success': Suono successo timbratura (ascendente)  
        - 'error': Suono errore (discendente, grave)
        - 'warning': Suono avviso doppia timbratura (medio)
        - 'hover': Suono hover pulsante (molto soft)
        - 'confirm': Suono conferma azione (doppio beep)
        - 'default': Suono generico
        """
        
        # Configurazione suoni enterprise
        sound_config = {
            'selection': {'freq': 800, 'duration': 50, 'pattern': 'single'},
            'success': {'freq': 1200, 'duration': 200, 'pattern': 'ascending'}, 
            'error': {'freq': 400, 'duration': 300, 'pattern': 'descending'},
            'warning': {'freq': 800, 'duration': 150, 'pattern': 'double'},
            'hover': {'freq': 600, 'duration': 30, 'pattern': 'single'},
            'confirm': {'freq': 1000, 'duration': 100, 'pattern': 'confirm'},
            'default': {'freq': 1000, 'duration': 200, 'pattern': 'single'}
        }
        
        config = sound_config.get(sound_type, sound_config['default'])
        sound_played = False

        try:
            # Implementazione pattern sonori distintivi
            if config['pattern'] == 'single':
                winsound.Beep(config['freq'], config['duration'])
                
            elif config['pattern'] == 'ascending':
                # Suono successo - 3 beep ascendenti
                for i in range(3):
                    freq = config['freq'] + (i * 200)
                    winsound.Beep(freq, config['duration'] // 3)
                    
            elif config['pattern'] == 'descending':
                # Suono errore - 3 beep discendenti
                for i in range(3):
                    freq = config['freq'] - (i * 100)
                    winsound.Beep(max(200, freq), config['duration'] // 3)
                    
            elif config['pattern'] == 'double':
                # Suono warning - doppio beep
                winsound.Beep(config['freq'], config['duration'])
                time.sleep(0.05)
                winsound.Beep(config['freq'] + 200, config['duration'])
                
            elif config['pattern'] == 'confirm':
                # Suono conferma - beep + pausa + beep più alto
                winsound.Beep(config['freq'], config['duration'])
                time.sleep(0.1)
                winsound.Beep(config['freq'] + 300, config['duration'])
                
            print(f"✅ Suono {sound_type} riprodotto")
            sound_played = True
            
        except Exception as e:
            print(f"❌ Errore audio {sound_type}: {e}")

        # Fallback per errori audio
        if not sound_played:
            try:
                # Beep di fallback più semplice
                winsound.Beep(1000, 200)
                print("✅ Suono fallback riprodotto")
                sound_played = True
            except Exception as e:
                print(f"❌ Anche fallback audio fallito: {e}")

        # Feedback visivo quando audio non disponibile
        if not sound_played and sound_type in ['error', 'warning']:
            try:
                # Flash visivo rosso per errori
                original_bg = self.root.cget('bg')
                flash_color = '#FFCDD2' if sound_type == 'error' else '#FFF3E0'
                self.root.configure(bg=flash_color)
                self.root.update()
                time.sleep(0.15)
                self.root.configure(bg=original_bg)
                print(f"✅ Feedback visivo {sound_type} attivato")
            except Exception as e:
                print(f"❌ Feedback visivo {sound_type} fallito: {e}")
    def _try_pygame_audio(self):
        """Metodo deprecato - ora usiamo approccio più semplice"""
        return False
        
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        current = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current)
        
    def cleanup(self):
        """Cleanup con chiusura database SQLite"""
        print("🔄 Chiusura sistema TIGOTÀ...")
        
        # Chiudi lettore NFC
        if hasattr(self, 'nfc_reader'):
            self.nfc_reader.stop_reading()
            print("✅ Lettore NFC chiuso")
        
        # Chiudi database SQLite in modo pulito
        if hasattr(self, 'database_manager'):
            try:
                # Backup finale prima della chiusura
                self.database_manager.create_daily_backup()
                close_database()
                print("✅ Database SQLite chiuso correttamente")
            except Exception as e:
                print(f"⚠️ Errore chiusura database: {e}")
        
        print("🎯 Sistema TIGOTÀ chiuso completamente")
    
    def create_timbratura_selectors(self, parent):
        """Crea selettori per tipo timbratura con icone chiare e funzionamento evidente"""
        # Titolo esplicativo
        title_frame = tk.Frame(parent, bg='#FFFFFF')
        title_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(title_frame,
                              text="SELEZIONA TIPO DI TIMBRATURA",
                              font=('Arial', 16, 'bold'),
                              bg='#FFFFFF',
                              fg='#333333')
        title_label.pack()
        
        # Container selettori
        selectors_frame = tk.Frame(parent, bg='#FFFFFF')
        selectors_frame.pack(fill='x', pady=(20, 15))
        
        # Etichetta semplificata
        instruction_label = tk.Label(parent,
                                   text="Scegli e avvicina il badge",
                                   font=('Segoe UI', 18, 'normal'),
                                   bg='#FFFFFF',
                                   fg='#424242')
        instruction_label.pack(pady=(0, 20))
        
        # Etichetta per mostrare la selezione corrente
        self.selection_label = tk.Label(parent, 
                                       text="SELEZIONE: ENTRATA", 
                                       font=('Segoe UI', 20, 'bold'),
                                       fg='#1976D2',
                                       bg='#FFFFFF',
                                       pady=15)
        self.selection_label.pack(pady=(0, 15))
        
        # Variabile per tracciare selezione
        self.timbratura_type = tk.StringVar(value="entrata")
        
        # Configurazione selettori - Design enterprise minimalista
        selectors_config = [
            {
                'value': 'entrata',
                'text': 'ENTRATA',
                'arrow': '→',  # Freccia a destra
                'color': '#1976D2',  # Blu primario
                'selected_color': '#0D47A1'  # Blu scuro per selezione
            },
            {
                'value': 'uscita', 
                'text': 'USCITA',
                'arrow': '←',  # Freccia a sinistra  
                'color': '#424242',  # Grigio scuro
                'selected_color': '#212121'  # Grigio molto scuro per selezione
            }
        ]
        
        # Grid per selettori 1x2 (due pulsanti affiancati)
        selectors_frame.grid_rowconfigure(0, weight=1)
        selectors_frame.grid_columnconfigure(0, weight=1)
        selectors_frame.grid_columnconfigure(1, weight=1)
        
        # Crea selettori
        self.selector_buttons = {}
        for i, config in enumerate(selectors_config):
            # Posiziona i 2 pulsanti affiancati (riga 0, colonne 0 e 1)
            row = 0
            col = i
            self.create_enterprise_selector_button(selectors_frame, config, row, col)

    def select_timbratura_type(self, value):
        """Seleziona tipo timbratura - Design Enterprise"""
        try:
            # Feedback sonoro per selezione
            self.play_sound('selection')
            
            self.timbratura_type.set(value)
            
            # Aggiorna il testo della selezione
            if hasattr(self, 'selection_label'):
                if value == 'entrata':
                    self.selection_label.configure(text="SELEZIONE: ENTRATA", fg='#1976D2')
                else:
                    self.selection_label.configure(text="SELEZIONE: USCITA", fg='#424242')
            
            # Aggiorna stile di selezione per pulsanti enterprise
            for key, refs in getattr(self, 'selector_buttons', {}).items():
                button = refs.get('button')
                content = refs.get('content')
                arrow = refs.get('arrow')
                text = refs.get('text')
                config = refs.get('config', {})
                
                if not button:
                    continue
                    
                if key == value:
                    # Selezionato - bordo spesso e colore di selezione
                    button.configure(bg=config.get('selected_color', '#1976D2'), 
                                   bd=6, relief='solid')
                    if content: content.configure(bg=config.get('selected_color', '#1976D2'))
                    if arrow: arrow.configure(bg=config.get('selected_color', '#1976D2'), fg='#FFFFFF')
                    if text: text.configure(bg=config.get('selected_color', '#1976D2'), fg='#FFFFFF')
                else:
                    # Non selezionato - stile neutro
                    button.configure(bg='#F5F5F5', bd=3, relief='solid')
                    if content: content.configure(bg='#F5F5F5')
                    if arrow: arrow.configure(bg='#F5F5F5', fg=config.get('color', '#424242'))
                    if text: text.configure(bg='#F5F5F5', fg=config.get('color', '#424242'))
                    
        except Exception as e:
            print(f"❌ Errore selezione enterprise: {e}")
    
    def create_enterprise_selector_button(self, parent, config, row, col):
        """Crea pulsanti selettori enterprise - Design minimalista giganti (min 200x200)"""
        # Container principale
        container = tk.Frame(parent, bg='#FFFFFF')
        container.grid(row=row, column=col, padx=20, pady=20, sticky='ew')
        
        # Pulsante selettore enterprise gigante (min 200x200)
        button = tk.Frame(container,
                         bg='#F5F5F5',
                         relief='solid',
                         bd=3,
                         highlightthickness=0,
                         width=250,  # Più grande di 200x200
                         height=200)
        button.pack_propagate(False)
        button.pack()
        
        # Container per contenuto centrato
        content = tk.Frame(button, bg='#F5F5F5')
        content.place(relx=0.5, rely=0.5, anchor='center')
        
        # Freccia grande e elegante
        arrow_label = tk.Label(content, 
                              text=config['arrow'],
                              font=('Segoe UI', 48, 'bold'),
                              fg=config['color'],
                              bg='#F5F5F5')
        arrow_label.pack(pady=(0, 10))
        
        # Testo principale grande
        text_label = tk.Label(content,
                             text=config['text'],
                             font=('Segoe UI', 24, 'bold'),
                             fg=config['color'],
                             bg='#F5F5F5')
        text_label.pack()
        
        # Salva riferimenti per aggiornamenti
        value = config['value']
        self.selector_buttons[value] = {
            'button': button,
            'content': content,
            'arrow': arrow_label,
            'text': text_label,
            'config': config
        }
        
        # Bind eventi per interazione
        for widget in [button, content, arrow_label, text_label]:
            widget.bind("<Button-1>", lambda e, v=value: self.select_timbratura_type(v))
            widget.bind("<Enter>", lambda e, v=value: self.hover_enterprise_selector(v, True))
            widget.bind("<Leave>", lambda e, v=value: self.hover_enterprise_selector(v, False))
    
    def hover_enterprise_selector(self, value, is_entering):
        """Effetto hover per selettori enterprise"""
        try:
            refs = self.selector_buttons.get(value, {})
            button = refs.get('button')
            if not button:
                return
                
            current_selection = self.timbratura_type.get()
            
            if is_entering and value != current_selection:
                # Hover su pulsante non selezionato
                button.configure(bd=4, highlightbackground='#BDBDBD')
            elif not is_entering and value != current_selection:
                # Lascia hover su pulsante non selezionato
                button.configure(bd=3, highlightbackground='#E0E0E0')
        except Exception as e:
            print(f"❌ Errore hover enterprise: {e}")
            
    def create_selector_button(self, parent, config, row, col):
        """Crea pulsanti selettori radio-style moderni"""
        # Container principale
        container = tk.Frame(parent, bg='#FFFFFF')
        container.grid(row=row, column=col, padx=15, pady=15, sticky='ew')
        
        # Pulsante selettore con stile radio (40% più grande)
        button = tk.Frame(container,
                         bg='#E0E0E0',
                         relief='solid',
                         bd=2,
                         highlightthickness=0,
                         width=224,
                         height=168)
        button.pack_propagate(False)
        button.pack()

        # Frame contenuto con padding
        content = tk.Frame(button, bg='#F5F5F5')
        content.pack(expand=True, fill='both', padx=15, pady=15)

        # Frame per l'icona centrata
        icon_frame = tk.Frame(content, bg='#F5F5F5')
        icon_frame.pack(expand=True, fill='both')

        if config['value'] == 'entrata':
            # Carica immagine ENTRATA
            try:
                entrata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "immagini", "ENTRATA.png")
                if os.path.exists(entrata_path):
                    from PIL import Image, ImageTk
                    entrata_img = Image.open(entrata_path)
                    entrata_img = entrata_img.resize((130, 130), Image.Resampling.LANCZOS)
                    entrata_photo = ImageTk.PhotoImage(entrata_img)
                    if not hasattr(self, 'selector_images'): 
                        self.selector_images = {}
                    self.selector_images['entrata'] = entrata_photo
                    porta_label = tk.Label(icon_frame, image=entrata_photo, bg='#F5F5F5')
                else:
                    porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                         bg='#F5F5F5', fg='#2196F3')
            except Exception as e:
                print(f"⚠️ Errore caricamento ENTRATA: {e}")
                porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                     bg='#F5F5F5', fg='#2196F3')
            porta_label.pack(expand=True)
        else:
            # Carica immagine USCITA
            try:
                uscita_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "immagini", "USCITA.png")
                if os.path.exists(uscita_path):
                    from PIL import Image, ImageTk
                    uscita_img = Image.open(uscita_path)
                    uscita_img = uscita_img.resize((130, 130), Image.Resampling.LANCZOS)
                    uscita_photo = ImageTk.PhotoImage(uscita_img)
                    if not hasattr(self, 'selector_images'): 
                        self.selector_images = {}
                    self.selector_images['uscita'] = uscita_photo
                    porta_label = tk.Label(icon_frame, image=uscita_photo, bg='#F5F5F5')
                else:
                    porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                         bg='#F5F5F5', fg='#000000')
            except Exception as e:
                print(f"⚠️ Errore caricamento USCITA: {e}")
                porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                     bg='#F5F5F5', fg='#000000')
            porta_label.pack(expand=True)

        # Click handler
        def on_click(event):
            self.select_timbratura_type(config['value'])
        
        # Hover effects per pulsanti selettori
        def on_enter(event):
            if config['value'] != self.timbratura_type.get():
                button.configure(bg='#E8E8E8', bd=3, relief='solid')
                content.configure(bg='#E8E8E8')
                icon_frame.configure(bg='#E8E8E8')
                porta_label.configure(bg='#E8E8E8')

        def on_leave(event):
            if config['value'] != self.timbratura_type.get():
                button.configure(bg='#F5F5F5', bd=2, relief='solid')
                content.configure(bg='#F5F5F5')
                icon_frame.configure(bg='#F5F5F5')
                porta_label.configure(bg='#F5F5F5')
                content.configure(bg=config['bg_color'])

        widgets = [button, content, icon_frame, porta_label]
        for widget in widgets:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.configure(cursor='hand2')
        
        # Salva riferimenti
        self.selector_buttons[config['value']] = {
            'container': container,
            'button': button,
            'content': content,
            'icon_frame': icon_frame,
            'porta_label': porta_label,
            'config': config
        }
        
        # Selezione iniziale
        if config['value'] == self.timbratura_type.get():
            self.select_timbratura_type(config['value'])
        
    # Rimuoviamo duplicati: handler già definiti e bind già applicati sopra
    # Selezione iniziale è già gestita sopra

    def _on_circle_hover_enter(self, canvas, circle_id, config):
        """Hover enter per bottoni circolari"""
        try:
            # Effetto ingrandimento del cerchio
            canvas.itemconfig(circle_id, width=6)  # Bordo più spesso
            canvas.configure(bg='#F8F9FA')  # Sfondo leggermente diverso
        except Exception as e:
            print(f"❌ Errore hover enter: {e}")
    
    def _on_circle_hover_leave(self, canvas, circle_id, config):
        """Hover leave per bottoni circolari"""
        try:
            # Ripristina dimensioni normali
            canvas.itemconfig(circle_id, width=4)  # Bordo normale
            canvas.configure(bg='#FFFFFF')  # Sfondo bianco
        except Exception as e:
            print(f"❌ Errore hover leave: {e}")
    # Fine hover_leave; rimosso blocco PNG errato
    
    def schedule_real_data_update(self):
        """Programma aggiornamenti automatici dei dati reali"""
        try:
            # Aggiorna dati dipendenti dal database reale
            if hasattr(self, 'update_real_employee_data'):
                self.update_real_employee_data()
            
            # Programma prossimo aggiornamento tra 30 secondi
            self.root.after(30000, self.schedule_real_data_update)
        except Exception as e:
            print(f"❌ Errore aggiornamento automatico: {e}")
            # Riprova tra 60 secondi se c'è un errore
            self.root.after(60000, self.schedule_real_data_update)
            
    def run(self):
        """Avvia app elite"""
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
        app = TigotaEliteDashboard()
        app.run()
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



