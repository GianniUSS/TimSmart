#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility per creare elementi grafici TIGOTA
Gestisce loghi, icone e elementi decorativi
"""

import tkinter as tk
from tkinter import Canvas
from config import COLORS

class TigotaGraphics:
    @staticmethod
    def create_tigota_logo(parent, width=400, height=120):
        """Crea il logo TIGOTA su Canvas"""
        canvas = Canvas(parent, width=width, height=height, 
                       bg=COLORS['card_bg'], highlightthickness=0)
        
        # Sfondo gradiente simulato
        for i in range(height):
            color_ratio = i / height
            # Gradiente da bianco a rosa molto chiaro
            r = int(255 - (255 - 252) * color_ratio)
            g = int(255 - (255 - 228) * color_ratio) 
            b = int(255 - (255 - 236) * color_ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color, width=1)
        
        # Testo TIGOTÀ stilizzato
        canvas.create_text(width//2, height//2 - 15, 
                          text="TIGOTÀ", 
                          font=('Segoe UI', 36, 'bold'),
                          fill=COLORS['tigota_pink'])
        
        # Sottotitolo
        canvas.create_text(width//2, height//2 + 20, 
                          text="Belli, Puliti, Profumati", 
                          font=('Segoe UI', 12, 'italic'),
                          fill=COLORS['text'])
        
        # Decorazione rosa
        canvas.create_rectangle(20, height-8, width-20, height-4, 
                               fill=COLORS['tigota_pink'], outline="")
        
        return canvas
    
    @staticmethod
    def create_nfc_icon(parent, size=80):
        """Crea icona NFC personalizzata"""
        canvas = Canvas(parent, width=size, height=size, 
                       bg=COLORS['card_bg'], highlightthickness=0)
        
        # Cerchio di sfondo
        margin = 10
        canvas.create_oval(margin, margin, size-margin, size-margin, 
                          fill=COLORS['tigota_light'], outline=COLORS['tigota_pink'], width=3)
        
        # Simbolo NFC stilizzato
        center = size // 2
        # Linee curve per simboleggiare le onde NFC
        canvas.create_arc(center-15, center-15, center+15, center+15, 
                         start=45, extent=90, outline=COLORS['tigota_pink'], width=4)
        canvas.create_arc(center-25, center-25, center+25, center+25, 
                         start=45, extent=90, outline=COLORS['tigota_pink'], width=3)
        canvas.create_arc(center-35, center-35, center+35, center+35, 
                         start=45, extent=90, outline=COLORS['tigota_pink'], width=2)
        
        # Punto centrale
        canvas.create_oval(center-3, center-3, center+3, center+3, 
                          fill=COLORS['tigota_pink'], outline="")
        
        return canvas
    
    @staticmethod
    def create_status_indicator(parent, status="active", size=20):
        """Crea indicatore di stato colorato"""
        canvas = Canvas(parent, width=size*3, height=size, 
                       bg=COLORS['card_bg'], highlightthickness=0)
        
        # Colore basato sullo status
        colors = {
            'active': COLORS['success'],
            'reading': COLORS['warning'], 
            'error': COLORS['error'],
            'tigota': COLORS['tigota_pink']
        }
        
        color = colors.get(status, COLORS['success'])
        
        # Cerchio indicatore
        canvas.create_oval(2, 2, size-2, size-2, 
                          fill=color, outline="")
        
        # Testo status
        text_map = {
            'active': 'ATTIVO',
            'reading': 'LETTURA',
            'error': 'ERRORE',
            'tigota': 'TIGOTÀ'
        }
        
        text = text_map.get(status, 'SYSTEM')
        canvas.create_text(size + 10, size//2, 
                          text=text, anchor='w',
                          font=('Segoe UI', 10, 'bold'),
                          fill=color)
        
        return canvas
    
    @staticmethod
    def create_decorative_border(parent, width, color=None):
        """Crea bordo decorativo TIGOTA"""
        if color is None:
            color = COLORS['tigota_pink']
            
        canvas = Canvas(parent, width=width, height=6, 
                       bg=COLORS['background'], highlightthickness=0)
        
        # Gradiente orizzontale
        sections = 50
        for i in range(sections):
            x1 = (width * i) // sections
            x2 = (width * (i + 1)) // sections
            
            # Fade effect
            alpha = abs(i - sections//2) / (sections//2)
            
            # Simula trasparenza variando il colore verso il bianco
            if color == COLORS['tigota_pink']:
                # Da rosa TIGOTA a rosa chiaro
                base_color = (233, 30, 99)  # #E91E63
                white = (255, 255, 255)
                
                r = int(base_color[0] + (white[0] - base_color[0]) * alpha * 0.7)
                g = int(base_color[1] + (white[1] - base_color[1]) * alpha * 0.7)
                b = int(base_color[2] + (white[2] - base_color[2]) * alpha * 0.7)
                
                section_color = f"#{r:02x}{g:02x}{b:02x}"
            else:
                section_color = color
            
            canvas.create_rectangle(x1, 1, x2, 5, 
                                   fill=section_color, outline="")
        
        return canvas
