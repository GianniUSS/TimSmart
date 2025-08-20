#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOT? Elite Dashboard - Sistema di Timbratura Premium con SQLite
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
import subprocess  # Per attivazione tastiera virtuale
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
        """Inizializza la dashboard TIGOT? Elite"""
        # Configurazione di base
        self.selected_action = None
        self.time_var = None
        self.sec_var = None
        self.is_closing = False
        self.active_timers = []
        self.kiosk_mode_active = False
        self.kiosk_exit_pin = "2580"
        self.badge_learn_mode = False
        self._buttons_disabled = False  # Flag per disabilitare temporaneamente i click sui pulsanti
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

        # Modalità tablet: ottimizzazioni per touchscreen e performance
        self.tablet_mode = True
        self.animations_enabled = True  # Mantieni animazioni ma semplificate per tablet
        self.virtual_keyboard_enabled = True  # Abilita supporto tastiera virtuale

        # LIMITI PERFORMANCE per fluidità garantita
        self.MAX_PARTICLES_TABLET = 6   # Ridotto per fluidità estrema
        self.MAX_PARTICLES_DESKTOP = 12  # Ridotto per performance
        self.particle_cleanup_counter = 0
        # OSK suppression flag
        self._suppress_osk = False
        # OSK availability (per evitare spam errori se mancano privilegi/tabtip)
        self._osk_unavailable = False

        # Carica configurazioni tablet da config_negozio.ini
        self._load_tablet_config()

    # ------------------------------------------------------------
    # Helpers di configurazione e scaling
    # ------------------------------------------------------------
    def _load_tablet_config(self) -> None:
        """Carica le impostazioni tablet/animazioni/tastiera/timeout da config_negozio.ini.
        Imposta attributi:
          - self.tablet_mode (bool)
          - self.animations_enabled (bool)
          - self.virtual_keyboard_enabled (bool)
          - self.auto_deselect_timeout (int, secondi)
          - self.feedback_toast_ms (int, ms) se presente in [UI]
        """
        try:
            import sys
            cfg = configparser.ConfigParser()
            # Determina la directory base - gestisce EXE compilato
            if getattr(sys, 'frozen', False):
                # Se è un EXE compilato con PyInstaller
                base_dir = os.path.dirname(sys.executable)
            else:
                # Se è script Python normale
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                except Exception:
                    base_dir = '.'
            cfg_path = os.path.join(base_dir, 'config_negozio.ini')
            print(f"[CONFIG] Caricando configurazione da: {cfg_path}")
            cfg.read(cfg_path, encoding='utf-8')

            if cfg.has_section('TABLET'):
                self.tablet_mode = cfg.getboolean('TABLET', 'modalita_tablet', fallback=self.tablet_mode)
                self.animations_enabled = cfg.getboolean('TABLET', 'animazioni_abilitate', fallback=self.animations_enabled)
                self.virtual_keyboard_enabled = cfg.getboolean('TABLET', 'tastiera_virtuale', fallback=self.virtual_keyboard_enabled)
                self.auto_deselect_timeout = cfg.getint('TABLET', 'auto_deselect_timeout', fallback=getattr(self, 'auto_deselect_timeout', 4) or 4)
            else:
                # Default sensati
                self.tablet_mode = getattr(self, 'tablet_mode', True)
                self.animations_enabled = getattr(self, 'animations_enabled', True)
                self.virtual_keyboard_enabled = getattr(self, 'virtual_keyboard_enabled', True)
                self.auto_deselect_timeout = getattr(self, 'auto_deselect_timeout', 4) or 4

            # Opzionale: durata toast feedback da [UI]
            if cfg.has_section('UI'):
                self.feedback_toast_ms = cfg.getint('UI', 'feedback_toast_ms', fallback=self.feedback_toast_ms)
        except Exception as e:
            print(f"[CFG] Errore caricando configurazione tablet: {e}")
            # Mantieni i default già impostati in __init__

    def init_scaling(self, parent: tk.Misc) -> None:
        """Inizializza i parametri di scaling in base alla risoluzione del display.
        Imposta:
          - self.vw, self.vh: dimensioni schermo in px
          - self.scale: fattore di scala relativo a 1280x800
        """
        try:
            sw = int(parent.winfo_screenwidth())
            sh = int(parent.winfo_screenheight())
        except Exception:
            sw, sh = 1280, 800

        self.vw = sw
        self.vh = sh
        base_w, base_h = 1280, 800
        # Usa il più piccolo per mantenere proporzioni; limita per evitare overscaling eccessivo
        scale = min(sw / base_w, sh / base_h)
        # Evita scale < 0.75 su schermi piccoli e > 3 su schermi molto grandi
        self.scale = max(0.75, min(3.0, scale))
        # Flag utile per UI specifiche
        self.is_tablet_resolution = (min(sw, sh) <= 800)

    def s(self, v: int) -> int:
        """Scala un valore intero in pixel secondo self.scale (fallback 1.0)."""
        try:
            return max(1, int(round(v * float(getattr(self, 'scale', 1.0)))))
        except Exception:
            return int(v)

    def draw_rounded_rect(self, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, radius: int,
                           fill: str = '', outline: str = '', width: int = 1) -> int:
        """Disegna un rettangolo arrotondato su un Canvas come UN SOLO item usando un poligono.
        Ritorna l'id dell'elemento, compatibile con itemconfig (fill/outline/width).
        """
        try:
            # Normalizza coordinate
            if x2 < x1:
                x1, x2 = x2, x1
            if y2 < y1:
                y1, y2 = y2, y1
            w = max(1, x2 - x1)
            h = max(1, y2 - y1)
            r = max(0, min(radius, w // 2, h // 2))
            if r <= 0:
                return canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)

            # Costruisci i punti approssimando gli archi con smooth
            # 8 punti chiave (uno per ogni direzione) + punti intermedi per curvatura
            steps = 6  # più alto = curva più liscia
            def corner(cx, cy, start_ang_deg):
                import math as _m
                pts = []
                for i in range(steps + 1):
                    ang = _m.radians(start_ang_deg + i * 90.0 / steps)
                    pts.append(cx + r * _m.cos(ang))
                    pts.append(cy + r * _m.sin(ang))
                return pts

            # Centri degli archi TL, TR, BR, BL
            tl = (x1 + r, y1 + r)
            tr = (x2 - r, y1 + r)
            br = (x2 - r, y2 - r)
            bl = (x1 + r, y2 - r)

            points = []
            # Partenza: in alto a sinistra, giro in senso orario
            points += corner(*tl, start_ang_deg=180)  # TL: 180->270
            points += corner(*tr, start_ang_deg=270)  # TR: 270->360
            points += corner(*br, start_ang_deg=0)    # BR: 0->90
            points += corner(*bl, start_ang_deg=90)   # BL: 90->180

            return canvas.create_polygon(points, smooth=True, fill=fill, outline=outline, width=width)
        except Exception as e:
            print(f"[UI] draw_rounded_rect fallback a rectangle: {e}")
            return canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)

    def create_icon_only_button(self, parent, icon_path: str, command, hover_color='#F0F8FF'):
        """Crea un bottone composto solo da un'icona, con bordo rosso armonico quando selezionato."""
        icon_size = int(self.vh * 0.35)
        border_margin = max(self.s(8), int(icon_size * 0.06))

        border_frame = tk.Frame(parent, bg='#FFFFFF', bd=0, highlightthickness=0)
        canvas = tk.Canvas(border_frame, width=icon_size, height=icon_size, bg='#FFFFFF', highlightthickness=0, bd=0, cursor='hand2')

        icon_img = None
        icon_id = None
        if icon_path and os.path.exists(icon_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                inner_size = max(icon_size - 2 * border_margin, int(icon_size * 0.72))
                img = img.resize((inner_size, inner_size), Image.Resampling.LANCZOS)
                icon_img = ImageTk.PhotoImage(img)
                icon_id = canvas.create_image(icon_size // 2, icon_size // 2, image=icon_img, anchor='center')
            except Exception as e:
                print(f"[ICON] Errore caricamento icona {icon_path}: {e}")

        canvas.pack(expand=True, fill='both')

        state = {
            'selected': False,
            'particles': [],
            'anim_job': None,
            'all_particle_ids': set(),
            'timer_job': None,
            'border_id': None
        }

        def clear_particles():
            if state.get('anim_job') is not None:
                canvas.after_cancel(state['anim_job'])
                state['anim_job'] = None
            border_frame.configure(relief='flat', bd=0, highlightthickness=0,
                                   highlightcolor='#FFFFFF', highlightbackground='#FFFFFF')
            if state.get('border_id'):
                try:
                    canvas.delete(state['border_id'])
                except Exception:
                    pass
                state['border_id'] = None
            if state.get('timer_job'):
                canvas.after_cancel(state['timer_job'])
                state['timer_job'] = None
            for particle in list(state['particles']):
                try:
                    canvas.delete(particle['id'])
                except Exception:
                    pass
            for particle_id in list(state['all_particle_ids']):
                try:
                    canvas.delete(particle_id)
                except Exception:
                    pass
            state['particles'].clear()
            state['all_particle_ids'].clear()
            self.particle_cleanup_counter += 1
            if self.particle_cleanup_counter % 8 == 0:
                import gc
                gc.collect()

        def create_sparkle_particle():
            import random
            import math
            cx, cy = icon_size // 2, icon_size // 2
            radius = icon_size * random.uniform(0.2, 0.6)
            ang = random.uniform(0, 2 * math.pi)
            px = cx + radius * math.cos(ang)
            py = cy + radius * math.sin(ang)
            particle_type = random.choice(['star', 'circle', 'diamond', 'heart'])
            size = random.randint(3, 8)
            colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98FB98', '#F0E68C', '#FFB6C1']
            color = random.choice(colors)
            if particle_type == 'star':
                points = []
                for i in range(10):
                    a2 = math.pi * i / 5
                    r = size * (1.8 if i % 2 == 0 else 0.7)
                    x = px + r * math.cos(a2)
                    y = py + r * math.sin(a2)
                    points.extend([x, y])
                particle_id = canvas.create_polygon(points, fill=color, outline='white', width=1)
            elif particle_type == 'circle':
                particle_id = canvas.create_oval(px - size, py - size, px + size, py + size, fill=color, outline='white', width=1)
            elif particle_type == 'diamond':
                points = [px, py - size, px + size, py, px, py + size, px - size, py]
                particle_id = canvas.create_polygon(points, fill=color, outline='white', width=1)
            else:
                particle_id = canvas.create_oval(px - size//2, py - size, px + size//2, py, fill=color, outline='white', width=1)
            import random as _r
            explosion_force = _r.uniform(0.5, 1.5)
            dx = _r.uniform(-4, 4) * explosion_force
            dy = _r.uniform(-20, -10) * explosion_force
            rotation = _r.uniform(-0.3, 0.3)
            life = _r.randint(80, 120) if self.tablet_mode else _r.randint(50, 80)
            state['all_particle_ids'].add(particle_id)
            return {'id': particle_id, 'type': particle_type, 'x': px, 'y': py, 'dx': dx, 'dy': dy,
                    'rotation': rotation, 'angle': 0, 'life': life, 'max_life': life, 'size': size,
                    'color': color, 'bounce_count': 0}

        def update_particles():
            max_particles = self.MAX_PARTICLES_TABLET if self.tablet_mode else self.MAX_PARTICLES_DESKTOP
            if len(state['particles']) > max_particles:
                excess = len(state['particles']) - max_particles
                for _ in range(excess):
                    old_particle = state['particles'].pop(0)
                    try:
                        canvas.delete(old_particle['id'])
                        state['all_particle_ids'].discard(old_particle['id'])
                    except Exception:
                        pass
            import math
            particles_to_remove = []
            particle_update_counter = getattr(update_particles, 'counter', 0) + 1
            update_particles.counter = particle_update_counter
            for i, particle in enumerate(list(state['particles'])):
                if self.tablet_mode and particle_update_counter % 3 != i % 3:
                    continue
                particle['x'] += particle['dx']
                particle['y'] += particle['dy']
                particle['life'] -= 1
                if not self.tablet_mode:
                    particle['angle'] += particle['rotation']
                    particle['dy'] += 0.4
                    particle['dx'] *= 0.98
                    if particle['x'] < 0 or particle['x'] > icon_size:
                        particle['dx'] *= -0.7
                        particle['bounce_count'] += 1
                    if particle['y'] > icon_size and particle['dy'] > 0 and particle['bounce_count'] < 2:
                        particle['dy'] *= -0.6
                        particle['bounce_count'] += 1
                else:
                    particle['dy'] += 0.8
                    particle['angle'] += particle['rotation'] * 0.5
                try:
                    if self.tablet_mode:
                        size = particle['size']
                        canvas.coords(particle['id'], particle['x'] - size//2, particle['y'] - size//2,
                                      particle['x'] + size//2, particle['y'] + size//2)
                    else:
                        if particle['type'] == 'star':
                            points = []
                            for j in range(10):
                                a3 = math.pi * j / 5 + particle['angle']
                                r = particle['size'] * (1.8 if j % 2 == 0 else 0.7)
                                x = particle['x'] + r * math.cos(a3)
                                y = particle['y'] + r * math.sin(a3)
                                points.extend([x, y])
                            canvas.coords(particle['id'], *points)
                        elif particle['type'] == 'circle':
                            size = particle['size']
                            pulse = 1 + 0.3 * math.sin(particle['angle'] * 3)
                            size *= pulse
                            canvas.coords(particle['id'], particle['x'] - size, particle['y'] - size,
                                          particle['x'] + size, particle['y'] + size)
                        elif particle['type'] == 'diamond':
                            size = particle['size']
                            ang = particle['angle']
                            points = []
                            for da in [0, math.pi/2, math.pi, 3*math.pi/2]:
                                x = particle['x'] + size * math.cos(da + ang)
                                y = particle['y'] + size * math.sin(da + ang)
                                points.extend([x, y])
                            canvas.coords(particle['id'], *points)
                        else:
                            size = particle['size']
                            canvas.coords(particle['id'], particle['x'] - size//2, particle['y'] - size,
                                          particle['x'] + size//2, particle['y'])
                    alpha = particle['life'] / particle['max_life']
                    if alpha < 0.1:
                        canvas.delete(particle['id'])
                        state['all_particle_ids'].discard(particle['id'])
                        particles_to_remove.append(particle)
                except Exception:
                    particles_to_remove.append(particle)
                    try:
                        canvas.delete(particle['id'])
                        state['all_particle_ids'].discard(particle['id'])
                    except Exception:
                        pass
                cleanup_distance = 50 if not self.tablet_mode else 20
                if (particle['life'] <= 0 or particle['y'] > icon_size + cleanup_distance or
                        particle['x'] < -cleanup_distance or particle['x'] > icon_size + cleanup_distance):
                    particles_to_remove.append(particle)
            for p in particles_to_remove:
                try:
                    canvas.delete(p['id'])
                    state['all_particle_ids'].discard(p['id'])
                except Exception:
                    pass
                if p in state['particles']:
                    state['particles'].remove(p)
            if state['particles'] and state['selected']:
                update_interval = 150 if self.tablet_mode else 80
                state['anim_job'] = canvas.after(update_interval, update_particles)
            else:
                state['anim_job'] = None

        def set_selected(flag: bool):
            state['selected'] = bool(flag)
            if state.get('timer_job'):
                canvas.after_cancel(state['timer_job'])
                state['timer_job'] = None
            if state['selected']:
                if state.get('border_id'):
                    try:
                        canvas.delete(state['border_id'])
                    except Exception:
                        pass
                    state['border_id'] = None
                gap = max(self.s(6), int(icon_size * 0.02))
                x1, y1 = gap, gap
                x2, y2 = icon_size - gap, icon_size - gap
                radius = int(icon_size * 0.18)
                try:
                    state['border_id'] = self.draw_rounded_rect(canvas, x1, y1, x2, y2, radius,
                                                                fill='', outline='#FF0000', width=self.s(6))
                except Exception:
                    state['border_id'] = canvas.create_rectangle(x1, y1, x2, y2, outline='#FF0000', width=self.s(6))
                timeout_ms = getattr(self, 'auto_deselect_timeout', 4) * 1000
                def auto_deselect():
                    set_selected(False)
                    if hasattr(self, 'selection_hint_var') and self.selection_hint_var is not None:
                        self.selection_hint_var.set('SELEZIONA INGRESSO/USCITA E AVVICINA IL BADGE AL LETTORE')
                state['timer_job'] = canvas.after(timeout_ms, auto_deselect)
                if self.tablet_mode:
                    for _ in range(self.MAX_PARTICLES_TABLET):
                        state['particles'].append(create_sparkle_particle())
                else:
                    for _ in range(self.MAX_PARTICLES_DESKTOP):
                        state['particles'].append(create_sparkle_particle())
                    for _ in range(3):
                        p = create_sparkle_particle()
                        p['size'] *= 1.3
                        p['life'] *= 1.2
                        state['particles'].append(p)
                if not state['particles'] or state['anim_job'] is None:
                    update_particles()
            else:
                border_frame.configure(relief='flat', bd=0, highlightthickness=0,
                                       highlightcolor='#FFFFFF', highlightbackground='#FFFFFF')
                if state.get('border_id'):
                    try:
                        canvas.delete(state['border_id'])
                    except Exception:
                        pass
                    state['border_id'] = None
                clear_particles()

        def handle_click(event=None):
            # Rispetta il blocco globale dei pulsanti (es. durante dialog modali)
            if getattr(self, '_buttons_disabled', False):
                return
            if self.tablet_mode:
                for _ in range(self.MAX_PARTICLES_TABLET // 2):
                    state['particles'].append(create_sparkle_particle())
            else:
                for _ in range(self.MAX_PARTICLES_DESKTOP):
                    state['particles'].append(create_sparkle_particle())
                def delayed_particles():
                    import random, math
                    for _ in range(6):
                        p = create_sparkle_particle()
                        angle = random.uniform(0, 2 * math.pi)
                        rad = icon_size * random.uniform(0.3, 0.8)
                        p['x'] = icon_size // 2 + rad * math.cos(angle)
                        p['y'] = icon_size // 2 + rad * math.sin(angle)
                        p['dx'] *= 1.3
                        p['dy'] *= 1.1
                        state['particles'].append(p)
                canvas.after(200, delayed_particles)
            if not state['anim_job']:
                update_particles()
            if callable(command):
                try:
                    command()
                except Exception as e:
                    print(f"Errore pulsante icona: {e}")

        canvas.bind('<Button-1>', handle_click)
        if icon_id is not None:
            canvas.tag_bind(icon_id, '<Button-1>', handle_click)
        return {
            'canvas': canvas,
            'border_frame': border_frame,
            'icon_id': icon_id,
            'icon_img': icon_img,
            'command': command,
            'set_selected': set_selected,
            'is_selected': lambda: state['selected'],
            'clear_particles': clear_particles,
            'state': state
        }
    def create_pill_button(self, parent, text: str, bg_color: str, fg_color: str, command, icon_path=None):
        """Crea un pulsante a pillola con testo e icona opzionale."""
        # Dimensioni proporzionali
        width = int(self.vw * 0.34)
        height = int(self.vh * 0.09)
        radius = max(self.s(16), int(height * 0.50))  # full pill
        font_size = max(self.s(24), int(height * 0.48))
        
        canvas = tk.Canvas(parent, width=width, height=height, bg='#FFFFFF', highlightthickness=0, bd=0, cursor='hand2')
        rect_id = self.draw_rounded_rect(canvas, 0, 0, width, height, radius, fill=bg_color, outline='', width=0)
        
        # Carica icona se specificata
        icon_img = None
        icon_id = None
        if icon_path and os.path.exists(icon_path):
            try:
                from PIL import Image, ImageTk
                # Ridimensiona l'icona per adattarla all'altezza del bottone
                icon_size = int(height * 0.6)  # 60% dell'altezza
                img = Image.open(icon_path)
                img = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                icon_img = ImageTk.PhotoImage(img)
                
                # Se non c'? testo, centra l'icona, altrimenti posiziona a sinistra
                if text.strip() == '':
                    # Solo icona - centrata
                    icon_x = width // 2
                    text_x = width // 2  # Il testo vuoto sar? invisibile
                else:
                    # Icona + testo - posiziona icona a sinistra e sposta testo a destra
                    icon_x = int(width * 0.25)  # 25% dalla sinistra
                    text_x = int(width * 0.65)  # 65% dalla sinistra
                
                icon_id = canvas.create_image(icon_x, height // 2, image=icon_img, anchor='center')
            except Exception as e:
                print(f"[ICON] Errore caricamento icona {icon_path}: {e}")
                text_x = width // 2
        else:
            text_x = width // 2
        
        # Crea il testo solo se non ? vuoto
        text_id = None
        if text.strip() != '':
            text_id = canvas.create_text(text_x, height // 2, text=text, fill=fg_color, font=('Segoe UI', font_size, 'bold'), anchor='center')
        
        state = {'selected': False}
        
        def set_selected(flag: bool):
            state['selected'] = bool(flag)
            if state['selected']:
                # Evidenzia con contorno spesso e leggero scurimento della pill
                outline_col = self._darken_color(bg_color, 0.35)
                canvas.itemconfig(rect_id, outline=outline_col, width=self.s(6), fill=self._darken_color(bg_color, 0.05))
            else:
                canvas.itemconfig(rect_id, outline='', width=0, fill=bg_color)
            # Mantieni testo leggibile solo se esiste
            if text_id is not None:
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
        
        # Elementi che rispondono al click
        clickable_items = [canvas, rect_id]
        if text_id is not None:
            clickable_items.append(text_id)
        if icon_id is not None:
            clickable_items.append(icon_id)
            
        for item in clickable_items:
            if hasattr(item, 'bind'):
                item.bind('<Button-1>', handle_click)
            else:
                canvas.tag_bind(item, '<Button-1>', handle_click)
        
        return {
            'canvas': canvas,
            'rect_id': rect_id,
            'text_id': text_id,
            'icon_id': icon_id,
            'icon_img': icon_img,
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
        """Dashboard TIGOT? - Full-screen, scaling 8" e mockup-spec con topbar brand."""
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

        # Setup cattura tastiera per lettori USB in modalit? tastiera
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

    # --- Root wiring & global controls ---
    def set_root(self, root: tk.Tk) -> None:
        """Imposta la root Tk e configura hook base."""
        self.root = root

    def _disable_all_buttons(self):
        """Blocca i click su tutti i pulsanti custom (rispettato dai nostri handler)."""
        self._buttons_disabled = True

    def _enable_all_buttons(self):
        """Sblocca i click su tutti i pulsanti custom."""
        self._buttons_disabled = False

    # --- Tastiera virtuale personalizzata ---
    def show_virtual_keyboard(self, target_widget=None):
        """Mostra la tastiera virtuale personalizzata se abilitata e non soppressa."""
        try:
            if self._suppress_osk:
                return
            if not self.tablet_mode or not self.virtual_keyboard_enabled:
                return
            
            # Importa e inizializza la tastiera virtuale COMPATTA
            if not hasattr(self, '_custom_keyboard'):
                from compact_keyboard import KeyboardManager
                self._custom_keyboard = KeyboardManager(self.root)
                print("[KEYBOARD] Tastiera virtuale COMPATTA inizializzata")
            
            # Mostra la tastiera per il widget specificato
            if target_widget:
                self._custom_keyboard.show(target_widget)
            else:
                # Se non specificato, cerca il widget attualmente in focus
                focused_widget = self.root.focus_get()
                if focused_widget:
                    self._custom_keyboard.show(focused_widget)
                else:
                    print("[KEYBOARD] Nessun widget target trovato")
            
            print("[KEYBOARD] Tastiera virtuale mostrata")
            
        except Exception as e:
            print(f"[KEYBOARD] Errore show_virtual_keyboard: {e}")

    def hide_virtual_keyboard(self):
        """Nasconde la tastiera virtuale personalizzata."""
        try:
            if hasattr(self, '_custom_keyboard'):
                self._custom_keyboard.hide()
                print("[KEYBOARD] Tastiera virtuale nascosta")
        except Exception as e:
            print(f"[KEYBOARD] Errore hide_virtual_keyboard: {e}")

    def create_brand_topbar(self, parent):
        """Crea topbar pi? spessa (?11% vh, min 84px), con logo TIGOTA centrato, accento rosso e icona a destra."""
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
                        try:
                            print("[DEBUG] Clic icona impostazioni rilevato")
                            self.open_pin_dialog()
                        except Exception as e:
                            print(f"[ERROR] Errore apertura impostazioni: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    # Binding multipli per maggiore robustezza
                    canvas.tag_bind(img_id_l, '<Button-1>', on_left_click)
                    canvas.tag_bind(img_id_l, '<ButtonPress-1>', on_left_click)
                    
                    # Salva il riferimento per debugging
                    self._settings_icon_id = img_id_l
                    self._settings_canvas = canvas
            except Exception as e:
                print(f"[ERROR] Errore setup icona impostazioni: {e}")
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
        """Apre il wizard di abbinamento - COPIATO ESATTAMENTE DALLE IMPOSTAZIONI."""
        # **IMPORTANTE**: Ferma il lettore NFC prima di aprire il dialog modale per evitare freeze
        print("[DEBUG] Stopping NFC reader before opening wizard...")
        
        # **STEP 0**: Cancella tutti i timer attivi dei selettori prima di aprire
        print("[DEBUG] Cancellando timer attivi dei selettori...")
        if hasattr(self, 'btn_ingresso') and self.btn_ingresso and 'state' in self.btn_ingresso:
            state = self.btn_ingresso['state']
            if state.get('timer_job'):
                self.root.after_cancel(state['timer_job'])
                state['timer_job'] = None
                print("[DEBUG] Timer Ingresso cancellato")
        
        if hasattr(self, 'btn_uscita') and self.btn_uscita and 'state' in self.btn_uscita:
            state = self.btn_uscita['state']
            if state.get('timer_job'):
                self.root.after_cancel(state['timer_job'])
                state['timer_job'] = None
                print("[DEBUG] Timer Uscita cancellato")
        
        # **STEP 1**: Ferma IMMEDIATAMENTE tutte le animazioni attive
        print("[DEBUG] Stopping all animations immediately...")
        if hasattr(self, 'btn_ingresso') and self.btn_ingresso:
            try:
                self.btn_ingresso['clear_particles']()
                self.btn_ingresso['set_selected'](False)
                print("[DEBUG] Ingresso animations stopped")
            except:
                pass
                
        if hasattr(self, 'btn_uscita') and self.btn_uscita:
            try:
                self.btn_uscita['clear_particles']()
                self.btn_uscita['set_selected'](False) 
                print("[DEBUG] Uscita animations stopped")
            except:
                pass
                
        # **STEP 2**: Disabilita TUTTI i pulsanti per evitare click ripetuti durante il dialog
        print("[DEBUG] Disabling all buttons...")
        self._disable_all_buttons()
        
        # **STEP 3**: Ferma completamente NFC reader e keyboard capture
        nfc_was_active = False
        if self.nfc_reader:
            try:
                nfc_was_active = True
                self.nfc_reader.stop_reading()
                print("[DEBUG] NFC reader stop command sent")
                
                # **CRITICO**: Attesa più lunga quando ci sono animazioni attive
                import time
                wait_time = 0.8 if self.selected_action else 0.3  # Più tempo se c'è selezione attiva
                time.sleep(wait_time)
                print(f"[DEBUG] NFC reader fully stopped (waited {wait_time}s)")
            except Exception as e:
                print(f"[DEBUG] Error stopping NFC reader: {e}")
                
        # **STEP 4**: Ferma keyboard capture
        try:
            self._stop_keyboard_capture()
            print("[DEBUG] Keyboard capture stopped")
        except:
            pass
            
        # **STEP 5**: Pulizia garbage collection se era attiva una selezione
        if self.selected_action:
            import gc
            collected = gc.collect()
            print(f"[DEBUG] Garbage collection: {collected} oggetti rimossi pre-wizard")
        
        # **STEP 6**: Pausa aggiuntiva per sicurezza prima di aprire il dialog modale
        import time
        time.sleep(0.3)  # Pausa finale per stabilizzazione
        
        try:
            print("[DEBUG] Iniziando creazione wizard abbinamento...")
            self._create_abbinamento_wizard_like_settings()
            print("[DEBUG] Wizard abbinamento aperto con successo")
        except Exception as e:
            print(f"[UI] Impossibile aprire wizard abbinamento: {e}")
            # **RECOVERY**: Riabilita tutto se fallisce
            self._enable_all_buttons()

    def _create_abbinamento_wizard_like_settings(self):
        """Crea wizard abbinamento usando ESATTAMENTE lo stesso stile delle impostazioni"""
        import tkinter as tk
        from tkinter import messagebox
        from database_sqlite import get_database_manager
        
        # Database
        db = get_database_manager()
        
        # Variabili wizard
        codice_var = tk.StringVar()
        nome_var = tk.StringVar()
        cognome_var = tk.StringVar()
        badge_var = tk.StringVar()
        current_step = [1]  # Lista per closure
        
        # Scaling IDENTICO alle impostazioni
        try:
            vw = self.root.winfo_screenwidth()
            vh = self.root.winfo_screenheight()
        except Exception:
            vw, vh = 1280, 800
        base_w, base_h = 1280, 800
        scale_factor = max(1.0, min(3.0, min(vw / base_w, vh / base_h)))
        def s(v: int) -> int:
            return max(1, int(round(v * scale_factor)))
        
        # **WINDOW SETUP OTTIMIZZATO COME LE IMPOSTAZIONI**
        print("[DEBUG] Creando dialog wizard tablet-friendly...")
        win = tk.Toplevel(self.root)
        win.title('Abbinamento Badge')
        
        # Finestra con dimensioni temporanee - sarà ridimensionata alla fine
        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
        except Exception:
            sw, sh = 1280, 800
        
        win_width = min(sw - 100, 800)  # Larghezza adatta al contenuto
        x = (sw - win_width) // 2
        # Posiziona in alto per lasciare spazio alla tastiera virtuale  
        y = max(20, (sh - 500) // 6)  # Stima approssimativa per il posizionamento

        # Imposta dimensioni temporanee - sarà ottimizzata dopo la creazione dei widget
        win.geometry(f"{win_width}x400+{x}+{y}")
        win.configure(bg='#FFFFFF')
        win.resizable(False, False)
        win.transient(self.root)
        print("[DEBUG] Dialog tablet-friendly configurato (SEMPRE IN PRIMO PIANO)")
        win.attributes('-topmost', True)
        win.grab_set()
        
        def show_tablet_keyboard():
            """Mostra tastiera tablet - IDENTICO ALLE IMPOSTAZIONI"""
            if self.tablet_mode and self.virtual_keyboard_enabled:
                print("[DEBUG] Campo cliccato (!entry) - mostrando tastiera virtuale")
                # Passa sempre il widget attivo al keyboard manager per assegnare il parent corretto
                focused = win.focus_get()
                self.root.after(100, lambda fw=focused: self.show_virtual_keyboard(fw))
            else:
                print("[DEBUG] Campo cliccato - modalità tablet disabilitata")
        
        def show_keyboard_for_field(event):
            """Binding corretto per campi - IDENTICO alle impostazioni funzionanti"""
            if self.tablet_mode and self.virtual_keyboard_enabled:
                print(f"[DEBUG] Campo cliccato ({event.widget.winfo_name()}) - mostrando tastiera virtuale")
                
                def _show_and_raise():
                    # **FIX CRITICO**: Rilascia grab prima di aprire tastiera
                    try:
                        win.grab_release()
                        print("[DEBUG] Grab rilasciato per permettere alla tastiera di funzionare")
                    except Exception as e:
                        print(f"[DEBUG] Errore nel rilasciare grab: {e}")
                    
                    self.show_virtual_keyboard(event.widget)
                    try:
                        if hasattr(self, '_custom_keyboard') and self._custom_keyboard:
                            # Porta la tastiera in primo piano (come nelle impostazioni)
                            self._custom_keyboard.keyboard.lift()
                            self._custom_keyboard.keyboard.attributes('-topmost', True)
                            self._custom_keyboard.keyboard.focus_force()
                            print("[DEBUG] Tastiera portata in primo piano")
                            
                            # Configura callback per ripristinare grab quando tastiera si chiude
                            def on_keyboard_close():
                                try:
                                    win.grab_set()
                                    win.lift()
                                    win.focus_force()
                                    print("[DEBUG] Grab ripristinato dopo chiusura tastiera")
                                except Exception as e:
                                    print(f"[DEBUG] Errore nel ripristinare grab: {e}")
                            
                            # Imposta callback di chiusura se non esiste già
                            if not hasattr(self._custom_keyboard, '_wizard_close_callback'):
                                self._custom_keyboard._wizard_close_callback = on_keyboard_close
                                original_close = getattr(self._custom_keyboard, 'close_keyboard', None)
                                if original_close:
                                    def wrapped_close():
                                        original_close()
                                        on_keyboard_close()
                                    self._custom_keyboard.close_keyboard = wrapped_close
                                    print("[DEBUG] Callback chiusura tastiera configurato")
                                    
                    except Exception as e:
                        print(f"[DEBUG] Errore nel portare tastiera in primo piano: {e}")
                    
                    # Assicura che la tastiera rimanga in primo piano
                    win.after(150, _ensure_keyboard_on_top)
                
                def _ensure_keyboard_on_top():
                    try:
                        if hasattr(self, '_custom_keyboard') and self._custom_keyboard and self._custom_keyboard.is_visible():
                            self._custom_keyboard.keyboard.lift()
                            self._custom_keyboard.keyboard.attributes('-topmost', True)
                    except:
                        pass
                
                # Delay per stabilizzare il focus
                self.root.after(100, _show_and_raise)
            else:
                print("[DEBUG] Campo cliccato - modalità tablet disabilitata")
        
        def close_wizard():
            """Chiusura wizard - IDENTICO ALLE IMPOSTAZIONI"""
            print("[DEBUG] Chiusura wizard...")
            # Chiudi tastiera in modo robusto (stessa logica impostazioni)
            try:
                print("[DEBUG] Chiusura tastiera da pulsante Annulla...")
                # Usa l'helper centralizzato (chiude TabTip/OSK, invia WM_CLOSE e nasconde)
                self.hide_virtual_keyboard()
                # Secondo tentativo dopo un breve delay per sicurezza
                self.root.after(300, lambda: self.hide_virtual_keyboard())
                # Fallback extra: kill TabTip se ancora appeso dopo 800ms
                def _fallback_kill_tabtip():
                    try:
                        subprocess.run(['taskkill', '/f', '/im', 'TabTip.exe'], capture_output=True, text=True, timeout=2)
                    except Exception:
                        pass
                self.root.after(800, _fallback_kill_tabtip)
            except Exception:
                pass
            
            self._enable_all_buttons()
            print("[DEBUG] Chiudendo tastiera virtuale automaticamente alla chiusura dialog...")
            win.destroy()
            print("[DEBUG] Dialog wizard chiuso, sistema riabilitato!")
        
        win.protocol("WM_DELETE_WINDOW", close_wizard)
        
        # **UI STRUCTURE OTTIMIZZATO - Spazi ridotti**
        # Header con titolo compatto
        header = tk.Frame(win, bg='#FFFFFF', height=s(40))  # Altezza ridotta
        header.pack(fill='x', pady=(s(6), s(3)))  # Spazi ridotti
        header.pack_propagate(False)
        
        title_font = ('Segoe UI', s(20), 'bold')
        title_label = tk.Label(header, text='Abbinamento Dipendente', font=title_font, bg='#FFFFFF', fg='#5FA8AF')
        title_label.pack(expand=True)
        
        # Status label compatto
        status_label = tk.Label(win, text="Step 1 di 3 · Codice dipendente", font=('Segoe UI', s(12)), bg='#FFFFFF', fg='#666666')
        status_label.pack(pady=(0, s(6)))  # Spazio ridotto
        
        # Main container compatto - non espande verticalmente
        main_container = tk.Frame(win, bg='#FFFFFF')
        main_container.pack(fill='x', expand=False, padx=s(20), pady=(0, s(6)))  # expand=False per non espandere verticalmente
        
        def clear_main():
            for widget in main_container.winfo_children():
                widget.destroy()
        
        def render_step1():
            clear_main()
            status_label.config(text="Step 1 di 3 · Codice dipendente")
            current_step[0] = 1
            
            # Label e Entry - Spazi ottimizzati
            tk.Label(main_container, text="Codice dipendente:", font=('Segoe UI', s(16), 'bold'), bg='#FFFFFF', fg='#333333').pack(anchor='w', pady=(s(3), s(1)))
            
            codice_entry = tk.Entry(main_container, textvariable=codice_var, font=('Segoe UI', s(18)), 
                                  bd=2, relief='solid', highlightthickness=1, highlightcolor='#20B2AA')
            codice_entry.pack(fill='x', ipady=s(8), pady=(0, s(6)))  # Spazio ridotto
            codice_entry.focus_set()
            codice_entry.bind('<FocusIn>', lambda e: print(f"[DEBUG] Campo ricevuto focus: {e.widget.winfo_name()}"))
            codice_entry.bind('<Button-1>', show_keyboard_for_field)
            codice_entry.bind('<KeyRelease>', lambda e: codice_var.set(''.join(ch for ch in codice_var.get() if ch.isdigit())[:10]))
            
            # Error label - Spazio ridotto
            error_label = tk.Label(main_container, text="", font=('Segoe UI', s(11)), fg='#E91E63', bg='#FFFFFF')
            error_label.pack(anchor='w', pady=(0, s(3)))  # Spazio ridotto
            
            # Buttons ingranditi per tablet - Spazio ottimizzato
            btn_frame = tk.Frame(main_container, bg='#FFFFFF')
            btn_frame.pack(fill='x', pady=s(8))  # Spazio ridotto
            
            # Pulsante Annulla ingrandito
            tk.Button(btn_frame, text='Annulla', font=('Segoe UI', s(18), 'bold'),  # Font aumentato da 14 a 18
                     bg='#F3F4F6', fg='#333333', command=close_wizard,
                     padx=s(20), pady=s(12)).pack(side='left')  # Aggiunto padding
            
            def go_step2():
                if not codice_var.get().strip():
                    error_label.config(text="Inserisci un codice valido")
                    winsound.Beep(800, 200)
                    return
                error_label.config(text="")
                render_step2()
            
            # Pulsante Avanti ingrandito
            tk.Button(btn_frame, text='Avanti ›', font=('Segoe UI', s(18), 'bold'),  # Font aumentato da 14 a 18
                     bg='#20B2AA', fg='white', command=go_step2,
                     padx=s(20), pady=s(12)).pack(side='right')  # Aggiunto padding
            
        def render_step2():
            clear_main()
            status_label.config(text="Step 2 di 3 · Nominativo")
            current_step[0] = 2
            
            # Nome - Spazi ottimizzati
            tk.Label(main_container, text="Nome:", font=('Segoe UI', s(16), 'bold'), bg='#FFFFFF', fg='#333333').pack(anchor='w', pady=(s(3), s(1)))
            nome_entry = tk.Entry(main_container, textvariable=nome_var, font=('Segoe UI', s(18)), 
                                bd=2, relief='solid', highlightthickness=1, highlightcolor='#20B2AA')
            nome_entry.pack(fill='x', ipady=s(8), pady=(0, s(6)))  # Spazio ridotto
            nome_entry.focus_set()
            nome_entry.bind('<FocusIn>', lambda e: print(f"[DEBUG] Campo ricevuto focus: {e.widget.winfo_name()}"))
            nome_entry.bind('<Button-1>', show_keyboard_for_field)
            
            # Cognome - Spazi ottimizzati
            tk.Label(main_container, text="Cognome (opzionale):", font=('Segoe UI', s(16), 'bold'), bg='#FFFFFF', fg='#333333').pack(anchor='w', pady=(s(3), s(1)))
            cognome_entry = tk.Entry(main_container, textvariable=cognome_var, font=('Segoe UI', s(18)), 
                                   bd=2, relief='solid', highlightthickness=1, highlightcolor='#20B2AA')
            cognome_entry.pack(fill='x', ipady=s(8), pady=(0, s(6)))  # Spazio ridotto
            cognome_entry.bind('<FocusIn>', lambda e: print(f"[DEBUG] Campo ricevuto focus: {e.widget.winfo_name()}"))
            cognome_entry.bind('<Button-1>', show_keyboard_for_field)
            
            # Buttons ingranditi per tablet - Spazio ottimizzato
            btn_frame = tk.Frame(main_container, bg='#FFFFFF')
            btn_frame.pack(fill='x', pady=s(8))  # Spazio ridotto
            
            # Pulsante Indietro ingrandito
            tk.Button(btn_frame, text='‹ Indietro', font=('Segoe UI', s(18), 'bold'),  # Font aumentato da 14 a 18
                     bg='#F3F4F6', fg='#333333', command=render_step1, 
                     padx=s(20), pady=s(12)).pack(side='left')  # Aggiunto padding
            
            def save_anagrafica():
                nome_var.set(nome_var.get().strip().title())
                cognome_var.set(cognome_var.get().strip().title())
                if not nome_var.get().strip():
                    winsound.Beep(800, 200)
                    return
                if db.upsert_dipendente(codice_var.get(), nome_var.get(), cognome_var.get() or None):
                    render_step3()
                else:
                    winsound.Beep(800, 200)
            
            # Pulsante Avanti ingrandito
            tk.Button(btn_frame, text='Avanti ›', font=('Segoe UI', s(18), 'bold'),  # Font aumentato da 14 a 18
                     bg='#20B2AA', fg='white', command=save_anagrafica,
                     padx=s(20), pady=s(12)).pack(side='right')  # Aggiunto padding
        
        def render_step3():
            clear_main()
            status_label.config(text="Step 3 di 3 · Badge NFC")
            current_step[0] = 3
            
            # Badge
            tk.Label(main_container, text="Badge NFC:", font=('Segoe UI', s(16), 'bold'), bg='#FFFFFF', fg='#333333').pack(anchor='w', pady=(s(3), s(1)))
            tk.Label(main_container, text="Premi 'Abilita Lettura' e avvicina il badge", font=('Segoe UI', s(12)), bg='#FFFFFF', fg='#666666').pack(anchor='w', pady=(0, s(3)))  # Spazio ridotto
            
            badge_row = tk.Frame(main_container, bg='#FFFFFF')
            badge_row.pack(fill='x', pady=(0, s(6)))  # Spazio ridotto
            
            badge_entry = tk.Entry(badge_row, textvariable=badge_var, font=('Consolas', s(16)), 
                                 bd=2, relief='solid', highlightthickness=1, highlightcolor='#20B2AA')
            badge_entry.pack(side='left', fill='x', expand=True, ipady=s(8))
            badge_entry.bind('<FocusIn>', lambda e: print(f"[DEBUG] Campo ricevuto focus: {e.widget.winfo_name()}"))
            badge_entry.bind('<Button-1>', show_keyboard_for_field)
            
            def enable_nfc_for_wizard():
                """Abilita la lettura NFC per l'abbinamento badge nel wizard"""
                print("[DEBUG] Abilita Lettura cliccato nel wizard")
                try:
                    # Ferma eventuale lettore attivo
                    if getattr(self, 'nfc_reader', None):
                        self.nfc_reader.stop_reading()
                    
                    # Crea callback specifico per il wizard
                    def on_wizard_badge_read(badge_id):
                        print(f"[DEBUG] Badge letto nel wizard: {badge_id}")
                        try:
                            # Aggiorna il campo badge nel thread principale
                            win.after(0, lambda: badge_var.set(badge_id.strip()))
                            # Ferma il lettore dopo la lettura
                            if getattr(self, 'nfc_reader', None):
                                self.nfc_reader.stop_reading()
                        except Exception as e:
                            print(f"[DEBUG] Errore aggiornamento badge nel wizard: {e}")
                    
                    # Avvia lettore con callback del wizard
                    from nfc_manager import NFCReader
                    self.nfc_reader = NFCReader(callback=on_wizard_badge_read)
                    self.nfc_reader.start_reading()
                    print("[DEBUG] Lettore NFC avviato per wizard")
                    
                    # Aggiorna UI per indicare lettura attiva
                    nfc_btn.config(text='Lettura Attiva...', bg='#27AE60')
                    
                except Exception as e:
                    print(f"[DEBUG] Errore avvio lettore NFC nel wizard: {e}")
                    winsound.Beep(800, 300)
            
            # Pulsante Abilita Lettura ingrandito
            nfc_btn = tk.Button(badge_row, text='Abilita Lettura', font=('Segoe UI', s(16), 'bold'),  # Font aumentato da 14 a 16
                     bg='#E91E63', fg='white', command=enable_nfc_for_wizard,
                     padx=s(18), pady=s(10))  # Padding aumentato
            nfc_btn.pack(side='right', padx=(s(10), 0), ipadx=s(15), ipady=s(8))
            
            # Buttons ingranditi per tablet
            btn_frame = tk.Frame(main_container, bg='#FFFFFF')
            btn_frame.pack(fill='x', pady=s(15))
            
            # Pulsante Indietro ingrandito
            tk.Button(btn_frame, text='‹ Indietro', font=('Segoe UI', s(18), 'bold'),  # Font aumentato da 14 a 18
                     bg='#F3F4F6', fg='#333333', command=render_step2,
                     padx=s(20), pady=s(12)).pack(side='left')  # Aggiunto padding
            
            def save_badge():
                print("[DEBUG] Salvataggio badge nel wizard...")
                badge_id = badge_var.get().strip()
                codice_dip = codice_var.get().strip()
                
                if not badge_id:
                    print("[DEBUG] Badge ID vuoto")
                    winsound.Beep(800, 200)
                    return
                
                if not codice_dip:
                    print("[DEBUG] Codice dipendente vuoto")
                    winsound.Beep(800, 200)
                    return
                
                try:
                    if db.abbina_badge_dipendente(codice_dip, badge_id):
                        nome_completo = f"{nome_var.get()} {cognome_var.get() or ''}".strip()
                        print(f"[DEBUG] Badge {badge_id} abbinato con successo a {nome_completo}")
                        messagebox.showinfo("Successo", f"Badge abbinato a {nome_completo}!")
                        close_wizard()
                    else:
                        print("[DEBUG] Errore abbinamento badge - db.abbina_badge_dipendente returned False")
                        winsound.Beep(800, 200)
                        messagebox.showerror("Errore", "Impossibile abbinare il badge. Riprova.")
                except Exception as e:
                    print(f"[DEBUG] Eccezione durante abbinamento badge: {e}")
                    winsound.Beep(800, 200)
                    messagebox.showerror("Errore", f"Errore durante abbinamento: {str(e)}")
            
            # Pulsante Salva Abbinamento ingrandito
            tk.Button(btn_frame, text='Salva Abbinamento', font=('Segoe UI', s(18), 'bold'),  # Font aumentato da 14 a 18
                     bg='#20B2AA', fg='white', command=save_badge,
                     padx=s(25), pady=s(12)).pack(side='right')  # Aggiunto padding extra per pulsante importante
        
        # Avvia con step 1
        render_step1()
        print("[DEBUG] Dialog wizard originale pronto, aspettando interazione...")
        
        # OTTIMIZZAZIONE FINALE: Ridimensiona finestra al contenuto effettivo
        win.update_idletasks()  # Assicura che tutti i widget abbiano le dimensioni corrette
        
        # Calcola l'altezza minima necessaria per il wizard
        actual_height = main_container.winfo_reqheight() + header.winfo_reqheight() + 120  # +120 per padding e decorazioni
        
        # Ridimensiona la finestra eliminando spazio bianco inutile
        current_geom = win.geometry().split('+')
        width_height = current_geom[0].split('x')
        width = int(width_height[0])
        x_pos = int(current_geom[1]) 
        y_pos = int(current_geom[2])
        
        # Applica nuove dimensioni ottimizzate per il wizard
        win.geometry(f"{width}x{actual_height}+{x_pos}+{y_pos}")
        print(f"[DEBUG] Finestra wizard ridimensionata automaticamente: {width}x{actual_height}")

    def _force_deselect_button(self, btn_attr_name):
        """Forza la deselezionamento completo di un selettore."""
        try:
            btn_dict = getattr(self, btn_attr_name, None)
            if not btn_dict or 'state' not in btn_dict or 'frame' not in btn_dict:
                return
                
            state = btn_dict['state']
            border_frame = btn_dict['frame']
            canvas = btn_dict.get('canvas')
            
            # 1. STOP COMPLETO animazioni
            state['selected'] = False
            if state.get('anim_job'):
                self.root.after_cancel(state['anim_job'])
                state['anim_job'] = None
            
            # 2. CLEAR particelle
            state['particles'].clear()
            
            # 3. RESET COMPLETO bordo visuale
            border_frame.configure(
                relief='flat',
                bd=0,
                highlightthickness=0,
                highlightcolor='#FFFFFF',
                highlightbackground='#FFFFFF'
            )
            
            # 4. CLEAR canvas se necessario
            if canvas and hasattr(canvas, 'delete'):
                try:
                    canvas.delete("particles")
                except:
                    pass
            
            print(f"[DEBUG] FORZA RESET selettore {btn_attr_name} completato")
            
        except Exception as e:
            print(f"[DEBUG] Errore forza reset {btn_attr_name}: {e}")

    def _reset_selector_border(self, btn_attr_name):
        """Reset del bordo di un selettore (Ingresso/Uscita)."""
        try:
            btn_dict = getattr(self, btn_attr_name, None)
            if btn_dict and 'state' in btn_dict and 'frame' in btn_dict:
                state = btn_dict['state']
                border_frame = btn_dict['frame']
                
                # Reset stato selezionato
                state['selected'] = False
                
                # Reset visuale del bordo
                border_frame.configure(
                    relief='flat',
                    bd=0,
                    highlightthickness=0,
                    highlightcolor='#FFFFFF',
                    highlightbackground='#FFFFFF'
                )
                
                # Ferma particelle
                state['particles'].clear()
                if state.get('anim_job'):
                    self.root.after_cancel(state['anim_job'])
                    state['anim_job'] = None
                    
                print(f"[DEBUG] Bordo selettore {btn_attr_name} resettato")
        except Exception as e:
            print(f"[DEBUG] Errore reset bordo {btn_attr_name}: {e}")

    def open_pin_dialog(self):
        """Apre il tastierino PIN per accedere alle impostazioni"""
        try:
            # Evita doppie aperture del PIN
            if getattr(self, '_pin_dialog_open', False):
                try:
                    if getattr(self, '_pin_dialog', None):
                        self._pin_dialog.deiconify(); self._pin_dialog.lift(); self._pin_dialog.focus_force()
                        print("[DEBUG] PIN già aperto - portato in primo piano")
                        return
                except Exception:
                    pass
            self._pin_dialog_open = True

            # BLOCCA il timer auto-deselect per evitare interferenze
            if hasattr(self, 'auto_deselect_timer') and self.auto_deselect_timer:
                self.root.after_cancel(self.auto_deselect_timer)
                self.auto_deselect_timer = None
                print("[DEBUG] Timer auto-deselect fermato per apertura PIN dialog")

            # Cancella timer dei selettori e ferma animazioni/particelle
            try:
                if hasattr(self, 'btn_ingresso') and self.btn_ingresso and 'state' in self.btn_ingresso:
                    state = self.btn_ingresso['state']
                    if state.get('timer_job'):
                        self.root.after_cancel(state['timer_job']); state['timer_job'] = None
                        print("[DEBUG] Timer Ingresso cancellato (PIN)")
                    self.btn_ingresso['clear_particles'](); self.btn_ingresso['set_selected'](False)
                if hasattr(self, 'btn_uscita') and self.btn_uscita and 'state' in self.btn_uscita:
                    state = self.btn_uscita['state']
                    if state.get('timer_job'):
                        self.root.after_cancel(state['timer_job']); state['timer_job'] = None
                        print("[DEBUG] Timer Uscita cancellato (PIN)")
                    self.btn_uscita['clear_particles'](); self.btn_uscita['set_selected'](False)
            except Exception as e:
                print(f"[DEBUG] Errore stop animazioni/timer selettori per PIN: {e}")

            # Disabilita i pulsanti per evitare interazioni durante il PIN
            try:
                self._disable_all_buttons()
            except Exception:
                pass

            # Ferma NFC e keyboard capture (evita sfarfallii/focus grab)
            try:
                if getattr(self, 'nfc_reader', None):
                    self.nfc_reader.stop_reading(); print("[DEBUG] NFC reader fermato (PIN)")
            except Exception:
                pass
            try:
                self._stop_keyboard_capture(); print("[DEBUG] Keyboard capture stopped (PIN)")
            except Exception:
                pass

            # Sopprimi e chiudi la tastiera virtuale durante il PIN
            self._suppress_osk = True
            try:
                self.hide_virtual_keyboard()
            except Exception:
                pass
            
            # Carica PIN da configurazione
            pin_corretto = self._load_pin_from_config()
            if not pin_corretto:
                pin_corretto = "1234"  # Default
            
            # Scaling per tablet
            try:
                vw = self.root.winfo_screenwidth()
                vh = self.root.winfo_screenheight()
            except Exception:
                vw, vh = 1280, 800
            base_w, base_h = 1280, 800
            scale_factor = max(1.0, min(3.0, min(vw / base_w, vh / base_h)))
            def s(v: int) -> int:
                return max(1, int(round(v * scale_factor)))
            
            # Finestra PIN - Dimensioni compatte per pulsanti quadrati
            pin_win = tk.Toplevel(self.root)
            pin_win.title('Accesso Impostazioni')
            pin_win.geometry(f'{s(450)}x{s(650)}')  # Dimensioni compatte per pulsanti quadrati perfetti
            try:
                pin_win.minsize(s(450), s(650))  # Evita tagli della riga inferiore
            except Exception:
                pass
            pin_win.configure(bg='#FFFFFF')
            pin_win.resizable(False, False)
            pin_win.transient(self.root)
            pin_win.attributes('-topmost', True)
            pin_win.grab_set()
            # Salva riferimento per evitare doppie aperture e poter ripristinare
            self._pin_dialog = pin_win
            
            # Centra la finestra
            pin_win.update_idletasks()
            x = (pin_win.winfo_screenwidth() // 2) - (pin_win.winfo_width() // 2)
            y = (pin_win.winfo_screenheight() // 2) - (pin_win.winfo_height() // 2)
            pin_win.geometry(f'+{x}+{y}')
            
            # Variabile PIN inserito
            pin_inserito = tk.StringVar()
            tentativo = [0]  # Lista per closure
            
            def _cleanup_after_pin():
                # Ripristina stato sistema dopo la chiusura del PIN
                try:
                    self._suppress_osk = False
                    self._pin_dialog_open = False
                    self._pin_dialog = None
                except Exception:
                    pass
                try:
                    self._enable_all_buttons()
                except Exception:
                    pass
                # Chiudi comunque l'OSK
                try:
                    self.hide_virtual_keyboard()
                except Exception:
                    pass

            def _cancel_pin():
                print("[DEBUG] PIN annullato dall'utente")
                _cleanup_after_pin()
                try:
                    pin_win.destroy()
                except Exception:
                    pass

            def check_pin():
                if pin_inserito.get() == pin_corretto:
                    print("[DEBUG] PIN corretto - aprendo impostazioni")
                    _cleanup_after_pin()
                    pin_win.destroy()
                    self.open_settings_dialog()
                else:
                    tentativo[0] += 1
                    print(f"[DEBUG] PIN errato - tentativo {tentativo[0]}")
                    pin_inserito.set("")
                    if tentativo[0] >= 3:
                        print("[DEBUG] Troppi tentativi - chiudendo dialog PIN")
                        winsound.Beep(800, 500)
                        _cancel_pin()
                    else:
                        winsound.Beep(800, 200)
                        error_label.config(text=f"PIN errato! Tentativo {tentativo[0]}/3")
            
            def add_digit(digit):
                current = pin_inserito.get()
                if len(current) < 6:  # Massimo 6 cifre
                    pin_inserito.set(current + str(digit))
                    if len(pin_inserito.get()) == len(pin_corretto):
                        pin_win.after(200, check_pin)  # Verifica automatica
            
            def clear_pin():
                pin_inserito.set("")
                error_label.config(text="")
            
            def backspace():
                current = pin_inserito.get()
                if current:
                    pin_inserito.set(current[:-1])
            
            # Header con più spazio
            tk.Label(pin_win, text='🔒 Accesso Impostazioni', font=('Segoe UI', s(20), 'bold'), 
                    bg='#FFFFFF', fg='#5FA8AF').pack(pady=(s(25), s(15)))
            
            # Display PIN con frame più spaziato
            pin_frame = tk.Frame(pin_win, bg='#FFFFFF')
            pin_frame.pack(pady=s(15))
            
            pin_display = tk.Entry(pin_frame, textvariable=pin_inserito, font=('Consolas', s(24)), 
                                 justify='center', state='readonly', show='●', width=8,
                                 bd=2, relief='solid', highlightthickness=1, highlightcolor='#20B2AA')
            pin_display.pack()
            
            # Error label con spazio definito
            error_label = tk.Label(pin_win, text="", font=('Segoe UI', s(12)), fg='#E91E63', bg='#FFFFFF', height=2)
            error_label.pack(pady=s(10))
            
            # Tastierino numerico con più spazio
            keypad_frame = tk.Frame(pin_win, bg='#FFFFFF')
            keypad_frame.pack(pady=s(20))
            
            # Griglia 4x3: numeri 1-9, poi *, 0, # (stile telefono)
            buttons = [
                [1, 2, 3],
                [4, 5, 6], 
                [7, 8, 9],
                ['C', 0, '←']
            ]
            
            for row_idx, row in enumerate(buttons):
                for col_idx, btn_text in enumerate(row):
                    if btn_text == 'C':
                        # Pulsante Clear rosso - Pulsante più largo e più corto
                        btn = tk.Button(keypad_frame, text='C', font=('Segoe UI', s(16), 'bold'),
                                      width=5, height=2, command=clear_pin,
                                      bg='#FF6B6B', fg='white', relief='raised', bd=2)
                    elif btn_text == '←':
                        # Pulsante Backspace arancione - Pulsante più largo e più corto
                        btn = tk.Button(keypad_frame, text='←', font=('Segoe UI', s(16), 'bold'),
                                      width=5, height=2, command=backspace,
                                      bg='#FFA500', fg='white', relief='raised', bd=2)
                    else:
                        # Pulsanti numerici grigi - Pulsanti più larghi e più corti
                        btn = tk.Button(keypad_frame, text=str(btn_text), font=('Segoe UI', s(16), 'bold'),
                                      width=5, height=2, command=lambda n=btn_text: add_digit(n),
                                      bg='#F0F0F0', fg='#333333', relief='raised', bd=2)
                    
                    btn.grid(row=row_idx, column=col_idx, padx=s(3), pady=s(3))
            
            # Riga pulsanti controllo con separazione adeguata
            control_frame = tk.Frame(pin_win, bg='#FFFFFF')
            control_frame.pack(pady=(s(25), s(20)))  # Più spazio dall'alto
            
            # Pulsante OK verde
            ok_btn = tk.Button(control_frame, text='✓ OK', font=('Segoe UI', s(14), 'bold'),
                              command=check_pin, bg='#27AE60', fg='white',
                              width=10, height=2, relief='raised', bd=3)
            ok_btn.pack(side=tk.LEFT, padx=s(15))
            
            # Pulsante Annulla rosso  
            cancel_btn = tk.Button(control_frame, text='✗ Annulla', font=('Segoe UI', s(14), 'bold'),
                                  command=_cancel_pin, bg='#E74C3C', fg='white',
                                  width=10, height=2, relief='raised', bd=3)
            cancel_btn.pack(side=tk.LEFT, padx=s(15))
            
            # Gestione tasti
            pin_win.bind('<Return>', lambda e: check_pin())
            pin_win.bind('<Escape>', lambda e: _cancel_pin())
            pin_win.protocol('WM_DELETE_WINDOW', lambda: _cancel_pin())
            
        except Exception as e:
            print(f"[ERROR] Errore creazione dialog PIN: {e}")
    
    def _load_pin_from_config(self):
        """Carica il PIN dalle impostazioni - gestisce EXE compilato"""
        try:
            import configparser
            import os
            import sys
            
            # Determina la directory base - gestisce EXE compilato
            if getattr(sys, 'frozen', False):
                # Se è un EXE compilato con PyInstaller
                base_dir = os.path.dirname(sys.executable)
            else:
                # Se è script Python normale
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                except Exception:
                    base_dir = '.'
            config_path = os.path.join(base_dir, 'config_negozio.ini')
            print(f"[CONFIG] Caricando PIN da: {config_path}")
            
            cfg = configparser.ConfigParser()
            cfg.read(config_path, encoding='utf-8')
            
            if cfg.has_section('TABLET'):
                pin = cfg.get('TABLET', 'pin_impostazioni', fallback='1234')
                print(f"[CONFIG] PIN caricato: {pin}")
                return pin
            
            print("[CONFIG] Sezione TABLET non trovata, usando PIN default")
            return '1234'  # Default
        except Exception as e:
            print(f"[ERROR] Errore lettura PIN: {e}")
            return '1234'

    def close_application(self, parent_win=None, on_cancel=None):
        """Chiude completamente l'applicazione con dialogo di conferma.
        - Usa sempre root come parent del dialog di conferma per evitare interazioni con altri wait_window.
        - Se parent_win è una finestra (es. Impostazioni), la disabilita temporaneamente finché il dialog è aperto.
        """
        print("[DEBUG] close_application chiamata")

        # Disabilita temporaneamente la finestra impostazioni (se presente) mentre il dialog è aperto
        if parent_win is not None:
            try:
                parent_win.attributes('-disabled', True)
                print("[DEBUG] Finestra impostazioni disabilitata durante la conferma chiusura")
            except Exception as e:
                print(f"[DEBUG] Impossibile disabilitare finestra impostazioni: {e}")

        # Crea dialogo personalizzato più grande e prominente (parent SEMPRE root)
        confirm_dialog = tk.Toplevel(self.root)
        self._confirm_close_dialog = confirm_dialog  # mantieni un riferimento per evitare GC
        confirm_dialog.title("Conferma Chiusura")
        confirm_dialog.configure(bg='#F5F5F5')

        print("[DEBUG] Dialogo creato come Toplevel, parent: root")

        # Dimensioni e posizionamento prominenti
        dialog_width = self.s(520)
        dialog_height = self.s(380)
        x = (self.root.winfo_screenwidth() - dialog_width) // 2
        # Posiziona in alto per lasciare spazio alla tastiera virtuale
        y = max(20, (self.root.winfo_screenheight() - dialog_height) // 4)  # Un quarto dall'alto invece che centro
        confirm_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        print(f"[DEBUG] Geometria impostata: {dialog_width}x{dialog_height}+{x}+{y}")

        # Porta in primo piano e modalità (transient su root)
        confirm_dialog.transient(self.root)
        confirm_dialog.grab_set()
        confirm_dialog.lift()
        confirm_dialog.focus_set()
        confirm_dialog.resizable(False, False)
        confirm_dialog.attributes('-topmost', True)  # Sempre in primo piano

        def cancel_close():
            print("[DEBUG] cancel_close chiamata - Chiusura applicazione annullata")
            try:
                if parent_win is not None:
                    parent_win.attributes('-disabled', False)
                    parent_win.lift()
                    parent_win.focus_set()
                    print("[DEBUG] Finestra impostazioni riabilitata")
                if on_cancel is not None:
                    on_cancel()
            except Exception as e:
                print(f"[DEBUG] Impossibile riabilitare finestra impostazioni: {e}")
            finally:
                confirm_dialog.destroy()

        # Impedisci chiusura accidentale via 'X'
        def _on_protocol_close():
            print("[DEBUG] Protocol WM_DELETE_WINDOW intercettato - annullo chiusura e chiamo cancel_close")
            cancel_close()
        confirm_dialog.protocol('WM_DELETE_WINDOW', _on_protocol_close)

        print("[DEBUG] Dialogo configurato come modale")

        # Titolo grande e prominente
        title_label = tk.Label(confirm_dialog,
                               text="⚠ CHIUSURA APPLICAZIONE",
                               font=('Segoe UI', self.s(24), 'bold'),
                               fg='#E74C3C', bg='#F5F5F5')
        title_label.pack(pady=self.s(30))

        # Messaggio principale
        message_label = tk.Label(confirm_dialog,
                                 text="Sei sicuro di voler chiudere\ncompletamente SmartTIM?",
                                 font=('Segoe UI', self.s(18)),
                                 fg='#2C3E50', bg='#F5F5F5',
                                 justify=tk.CENTER)
        message_label.pack(pady=self.s(25))

        # Frame per i pulsanti
        buttons_frame = tk.Frame(confirm_dialog, bg='#F5F5F5')
        buttons_frame.pack(pady=self.s(35))

        def confirm_close():
            print("[DEBUG] confirm_close chiamata - Chiusura applicazione confermata dall'utente")
            try:
                confirm_dialog.destroy()
            except:
                pass
            
            try:
                if self.tablet_mode and self.virtual_keyboard_enabled:
                    self.hide_virtual_keyboard()
                if hasattr(self, 'nfc_reader') and self.nfc_reader:
                    self.nfc_reader.stop_reading()
                    
                print("[DEBUG] Chiamando root.quit() per fermare mainloop")
                self.root.quit()
                
                print("[DEBUG] Chiamando root.destroy() per distruggere finestra")
                self.root.destroy()
                
                # Forza chiusura immediata del processo Python
                print("[DEBUG] Forza chiusura con os._exit(0)")
                import os
                os._exit(0)
                
            except Exception as e:
                print(f"[ERROR] Errore durante chiusura: {e}")
                # Forza chiusura anche in caso di errore
                import os
                try:
                    os._exit(0)
                except:
                    import sys
                    sys.exit(1)

        # Pulsante Sì - rosso e molto prominente
        yes_btn = tk.Button(buttons_frame, text="SÌ, CHIUDI",
                            font=('Segoe UI', self.s(16), 'bold'),
                            bg='#E74C3C', fg='white',
                            width=14, height=3,
                            relief='raised', bd=4,
                            command=confirm_close)
        yes_btn.pack(side=tk.LEFT, padx=self.s(20))

        # Pulsante No - verde e prominente
        no_btn = tk.Button(buttons_frame, text="NO, ANNULLA",
                           font=('Segoe UI', self.s(16), 'bold'),
                           bg='#27AE60', fg='white',
                           width=14, height=3,
                           relief='raised', bd=4,
                           command=cancel_close)
        no_btn.pack(side=tk.LEFT, padx=self.s(20))

        no_btn.focus_set()

        confirm_dialog.bind('<Return>', lambda e: cancel_close())
        confirm_dialog.bind('<Escape>', lambda e: cancel_close())

    def open_confirm_close_from_settings(self, settings_win):
        """Flusso robusto: nasconde la finestra Impostazioni e apre la conferma su root.
        Se l'utente annulla, ri-mostra la finestra Impostazioni.
        """
        print("[DEBUG] open_confirm_close_from_settings: inizio procedura")
        try:
            # Nascondi (withdraw) invece di lasciare visibile la finestra Impostazioni
            try:
                print("[DEBUG] Fermando keep_on_top e nascondendo impostazioni...")
                # Ferma il loop keep_on_top per non rubare focus al dialog di conferma
                if hasattr(settings_win, '_stop_keep_on_top'):
                    settings_win._stop_keep_on_top()
                    print("[DEBUG] Keep_on_top fermato")
                settings_win.withdraw()
                print("[DEBUG] Impostazioni nascoste (withdraw) per conferma chiusura")
            except Exception as e:
                print(f"[DEBUG] ERRORE withdraw impostazioni: {e}")
            
            # Apri conferma su root con callback di ripristino
            def _on_cancel():
                print("[DEBUG] _on_cancel chiamato - ripristino impostazioni")
                try:
                    settings_win.deiconify()
                    settings_win.lift()
                    settings_win.focus_force()
                    # Riavvia il mantenimento topmost se presente
                    if hasattr(settings_win, '_start_keep_on_top'):
                        settings_win._start_keep_on_top()
                        print("[DEBUG] Keep_on_top riavviato")
                    print("[DEBUG] Impostazioni ripristinate dopo annullo chiusura")
                except Exception as e:
                    print(f"[DEBUG] ERRORE ripristino impostazioni: {e}")
            
            print("[DEBUG] Chiamando close_application con callback...")
            # Usa il metodo close_application con callback di ripristino
            self.close_application(parent_win=None, on_cancel=_on_cancel)
            print("[DEBUG] close_application chiamata completata")
            
        except Exception as e:
            print(f"[DEBUG] ERRORE CRITICO open_confirm_close_from_settings: {e}")
            import traceback
            print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
            # Fallback: riabilita comunque le impostazioni in caso di errore
            try:
                settings_win.deiconify()
                settings_win.lift()
                if hasattr(settings_win, '_start_keep_on_top'):
                    settings_win._start_keep_on_top()
            except:
                pass

    def open_settings_dialog(self):
        """Apre la finestra Impostazioni con i campi 'codice_sede', 'codice_negozio', 'ora trasferimento' e 'cartella trasferimento'."""
        # **IMPORTANTE**: Ferma il lettore NFC prima di aprire il dialog modale per evitare freeze
        print("[DEBUG] Stopping NFC reader before opening settings...")
        
        # **STEP 0**: Cancella tutti i timer attivi dei selettori prima di aprire
        print("[DEBUG] Cancellando timer attivi dei selettori...")
        if hasattr(self, 'btn_ingresso') and self.btn_ingresso and 'state' in self.btn_ingresso:
            state = self.btn_ingresso['state']
            if state.get('timer_job'):
                self.root.after_cancel(state['timer_job'])
                state['timer_job'] = None
                print("[DEBUG] Timer Ingresso cancellato")
        
        if hasattr(self, 'btn_uscita') and self.btn_uscita and 'state' in self.btn_uscita:
            state = self.btn_uscita['state']
            if state.get('timer_job'):
                self.root.after_cancel(state['timer_job'])
                state['timer_job'] = None
                print("[DEBUG] Timer Uscita cancellato")
        
        # **STEP 1**: Ferma IMMEDIATAMENTE tutte le animazioni attive
        print("[DEBUG] Stopping all animations immediately...")
        if hasattr(self, 'btn_ingresso') and self.btn_ingresso:
            try:
                self.btn_ingresso['clear_particles']()
                self.btn_ingresso['set_selected'](False)
                print("[DEBUG] Ingresso animations stopped")
            except:
                pass
                
        if hasattr(self, 'btn_uscita') and self.btn_uscita:
            try:
                self.btn_uscita['clear_particles']()
                self.btn_uscita['set_selected'](False) 
                print("[DEBUG] Uscita animations stopped")
            except:
                pass
                
        # **STEP 2**: Disabilita TUTTI i pulsanti per evitare click ripetuti durante il dialog
        print("[DEBUG] Disabling all buttons...")
        self._disable_all_buttons()
        
        # **STEP 3**: Ferma completamente NFC reader e keyboard capture
        nfc_was_active = False
        if self.nfc_reader:
            try:
                nfc_was_active = True
                self.nfc_reader.stop_reading()
                print("[DEBUG] NFC reader stop command sent")
                
                # **CRITICO**: Attesa pi? lunga quando ci sono animazioni attive
                import time
                wait_time = 0.8 if self.selected_action else 0.3  # Pi? tempo se c'? selezione attiva
                time.sleep(wait_time)
                print(f"[DEBUG] NFC reader fully stopped (waited {wait_time}s)")
            except Exception as e:
                print(f"[DEBUG] Error stopping NFC reader: {e}")
                
        # **STEP 4**: Ferma keyboard capture
        try:
            self._stop_keyboard_capture()
            print("[DEBUG] Keyboard capture stopped")
        except:
            pass
            
        # **STEP 5**: Pulizia garbage collection se era attiva una selezione
        if self.selected_action:
            import gc
            collected = gc.collect()
            print(f"[DEBUG] Garbage collection: {collected} oggetti rimossi pre-dialog")
        
        # **STEP 6**: Pausa aggiuntiva per sicurezza prima di aprire il dialog modale
        import time
        time.sleep(0.3)  # Pausa finale per stabilizzazione
        
        try:
            print("[DEBUG] Iniziando creazione dialog impostazioni...")
            
            import tkinter as tk
            from tkinter import messagebox, filedialog
            import configparser
            import os
            from datetime import datetime
            
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

            # Crea finestra - VERSION TABLET OTTIMIZZATA (non full-screen)
            print("[DEBUG] Creando dialog impostazioni tablet-friendly...")
            win = tk.Toplevel(self.root)
            win.title('Impostazioni')
            
            # Dimensioni ottimizzate per tablet (non full-screen per evitare problemi)
            try:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
            except Exception:
                sw, sh = 1280, 800
                
            # Finestra con dimensioni temporanee - sarà ridimensionata alla fine
            win_width = min(sw - 100, 1000)
            x = (sw - win_width) // 2
            # Posiziona in alto per lasciare spazio alla tastiera virtuale  
            y = max(20, (sh - 500) // 6)  # Stima approssimativa per il posizionamento

            # Imposta dimensioni temporanee - sarà ottimizzata dopo la creazione dei widget
            win.geometry(f"{win_width}x400+{x}+{y}")
            win.configure(bg='#FFFFFF')
            
            # CORREZIONE CRITICA: Dialog sempre in primo piano
            win.transient(self.root)  # Collegato alla finestra principale
            win.attributes('-topmost', True)  # Sempre sopra
            win.lift()  # Porta in primo piano
            win.focus_force()  # Forza il focus

            # Mantieni in primo piano periodicamente, con controllo avvio/stop
            win._keep_on_top_job = None
            win._keep_on_top_enabled = True

            def _ensure_keyboard_on_top():
                try:
                    if hasattr(self, '_custom_keyboard') and getattr(self._custom_keyboard, 'is_visible', lambda: False)():
                        kb = getattr(self._custom_keyboard, 'keyboard', None)
                        if kb and getattr(kb, 'winfo_exists', lambda: False)():
                            try:
                                kb.lift(); kb.attributes('-topmost', True)
                            except Exception:
                                pass
                except Exception:
                    pass

            def _keep_on_top_tick():
                try:
                    # se finestra non visibile o disabilitata, non rubare focus
                    if not win._keep_on_top_enabled:
                        win._keep_on_top_job = None
                        return
                    if win.winfo_exists() and win.winfo_viewable():
                        win.lift()
                        win.attributes('-topmost', True)
                        # rialza anche la tastiera se visibile (meno frequente)
                        _ensure_keyboard_on_top()
                    win._keep_on_top_job = win.after(1500, _keep_on_top_tick)  # Ogni 1.5 secondi invece di 500ms
                except Exception:
                    win._keep_on_top_job = None

            def _start_keep_on_top():
                try:
                    win._keep_on_top_enabled = True
                    if win._keep_on_top_job is None:
                        win._keep_on_top_job = win.after(100, _keep_on_top_tick)
                except Exception:
                    pass

            def _stop_keep_on_top():
                try:
                    win._keep_on_top_enabled = False
                    if win._keep_on_top_job is not None:
                        win.after_cancel(win._keep_on_top_job)
                        win._keep_on_top_job = None
                except Exception:
                    pass

            # Esporta i controlli per uso esterno (es. conferma chiusura)
            win._start_keep_on_top = _start_keep_on_top
            win._stop_keep_on_top = _stop_keep_on_top

            _start_keep_on_top()  # Avvia il mantenimento in primo piano

            print("[DEBUG] Dialog tablet-friendly configurato (SEMPRE IN PRIMO PIANO)")

            # Stili touch-friendly ma dimensioni normali
            title_font = ('Segoe UI', 28, 'bold')
            label_font = ('Segoe UI', 20)
            entry_font = ('Segoe UI', 18)
            btn_font = ('Segoe UI', 18, 'bold')

            container = tk.Frame(win, bg='#FFFFFF')
            container.pack(fill='x', expand=False, padx=32, pady=20)  # expand=False per non espandere verticalmente

            # Header con titolo centrato (senza pulsante Annulla) - spazio ridotto
            header = tk.Frame(container, bg='#FFFFFF')
            header.pack(fill='x', pady=(0, 15))  # Ridotto da 30 a 15 per stringere di più
            
            # Titolo centrato con padding ridotto
            title_label = tk.Label(header, text='Impostazioni', font=title_font, bg='#FFFFFF', fg='#5FA8AF')
            title_label.pack(side='top', pady=(0, 5))  # Ridotto da 10 a 5

            form = tk.Frame(container, bg='#FFFFFF')
            form.pack(fill='x', expand=False, pady=5)  # Ridotto ulteriormente da 10 a 5
            form.grid_columnconfigure(1, weight=1)

            # Carica valori esistenti
            sede_corrente, negozio_corrente = _load_codes()
            ora_corrente, cartella_corrente = _load_transfer()

            # Campo Codice Sede - padding ridotto
            tk.Label(form, text='Codice Sede:', font=label_font, bg='#FFFFFF').grid(row=0, column=0, sticky='w', pady=6, padx=(0, 16))  # Ridotto da 10 a 6
            sede_var = tk.StringVar(value=sede_corrente)
            sede_entry = tk.Entry(form, textvariable=sede_var, font=entry_font, relief='solid', bd=1)
            sede_entry.grid(row=0, column=1, sticky='ew', pady=6, ipady=8)  # Ridotto da 10 a 6
            
            # Binding tastiera virtuale per tablet
            # Variabile per gestire intelligentemente la tastiera virtuale
            keyboard_timer_id = None
            current_focused_field = None

            def show_keyboard_for_field(event):
                """Mostra tastiera virtuale solo quando si clicca su un campo"""
                nonlocal keyboard_timer_id, current_focused_field

                # Cancella timer di chiusura se esiste
                if keyboard_timer_id:
                    self.root.after_cancel(keyboard_timer_id)
                    keyboard_timer_id = None

                current_focused_field = event.widget

                if self.tablet_mode and self.virtual_keyboard_enabled:
                    print(f"[DEBUG] Campo cliccato ({event.widget.winfo_name()}) - mostrando tastiera virtuale")
                    def _show_and_raise():
                        self.show_virtual_keyboard(event.widget)
                        try:
                            if hasattr(self, '_custom_keyboard'):
                                self._custom_keyboard.bring_to_front()
                        except Exception:
                            pass
                        win.after(150, _ensure_keyboard_on_top)
                    self.root.after(100, _show_and_raise)

            def hide_keyboard_when_unfocus(event):
                """Nasconde tastiera virtuale quando si perde il focus (con controllo intelligente)"""
                nonlocal keyboard_timer_id, current_focused_field

                if self.tablet_mode and self.virtual_keyboard_enabled:
                    # Cancella timer precedente
                    if keyboard_timer_id:
                        self.root.after_cancel(keyboard_timer_id)

                    def delayed_hide():
                        # Nasconde solo se non c'è un altro campo attivo e il focus non è sulla tastiera
                        focused = self.root.focus_get()
                        # Se focus è su una delle entry, mantieni la tastiera
                        if focused in [sede_entry, negozio_entry, ora_entry, cartella_entry]:
                            print("[DEBUG] Campo perso focus ma altro campo attivo - tastiera rimane aperta")
                            return
                        # Se focus è sulla tastiera virtuale o sui suoi widget, non nascondere
                        try:
                            kb = getattr(getattr(self, '_custom_keyboard', None), 'keyboard', None)
                            if kb and getattr(kb, 'winfo_exists', lambda: False)():
                                top = focused.winfo_toplevel() if focused else None
                                if top == kb:
                                    print("[DEBUG] Focus sulla tastiera - non nascondo")
                                    return
                        except Exception:
                            pass
                        # Altrimenti nascondi
                        print("[DEBUG] Campo perso focus definitivo - nascondendo tastiera")
                        self.hide_virtual_keyboard()

                    print(f"[DEBUG] Campo perso focus ({event.widget.winfo_name()}) - controllo tra 800ms")
                    keyboard_timer_id = self.root.after(800, delayed_hide)

            def on_field_focus_in(event):
                """Aggiorna il campo corrente quando riceve il focus"""
                nonlocal current_focused_field
                current_focused_field = event.widget
                print(f"[DEBUG] Campo ricevuto focus: {event.widget.winfo_name()}")

            sede_entry.bind('<Button-1>', show_keyboard_for_field)  # Click del mouse/touch
            sede_entry.bind('<FocusOut>', hide_keyboard_when_unfocus)
            sede_entry.bind('<FocusIn>', on_field_focus_in)

            # Campo Codice Negozio - padding ridotto
            tk.Label(form, text='Codice Negozio:', font=label_font, bg='#FFFFFF').grid(row=1, column=0, sticky='w', pady=6, padx=(0, 16))  # Ridotto da 10 a 6
            negozio_var = tk.StringVar(value=negozio_corrente)
            negozio_entry = tk.Entry(form, textvariable=negozio_var, font=entry_font, relief='solid', bd=1)
            negozio_entry.grid(row=1, column=1, sticky='ew', pady=6, ipady=8)  # Ridotto da 10 a 6
            negozio_entry.bind('<Button-1>', show_keyboard_for_field)
            negozio_entry.bind('<FocusOut>', hide_keyboard_when_unfocus)
            negozio_entry.bind('<FocusIn>', on_field_focus_in)

            # Campo Ora Trasferimento - padding ridotto
            tk.Label(form, text='Ora Trasferimento (HH:MM):', font=label_font, bg='#FFFFFF').grid(row=2, column=0, sticky='w', pady=6, padx=(0, 16))  # Ridotto da 10 a 6
            ora_var = tk.StringVar(value=ora_corrente)
            ora_entry = tk.Entry(form, textvariable=ora_var, font=entry_font, relief='solid', bd=1)
            ora_entry.grid(row=2, column=1, sticky='ew', pady=6, ipady=8)  # Ridotto da 10 a 6
            ora_entry.bind('<Button-1>', show_keyboard_for_field)
            ora_entry.bind('<FocusOut>', hide_keyboard_when_unfocus)
            ora_entry.bind('<FocusIn>', on_field_focus_in)

            # Campo Cartella Trasferimento con browse - padding ridotto
            tk.Label(form, text='Cartella Trasferimento:', font=label_font, bg='#FFFFFF').grid(row=3, column=0, sticky='w', pady=6, padx=(0, 16))  # Ridotto da 10 a 6
            cartella_var = tk.StringVar(value=cartella_corrente)
            
            # Frame per entry + button
            cartella_frame = tk.Frame(form, bg='#FFFFFF')
            cartella_frame.grid(row=3, column=1, sticky='ew', pady=6)  # Ridotto da 10 a 6
            cartella_frame.grid_columnconfigure(0, weight=1)
            
            cartella_entry = tk.Entry(cartella_frame, textvariable=cartella_var, font=entry_font, relief='solid', bd=1)
            cartella_entry.grid(row=0, column=0, sticky='ew', ipady=8, padx=(0, 8))
            cartella_entry.bind('<Button-1>', show_keyboard_for_field)
            cartella_entry.bind('<FocusOut>', hide_keyboard_when_unfocus)
            cartella_entry.bind('<FocusIn>', on_field_focus_in)
            
            def browse_directory():
                try:
                    directory = filedialog.askdirectory(
                        title="Seleziona cartella di trasferimento",
                        initialdir=cartella_var.get() if cartella_var.get() else None
                    )
                    if directory:
                        cartella_var.set(directory)
                except Exception as e:
                    print(f"[DEBUG] Errore browse directory: {e}")
                    
            browse_btn = tk.Button(cartella_frame, text='Sfoglia', font=('Segoe UI', 16), command=browse_directory,
                                 bg='#E0E0E0', fg='black', padx=16, pady=4)
            browse_btn.grid(row=0, column=1)

            # Pulsanti Salva/Annulla subito dopo i campi - elimina spazio bianco
            buttons_frame = tk.Frame(container, bg='#FFFFFF')
            buttons_frame.pack(fill='x', pady=(20, 0))  # Solo padding sopra, nessun side='bottom'

            def save_and_close():
                # Chiudi tastiera virtuale prima di salvare
                if self.tablet_mode and self.virtual_keyboard_enabled:
                    print("[DEBUG] Chiusura tastiera da pulsante Salva...")
                    self.hide_virtual_keyboard()
                    # Secondo tentativo dopo delay
                    self.root.after(300, lambda: self.hide_virtual_keyboard())
                    
                seat_code = sede_var.get().strip()
                shop_code = negozio_var.get().strip()
                transfer_time = ora_var.get().strip()
                transfer_folder = cartella_var.get().strip()
                
                # Validazione base
                if not seat_code or not shop_code:
                    messagebox.showerror("Errore", "I campi 'Codice Sede' e 'Codice Negozio' sono obbligatori.")
                    return
                
                # Salva configurazione
                if _save_codes(seat_code, shop_code, transfer_time, transfer_folder):
                    print(f"[CFG] Configurazione salvata: Sede={seat_code}, Negozio={shop_code}, Ora={transfer_time}")
                    messagebox.showinfo("Successo", "Configurazione salvata correttamente!")
                    safe_close()  # Usa chiusura sicura invece di win.destroy()
                else:
                    messagebox.showerror("Errore", "Errore durante il salvataggio della configurazione.")

            save_btn = tk.Button(buttons_frame, text='Salva', font=btn_font, command=save_and_close,
                               bg='#5FA8AF', fg='white', padx=self.s(24), pady=self.s(12))
            save_btn.pack(side='left', padx=(0, self.s(16)))
            
            # Pulsante Annulla al centro
            def cancel_action():
                print("[DEBUG] Annulla cliccato")
                # Chiudi tastiera virtuale prima di chiudere il dialog
                if self.tablet_mode and self.virtual_keyboard_enabled:
                    print("[DEBUG] Chiusura tastiera da pulsante Annulla...")
                    self.hide_virtual_keyboard()
                    # Secondo tentativo dopo delay
                    self.root.after(300, lambda: self.hide_virtual_keyboard())
                safe_close()  # Usa chiusura sicura invece di win.destroy()
                
            btn_cancel = tk.Button(buttons_frame, text='Annulla', font=btn_font, command=cancel_action,
                                 bg='#E0E0E0', fg='black', padx=self.s(20), pady=self.s(12))
            btn_cancel.pack(side='left', padx=(self.s(8), self.s(8)))
            
            def on_close_app_click():
                print("[DEBUG] Bottone 'Chiudi App' cliccato - avvio procedura chiusura")
                try:
                    self.open_confirm_close_from_settings(win)
                    print("[DEBUG] Procedura chiusura avviata con successo")
                except Exception as e:
                    print(f"[DEBUG] ERRORE nell'avvio procedura chiusura: {e}")
                    import traceback
                    print(f"[DEBUG] Traceback: {traceback.format_exc()}")

            close_btn = tk.Button(buttons_frame, text='🚪 Chiudi App', font=btn_font, 
                                command=on_close_app_click,
                                bg='#FF6B6B', fg='white', padx=self.s(20), pady=self.s(12))
            close_btn.pack(side='right', padx=(self.s(16), 0))

            # Mantieni la tastiera sempre sopra quando il dialog guadagna focus o cambia
            try:
                win.bind('<FocusIn>', lambda e: _ensure_keyboard_on_top())
                win.bind('<Map>', lambda e: _ensure_keyboard_on_top())
                win.bind('<Configure>', lambda e: _ensure_keyboard_on_top())
            except Exception:
                pass

            # **IMPORTANTE**: Riattiva il sistema quando il dialog si chiude
            def _on_dialog_close():
                nonlocal keyboard_timer_id
                print("[DEBUG] Re-enabling all buttons after dialog close...")
                
                # Cancella timer keyboard se attivo
                if keyboard_timer_id:
                    self.root.after_cancel(keyboard_timer_id)
                    keyboard_timer_id = None
                    print("[DEBUG] Timer tastiera cancellato")
                
                # Ferma il loop keep_on_top
                try:
                    if hasattr(win, '_stop_keep_on_top'):
                        win._stop_keep_on_top()
                    win.attributes('-topmost', False)  # Rimuovi topmost
                except:
                    pass
                # Chiudi la tastiera virtuale se aperta
                if self.tablet_mode and self.virtual_keyboard_enabled:
                    print("[DEBUG] Chiudendo tastiera virtuale automaticamente alla chiusura dialog...")
                    self.hide_virtual_keyboard()
                    # Aggiungi un secondo tentativo di chiusura dopo un breve delay
                    self.root.after(500, lambda: self.hide_virtual_keyboard())
                self._enable_all_buttons()

            # Gestione chiusura dialog migliorata
            def on_dialog_destroy():
                print("[DEBUG] Dialog chiuso con X - chiamando _on_dialog_close...")
                _on_dialog_close()
                
            def safe_close():
                """Chiude il dialog in modo sicuro fermando tutti i timer."""
                try:
                    _on_dialog_close()
                    win.destroy()
                except:
                    pass
                
            win.protocol("WM_DELETE_WINDOW", safe_close)

            print("[DEBUG] Dialog impostazioni originale pronto, aspettando interazione...")
            
            # OTTIMIZZAZIONE FINALE: Ridimensiona finestra al contenuto effettivo
            win.update_idletasks()  # Assicura che tutti i widget abbiano le dimensioni corrette
            
            # Calcola l'altezza minima necessaria
            actual_height = container.winfo_reqheight() + 80  # +80 per padding e decorazioni finestra
            
            # Ridimensiona la finestra eliminando spazio bianco inutile
            current_geom = win.geometry().split('+')
            width_height = current_geom[0].split('x')
            width = int(width_height[0])
            x_pos = int(current_geom[1]) 
            y_pos = int(current_geom[2])
            
            # Applica nuove dimensioni ottimizzate
            win.geometry(f"{width}x{actual_height}+{x_pos}+{y_pos}")
            print(f"[DEBUG] Finestra ridimensionata automaticamente: {width}x{actual_height}")
            
            # Focus al primo campo per facilitare l'uso
            win.after(200, lambda: sede_entry.focus_set())

            # **CRITICO**: Aspetta che l'utente interagisci con il dialog
            win.wait_window()
            
            print("[DEBUG] Dialog originale chiuso, sistema riabilitato!")
            
        except Exception as e:
            print(f"[UI] ERRORE CRITICO apertura impostazioni originale: {e}")
            import traceback
            print(f"[UI] TRACEBACK: {traceback.format_exc()}")
            # **IMPORTANTE**: Riattiva tutto anche in caso di errore
            print("[DEBUG] Re-enabling all buttons after settings error...")
            self._enable_all_buttons()            # Helpers lettura/scrittura config_negozio.ini
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
            # Allinea al wizard: tieni topmost per affidabilit? focus/tastiera
            try:
                win.attributes('-topmost', True)
            except Exception:
                pass
            win.transient(self.root)
            win.grab_set()

            # Stili (touch-friendly, pi? grandi per full-screen)
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
            # Binding per tastiera virtuale su tablet
            sede_entry.bind('<FocusIn>', self.on_entry_focus)
            sede_entry.bind('<FocusOut>', self.on_entry_unfocus)

            tk.Label(form, text='Codice Negozio', font=label_font, bg='#FFFFFF').grid(row=1, column=0, sticky='w', pady=(0, self.s(8)))
            negozio_var = tk.StringVar()
            negozio_entry = tk.Entry(form, textvariable=negozio_var, font=entry_font)
            negozio_entry.grid(row=1, column=1, sticky='ew', padx=(self.s(16), 0), pady=(0, self.s(12)), ipady=self.s(10))
            # Binding per tastiera virtuale su tablet
            negozio_entry.bind('<FocusIn>', self.on_entry_focus)
            negozio_entry.bind('<FocusOut>', self.on_entry_unfocus)

            # Ora trasferimento (HH:MM)
            tk.Label(form, text='Ora trasferimento (HH:MM)', font=label_font, bg='#FFFFFF').grid(row=2, column=0, sticky='w', pady=(0, self.s(8)))
            ora_var = tk.StringVar()
            ora_entry = tk.Entry(form, textvariable=ora_var, font=entry_font)
            ora_entry.grid(row=2, column=1, sticky='ew', padx=(self.s(16), 0), pady=(0, self.s(12)), ipady=self.s(10))
            # Binding per tastiera virtuale su tablet
            ora_entry.bind('<FocusIn>', self.on_entry_focus)
            ora_entry.bind('<FocusOut>', self.on_entry_unfocus)

            # Cartella trasferimento con Sfoglia
            tk.Label(form, text='Cartella trasferimento', font=label_font, bg='#FFFFFF').grid(row=3, column=0, sticky='w', pady=(0, self.s(8)))
            dir_var = tk.StringVar()
            dir_entry = tk.Entry(form, textvariable=dir_var, font=entry_font)
            dir_entry.grid(row=3, column=1, sticky='ew', padx=(self.s(16), 0), pady=(0, self.s(12)), ipady=self.s(10))
            # Binding per tastiera virtuale su tablet
            dir_entry.bind('<FocusIn>', self.on_entry_focus)
            dir_entry.bind('<FocusOut>', self.on_entry_unfocus)
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
                # Dialog modale touch-friendly in stile TIGOT?
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

                    # Tema TIGOT?
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

                    # Modalit?
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
                # Usa la nostra tastiera personalizzata
                try:
                    if hasattr(self, '_custom_keyboard'):
                        self._custom_keyboard.hide()
                        print("[KEYBOARD] Tastiera virtuale nascosta")
                except Exception as e:
                    print(f"[KEYBOARD] Errore chiusura tastiera: {e}")

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


            # Tastiera touch: usa logica del wizard + verifica visibilit? con fallback snello
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
                # Funzione semplificata - ora gestita da _show_touch_keyboard
                return True

            def _show_touch_keyboard(event=None):
                try:
                    if event is not None and getattr(event, 'widget', None) is not None:
                        try:
                            event.widget.focus_set()
                        except Exception:
                            pass
                    
                    # Usa la nostra tastiera COMPATTA
                    if not hasattr(self, '_custom_keyboard'):
                        from compact_keyboard import KeyboardManager
                        self._custom_keyboard = KeyboardManager(self.root)
                        print("[KEYBOARD] Tastiera virtuale COMPATTA inizializzata nelle impostazioni")
                    
                    # Mostra per il widget che ha scatenato l'evento o quello in focus
                    target_widget = None
                    if event and hasattr(event, 'widget'):
                        target_widget = event.widget
                    else:
                        target_widget = win.focus_get()
                    
                    if target_widget:
                        win.after(30, lambda: self._custom_keyboard.show(target_widget))
                        print("[KEYBOARD] Tastiera mostrata nelle impostazioni")
                        
                except Exception as e:
                    print(f"[KEYBOARD] Errore apertura tastiera nelle impostazioni: {e}")

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
            
            # **IMPORTANTE**: Riattiva il lettore NFC quando il dialog si chiude
            def _on_dialog_close():
                # **CRITICO**: Riabilita tutti i pulsanti quando il dialog si chiude
                print("[DEBUG] Re-enabling all buttons after dialog close...")
                self._enable_all_buttons()
                
                try:
                    if nfc_was_active and self.selected_action:
                        print("[DEBUG] Restarting NFC reader after settings closed...")
                        self.enable_nfc_reading()
                        print("[DEBUG] NFC reader restarted")
                except Exception as e:
                    print(f"[DEBUG] Error restarting NFC reader: {e}")
            
            # Aggiungi callback di chiusura al dialog
            original_destroy = win.destroy
            def enhanced_destroy():
                _on_dialog_close()
                original_destroy()
            win.destroy = enhanced_destroy
            
        except Exception as e:
            print(f"[UI] ERRORE CRITICO apertura impostazioni: {e}")
            import traceback
            print(f"[UI] TRACEBACK: {traceback.format_exc()}")
            # **IMPORTANTE**: Riattiva tutto anche in caso di errore
            print("[DEBUG] Re-enabling all buttons after settings error...")
            self._enable_all_buttons()
            
            # **IMPORTANTE**: Riattiva NFC anche in caso di errore
            try:
                if nfc_was_active and self.selected_action:
                    print("[DEBUG] Restarting NFC reader after settings error...")
                    self.enable_nfc_reading()
            except Exception:
                pass

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
                return True  # Non ? errore

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
                        # Se l'orario odierno ? appena passato (entro 60s), esegui tra 5s; altrimenti programma domani
                        from datetime import timedelta
                        if (now - run_at).total_seconds() <= 60:
                            run_at = now + timedelta(seconds=5)
                        else:
                            run_at = run_at + timedelta(days=1)
                    wait_s = max(1, int((run_at - now).total_seconds()))
                    
                    # SICUREZZA: Limita attesa massima a 1 ora
                    MAX_WAIT_SECONDS = 3600  # 1 ora
                    if wait_s > MAX_WAIT_SECONDS:
                        wait_s = MAX_WAIT_SECONDS
                        print(f"[TRANSFER] Attesa limitata a {MAX_WAIT_SECONDS}s per sicurezza")
                        
                    print(f"[TRANSFER] Scheduler prossimo run alle {run_at.strftime('%Y-%m-%d %H:%M:%S')} (tra {wait_s}s)")
                    
                    # Attendi in porzioni per permettere stop rapido
                    step = 10  # Aumentato da 5 a 10 per ridurre overhead
                    waited = 0
                    while waited < wait_s and not self._transfer_stop.is_set():
                        chunk = min(step, wait_s - waited)
                        time.sleep(chunk)
                        waited += chunk
                        
                        # Log periodico per debugging (ogni 5 minuti)
                        if waited % 300 == 0 and waited > 0:
                            remaining = wait_s - waited
                            print(f"[TRANSFER] Attesa in corso: {remaining}s rimanenti")
                            
                    if self._transfer_stop.is_set():
                        print("[TRANSFER] Scheduler fermato manualmente")
                        break
                    # Esegui export
                    print(f"[TRANSFER] Scheduler avvio export alle {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    try:
                        self.export_pending_timbrature_to_txt()
                        print("[TRANSFER] Export completato con successo")
                    except Exception as export_error:
                        print(f"[TRANSFER] Errore durante export: {export_error}")
                    # poi loop per il prossimo giorno
                except Exception as e:
                    print(f"[TRANSFER] Scheduler errore: {e}")
                    import traceback
                    print(f"[TRANSFER] Traceback: {traceback.format_exc()}")
                    time.sleep(60)  # Attendi 1 minuto invece di 30s per ridurre spam di errori

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
        CLOCK_TOP_PADDING_RATIO = 0.001
        CLOCK_BOTTOM_PADDING_RATIO = 0.0005  # ridotto per meno bianco sotto
        TIME_FONT_SIZE_RATIO = 0.20
        DATE_FONT_SIZE_RATIO = 0.038
        DATE_TOP_PADDING_RATIO = 0.0005  # ridotto
        
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
        """Crea i selettori Ingresso/Uscita con istruzioni sotto (mutualmente esclusivi), pi? centrati e con meno spazio sotto."""
        BUTTONS_TOP_PADDING_RATIO = 0.0005  # drasticamente ridotto per avvicinare alla data
        BUTTONS_BOTTOM_PADDING_RATIO = 0.003  # ulteriormente ridotto per i selettori ingranditi
        BUTTON_SPACING_RATIO = 0.08
        INSTRUCTIONS_TOP_PADDING_RATIO = 0.002  # ulteriormente ridotto per i selettori ingranditi
        INSTRUCTIONS_COLOR = '#5FA8AF'
        
        buttons_wrapper = tk.Frame(parent, bg='#FFFFFF')
        buttons_wrapper.pack(pady=(
            int(self.vh * BUTTONS_TOP_PADDING_RATIO), 
            int(self.vh * BUTTONS_BOTTOM_PADDING_RATIO)
        ))
        
        buttons_row = tk.Frame(buttons_wrapper, bg='#FFFFFF')
        buttons_row.pack()
        
        def select_ingresso():
            # Controlla se i pulsanti sono disabilitati
            if getattr(self, '_buttons_disabled', False):
                print("[DEBUG] Click su Ingresso ignorato - pulsanti disabilitati")
                return
                
            self.selected_action = 'in'
            
            # PRIMA deseleziona l'altro pulsante (se esiste)
            if hasattr(self, 'btn_uscita') and self.btn_uscita:
                self.btn_uscita['set_selected'](False)
            
            # POI cancella le particelle da entrambi per sicurezza
            if hasattr(self, 'btn_ingresso') and hasattr(self.btn_ingresso, 'clear_particles'):
                self.btn_ingresso['clear_particles']()
            if hasattr(self, 'btn_uscita') and hasattr(self.btn_uscita, 'clear_particles'):
                self.btn_uscita['clear_particles']()
                
            # INFINE seleziona il pulsante corrente  
            if hasattr(self, 'btn_ingresso') and self.btn_ingresso:
                self.btn_ingresso['set_selected'](True)
                
            print('[UI] Selezionato: Ingresso')
            # Aggiorna messaggio dinamico
            if hasattr(self, 'selection_hint_var'):
                self.selection_hint_var.set('HAI SELEZIONATO INGRESSO — ORA PUOI AVVICINARE IL BADGE AL LETTORE')
            if hasattr(self, 'selection_hint_label'):
                self.selection_hint_label.config(fg='#20B2AA')
            # Abilita lettura NFC
            try:
                self.enable_nfc_reading()
            except Exception as e:
                print(f"[NFC] Errore attivazione lettura: {e}")
            
            # Debug icona impostazioni dopo selezione (opzionale, sicuro)
            try:
                if hasattr(self, 'debug_settings_icon'):
                    self.debug_settings_icon()
            except Exception:
                pass
        
        def select_uscita():
            # Controlla se i pulsanti sono disabilitati
            if getattr(self, '_buttons_disabled', False):
                print("[DEBUG] Click su Uscita ignorato - pulsanti disabilitati")
                return
                
            self.selected_action = 'out'
            
            # PRIMA deseleziona l'altro pulsante (se esiste)
            if hasattr(self, 'btn_ingresso') and self.btn_ingresso:
                self.btn_ingresso['set_selected'](False)
            
            # POI cancella le particelle da entrambi per sicurezza
            if hasattr(self, 'btn_ingresso') and hasattr(self.btn_ingresso, 'clear_particles'):
                self.btn_ingresso['clear_particles']()
            if hasattr(self, 'btn_uscita') and hasattr(self.btn_uscita, 'clear_particles'):
                self.btn_uscita['clear_particles']()
                
            # INFINE seleziona il pulsante corrente
            if hasattr(self, 'btn_uscita') and self.btn_uscita:
                self.btn_uscita['set_selected'](True)
                
            print('[UI] Selezionato: Uscita')
            # Aggiorna messaggio dinamico
            if hasattr(self, 'selection_hint_var'):
                self.selection_hint_var.set('HAI SELEZIONATO USCITA — ORA PUOI AVVICINARE IL BADGE AL LETTORE')
            if hasattr(self, 'selection_hint_label'):
                self.selection_hint_label.config(fg='#20B2AA')
            # Abilita lettura NFC
            try:
                self.enable_nfc_reading()
            except Exception as e:
                print(f"[NFC] Errore attivazione lettura: {e}")
            
            # Debug icona impostazioni dopo selezione (opzionale, sicuro)
            try:
                if hasattr(self, 'debug_settings_icon'):
                    self.debug_settings_icon()
            except Exception:
                pass
            
        # Percorsi delle icone
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_ingresso_path = os.path.join(base_dir, 'Immagini', 'ENTRATA.png')
        icon_uscita_path = os.path.join(base_dir, 'Immagini', 'USCITA.png')
        
        # Crea bottoni con sole icone del sapone
        self.btn_ingresso = self.create_icon_only_button(
            buttons_row,
            icon_ingresso_path,
            select_ingresso
        )
        self.btn_ingresso['border_frame'].pack(side='left')
        
        spacer = tk.Frame(
            buttons_row, 
            width=int(self.vw * BUTTON_SPACING_RATIO), 
            bg='#FFFFFF'
        )
        spacer.pack(side='left')
        
        self.btn_uscita = self.create_icon_only_button(
            buttons_row,
            icon_uscita_path,
            select_uscita
        )
        self.btn_uscita['border_frame'].pack(side='left')
        
        self.btn_ingresso['set_selected'](False)
        self.btn_uscita['set_selected'](False)
        self.selected_action = None
        
        instructions_wrapper = tk.Frame(buttons_wrapper, bg='#FFFFFF')
        instructions_wrapper.pack(pady=(int(self.vh * INSTRUCTIONS_TOP_PADDING_RATIO), 0))
        
        instr_font = max(self.s(14), int(self.vh * 0.025))  # Font leggermente pi? grande per unica riga
        
        # UNICA RIGA DINAMICA - Cambia in base allo stato di selezione
        self.dynamic_instructions_var = tk.StringVar(value='SELEZIONA INGRESSO/USCITA E AVVICINA IL BADGE AL LETTORE')
        self.dynamic_instructions_label = tk.Label(
            instructions_wrapper,
            textvariable=self.dynamic_instructions_var,
            font=('Segoe UI', instr_font, 'bold'),
            bg='#FFFFFF',
            fg=INSTRUCTIONS_COLOR
        )
        self.dynamic_instructions_label.pack()

        # Rimuovo le vecchie variabili - ora uso solo quella dinamica
        self.selection_hint_var = self.dynamic_instructions_var  # Compatibilit?
        self.selection_hint_label = self.dynamic_instructions_label  # Compatibilit?
        
        # Icona impostazioni in alto a destra

    def create_nfc_indicator(self, parent):
        """Crea indicatore NFC in basso a destra; solo logo (senza testo), posizionamento assoluto."""
        # Container posizionato assolutamente in basso a destra
        nfc_container = tk.Frame(parent, bg='#FFFFFF')
        
        # Logo NFC ingrandito per maggiore visibilità 
        icon_size = max(self.s(160), int(self.vh * 0.18))

        # Prova a caricare un logo NFC dalla cartella immagini; se non trovato, fallback all'icona disegnata
        self.nfc_photo = None
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 1) Priorit?: percorso specificato dall'utente
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
                # Preferisci Pillow per qualit? e per supporto JPEG
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
        
        # Posiziona il container in modo assoluto in basso a destra

    def debug_settings_icon(self):
        """Placeholder per debug dell'icona impostazioni, evita AttributeError se invocato."""
        try:
            print("[DEBUG] debug_settings_icon() chiamato")
        except Exception:
            pass
    # Nessuna azione per ora; qui potremmo verificare/ricreare l'icona impostazioni

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
            
            date_str = f"{giorno_settimana} {now.day} {mese} {now.year}".upper()
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
            # Verifica se il badge ? abbinato ad un dipendente
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
                            self.selection_hint_var.set("SELEZIONA PRIMA INGRESSO O USCITA, POI AVVICINA IL BADGE")
                            if hasattr(self, 'selection_hint_label') and self.selection_hint_label is not None:
                                self.selection_hint_label.config(fg='#EF4444')
                            self._show_tigota_toast('warning', 'SELEZIONA INGRESSO O USCITA')
                            try:
                                winsound.Beep(440, 220)
                            except Exception:
                                try:
                                    winsound.MessageBeep(winsound.MB_ICONHAND)
                                except Exception:
                                    pass
                            return

                        if is_known:
                            azione = 'Ingresso' if self.selected_action == 'in' else ('Uscita' if self.selected_action == 'out' else '?')
                            nominativo = (dip_nome or '').strip()
                            if dip_cognome:
                                nominativo = f"{nominativo} {dip_cognome.strip()}".strip()
                            msg = f"{('Ciao ' + nominativo + ' ? ') if nominativo else ''}Badge: {badge_id} ? {azione} registrata"
                            self.selection_hint_var.set(msg)
                            if hasattr(self, 'selection_hint_label') and self.selection_hint_label is not None:
                                self.selection_hint_label.config(fg='#20B2AA')  # Colore uniforme per entrambi
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
                            # Toast stile TIGOT? (success)
                            display_name = nominativo if nominativo else None
                            self._show_tigota_toast('success', f"{azione} registrata", name=display_name)
                            # CANCELLA PARTICELLE DOPO TIMBRATURA RIUSCITA
                            if hasattr(self, 'btn_ingresso') and hasattr(self.btn_ingresso, 'clear_particles'):
                                self.btn_ingresso['clear_particles']()
                            if hasattr(self, 'btn_uscita') and hasattr(self.btn_uscita, 'clear_particles'):
                                self.btn_uscita['clear_particles']()
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
                            # Toast stile TIGOT? (errore)
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
        """Mostra un toast stile TIGOT? (borderless, topmost), ancora pi? grande, con saluto opzionale e bordo Uscita."""
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
        tk.Label(header, text='TIGOT?', font=('Segoe UI', s(34), 'bold'), fg=fg, bg=header_bg, padx=s(28), pady=s(16)).pack(anchor='w')

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
                self.selection_hint_var.set('SELEZIONA INGRESSO/USCITA E AVVICINA IL BADGE AL LETTORE')
            if hasattr(self, 'selection_hint_label') and self.selection_hint_label is not None:
                self.selection_hint_label.config(fg='#5FA8AF')
        except Exception:
            pass

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("TIGOT? Elite - Sistema Timbratura")
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

    print("? TIGOT? Elite Dashboard full-screen pronto per tablet 8\"")
    root.mainloop()



