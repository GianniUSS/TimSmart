#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componenti Grafici TIGOTÀ per Tablet Touch
Design moderno con elementi touch-friendly
"""

import tkinter as tk
from tkinter import Canvas
import math
import time
from config_tablet import COLORS, TABLET_CONFIG

class TigotaTabletGraphics:
    
    @staticmethod
    def create_modern_card(parent, width, height, bg_color=None, elevation=None):
        """Crea una card moderna con ombra"""
        if bg_color is None:
            bg_color = COLORS['card_bg']
        if elevation is None:
            elevation = TABLET_CONFIG['card_elevation']
            
        # Container per ombra
        shadow_frame = tk.Frame(parent, bg=COLORS['shadow'])
        
        # Card principale
        card_frame = tk.Frame(shadow_frame, bg=bg_color, 
                             width=width, height=height)
        card_frame.pack(padx=elevation//2, pady=elevation//2)
        card_frame.pack_propagate(False)
        
        return shadow_frame, card_frame
    
    @staticmethod
    def create_tigota_logo_modern(parent, width=600, height=120):
        """Crea logo TIGOTÀ moderno per tablet"""
        canvas = Canvas(parent, width=width, height=height, 
                       bg=COLORS['background'], highlightthickness=0)
        
        # Sfondo con gradiente
        TigotaTabletGraphics._draw_gradient(canvas, 0, 0, width, height,
                                          COLORS['tigota_light'], COLORS['background'])
        
        # Cerchio decorativo di sfondo
        circle_size = height - 20
        circle_x = width // 2
        circle_y = height // 2
        
        # Cerchi concentrici per effetto depth
        for i in range(3):
            radius = circle_size // 2 - (i * 8)
            alpha = 0.1 + (i * 0.05)
            color = TigotaTabletGraphics._blend_colors(COLORS['tigota_pink'], 
                                                     COLORS['background'], alpha)
            
            canvas.create_oval(circle_x - radius, circle_y - radius,
                             circle_x + radius, circle_y + radius,
                             fill=color, outline="")
        
        # Testo TIGOTÀ principale
        canvas.create_text(width//2, height//2 - 10,
                          text="TIGOTÀ",
                          font=('Segoe UI', 42, 'bold'),
                          fill=COLORS['tigota_pink'],
                          anchor='center')
        
        # Sottotitolo elegante
        canvas.create_text(width//2, height//2 + 25,
                          text="Timbratura Dipendenti",
                          font=('Segoe UI', 14, 'normal'),
                          fill=COLORS['text_light'],
                          anchor='center')
        
        return canvas
    
    @staticmethod
    def create_nfc_zone_modern(parent, size=200):
        """Crea zona NFC moderna e touch-friendly"""
        canvas = Canvas(parent, width=size, height=size,
                       bg=COLORS['background'], highlightthickness=0)
        
        center = size // 2
        
        # Zona touch circolare con gradiente
        for i in range(30):
            radius = center - 20 - i
            if radius <= 0:
                break
                
            alpha = 1.0 - (i / 30.0)
            color = TigotaTabletGraphics._blend_colors(COLORS['tigota_light'],
                                                     COLORS['background'], alpha)
            
            canvas.create_oval(center - radius, center - radius,
                             center + radius, center + radius,
                             fill=color, outline="")
        
        # Bordo principale
        canvas.create_oval(center - (center - 20), center - (center - 20),
                         center + (center - 20), center + (center - 20),
                         outline=COLORS['tigota_pink'], width=4, fill="")
        
        # Icona NFC stilizzata
        TigotaTabletGraphics._draw_nfc_waves(canvas, center, center, 40)
        
        # Punto centrale
        canvas.create_oval(center - 8, center - 8, center + 8, center + 8,
                          fill=COLORS['tigota_pink'], outline="")
        
        return canvas
    
    @staticmethod
    def _draw_nfc_waves(canvas, x, y, max_radius):
        """Disegna onde NFC stilizzate"""
        for i in range(4):
            radius = max_radius - (i * 10)
            start_angle = 45 + (i * 5)
            extent = 90 - (i * 10)
            
            canvas.create_arc(x - radius, y - radius, x + radius, y + radius,
                            start=start_angle, extent=extent,
                            outline=COLORS['tigota_pink'], 
                            width=3 - (i * 0.5), style='arc')
    
    @staticmethod
    def create_touch_button(parent, text, command=None, bg_color=None, width=200, height=60):
        """Crea pulsante touch-friendly"""
        if bg_color is None:
            bg_color = COLORS['tigota_pink']
        
        # Container per effetto hover
        button_container = tk.Frame(parent, bg=COLORS['background'])
        
        # Pulsante principale
        button = tk.Button(button_container, text=text, command=command,
                          bg=bg_color, fg=COLORS['background'],
                          font=('Segoe UI', 16, 'bold'),
                          width=width//10, height=height//20,
                          relief='flat', bd=0,
                          activebackground=COLORS['button_hover'],
                          activeforeground=COLORS['background'])
        button.pack(padx=5, pady=5)
        
        return button_container, button
    
    @staticmethod
    def create_status_indicator_modern(parent, status="active", size=40):
        """Crea indicatore di stato moderno"""
        canvas = Canvas(parent, width=size*4, height=size,
                       bg=COLORS['background'], highlightthickness=0)
        
        # Colori per stati
        status_colors = {
            'active': COLORS['nfc_active'],
            'reading': COLORS['warning'],
            'error': COLORS['error'],
            'standby': COLORS['text_light']
        }
        
        color = status_colors.get(status, COLORS['nfc_active'])
        
        # Cerchio principale con glow effect
        for i in range(5):
            radius = (size // 2) - (i * 2)
            alpha = 1.0 - (i * 0.15)
            glow_color = TigotaTabletGraphics._blend_colors(color, COLORS['background'], alpha)
            
            canvas.create_oval(size//2 - radius, size//2 - radius,
                             size//2 + radius, size//2 + radius,
                             fill=glow_color, outline="")
        
        # Testo stato
        status_text = {
            'active': 'ATTIVO',
            'reading': 'LETTURA',
            'error': 'ERRORE',
            'standby': 'STANDBY'
        }
        
        text = status_text.get(status, 'SISTEMA')
        canvas.create_text(size + 20, size//2, text=text,
                          font=('Segoe UI', 12, 'bold'),
                          fill=color, anchor='w')
        
        return canvas
    
    @staticmethod
    def create_feedback_popup(parent, movement_type, badge_id, timestamp):
        """Crea popup di feedback per timbratura"""
        popup_width = 400
        popup_height = 300
        
        # Overlay semi-trasparente
        overlay = tk.Toplevel(parent)
        overlay.attributes('-topmost', True)
        overlay.overrideredirect(True)
        overlay.configure(bg=COLORS['shadow'])
        
        # Centra popup
        screen_width = overlay.winfo_screenwidth()
        screen_height = overlay.winfo_screenheight()
        x = (screen_width - popup_width) // 2
        y = (screen_height - popup_height) // 2
        overlay.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        
        # Card popup
        shadow_frame, card_frame = TigotaTabletGraphics.create_modern_card(
            overlay, popup_width-20, popup_height-20, COLORS['card_bg'], 10)
        shadow_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Contenuto popup
        content_frame = tk.Frame(card_frame, bg=COLORS['card_bg'])
        content_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
        # Icona movimento
        icon_text = "✅ 🚪➡️" if movement_type == "ENTRATA" else "✅ 🚪⬅️"
        icon_color = COLORS['success'] if movement_type == "ENTRATA" else COLORS['warning']
        
        icon_label = tk.Label(content_frame, text=icon_text,
                             font=('Segoe UI Emoji', 32, 'normal'),
                             bg=COLORS['card_bg'], fg=icon_color)
        icon_label.pack(pady=(0, 20))
        
        # Tipo movimento
        movement_label = tk.Label(content_frame, text=movement_type,
                                 font=('Segoe UI', 24, 'bold'),
                                 bg=COLORS['card_bg'], fg=icon_color)
        movement_label.pack(pady=(0, 10))
        
        # Badge ID
        badge_label = tk.Label(content_frame, text=f"Badge: {badge_id}",
                              font=('Segoe UI', 16, 'normal'),
                              bg=COLORS['card_bg'], fg=COLORS['text'])
        badge_label.pack(pady=(0, 10))
        
        # Timestamp
        time_label = tk.Label(content_frame, text=timestamp,
                             font=('Consolas', 14, 'normal'),
                             bg=COLORS['card_bg'], fg=COLORS['text_light'])
        time_label.pack(pady=(0, 20))
        
        # Messaggio successo
        success_label = tk.Label(content_frame, text="Timbratura registrata con successo!",
                                font=('Segoe UI', 14, 'normal'),
                                bg=COLORS['card_bg'], fg=COLORS['success'])
        success_label.pack()
        
        return overlay
    
    @staticmethod
    def _draw_gradient(canvas, x1, y1, x2, y2, color1, color2, steps=50):
        """Disegna gradiente su canvas"""
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        width = x2 - x1
        height = y2 - y1
        
        for i in range(steps):
            ratio = i / (steps - 1)
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Linee orizzontali per gradiente verticale
            y = y1 + (height * i) // steps
            next_y = y1 + (height * (i + 1)) // steps
            
            canvas.create_rectangle(x1, y, x2, next_y, fill=color, outline="")
    
    @staticmethod
    def _blend_colors(color1, color2, alpha):
        """Miscela due colori con alpha"""
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        r = int(rgb1[0] * alpha + rgb2[0] * (1 - alpha))
        g = int(rgb1[1] * alpha + rgb2[1] * (1 - alpha))
        b = int(rgb1[2] * alpha + rgb2[2] * (1 - alpha))
        
        return f"#{r:02x}{g:02x}{b:02x}"
