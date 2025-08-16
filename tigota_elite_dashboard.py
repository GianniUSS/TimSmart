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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass
from nfc_manager import NFCReader  # Lettore NFC
try:
    import importlib
    pygame = importlib.import_module('pygame')  # type: ignore
    PYGAME_AVAILABLE = True
except Exception:
    pygame = None  # type: ignore
    PYGAME_AVAILABLE = False

# Supporto immagine (JPEG/PNG/GIF) con Pillow
try:
    from PIL import Image, ImageTk  # type: ignore
    PIL_AVAILABLE = True
except Exception:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    PIL_AVAILABLE = False

class TigotaEliteDashboard:
    def __init__(self):
        """Inizializza la dashboard TIGOTÀ Elite"""
        # Configurazione di base
        self.selected_action = None
        self.time_var = None
        self.sec_var = None
        self.is_closing = False
        self.active_timers = []
        self.kiosk_mode_active = False
        self.kiosk_exit_pin = "2580"
        self.badge_learn_mode = False
        self.nfc_learn_mode = False
        self._programmatic_update = False
        self.is_tablet_resolution = False
        self.show_seconds = True
        self.nfc_reader = None  # Istanza lettore NFC
        # Cattura tastiera per lettori "ID Card Reader" (modalità tastiera)
        self._hid_entry = None
        self._badge_buffer = ''
        self._capture_active = False
        # Scheduler trasferimento TXT
        self._transfer_thread = None
        self._transfer_stop = threading.Event()
        # Feedback toast duration (ms), overridable via config [UI] feedback_toast_ms
        self.feedback_toast_ms = 2000

        # Design tokens per interfaccia professionale moderna
        self.design_tokens = {
            # Colori primari - palette blu moderna
            'primary': '#2563EB',           # Blu moderno e professionale
            'primary_light': '#3B82F6',     # Blu chiaro per hover
            'primary_dark': '#1D4ED8',      # Blu scuro per stati attivi

            # Colori di stato
            'success': '#10B981',           # Verde smeraldo moderno
            'warning': '#F59E0B',           # Ambra per attenzioni
            'danger': '#EF4444',            # Rosso moderno
            'info': '#06B6D4',              # Ciano per informazioni

            # Palette neutri - scala grigia moderna
            'white': '#FFFFFF',
            'gray_50': '#F9FAFB',           # Sfondo principale
            'gray_100': '#F3F4F6',          # Sfondo secondario
            'gray_200': '#E5E7EB',          # Bordi sottili
            'gray_300': '#D1D5DB',          # Bordi normali
            'gray_400': '#9CA3AF',          # Testo disabilitato
            'gray_500': '#6B7280',          # Testo secondario
            'gray_600': '#4B5563',          # Testo principale
            'gray_700': '#374151',          # Testi importanti
            'gray_800': '#1F2937',          # Intestazioni
            'gray_900': '#111827',          # Testo massimo contrasto

            # Background e superfici
            'background': '#F9FAFB',        # Sfondo app
            'surface': '#FFFFFF',           # Card e superfici
            'surface_elevated': '#FFFFFF',   # Superfici elevate (modal, dropdown)

            # Testo - gerarchia tipografica
            'text_primary': '#111827',       # Testo principale
            'text_secondary': '#6B7280',     # Testo secondario
            'text_muted': '#9CA3AF',        # Testo disabilitato
            'text_inverse': '#FFFFFF',      # Testo su sfondo scuro

            # Spaziature - sistema 8pt
            'spacing_xs': 4,
            'spacing_sm': 8,
            'spacing_md': 16,
            'spacing_lg': 24,
            'spacing_xl': 32,
            'spacing_2xl': 48,
            'spacing_3xl': 64,

            # Ombre - colori grigi per simulare ombre
            'shadow_sm': '#E5E7EB',        # Ombra sottile
            'shadow_md': '#D1D5DB',        # Ombra media
            'shadow_lg': '#9CA3AF',        # Ombra pronunciata

            # Border radius - angoli moderni
            'radius_sm': 6,
            'radius_md': 8,
            'radius_lg': 12,
            'radius_xl': 16,

            # Typography - font sizing moderna
            'font_xs': 12,
            'font_sm': 14,
            'font_base': 16,
            'font_lg': 18,
            'font_xl': 20,
            'font_2xl': 24,
            'font_3xl': 30,
            'font_4xl': 36,
            'font_5xl': 48
        }

        # Carica configurazione kiosk
        self.load_kiosk_config()

    def set_root(self, root):
        """Imposta il riferimento alla finestra root"""
        self.root = root

    # --- Tablet scaling helpers ---
    def init_scaling(self, parent):
        """Calcola fattore di scala e dimensioni viewport ottimizzate per tablet 8" (baseline 1280x800)."""
        try:
            self.vw = parent.winfo_screenwidth()
            self.vh = parent.winfo_screenheight()
        except tk.TclError:
            # Fallback se la finestra non è ancora pronta
            self.vw, self.vh = 1280, 800
        
        # Baseline per tablet 8 pollici
        BASE_WIDTH, BASE_HEIGHT = 1280, 800
        
        # Calcolo scaling factor con bounds di sicurezza
        scale_x = self.vw / BASE_WIDTH
        scale_y = self.vh / BASE_HEIGHT
        self.scale = max(0.5, min(3.0, min(scale_x, scale_y)))  # Limiti ragionevoli
        
        # Helper per scaling con cache
        self._scale_cache = {}
        def scaled_value(v):
            if v not in self._scale_cache:
                self._scale_cache[v] = max(1, int(round(v * self.scale)))
            return self._scale_cache[v]
        
        self.s = scaled_value

    # --- Drawing helpers ---
    def draw_rounded_rect(self, canvas: tk.Canvas, x1, y1, x2, y2, radius, **kwargs):
        """Disegna un rettangolo con angoli arrotondati ottimizzato."""
        # Validazione parametri
        if x2 <= x1 or y2 <= y1:
            return None
            
        # Calcolo radius sicuro
        max_radius = min((x2 - x1) / 2, (y2 - y1) / 2)
        r = max(0, min(radius, max_radius))
        
        if r == 0:
            # Rectangle normale se radius troppo piccolo
            return canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
        
        # Punti per polygon arrotondato ottimizzato
        points = [
            x1 + r, y1,           # Top edge start
            x2 - r, y1,           # Top edge end  
            x2, y1 + r,           # Top-right corner
            x2, y2 - r,           # Right edge
            x2 - r, y2,           # Bottom-right corner
            x1 + r, y2,           # Bottom edge
            x1, y2 - r,           # Bottom-left corner
            x1, y1 + r,           # Left edge back to start
        ]
        
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def create_pill_button(self, parent, text: str, bg_color: str, fg_color: str, command):
        """Crea un pulsante pill button responsive con raggio pieno e testo ben visibile.
        Supporta stato di selezione (selector) con contorno evidenziato.
        """
        # Dimensioni proporzionali
        width = int(self.vw * 0.34)
        height = int(self.vh * 0.09)
        radius = max(self.s(16), int(height * 0.50))  # full pill
        font_size = max(self.s(24), int(height * 0.48))
        
        canvas = tk.Canvas(parent, width=width, height=height, bg='#FFFFFF', highlightthickness=0, bd=0, cursor='hand2')
        rect_id = self.draw_rounded_rect(canvas, 0, 0, width, height, radius, fill=bg_color, outline='', width=0)
        text_id = canvas.create_text(width // 2, height // 2, text=text, fill=fg_color, font=('Segoe UI', font_size, 'bold'), anchor='center')
        
        state = {'selected': False}
        
        def set_selected(flag: bool):
            state['selected'] = bool(flag)
            if state['selected']:
                # Evidenzia con contorno spesso e leggero scurimento della pill
                outline_col = self._darken_color(bg_color, 0.35)
                canvas.itemconfig(rect_id, outline=outline_col, width=self.s(6), fill=self._darken_color(bg_color, 0.05))
            else:
                canvas.itemconfig(rect_id, outline='', width=0, fill=bg_color)
            # Mantieni testo leggibile
            canvas.itemconfig(text_id, fill=fg_color)
        
        def handle_click(event=None):
            # Effetto click breve
            original = canvas.itemcget(rect_id, 'fill')
            darker = self._darken_color(original.lstrip('#'), 0.1) if isinstance(original, str) else bg_color
            try:
                canvas.itemconfig(rect_id, fill=darker)
                canvas.after(120, lambda: canvas.itemconfig(rect_id, fill=original))
            except Exception:
                pass
            # Esegui callback
            if callable(command):
                try:
                    command()
                except Exception as e:
                    print(f'Errore pulsante: {e}')
        
        for item in [canvas, rect_id, text_id]:
            if hasattr(item, 'bind'):
                item.bind('<Button-1>', handle_click)
            else:
                canvas.tag_bind(item, '<Button-1>', handle_click)
        
        return {
            'canvas': canvas,
            'rect_id': rect_id,
            'text_id': text_id,
            'bg_color': bg_color,
            'fg_color': fg_color,
            'command': command,
            'set_selected': set_selected,
            'is_selected': lambda: state['selected'],
        }
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Scurisce un colore hex di un fattore dato."""
        try:
            # Rimuovi # se presente
            hex_color = hex_color.lstrip('#')
            
            # Converti in RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Applica scurimento
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color  # Ritorna colore originale se errore

    # --- Layout main ---
    def build_dashboard(self, parent):
        """Dashboard TIGOTÀ - Full-screen, scaling 8" e mockup-spec con topbar brand."""
        parent.configure(bg='#FFFFFF')
        self.init_scaling(parent)

        # Wrapper a griglia per: header (row 0), spacer top (row 1), contenuto (row 2), spacer bottom (row 3), footer NFC (row 4)
        outer = tk.Frame(parent, bg='#FFFFFF')
        outer.pack(fill='both', expand=True)
        for r, w in ((0, 0), (1, 1), (2, 0), (3, 1), (4, 0)):
            outer.grid_rowconfigure(r, weight=w)
        outer.grid_columnconfigure(0, weight=1)

        # Topbar brand
        self.create_brand_topbar(outer)

        # Spacer superiore per centrare verticalmente
        tk.Frame(outer, bg='#FFFFFF').grid(row=1, column=0, sticky='nsew')

        # Contenuto centrato
        content = tk.Frame(outer, bg='#FFFFFF')
        content.grid(row=2, column=0, sticky='n')

        # Contenuto principale
        self.create_large_clock(content)
        self.create_action_buttons(content)

        # Spacer inferiore per centrare verticalmente
        tk.Frame(outer, bg='#FFFFFF').grid(row=3, column=0, sticky='nsew')

        # Barra NFC ancorata in basso (nuova row 4)
        self.create_nfc_indicator(outer)

        # Setup cattura tastiera per lettori USB in modalità tastiera
        try:
            self._setup_keyboard_capture()
        except Exception as e:
            print(f"[NFC] Setup keyboard capture fallito: {e}")

        # Avvia scheduler trasferimento TXT giornaliero
        try:
            self._start_transfer_scheduler()
        except Exception as e:
            print(f"[TRANSFER] Avvio scheduler fallito: {e}")

    # Nota: il wizard ora si apre cliccando l'icona in alto a destra; F10 disabilitato su richiesta.

    def create_brand_topbar(self, parent):
        """Crea topbar più spessa (≈11% vh, min 84px), con logo TIGOTA centrato, accento rosso e icona a destra."""
        import tkinter.font as tkfont

        # Dimensioni e proporzioni
        TOPBAR_HEIGHT_RATIO = 0.11  # era 0.09
        LOGO_FONT_RATIO = 0.66
        ACCENT_WIDTH_RATIO = 0.70
        ACCENT_HEIGHT_RATIO = 0.28
        ACCENT_SKEW_RATIO = 0.20
        ACCENT_OFFSET_Y_RATIO = 0.10

        # Stile brand TIGOTA
        BRAND_BG_COLOR = '#5FA8AF'
        BRAND_TEXT_COLOR = '#FFFFFF'
        BRAND_ACCENT_COLOR = '#E22646'

        bar_height = max(self.s(84), int(self.vh * TOPBAR_HEIGHT_RATIO))

        topbar_frame = tk.Frame(parent, bg=BRAND_BG_COLOR, height=bar_height)
        topbar_frame.grid(row=0, column=0, sticky='ew')
        topbar_frame.grid_propagate(False)

        canvas = tk.Canvas(topbar_frame, bg=BRAND_BG_COLOR, highlightthickness=0, bd=0, height=bar_height)
        canvas.pack(fill='both', expand=True)

        logo_font_size = max(12, int(bar_height * LOGO_FONT_RATIO))
        brand_font = tkfont.Font(family='Segoe UI', size=logo_font_size, weight='bold')

        # Carica icone topbar: sinistra (impostazioni), centro (logo TIGOTA), destra (NFC/info)
        self._topbar_left_icon = None
        self._topbar_center_logo = None
        self._topbar_icon = None
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Sinistra: icona impostazioni
            left_icon_path = os.path.join(base_dir, 'Immagini', 'icona_setting.png')
            if os.path.exists(left_icon_path):
                target_h_l = int(bar_height * 0.70)
                if PIL_AVAILABLE:
                    try:
                        pil_left = Image.open(left_icon_path)
                        w, h = pil_left.size
                        if h > 0:
                            scale = target_h_l / float(h)
                            new_w = max(1, int(round(w * scale)))
                            new_h = max(1, int(round(h * scale)))
                            resample = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
                            pil_left = pil_left.resize((new_w, new_h), resample)
                        self._topbar_left_icon = ImageTk.PhotoImage(pil_left)
                    except Exception:
                        self._topbar_left_icon = None
                else:
                    try:
                        img = tk.PhotoImage(file=left_icon_path)
                        if img.height() > target_h_l:
                            factor = max(1, img.height() // max(1, target_h_l))
                            img = img.subsample(factor, factor)
                        self._topbar_left_icon = img
                    except Exception:
                        self._topbar_left_icon = None
            # Centro: logo TIGOTA
            center_candidates = [
                os.path.join(base_dir, 'Immagini', 'logo_tigota.png'),
                os.path.join(base_dir, 'Immagini', 'logo_tigota_white.png'),
                os.path.join(base_dir, 'Immagini', 'logo_tigota_transparent.png'),
                os.path.join(base_dir, 'Immagini', 'logo_tigota.jpg'),
                os.path.join(base_dir, 'Immagini', 'logo_tigota.jpeg'),
                os.path.join(base_dir, 'Immagini', 'TIGOTA_logo.png'),
            ]
            center_logo_path = next((p for p in center_candidates if os.path.exists(p)), None)
            if center_logo_path:
                target_h_c = int(bar_height * 1.0)  # Massimo possibile: 100% dell'altezza
                ext = os.path.splitext(center_logo_path)[1].lower()
                if PIL_AVAILABLE:
                    try:
                        pil_logo = Image.open(center_logo_path)
                        w, h = pil_logo.size
                        if h > 0:
                            scale = target_h_c / float(h)
                            new_w = max(1, int(round(w * scale)))
                            new_h = max(1, int(round(h * scale)))
                            resample = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
                            pil_logo = pil_logo.resize((new_w, new_h), resample)
                        self._topbar_center_logo = ImageTk.PhotoImage(pil_logo)
                    except Exception:
                        self._topbar_center_logo = None
                else:
                    if ext in ('.png', '.gif'):
                        try:
                            img = tk.PhotoImage(file=center_logo_path)
                            if img.height() > target_h_c:
                                factor = max(1, img.height() // max(1, target_h_c))
                                img = img.subsample(factor, factor)
                            self._topbar_center_logo = img
                        except Exception:
                            self._topbar_center_logo = None

            # Destra: icona NFC/info
            icon_path = os.path.join(base_dir, 'Immagini', 'icon_badge_nfc_text_longbody_bigger_transparent_512.png')
            if os.path.exists(icon_path):
                target_h = int(bar_height * 0.82)
                if PIL_AVAILABLE:
                    try:
                        pil_img = Image.open(icon_path)
                        w, h = pil_img.size
                        if h > 0:
                            scale = target_h / float(h)
                            new_w = max(1, int(round(w * scale)))
                            new_h = max(1, int(round(h * scale)))
                            resample = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
                            pil_img = pil_img.resize((new_w, new_h), resample)
                        self._topbar_icon = ImageTk.PhotoImage(pil_img)
                    except Exception:
                        self._topbar_icon = None
                else:
                    try:
                        img = tk.PhotoImage(file=icon_path)
                        if img.height() > target_h:
                            factor = max(1, img.height() // max(1, target_h))
                            img = img.subsample(factor, factor)
                        self._topbar_icon = img
                    except Exception:
                        self._topbar_icon = None
        except Exception:
            self._topbar_icon = None

        def redraw_logo(event=None):
            canvas.delete('all')
            h = bar_height
            w = canvas.winfo_width() or self.vw
            cx, cy = w // 2, h // 2
            
            # Centro: preferisci logo immagine, fallback al testo semplice (senza accento)
            if getattr(self, '_topbar_center_logo', None) is not None:
                try:
                    canvas.create_image(cx, cy, image=self._topbar_center_logo, anchor='center')
                except Exception:
                    # Fallback testo semplice
                    canvas.create_text(cx, cy, text='TIGOTA', anchor='center', font=brand_font, fill=BRAND_TEXT_COLOR)
            else:
                # Disegna solo il testo centrato senza accento (come nello screenshot)
                canvas.create_text(cx, cy, text='TIGOTA', anchor='center', font=brand_font, fill=BRAND_TEXT_COLOR)

            # Disegna icona in alto a sinistra (impostazioni) se disponibile
            try:
                if getattr(self, '_topbar_left_icon', None) is not None:
                    margin_l = self.s(14)
                    img_id_l = canvas.create_image(margin_l, cy, image=self._topbar_left_icon, anchor='w')
                    def on_left_click(evt=None):
                        self.open_settings_dialog()
                    canvas.tag_bind(img_id_l, '<Button-1>', on_left_click)
                    canvas.configure(cursor='hand2')
            except Exception:
                pass

            # Disegna icona in alto a destra se disponibile
            try:
                if getattr(self, '_topbar_icon', None) is not None:
                    margin = self.s(14)
                    # Crea l'immagine e rendila cliccabile per aprire il wizard
                    img_id = canvas.create_image(w - margin, cy, image=self._topbar_icon, anchor='e')
                    def on_icon_click(evt=None):
                        self.open_abbinamento_wizard()
                    canvas.tag_bind(img_id, '<Button-1>', on_icon_click)
                    canvas.configure(cursor='hand2')
            except Exception:
                pass


        canvas.bind('<Configure>', redraw_logo)
        topbar_frame.after(10, redraw_logo)

    def open_abbinamento_wizard(self):
        """Apre il wizard di abbinamento (singola istanza)."""
        try:
            # Se è già aperto, porta in primo piano e metti focus
            if hasattr(self, '_abbinamento_wizard') and self._abbinamento_wizard and self._abbinamento_wizard.winfo_exists():
                try:
                    self._abbinamento_wizard.deiconify()
                    self._abbinamento_wizard.lift()
                    self._abbinamento_wizard.focus_force()
                    return
                except Exception:
                    pass
            from abbinamento_wizard import AbbinamentoWizard
            # Crea nuova istanza e memorizza riferimento
            self._abbinamento_wizard = AbbinamentoWizard(self.root)
        except Exception as e:
            print(f"[UI] Impossibile aprire wizard abbinamento: {e}")

    def open_settings_dialog(self):
        """Apre la finestra Impostazioni con i campi 'codice_sede', 'codice_negozio', 'ora trasferimento' e 'cartella trasferimento'."""
        try:
            from tkinter import messagebox, filedialog

            # Helpers lettura/scrittura config_negozio.ini
            def _config_path():
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                except Exception:
                    base_dir = '.'
                return os.path.join(base_dir, 'config_negozio.ini')

            def _load_codes():
                cfg = configparser.ConfigParser()
                cfg.read(_config_path(), encoding='utf-8')
                sede = ''
                negozio = ''
                if cfg.has_section('AZIENDA'):
                    sede = cfg.get('AZIENDA', 'codice_sede', fallback='').strip()
                    negozio = cfg.get('AZIENDA', 'codice_negozio', fallback='').strip()
                # backward-compat: se non presenti, prova da [NEGOZIO].numero
                if not negozio and cfg.has_section('NEGOZIO'):
                    negozio = cfg.get('NEGOZIO', 'numero', fallback='').strip()
                return sede, negozio

            def _load_transfer():
                cfg = configparser.ConfigParser()
                cfg.read(_config_path(), encoding='utf-8')
                # Default: 02:00 e cartella 'export' nella base dir
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                except Exception:
                    base_dir = '.'
                default_dir = os.path.join(base_dir, 'export')
                ora = '02:00'
                cartella = default_dir
                if cfg.has_section('TRASFERIMENTO'):
                    ora = cfg.get('TRASFERIMENTO', 'ora', fallback=ora).strip() or ora
                    cartella = cfg.get('TRASFERIMENTO', 'cartella', fallback=cartella).strip() or cartella
                return ora, cartella

            def _save_codes(cod_sede: str, cod_negozio: str, ora_tx: str, dir_tx: str) -> bool:
                try:
                    path = _config_path()
                    cfg = configparser.ConfigParser()
                    # Leggi esistente per preservare le altre sezioni/chiavi
                    cfg.read(path, encoding='utf-8')
                    if not cfg.has_section('AZIENDA'):
                        cfg.add_section('AZIENDA')
                    cfg.set('AZIENDA', 'codice_sede', cod_sede.strip())
                    cfg.set('AZIENDA', 'codice_negozio', cod_negozio.strip())
                    # Sezione trasferimento
                    if not cfg.has_section('TRASFERIMENTO'):
                        cfg.add_section('TRASFERIMENTO')
                    cfg.set('TRASFERIMENTO', 'ora', ora_tx.strip())
                    cfg.set('TRASFERIMENTO', 'cartella', dir_tx.strip())
                    # Aggiorna metadati in [SISTEMA]
                    if not cfg.has_section('SISTEMA'):
                        cfg.add_section('SISTEMA')
                    cfg.set('SISTEMA', 'ultima_modifica', datetime.now().strftime('%Y-%m-%d'))
                    # Scrivi file
                    with open(path, 'w', encoding='utf-8') as f:
                        cfg.write(f)
                    return True
                except Exception as e:
                    print(f"[CFG] Errore salvataggio config: {e}")
                    return False

            # Crea finestra
            win = tk.Toplevel(self.root)
            win.title('Impostazioni')
            # Full-screen touch modal per tablet
            try:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
            except Exception:
                sw, sh = 1280, 800
            try:
                win.attributes('-fullscreen', True)
            except Exception:
                win.geometry(f"{sw}x{sh}+0+0")
            win.configure(bg='#FFFFFF')
            # Allinea al wizard: tieni topmost per affidabilità focus/tastiera
            try:
                win.attributes('-topmost', True)
            except Exception:
                pass
            win.transient(self.root)
            win.grab_set()

            # Stili (touch-friendly, più grandi per full-screen)
            title_font = ('Segoe UI', max(24, int(self.s(32))), 'bold')
            label_font = ('Segoe UI', max(18, int(self.s(22))))
            entry_font = ('Segoe UI', max(18, int(self.s(22))))
            btn_font = ('Segoe UI', max(18, int(self.s(22))), 'bold')

            container = tk.Frame(win, bg='#FFFFFF')
            container.pack(fill='both', expand=True, padx=self.s(32), pady=self.s(28))

            # Header con titolo centrato e Annulla a destra (grid 3 colonne)
            header = tk.Frame(container, bg='#FFFFFF')
            header.pack(fill='x', pady=(0, self.s(12)))
            header.grid_columnconfigure(0, weight=1)
            header.grid_columnconfigure(1, weight=0)
            header.grid_columnconfigure(2, weight=1)
            # Spaziatore sx
            tk.Label(header, text='', bg='#FFFFFF').grid(row=0, column=0, sticky='ew')
            # Titolo centrato
            tk.Label(header, text='Impostazioni', font=title_font, bg='#FFFFFF', fg='#5FA8AF').grid(row=0, column=1, sticky='n')
            # Pulsante Annulla a destra (configurato dopo per chiudere anche la tastiera)
            btn_cancel = tk.Button(header, text='Annulla', font=btn_font, command=win.destroy)
            btn_cancel.grid(row=0, column=2, sticky='e')

            form = tk.Frame(container, bg='#FFFFFF')
            form.pack(fill='x', expand=False, pady=(self.s(12), 0))

            # Campi
            tk.Label(form, text='Codice Sede', font=label_font, bg='#FFFFFF').grid(row=0, column=0, sticky='w', pady=(0, self.s(8)))
            sede_var = tk.StringVar()
            sede_entry = tk.Entry(form, textvariable=sede_var, font=entry_font)
            sede_entry.grid(row=0, column=1, sticky='ew', padx=(self.s(16), 0), pady=(0, self.s(12)), ipady=self.s(10))

            tk.Label(form, text='Codice Negozio', font=label_font, bg='#FFFFFF').grid(row=1, column=0, sticky='w', pady=(0, self.s(8)))
            negozio_var = tk.StringVar()
            negozio_entry = tk.Entry(form, textvariable=negozio_var, font=entry_font)
            negozio_entry.grid(row=1, column=1, sticky='ew', padx=(self.s(16), 0), pady=(0, self.s(12)), ipady=self.s(10))

            # Ora trasferimento (HH:MM)
            tk.Label(form, text='Ora trasferimento (HH:MM)', font=label_font, bg='#FFFFFF').grid(row=2, column=0, sticky='w', pady=(0, self.s(8)))
            ora_var = tk.StringVar()
            ora_entry = tk.Entry(form, textvariable=ora_var, font=entry_font)
            ora_entry.grid(row=2, column=1, sticky='ew', padx=(self.s(16), 0), pady=(0, self.s(12)), ipady=self.s(10))

            # Cartella trasferimento con Sfoglia
            tk.Label(form, text='Cartella trasferimento', font=label_font, bg='#FFFFFF').grid(row=3, column=0, sticky='w', pady=(0, self.s(8)))
            dir_var = tk.StringVar()
            dir_entry = tk.Entry(form, textvariable=dir_var, font=entry_font)
            dir_entry.grid(row=3, column=1, sticky='ew', padx=(self.s(16), 0), pady=(0, self.s(12)), ipady=self.s(10))
            def on_browse():
                initial = dir_var.get().strip() or os.path.dirname(os.path.abspath(__file__))
                chosen = filedialog.askdirectory(mustexist=False, initialdir=initial)
                if chosen:
                    dir_var.set(chosen)
            browse_btn = tk.Button(form, text='Sfoglia...', font=btn_font, command=on_browse)
            browse_btn.grid(row=3, column=2, sticky='w', padx=(self.s(12), 0), pady=(0, self.s(12)))

            form.grid_columnconfigure(1, weight=1)
            form.grid_columnconfigure(2, weight=0)

            # Carica valori correnti
            cur_sede, cur_negozio = _load_codes()
            cur_ora, cur_dir = _load_transfer()
            sede_var.set(cur_sede)
            negozio_var.set(cur_negozio)
            ora_var.set(cur_ora)
            dir_var.set(cur_dir)

            # Note
            note = tk.Label(container, text='I campi sono obbligatori. Usare solo cifre/lettere senza spazi.', font=('Segoe UI', max(14, int(self.s(18)))), bg='#FFFFFF', fg='#6B7280')
            note.pack(anchor='w', pady=(self.s(10), self.s(16)))

            # Pulsanti
            btns = tk.Frame(container, bg='#FFFFFF')
            btns.pack(fill='x', pady=(self.s(16), 0))

            # --- Gestione messaggi modali/topmost e chiusura tastiera/finestra ---
            def _show_message(kind: str, title: str, text: str):
                # Dialog modale touch-friendly in stile TIGOTÀ
                try:
                    win.update_idletasks()
                except Exception:
                    pass
                try:
                    dlg = tk.Toplevel(win)
                    try:
                        dlg.transient(win)
                        dlg.attributes('-topmost', True)
                        dlg.resizable(False, False)
                    except Exception:
                        pass
                    dlg.configure(bg='#FFFFFF')

                    # Tema TIGOTÀ
                    brand = '#5FA8AF'
                    ok_bg = '#20B2AA'
                    warn = '#F59E0B'
                    err = '#EF4444'
                    header_bg = brand if kind == 'info' else (warn if kind == 'warning' else err)
                    btn_bg = ok_bg if kind == 'info' else header_bg

                    # Dimensioni touch
                    try:
                        s = self.s
                    except Exception:
                        s = lambda v: v
                    width = max(360, min(640, int((getattr(self, 'vw', 800) or 800) * 0.48)))

                    # Header brand
                    header = tk.Frame(dlg, bg=header_bg)
                    header.pack(fill='x')
                    tk.Label(header, text=title, font=('Segoe UI', s(22)), fg='#FFFFFF', bg=header_bg, padx=s(16), pady=s(10)).pack(anchor='w')

                    # Corpo
                    body = tk.Frame(dlg, bg='#FFFFFF')
                    body.pack(fill='both', expand=True, padx=s(18), pady=s(16))
                    tk.Label(body, text=text, font=('Segoe UI', s(16)), fg='#374151', bg='#FFFFFF', justify='left', wraplength=width - s(36)).pack(anchor='w')

                    # Pulsante OK grande
                    btn = tk.Button(
                        body,
                        text='OK',
                        font=('Segoe UI', s(18), 'bold'),
                        bg=btn_bg,
                        fg='#FFFFFF',
                        activebackground=btn_bg,
                        activeforeground='#FFFFFF',
                        relief='raised',
                        bd=2,
                        command=dlg.destroy
                    )
                    btn.pack(fill='x', pady=(s(16), 0), ipadx=s(12), ipady=s(10))

                    # Posizionamento centrato
                    try:
                        dlg.update_idletasks()
                        dw = max(width, dlg.winfo_width())
                        dh = dlg.winfo_height()
                        pw = max(800, win.winfo_width())
                        ph = max(600, win.winfo_height())
                        px = win.winfo_rootx(); py = win.winfo_rooty()
                        x = px + (pw - dw) // 2
                        y = py + (ph - dh) // 2
                        dlg.geometry(f"{dw}x{dh}+{max(0,x)}+{max(0,y)}")
                    except Exception:
                        pass

                    # Modalità
                    try:
                        dlg.grab_set()
                        dlg.lift()
                        dlg.focus_force()
                        btn.focus_set()
                        dlg.bind('<Escape>', lambda e: dlg.destroy())
                        dlg.bind('<Return>', lambda e: dlg.destroy())
                    except Exception:
                        pass
                    dlg.wait_window()
                except Exception:
                    # Fallback
                    try:
                        messagebox.showinfo(title, text, parent=win)
                    except Exception:
                        pass

            def _close_touch_keyboard():
                # Chiusura/Hide robusta (come nel wizard): SC_CLOSE, WM_CLOSE e ShowWindow(SW_HIDE)
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    WM_SYSCOMMAND = 0x0112
                    SC_CLOSE = 0xF060
                    WM_CLOSE = 0x0010
                    SW_HIDE = 0
                    for cls in ('IPTip_Main_Window', 'OSKMainClass'):
                        try:
                            hwnd = user32.FindWindowW(cls, None)
                        except Exception:
                            hwnd = 0
                        if hwnd:
                            try:
                                user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_CLOSE, 0)
                            except Exception:
                                pass
                            try:
                                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                            except Exception:
                                pass
                            try:
                                user32.ShowWindow(hwnd, SW_HIDE)
                            except Exception:
                                pass
                except Exception:
                    pass
                # Best-effort: chiudi solo OSK se attivo (evitiamo kill di TabTip)
                try:
                    import subprocess
                    subprocess.Popen(['taskkill', '/IM', 'osk.exe', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                except Exception:
                    pass

            def _on_close_settings():
                try:
                    _close_touch_keyboard()
                except Exception:
                    pass
                try:
                    win.destroy()
                except Exception:
                    pass

            try:
                win.protocol('WM_DELETE_WINDOW', _on_close_settings)
            except Exception:
                pass

            # Configura il pulsante Annulla per usare la chiusura personalizzata
            try:
                btn_cancel.configure(command=_on_close_settings)
            except Exception:
                pass

            def on_save():
                cod_sede = (sede_var.get() or '').strip()
                cod_negozio = (negozio_var.get() or '').strip()
                ora_tx = (ora_var.get() or '').strip()
                dir_tx = (dir_var.get() or '').strip()
                # Validazione semplice
                if not cod_sede or not cod_negozio:
                    _show_message('warning', 'Campi obbligatori', 'Inserisci sia Codice Sede che Codice Negozio.')
                    return
                # Evita caratteri non alfanumerici (consentiamo /-?_ al bisogno, ma manteniamo semplice)
                def _valid(s):
                    return all(c.isalnum() for c in s)
                if not _valid(cod_sede) or not _valid(cod_negozio):
                    _show_message('warning', 'Formato non valido', 'Usa solo lettere e numeri, senza spazi.')
                    return
                # Validazione ora HH:MM 24h
                import re
                if not re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", ora_tx):
                    _show_message('warning', 'Ora non valida', 'Inserisci l\'ora nel formato HH:MM (24h).')
                    return
                # Validazione directory
                if not dir_tx:
                    _show_message('warning', 'Cartella mancante', 'Seleziona la cartella di trasferimento.')
                    return
                # Crea la cartella se non esiste
                try:
                    os.makedirs(dir_tx, exist_ok=True)
                except Exception as e:
                    _show_message('error', 'Errore cartella', f'Impossibile creare/accedere alla cartella:\n{dir_tx}\n{e}')
                    return

                if _save_codes(cod_sede, cod_negozio, ora_tx, dir_tx):
                    # Mostra conferma sopra alla finestra Impostazioni
                    try:
                        win.lift(); win.focus_force()
                    except Exception:
                        pass
                    _show_message('info', 'Salvato', 'Impostazioni salvate correttamente.')
                    try:
                        _close_touch_keyboard()
                    except Exception:
                        pass
                    win.destroy()
                    # Riavvia scheduler trasferimento per applicare la nuova ora
                    try:
                        self._restart_transfer_scheduler()
                    except Exception as e:
                        print(f"[TRANSFER] Riavvio scheduler fallito: {e}")
                else:
                    _show_message('error', 'Errore', 'Impossibile salvare le impostazioni.')

            # Pulsante Salva
            save_btn = tk.Button(btns, text='Salva', font=btn_font, command=on_save)
            save_btn.pack(side='left', ipadx=self.s(24), ipady=self.s(12))

            # Pulsante Esporta ora (esegue export immediato delle timbrature pending)
            def on_export_now():
                try:
                    _close_touch_keyboard()
                except Exception:
                    pass
                # Conta pending prima di esportare per feedback
                try:
                    from database_sqlite import get_database_manager
                    db = get_database_manager()
                    pending = db.get_timbrature_pending()
                    count = len(pending)
                except Exception:
                    count = None
                ok = False
                try:
                    ok = self.export_pending_timbrature_to_txt()
                except Exception:
                    ok = False
                if ok:
                    if count is not None:
                        _show_message('info', 'Export completato', f'Esportate {count} timbrature pending in TXT.')
                    else:
                        _show_message('info', 'Export completato', 'File TXT generato nella cartella di trasferimento.')
                else:
                    _show_message('error', 'Errore export', 'Impossibile generare il file TXT. Verifica impostazioni e riprova.')

            export_btn = tk.Button(btns, text='Esporta ora', font=btn_font, command=on_export_now)
            export_btn.pack(side='left', padx=(self.s(12), 0), ipadx=self.s(18), ipady=self.s(12))


            # Tastiera touch: usa logica del wizard + verifica visibilità con fallback snello
            def _is_keyboard_visible():
                try:
                    import ctypes
                    from ctypes import wintypes
                    classes = ['IPTip_Main_Window', 'OSKMainClass']
                    user32 = ctypes.windll.user32
                    rect = wintypes.RECT()
                    for cls in classes:
                        hwnd = user32.FindWindowW(cls, None)
                        if hwnd and user32.IsWindowVisible(hwnd):
                            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                                # visibile solo se occupa parte bassa schermo
                                h = win.winfo_screenheight() if hasattr(win, 'winfo_screenheight') else 800
                                return rect.top > int(h * 0.45)
                    return False
                except Exception:
                    return False

            _kb_sequence_running = False

            def _ensure_touch_keyboard(initial=False):
                try:
                    import subprocess, os
                    nonlocal _kb_sequence_running
                    if _kb_sequence_running:
                        return True
                    _kb_sequence_running = True
                    # 1) Registro (come wizard)
                    try:
                        import winreg
                        if winreg is not None:
                            key_path = r"Software\\Microsoft\\TabletTip\\1.7"
                            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
                                for name, val in (
                                    ("EnableTouchKeyboardAutoInvoke", 1),
                                    ("EnableDesktopModeAutoInvoke", 1),
                                    ("EnableHardwareKeyboard", 1),
                                ):
                                    try:
                                        winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, int(val))
                                    except Exception:
                                        pass
                    except Exception:
                        pass
                    # 2) ctfmon (come wizard)
                    try:
                        ctf_paths = [
                            os.path.join(os.environ.get('SystemRoot', r'C:\\Windows'), 'System32', 'ctfmon.exe'),
                            os.path.join(os.environ.get('SystemRoot', r'C:\\Windows'), 'SysWOW64', 'ctfmon.exe'),
                        ]
                        for cp in ctf_paths:
                            if os.path.exists(cp):
                                try:
                                    subprocess.Popen([cp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x00000008)
                                    break
                                except Exception:
                                    continue
                    except Exception:
                        pass
                    # Helpers per stadi
                    def _stage_ms_inputapp():
                        try:
                            subprocess.Popen(['cmd', '/c', 'start', '', 'ms-inputapp:'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                            return True
                        except Exception:
                            try:
                                subprocess.Popen(['explorer.exe', 'ms-inputapp:'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                return True
                            except Exception:
                                return False
                    def _stage_tabtip():
                        try:
                            paths = [
                                os.path.join(os.environ.get('ProgramFiles', r'C:\\Program Files'), 'Common Files', 'microsoft shared', 'ink', 'TabTip.exe'),
                                os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\\Program Files (x86)'), 'Common Files', 'microsoft shared', 'ink', 'TabTip.exe'),
                            ]
                            for p in paths:
                                if os.path.exists(p):
                                    try:
                                        os.startfile(p)
                                        return True
                                    except Exception:
                                        try:
                                            subprocess.Popen([p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x00000008)
                                            return True
                                        except Exception:
                                            continue
                            return False
                        except Exception:
                            return False
                    def _stage_osk():
                        try:
                            subprocess.Popen(['osk.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x00000008)
                            return True
                        except Exception:
                            return False
                    def _finish_sequence():
                        nonlocal _kb_sequence_running
                        _kb_sequence_running = False

                    # Avvia ms-inputapp subito
                    _stage_ms_inputapp()
                    # Dopo 150ms se non visibile, prova TabTip
                    try:
                        win.after(150, lambda: (not _is_keyboard_visible()) and _stage_tabtip())
                    except Exception:
                        pass
                    # Dopo 800ms se non visibile, prova OSK
                    try:
                        win.after(800, lambda: (not _is_keyboard_visible()) and _stage_osk())
                    except Exception:
                        pass
                    # Sblocca la sequenza dopo 1200ms
                    try:
                        win.after(1200, _finish_sequence)
                    except Exception:
                        _finish_sequence()
                    return True
                except Exception:
                    _kb_sequence_running = False
                    return False

            def _show_touch_keyboard(event=None):
                try:
                    if event is not None and getattr(event, 'widget', None) is not None:
                        try:
                            event.widget.focus_set()
                        except Exception:
                            pass
                    # Piccolo delay per lasciare stabilizzare il focus
                    win.after(30, _ensure_touch_keyboard)
                except Exception:
                    _ensure_touch_keyboard()

            # Binding: solo click e rilascio click per evitare apertura automatica
            for entry in (sede_entry, negozio_entry, ora_entry, dir_entry):
                try:
                    entry.bind('<Button-1>', _show_touch_keyboard)
                    entry.bind('<ButtonRelease-1>', _show_touch_keyboard)
                except Exception:
                    pass

            # Esc per chiudere
            try:
                win.bind('<Escape>', lambda e: _on_close_settings())
            except Exception:
                pass

            # Focus iniziale
            try:
                if not cur_sede:
                    sede_entry.focus_set()
                else:
                    negozio_entry.focus_set()
            except Exception:
                pass

            win.focus_force()
        except Exception as e:
            print(f"[UI] Errore apertura impostazioni: {e}")

    # --- Trasferimento TXT giornaliero ---
    def _read_transfer_settings(self):
        """Legge ora e cartella di trasferimento + codici sede/negozio da config_negozio.ini."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = '.'
        cfg_path = os.path.join(base_dir, 'config_negozio.ini')
        cfg = configparser.ConfigParser()
        try:
            cfg.read(cfg_path, encoding='utf-8')
        except Exception:
            cfg.read(cfg_path)
        # Default
        ora = '02:00'
        export_dir = os.path.join(base_dir, 'export')
        sede = ''
        negozio = ''
        if cfg.has_section('TRASFERIMENTO'):
            try:
                ora = (cfg.get('TRASFERIMENTO', 'ora', fallback=ora) or ora).strip()
            except Exception:
                pass
            try:
                export_dir = (cfg.get('TRASFERIMENTO', 'cartella', fallback=export_dir) or export_dir).strip()
            except Exception:
                pass
        if cfg.has_section('AZIENDA'):
            try:
                sede = (cfg.get('AZIENDA', 'codice_sede', fallback='') or '').strip()
            except Exception:
                pass
            try:
                negozio = (cfg.get('AZIENDA', 'codice_negozio', fallback='') or '').strip()
            except Exception:
                pass
        return ora, export_dir, sede, negozio

    def export_pending_timbrature_to_txt(self) -> bool:
        """Esporta timbrature con sync_status='pending' in un TXT e le marca come sincronizzate.
        Formato righe (senza header): CODSEDE;CODNEGOZIO;BADGE;TIPO;YYYYMMDD;HHMMSS
        """
        path_tmp = None
        try:
            from database_sqlite import get_database_manager
        except Exception as e:
            print(f"[TRANSFER] DB non disponibile: {e}")
            return False
        try:
            ora_str, out_dir, cod_sede, cod_negozio = self._read_transfer_settings()
            # Crea cartella se manca
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            print(f"[TRANSFER] Config/cartella trasferimento non valida: {e}")
            return False

        try:
            db = get_database_manager()
            rows = db.get_timbrature_pending()
            if not rows:
                print("[TRANSFER] Nessuna timbratura pending da esportare")
                return True  # Non è errore

            # Prepara nome file: ORE{CODICE_NEGOZIO}{YYYYMMDDHHMMSS}.TXT
            now = datetime.now()
            ts = now.strftime('%Y%m%d%H%M%S')
            codice_negozio = (cod_negozio or '').strip()
            filename = f"ORE{codice_negozio}{ts}.TXT"
            path_tmp = os.path.join(out_dir, filename + ".part")
            path_final = os.path.join(out_dir, filename)

            def _fmt_dt(ts_val):
                s = str(ts_val)
                # atteso 'YYYY-MM-DD HH:MM:SS[.fff]' -> split
                try:
                    date_part, time_part = s.split(' ')
                except ValueError:
                    # fallback: tutto in data
                    date_part = s[:10]
                    time_part = s[11:19]
                ymd = date_part.replace('-', '')
                hms = time_part.split('.')[0].replace(':', '')
                return ymd, hms

            # Scrivi file atomico
            with open(path_tmp, 'w', encoding='utf-8', newline='') as f:
                for r in rows:
                    # Codice da esportare: codice dipendente associato al badge (wizard), numerico a 10 cifre (pad con zeri)
                    raw_badge = (r.get('badge_id') or '').strip()
                    emp_code_digits = ''
                    try:
                        dip = db.get_dipendente_by_badge(raw_badge)
                        if dip and 'codice' in dip and dip['codice'] is not None:
                            emp_code_digits = ''.join(ch for ch in str(dip['codice']) if ch.isdigit())
                    except Exception:
                        emp_code_digits = ''
                    if not emp_code_digits:
                        # Fallback: usa solo le cifre del badge_id
                        emp_code_digits = ''.join(ch for ch in raw_badge if ch.isdigit()) or '0'
                    badge10 = emp_code_digits[-10:].rjust(10, '0')
                    # Tipo: 1=entrata, 0=uscita
                    tipo_txt = (r.get('tipo') or '').strip().lower()
                    tipo_flag = '1' if tipo_txt == 'entrata' else '0'
                    # Data/ora: GGMMAA e HHMM
                    ymd, hms = _fmt_dt(r.get('timestamp'))  # ymd=YYYYMMDD, hms=HHMMSS
                    ddmmyy = ymd[6:8] + ymd[4:6] + ymd[2:4]
                    hhmm = hms[0:2] + hms[2:4]
                    # SEDE + BADGE(10) + TIPO + 0000 + GGMMAA + HHMM (senza separatori)
                    sede_code = (cod_sede or '').strip()
                    record = f"{sede_code}{badge10}{tipo_flag}0000{ddmmyy}{hhmm}\r\n"
                    f.write(record)
            os.replace(path_tmp, path_final)

            # Marca come sincronizzate
            ids = [r.get('id') for r in rows if r.get('id') is not None]
            if ids:
                db.mark_timbrature_synced(ids)
            print(f"[TRANSFER] Esportate {len(rows)} timbrature in {path_final}")
            return True
        except Exception as e:
            try:
                if path_tmp and os.path.exists(path_tmp):
                    os.remove(path_tmp)
            except Exception:
                pass
            print(f"[TRANSFER] Errore export TXT: {e}")
            return False

    def _start_transfer_scheduler(self):
        """Avvia un thread daemon che esegue l'export TXT ogni giorno all'ora configurata."""
        if self._transfer_thread and self._transfer_thread.is_alive():
            return

        def _loop():
            while not self._transfer_stop.is_set():
                try:
                    ora_str, _, _, _ = self._read_transfer_settings()
                    # Parse orario con tolleranza: accetta "HH:MM", "HH.MM", "HHMM" o solo "H/H H"
                    hh, mm = 2, 0  # default 02:00
                    try:
                        s = (ora_str or '').strip()
                        s = s.replace('.', ':')
                        s = s.replace(' ', '')
                        if ':' in s:
                            parts = s.split(':')
                            if len(parts) >= 2:
                                hh = int(parts[0])
                                mm = int(parts[1][:2])
                        elif len(s) in (3, 4) and s.isdigit():
                            # Es. 930 -> 09:30, 1430 -> 14:30
                            hh = int(s[:-2])
                            mm = int(s[-2:])
                        elif len(s) in (1, 2) and s.isdigit():
                            # Solo ora
                            hh = int(s)
                            mm = 0
                        # Normalizza range
                        hh = max(0, min(23, hh))
                        mm = max(0, min(59, mm))
                    except Exception:
                        pass
                    now = datetime.now()
                    run_at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
                    if run_at <= now:
                        # Se l'orario odierno è appena passato (entro 60s), esegui tra 5s; altrimenti programma domani
                        from datetime import timedelta
                        if (now - run_at).total_seconds() <= 60:
                            run_at = now + timedelta(seconds=5)
                        else:
                            run_at = run_at + timedelta(days=1)
                    wait_s = max(1, int((run_at - now).total_seconds()))
                    print(f"[TRANSFER] Scheduler prossimo run alle {run_at.strftime('%Y-%m-%d %H:%M:%S')} (tra {wait_s}s)")
                    # Attendi in porzioni per permettere stop rapido
                    step = 5
                    waited = 0
                    while waited < wait_s and not self._transfer_stop.is_set():
                        chunk = min(step, wait_s - waited)
                        time.sleep(chunk)
                        waited += chunk
                    if self._transfer_stop.is_set():
                        break
                    # Esegui export
                    print(f"[TRANSFER] Scheduler avvio export alle {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    self.export_pending_timbrature_to_txt()
                    # poi loop per il prossimo giorno
                except Exception as e:
                    print(f"[TRANSFER] Scheduler errore: {e}")
                    time.sleep(30)

        self._transfer_stop.clear()
        t = threading.Thread(target=_loop, name='TransferScheduler', daemon=True)
        t.start()
        self._transfer_thread = t

    def _stop_transfer_scheduler(self):
        try:
            self._transfer_stop.set()
            t = self._transfer_thread
            if t and t.is_alive():
                t.join(timeout=1.5)
        except Exception:
            pass

    def _restart_transfer_scheduler(self):
        self._stop_transfer_scheduler()
        self._start_transfer_scheduler()
    

    def create_large_clock(self, parent):
        """Crea orologio e data centralizzati con padding ottimizzato (meno bianco sotto)."""
        # Costanti per il clock (adattate)
        CLOCK_TOP_PADDING_RATIO = 0.008
        CLOCK_BOTTOM_PADDING_RATIO = 0.002  # ridotto per meno bianco sotto
        TIME_FONT_SIZE_RATIO = 0.20
        DATE_FONT_SIZE_RATIO = 0.032
        DATE_TOP_PADDING_RATIO = 0.004  # ridotto
        
        BRAND_TEXT_COLOR = '#5FA8AF'
        
        clock_wrapper = tk.Frame(parent, bg='#FFFFFF')
        clock_wrapper.pack(pady=(
            int(self.vh * CLOCK_TOP_PADDING_RATIO), 
            int(self.vh * CLOCK_BOTTOM_PADDING_RATIO)
        ))
        
        self.time_var = tk.StringVar()
        self.date_var = tk.StringVar()
        
        time_font_size = max(self.s(112), int(self.vh * TIME_FONT_SIZE_RATIO))
        date_font_size = max(self.s(20), int(self.vh * DATE_FONT_SIZE_RATIO))
        
        self.time_label = tk.Label(
            clock_wrapper, 
            textvariable=self.time_var,
            font=('Segoe UI', time_font_size, 'bold'),
            bg='#FFFFFF', 
            fg=BRAND_TEXT_COLOR,
            anchor='center'
        )
        self.time_label.pack()
        
        self.date_label = tk.Label(
            clock_wrapper, 
            textvariable=self.date_var,
            font=('Segoe UI', date_font_size, 'bold'),
            bg='#FFFFFF', 
            fg=BRAND_TEXT_COLOR,
            anchor='center'
        )
        self.date_label.pack(pady=(int(self.vh * DATE_TOP_PADDING_RATIO), 0))
        
        self.update_tigota_clock()

    def create_action_buttons(self, parent):
        """Crea i selettori Ingresso/Uscita con istruzioni sotto (mutualmente esclusivi), più centrati e con meno spazio sotto."""
        BUTTONS_TOP_PADDING_RATIO = 0.006
        BUTTONS_BOTTOM_PADDING_RATIO = 0.005  # ridotto
        BUTTON_SPACING_RATIO = 0.04
        INSTRUCTIONS_TOP_PADDING_RATIO = 0.006  # ridotto
        INSTRUCTIONS_COLOR = '#5FA8AF'
        
        buttons_wrapper = tk.Frame(parent, bg='#FFFFFF')
        buttons_wrapper.pack(pady=(
            int(self.vh * BUTTONS_TOP_PADDING_RATIO), 
            int(self.vh * BUTTONS_BOTTOM_PADDING_RATIO)
        ))
        
        buttons_row = tk.Frame(buttons_wrapper, bg='#FFFFFF')
        buttons_row.pack()
        
        def select_ingresso():
            self.selected_action = 'in'
            if hasattr(self, 'btn_ingresso') and self.btn_ingresso:
                self.btn_ingresso['set_selected'](True)
            if hasattr(self, 'btn_uscita') and self.btn_uscita:
                self.btn_uscita['set_selected'](False)
            print('[UI] Selezionato: Ingresso')
            # Aggiorna messaggio sotto le istruzioni
            if hasattr(self, 'selection_hint_var'):
                self.selection_hint_var.set('Selezionato: Ingresso — avvicina il badge al lettore')
            if hasattr(self, 'selection_hint_label'):
                self.selection_hint_label.config(fg='#20B2AA')
            # Abilita lettura NFC
            try:
                self.enable_nfc_reading()
            except Exception as e:
                print(f"[NFC] Errore attivazione lettura: {e}")
        
        def select_uscita():
            self.selected_action = 'out'
            if hasattr(self, 'btn_ingresso') and self.btn_ingresso:
                self.btn_ingresso['set_selected'](False)
            if hasattr(self, 'btn_uscita') and self.btn_uscita:
                self.btn_uscita['set_selected'](True)
            print('[UI] Selezionato: Uscita')
            # Aggiorna messaggio sotto le istruzioni
            if hasattr(self, 'selection_hint_var'):
                self.selection_hint_var.set('Selezionato: Uscita — avvicina il badge al lettore')
            if hasattr(self, 'selection_hint_label'):
                self.selection_hint_label.config(fg='#E91E63')
            # Abilita lettura NFC
            try:
                self.enable_nfc_reading()
            except Exception as e:
                print(f"[NFC] Errore attivazione lettura: {e}")
        
        self.btn_ingresso = self.create_pill_button(
            buttons_row, 
            'Ingresso', 
            '#20B2AA', 
            '#FFFFFF', 
            select_ingresso
        )
        self.btn_ingresso['canvas'].pack(side='left')
        
        spacer = tk.Frame(
            buttons_row, 
            width=int(self.vw * BUTTON_SPACING_RATIO), 
            bg='#FFFFFF'
        )
        spacer.pack(side='left')
        
        self.btn_uscita = self.create_pill_button(
            buttons_row, 
            'Uscita', 
            '#E91E63', 
            '#FFFFFF', 
            select_uscita
        )
        self.btn_uscita['canvas'].pack(side='left')
        
        self.btn_ingresso['set_selected'](False)
        self.btn_uscita['set_selected'](False)
        self.selected_action = None
        
        instructions_wrapper = tk.Frame(buttons_wrapper, bg='#FFFFFF')
        instructions_wrapper.pack(pady=(int(self.vh * INSTRUCTIONS_TOP_PADDING_RATIO), 0))
        
        instr_font = max(self.s(12), int(self.vh * 0.020))
        tk.Label(
            instructions_wrapper,
            text="1. Seleziona Ingresso/Uscita",
            font=('Segoe UI', instr_font, 'normal'),
            bg='#FFFFFF',
            fg=INSTRUCTIONS_COLOR
        ).pack()
        tk.Label(
            instructions_wrapper,
            text="2. Avvicina il badge al lettore",
            font=('Segoe UI', instr_font, 'normal'),
            bg='#FFFFFF',
            fg=INSTRUCTIONS_COLOR
        ).pack()

        # Messaggio dinamico con selezione e invito ad avvicinare il badge
        self.selection_hint_var = tk.StringVar(value='')
        self.selection_hint_label = tk.Label(
            instructions_wrapper,
            textvariable=self.selection_hint_var,
            font=('Segoe UI', instr_font, 'bold'),
            bg='#FFFFFF',
            fg=INSTRUCTIONS_COLOR
        )
        self.selection_hint_label.pack(pady=(int(self.vh * 0.004), 0))

    def create_nfc_indicator(self, parent):
        """Crea indicatore NFC in basso a destra; solo logo (senza testo), più grande."""
        # Container per la barra inferiore (nuova row 4)
        nfc_bar = tk.Frame(parent, bg='#FFFFFF')
        nfc_bar.grid(row=4, column=0, sticky='sew')

        nfc_container = tk.Frame(nfc_bar, bg='#FFFFFF')
        nfc_container.pack(side='right', padx=self.s(16), pady=(self.s(8), self.s(96)))

        # Logo massimo (≈25% dell'altezza viewport, minimo 200px)
        icon_size = max(self.s(200), int(self.vh * 0.25))

        # Prova a caricare un logo NFC dalla cartella immagini; se non trovato, fallback all'icona disegnata
        self.nfc_photo = None
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 1) Priorità: percorso specificato dall'utente
            preferred_paths = [
                os.path.join(base_dir, 'Immagini', 'logo_nfc.png'),
                os.path.join(base_dir, 'Immagini', 'logo_nfc.gif'),
                os.path.join(base_dir, 'Immagini', 'logo_nfc.jpg'),
                os.path.join(base_dir, 'Immagini', 'logo_nfc.jpeg'),
                os.path.join(base_dir, 'Immagini', 'logo_nfc.PNG'),
                os.path.join(base_dir, 'Immagini', 'logo_nfc.GIF'),
                os.path.join(base_dir, 'Immagini', 'logo_nfc.JPG'),
                os.path.join(base_dir, 'Immagini', 'logo_nfc.JPEG'),
            ]
            logo_path = next((p for p in preferred_paths if os.path.exists(p)), None)

            # 2) Fallback: ricerca generica in cartelle comuni
            if not logo_path:
                candidate_dirs = ['', 'immagini', 'Immagini', 'images', 'Images', 'assets', 'static', 'resources', 'res']
                candidate_names = [
                    'nfc.png', 'nfc_logo.png', 'logo_nfc.png', 'nfc-icon.png', 'nfc_icon.png', 'nfc.gif',
                    'logo_nfc.jpg', 'logo_nfc.jpeg', 'nfc.jpg', 'nfc.jpeg', 'nfc_logo.jpg'
                ]
                for d in candidate_dirs:
                    for name in candidate_names:
                        p = os.path.join(base_dir, d, name) if d else os.path.join(base_dir, name)
                        if os.path.exists(p):
                            logo_path = p
                            break
                    if logo_path:
                        break

            if logo_path:
                ext = os.path.splitext(logo_path)[1].lower()
                # Preferisci Pillow per qualità e per supporto JPEG
                if PIL_AVAILABLE:
                    try:
                        pil_img = Image.open(logo_path)
                        w, h = pil_img.size
                        if w > 0 and h > 0:
                            scale = icon_size / max(w, h)
                            new_w = max(1, int(round(w * scale)))
                            new_h = max(1, int(round(h * scale)))
                            resample = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
                            pil_img = pil_img.resize((new_w, new_h), resample)
                        self.nfc_photo = ImageTk.PhotoImage(pil_img)
                    except Exception:
                        self.nfc_photo = None
                else:
                    # Fallback: usa PhotoImage solo per PNG/GIF
                    if ext in ('.png', '.gif'):
                        img = tk.PhotoImage(file=logo_path)
                        # Downscale se troppo grande; upscaling non gestito senza Pillow
                        if img.width() > icon_size:
                            factor = max(1, img.width() // icon_size)
                            img = img.subsample(factor, factor)
                        self.nfc_photo = img
                    else:
                        self.nfc_photo = None
        except Exception:
            self.nfc_photo = None

        if self.nfc_photo is not None:
            img_label = tk.Label(nfc_container, image=self.nfc_photo, bg='#FFFFFF')
            img_label.pack(side='left', padx=(0, self.s(6)))
        else:
            # Fallback: icona disegnata come prima
            nfc_canvas = tk.Canvas(
                nfc_container,
                width=icon_size,
                height=icon_size,
                bg='#FFFFFF',
                highlightthickness=0,
                bd=0
            )
            nfc_canvas.pack(side='left', padx=(0, self.s(6)))

            card_size = int(icon_size * 0.4)
            card_x = (icon_size - card_size) // 2
            card_y = int(icon_size * 0.3)

            nfc_canvas.create_rectangle(
                card_x, card_y,
                card_x + card_size, card_y + int(card_size * 0.6),
                outline='#777777',
                width=2
            )

            wave_center_x = card_x - int(card_size * 0.3)
            wave_center_y = card_y + int(card_size * 0.3)

            for radius in [8, 12, 16]:
                scaled_radius = self.s(radius)
                nfc_canvas.create_arc(
                    wave_center_x - scaled_radius,
                    wave_center_y - scaled_radius,
                    wave_center_x + scaled_radius,
                    wave_center_y + scaled_radius,
                    start=-30,
                    extent=60,
                    style='arc',
                    outline='#777777',
                    width=2
                )

        # Nota: rimosso testo "NFC" su richiesta, resta solo il logo

    def update_tigota_clock(self):
        """Aggiorna orologio e data con gestione errori migliorata."""
        try:
            now = datetime.now()
            
            # Formato tempo HH:MM
            time_str = now.strftime('%H:%M')
            self.time_var.set(time_str)
            
            # Formato data italiana completa
            giorni_settimana = [
                'Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 
                'Venerdì', 'Sabato', 'Domenica'
            ]
            mesi_anno = [
                'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
                'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
            ]
            
            giorno_settimana = giorni_settimana[now.weekday()]
            mese = mesi_anno[now.month - 1]
            
            date_str = f"{giorno_settimana} {now.day} {mese} {now.year}"
            self.date_var.set(date_str)
            
        except Exception as e:
            print(f"Errore aggiornamento clock: {e}")
            # Fallback con valori safe
            self.time_var.set("--:--")
            self.date_var.set("-- -- ---- ----")
        
        finally:
            # Schedula prossimo aggiornamento
            if hasattr(self, 'root') and self.root:
                self.root.after(1000, self.update_tigota_clock)

    # --- NFC integration ---
    def enable_nfc_reading(self):
        """Avvia la lettura del badge NFC dopo la selezione dell'evento."""
        try:
            print("[NFC] enable_nfc_reading: richiesta avvio")
            # Ferma un'eventuale lettura precedente
            if getattr(self, 'nfc_reader', None):
                try:
                    self.nfc_reader.stop_reading()
                except Exception:
                    pass
            # Crea nuovo lettore con callback
            self.nfc_reader = NFCReader(callback=self.on_badge_read)
            self.nfc_reader.start_reading()
            print("[NFC] Lettura abilitata: avvicina il badge")

            # Attiva anche la cattura tastiera (ID Card Reader)
            self._start_keyboard_capture()
        except Exception as e:
            print(f"[NFC] Impossibile avviare lettura: {e}")

    def on_badge_read(self, badge_id: str):
        """Callback eseguito al rilevamento del badge; aggiorna l'UI in main thread e ferma la lettura."""
        try:
            # Verifica se il badge è abbinato ad un dipendente
            is_known = False
            dip_nome = None
            dip_cognome = None
            try:
                from database_sqlite import get_database_manager
                db = get_database_manager()
                dip = db.get_dipendente_by_badge(badge_id)
                if dip:
                    is_known = True
                    dip_nome = dip.get('nome')
                    dip_cognome = dip.get('cognome')
            except Exception as db_err:
                print(f"[DB] Impossibile verificare badge nel DB: {db_err}")

            # Aggiorna UI in modo thread-safe e salva timbratura
            def _update_ui():
                try:
                    if hasattr(self, 'selection_hint_var') and self.selection_hint_var is not None:
                        # Determina azione selezionata
                        action = getattr(self, 'selected_action', None)
                        tipo_str = 'entrata' if action == 'in' else ('uscita' if action == 'out' else None)
                        if not tipo_str:
                            # Nessuna azione selezionata: notifica e non salvare
                            self.selection_hint_var.set("Seleziona Ingresso o Uscita prima di timbrare")
                            if hasattr(self, 'selection_hint_label') and self.selection_hint_label is not None:
                                self.selection_hint_label.config(fg='#EF4444')
                            self._show_tigota_toast('warning', 'Seleziona Ingresso o Uscita')
                            try:
                                winsound.Beep(440, 220)
                            except Exception:
                                try:
                                    winsound.MessageBeep(winsound.MB_ICONHAND)
                                except Exception:
                                    pass
                            return

                        if is_known:
                            azione = 'Ingresso' if self.selected_action == 'in' else ('Uscita' if self.selected_action == 'out' else '—')
                            nominativo = (dip_nome or '').strip()
                            if dip_cognome:
                                nominativo = f"{nominativo} {dip_cognome.strip()}".strip()
                            msg = f"{('Ciao ' + nominativo + ' — ') if nominativo else ''}Badge: {badge_id} — {azione} registrata"
                            self.selection_hint_var.set(msg)
                            if hasattr(self, 'selection_hint_label') and self.selection_hint_label is not None:
                                self.selection_hint_label.config(fg='#20B2AA' if self.selected_action == 'in' else '#E91E63')
                            # Beep di conferma lettura
                            try:
                                winsound.Beep(1000, 150)
                            except Exception:
                                try:
                                    winsound.MessageBeep()
                                except Exception:
                                    pass
                            # Salva timbratura nel DB (nota: sync_status default = 'pending')
                            try:
                                if 'db' in locals():
                                    db.save_timbratura(badge_id, tipo_str, dip_nome, dip_cognome)
                            except Exception as se:
                                print(f"[DB] Errore salvataggio timbratura: {se}")
                            # Toast stile TIGOTÀ (success)
                            display_name = nominativo if nominativo else None
                            self._show_tigota_toast('success', f"{azione} registrata", name=display_name)
                        else:
                            # Badge non riconosciuto: mostra messaggio di attenzione in rosso
                            self.selection_hint_var.set("Attenzione: badge non riconosciuto")
                            if hasattr(self, 'selection_hint_label') and self.selection_hint_label is not None:
                                self.selection_hint_label.config(fg='#EF4444')  # rosso di avviso
                            # Beep di errore
                            try:
                                winsound.Beep(440, 220)
                            except Exception:
                                try:
                                    winsound.MessageBeep(winsound.MB_ICONHAND)
                                except Exception:
                                    pass
                            # Salva comunque la timbratura (senza nominativo), per tracciamento
                            try:
                                if 'db' in locals() and tipo_str:
                                    db.save_timbratura(badge_id, tipo_str, None, None)
                            except Exception as se:
                                print(f"[DB] Errore salvataggio timbratura (unknown badge): {se}")
                            # Toast stile TIGOTÀ (errore)
                            self._show_tigota_toast('error', "Badge non riconosciuto")
                except Exception:
                    pass
                # Ferma lettore dopo una lettura per evitare duplicati rapidi
                try:
                    if getattr(self, 'nfc_reader', None):
                        self.nfc_reader.stop_reading()
                        print("[NFC] Lettura fermata dopo badge")
                except Exception:
                    pass
                # Disattiva cattura tastiera
                try:
                    self._stop_keyboard_capture()
                except Exception:
                    pass
                # Richiedi nuova selezione (Ingresso/Uscita) per riabilitare la lettura
                try:
                    self._post_timbratura_cleanup()
                except Exception:
                    pass
            if hasattr(self, 'root') and self.root:
                self.root.after(0, _update_ui)
            else:
                _update_ui()
        except Exception as e:
            print(f"[NFC] Errore in callback badge: {e}")

    # --- Keyboard wedge capture (ID Card Reader) ---
    def _setup_keyboard_capture(self):
        """Crea un Entry nascosto per catturare input tastiera dai lettori USB "ID Card Reader"."""
        if not hasattr(self, 'root') or not self.root:
            return
        if self._hid_entry is not None:
            return
        # Entry invisibile e molto piccolo, fuori dallo schermo
        self._hid_entry = tk.Entry(self.root)
        try:
            self._hid_entry.place(x=-1000, y=-1000, width=1, height=1)
        except Exception:
            # Fallback
            self._hid_entry.pack_forget()
        # Bind eventi tasti
        self._hid_entry.bind('<Key>', self._on_hid_key)
        self._hid_entry.bind('<Return>', self._on_hid_return)
        # Mantieni focus se attiva la cattura
        self._hid_entry.bind('<FocusOut>', lambda e: self._refocus_hid() if self._capture_active else None)

    def _start_keyboard_capture(self):
        self._badge_buffer = ''
        self._capture_active = True
        print("[NFC] Keyboard capture: START")
        self._refocus_hid()
        # Ripeti il refocus poco dopo per sicurezza
        try:
            if hasattr(self, 'root') and self.root:
                self.root.after(50, self._refocus_hid)
        except Exception:
            pass

    def _stop_keyboard_capture(self):
        self._capture_active = False
        self._badge_buffer = ''

    def _refocus_hid(self):
        try:
            if self._hid_entry is not None and self._capture_active:
                if hasattr(self, 'root') and self.root:
                    # Esegui il focus in maniera asincrona per evitare blocchi nell'handler di click
                    self.root.after(0, lambda: self._hid_entry.focus_set())
                else:
                    self._hid_entry.focus_set()
        except Exception:
            pass

    def _on_hid_key(self, event):
        if not self._capture_active:
            return
        try:
            if event.keysym == 'Return':
                self._on_hid_return(event)
                return
            ch = event.char
            # Accetta solo stampabili (evita ctrl, shift, ecc.)
            if ch and ch.isprintable():
                self._badge_buffer += ch
        except Exception:
            pass

    def _on_hid_return(self, event):
        if not self._capture_active:
            return
        badge = (self._badge_buffer or '').strip()
        self._badge_buffer = ''
        if badge:
            # Gestisci direttamente come lettura badge
            print(f"[NFC] Badge (ID Card Reader): {badge}")
            try:
                self.on_badge_read(badge)
            except Exception as e:
                print(f"[NFC] Errore gestione badge tastiera: {e}")

    def select_action(self, action_type):
        """Con selettori: aggiorna lo stato selezionato senza popup; logga eventuale mancata selezione."""
        try:
            if action_type == 'in':
                self.selected_action = 'in'
                if hasattr(self, 'btn_ingresso'):
                    self.btn_ingresso['set_selected'](True)
                if hasattr(self, 'btn_uscita'):
                    self.btn_uscita['set_selected'](False)
                print('[UI] Selezionato: Ingresso')
            elif action_type == 'out':
                self.selected_action = 'out'
                if hasattr(self, 'btn_ingresso'):
                    self.btn_ingresso['set_selected'](False)
                if hasattr(self, 'btn_uscita'):
                    self.btn_uscita['set_selected'](True)
                print('[UI] Selezionato: Uscita')
            else:
                print(f"[UI] Azione non riconosciuta: {action_type}")
                return
        except Exception as e:
            print(f"Errore nella gestione selezione {action_type}: {e}")

    def load_kiosk_config(self):
        """Fallback: imposta configurazione kiosk di base se non presente."""
        # In un setup reale potremmo leggere da config.ini; qui impostiamo default sicuri
        self.kiosk_mode_active = True
        self.kiosk_exit_pin = self.kiosk_exit_pin or "2580"
        # Flag tablet per font/padding maggiorati
        self.is_tablet_resolution = True

    # --- UI feedback helpers ---
    def _get_feedback_duration_ms(self) -> int:
        """Legge durata toast da config_negozio.ini [UI] feedback_toast_ms, fallback a self.feedback_toast_ms."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = '.'
        cfg_path = os.path.join(base_dir, 'config_negozio.ini')
        import configparser as _cp
        cfg = _cp.ConfigParser()
        try:
            cfg.read(cfg_path, encoding='utf-8')
        except Exception:
            cfg.read(cfg_path)
        try:
            if cfg.has_section('UI'):
                v = cfg.get('UI', 'feedback_toast_ms', fallback=str(self.feedback_toast_ms)).strip()
                iv = int(v)
                if iv <= 0:
                    return self.feedback_toast_ms
                return min(iv, 10000)
        except Exception:
            pass
        return self.feedback_toast_ms

    def _show_tigota_toast(self, kind, text, duration_ms=None, name=None):
        """Mostra un toast stile TIGOTÀ (borderless, topmost), ancora più grande, con saluto opzionale e bordo Uscita."""
        if not hasattr(self, 'root') or not self.root:
            return
        dur = duration_ms if isinstance(duration_ms, int) and duration_ms > 0 else self._get_feedback_duration_ms()
        # Palette
        ok_bg = '#20B2AA'   # success
        warn = '#F59E0B'
        err = '#E91E63'
        header_bg = ok_bg if kind == 'success' else (warn if kind == 'warning' else err)
        body_bg = '#FFFFFF'
        fg = '#FFFFFF'

        # Finestra
        toast = tk.Toplevel(self.root)
        try:
            toast.overrideredirect(True)
        except Exception:
            pass
        try:
            toast.attributes('-topmost', True)
        except Exception:
            pass

        # Bordi con colore pulsante Uscita
        uscita_border = '#E91E63'
        toast.configure(bg=uscita_border)

        s = self.s
        # Card interna con padding (bordo visibile tutto intorno)
        container = tk.Frame(toast, bg=body_bg, bd=0, highlightthickness=0)
        container.pack(fill='both', expand=True, padx=s(12), pady=s(12))

        header = tk.Frame(container, bg=header_bg, bd=0, highlightthickness=0)
        header.pack(fill='x')
        tk.Label(header, text='TIGOTÀ', font=('Segoe UI', s(34), 'bold'), fg=fg, bg=header_bg, padx=s(28), pady=s(16)).pack(anchor='w')

        body = tk.Frame(container, bg=body_bg)
        body.pack(fill='both', expand=True, padx=s(36), pady=s(26))
        if name:
            tk.Label(body, text=f"Ciao {name}", font=('Segoe UI', s(42), 'bold'), fg='#111827', bg=body_bg).pack(pady=(0, s(8)))
        tk.Label(body, text=text, font=('Segoe UI', s(30), 'bold'), fg='#374151', bg=body_bg).pack()

        # Centro schermo
        try:
            toast.update_idletasks()
            rw = max(800, self.root.winfo_width())
            w = max(int(rw * 0.65), s(800), toast.winfo_width())
            h = toast.winfo_height()
            rx = self.root.winfo_rootx(); ry = self.root.winfo_rooty()
            rh = self.root.winfo_height()
            x = rx + (rw - w)//2
            y = ry + (rh - h)//2
            toast.geometry(f"{w}x{h}+{max(0,x)}+{max(0,y)}")
        except Exception:
            pass
        toast.after(dur, lambda: toast.destroy() if toast.winfo_exists() else None)

    def _post_timbratura_cleanup(self):
        """Dopo una timbratura, richiede una nuova selezione azzerando lo stato e lasciando la lettura NFC disabilitata."""
        # Pulisci selezione
        try:
            self.selected_action = None
            if hasattr(self, 'btn_ingresso') and self.btn_ingresso:
                self.btn_ingresso['set_selected'](False)
            if hasattr(self, 'btn_uscita') and self.btn_uscita:
                self.btn_uscita['set_selected'](False)
        except Exception:
            pass
        # Messaggio istruzioni
        try:
            if hasattr(self, 'selection_hint_var') and self.selection_hint_var is not None:
                self.selection_hint_var.set('Seleziona Ingresso o Uscita per abilitare la lettura')
            if hasattr(self, 'selection_hint_label') and self.selection_hint_label is not None:
                self.selection_hint_label.config(fg='#5FA8AF')
        except Exception:
            pass

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("TIGOTÀ Elite - Sistema Timbratura")
    # Full-screen per tablet 8" (kiosk-like)
    try:
        root.attributes('-fullscreen', True)
    except Exception:
        # Fallback: massimizza
        root.state('zoomed')
    root.configure(bg="#FFFFFF")

    dashboard = TigotaEliteDashboard()
    dashboard.set_root(root)
    dashboard.build_dashboard(root)

    # Garantisce lo stop dello scheduler alla chiusura applicazione
    def _on_close():
        try:
            dashboard._stop_transfer_scheduler()
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass
    try:
        root.protocol('WM_DELETE_WINDOW', _on_close)
    except Exception:
        pass

    print("✅ TIGOTÀ Elite Dashboard full-screen pronto per tablet 8\"")
    root.mainloop()



