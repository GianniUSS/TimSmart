#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selettore Temi per SmartTIM
Permette di scegliere tra diversi temi grafici
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from temi_alternativi import LIGHT_COLORS, DARK_GAMING_COLORS, PASTEL_COLORS

class ThemeSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SmartTIM - Selettore Temi")
        self.root.geometry("600x500")
        self.root.configure(bg='#2C3E50')
        
        # Temi disponibili
        self.themes = {
            "Scuro Moderno": {
                'background': '#1E1E2E',
                'primary': '#313244',
                'secondary': '#45475A',
                'accent': '#89B4FA',
                'text': '#CDD6F4',
                'highlight': '#A6E3A1',
                'card_bg': '#585B70',
                'border': '#74C7EC',
                'success': '#A6E3A1',
                'warning': '#F9E2AF',
                'error': '#F38BA8',
                'gradient_start': '#89B4FA',
                'gradient_end': '#CBA6F7'
            },
            "Chiaro Moderno": LIGHT_COLORS,
            "Gaming Scuro": DARK_GAMING_COLORS,
            "Pastello Elegante": PASTEL_COLORS
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura l'interfaccia del selettore"""
        # Titolo
        title_label = tk.Label(self.root, 
                              text="🎨 Selettore Temi SmartTIM",
                              font=('Segoe UI', 20, 'bold'),
                              bg='#2C3E50', fg='white')
        title_label.pack(pady=20)
        
        # Frame principale
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Lista temi
        self.create_theme_list(main_frame)
        
        # Anteprima
        self.create_preview(main_frame)
        
        # Pulsanti
        self.create_buttons(main_frame)
        
    def create_theme_list(self, parent):
        """Crea la lista dei temi"""
        list_frame = tk.LabelFrame(parent, text="Temi Disponibili",
                                  bg='#34495E', fg='white',
                                  font=('Segoe UI', 12, 'bold'))
        list_frame.pack(fill='x', pady=10)
        
        # Listbox per temi
        self.theme_listbox = tk.Listbox(list_frame,
                                       bg='#34495E', fg='white',
                                       selectbackground='#3498DB',
                                       font=('Segoe UI', 11),
                                       height=4)
        self.theme_listbox.pack(fill='x', padx=10, pady=10)
        
        # Popola lista
        for theme_name in self.themes.keys():
            self.theme_listbox.insert(tk.END, theme_name)
            
        # Seleziona primo tema
        self.theme_listbox.selection_set(0)
        self.theme_listbox.bind('<<ListboxSelect>>', self.on_theme_select)
        
    def create_preview(self, parent):
        """Crea l'anteprima del tema"""
        preview_frame = tk.LabelFrame(parent, text="Anteprima",
                                     bg='#34495E', fg='white',
                                     font=('Segoe UI', 12, 'bold'))
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        # Canvas per anteprima
        self.preview_canvas = tk.Canvas(preview_frame, height=200,
                                       bg='white', highlightthickness=0)
        self.preview_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Mostra anteprima iniziale
        self.update_preview()
        
    def create_buttons(self, parent):
        """Crea i pulsanti di controllo"""
        button_frame = tk.Frame(parent, bg='#2C3E50')
        button_frame.pack(fill='x', pady=10)
        
        # Pulsante applica
        apply_btn = tk.Button(button_frame, text="✅ Applica Tema",
                             font=('Segoe UI', 12, 'bold'),
                             bg='#27AE60', fg='white',
                             command=self.apply_theme,
                             relief='flat', padx=20, pady=10)
        apply_btn.pack(side='left', padx=5)
        
        # Pulsante test
        test_btn = tk.Button(button_frame, text="🔍 Test App",
                            font=('Segoe UI', 12, 'bold'),
                            bg='#3498DB', fg='white',
                            command=self.test_app,
                            relief='flat', padx=20, pady=10)
        test_btn.pack(side='left', padx=5)
        
        # Pulsante chiudi
        close_btn = tk.Button(button_frame, text="❌ Chiudi",
                             font=('Segoe UI', 12, 'bold'),
                             bg='#E74C3C', fg='white',
                             command=self.root.destroy,
                             relief='flat', padx=20, pady=10)
        close_btn.pack(side='right', padx=5)
        
    def on_theme_select(self, event=None):
        """Gestisce la selezione di un tema"""
        self.update_preview()
        
    def update_preview(self):
        """Aggiorna l'anteprima del tema"""
        selection = self.theme_listbox.curselection()
        if not selection:
            return
            
        theme_name = self.theme_listbox.get(selection[0])
        theme_colors = self.themes[theme_name]
        
        # Pulisci canvas
        self.preview_canvas.delete("all")
        
        # Disegna anteprima
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas non ancora renderizzato
            self.root.after(100, self.update_preview)
            return
            
        # Sfondo
        self.preview_canvas.create_rectangle(0, 0, canvas_width, canvas_height,
                                           fill=theme_colors['background'],
                                           outline="")
        
        # Header simulato
        self.preview_canvas.create_rectangle(20, 20, canvas_width-20, 60,
                                           fill=theme_colors['primary'],
                                           outline=theme_colors['border'])
        self.preview_canvas.create_text(canvas_width//2, 40,
                                       text="🏢 LOGO CLIENTE",
                                       fill=theme_colors['text'],
                                       font=('Segoe UI', 12, 'bold'))
        
        # Area centrale
        self.preview_canvas.create_rectangle(50, 80, canvas_width-50, 140,
                                           fill=theme_colors['card_bg'],
                                           outline=theme_colors['border'])
        self.preview_canvas.create_text(canvas_width//2, 100,
                                       text="Mercoledì, 7 Agosto 2024",
                                       fill=theme_colors['text'],
                                       font=('Segoe UI', 10))
        self.preview_canvas.create_text(canvas_width//2, 120,
                                       text="14:30:25",
                                       fill=theme_colors['accent'],
                                       font=('Segoe UI', 16, 'bold'))
        
        # Area NFC
        self.preview_canvas.create_rectangle(canvas_width-120, 150, canvas_width-20, 180,
                                           fill=theme_colors['secondary'],
                                           outline=theme_colors['border'])
        self.preview_canvas.create_text(canvas_width-70, 165,
                                       text="📡 NFC Ready",
                                       fill=theme_colors['success'],
                                       font=('Segoe UI', 9))
        
    def apply_theme(self):
        """Applica il tema selezionato"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un tema!")
            return
            
        theme_name = self.theme_listbox.get(selection[0])
        theme_colors = self.themes[theme_name]
        
        try:
            # Leggi config attuale
            with open('config.py', 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Trova e sostituisci la sezione COLORS
            import re
            pattern = r'COLORS = \{[^}]+\}'
            
            new_colors = "COLORS = {\n"
            for key, value in theme_colors.items():
                new_colors += f"    '{key}': '{value}',\n"
            new_colors = new_colors.rstrip(',\n') + "\n}"
            
            new_content = re.sub(pattern, new_colors, config_content, flags=re.DOTALL)
            
            # Salva nuovo config
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            messagebox.showinfo("Successo", 
                               f"Tema '{theme_name}' applicato con successo!\n"
                               "Riavvia l'app per vedere le modifiche.")
                               
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'applicazione del tema: {e}")
            
    def test_app(self):
        """Avvia l'app per testare il tema"""
        try:
            import subprocess
            import sys
            
            # Avvia l'app in background
            subprocess.Popen([sys.executable, 'app_modern_timbratura.py'])
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nell'avvio dell'app: {e}")

def main():
    """Avvia il selettore temi"""
    try:
        app = ThemeSelector()
        app.root.mainloop()
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
