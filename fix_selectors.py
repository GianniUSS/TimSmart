#!/usr/bin/env python3
"""
Script per sostituire gli emoji dei selettori con le immagini ENTRATA.png e USCITA.png
"""

import os
import re

def update_selectors():
    """Aggiorna i selettori con le nuove immagini"""
    
    # Leggi il file
    with open('tigota_elite_dashboard.py', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Pattern per il primo emoji (ENTRATA)
    pattern1 = r"""            porta_label = tk\.Label\(icon_frame,
                                 text='[^']*',
                                 font=\('Segoe UI Emoji', 26\),
                                 bg=config\['bg_color'\],
                                 fg=config\['icon_color'\]\)
            porta_label\.pack\(side='left', padx=\(0,6\)\)"""
    
    # Sostituzione per ENTRATA
    replacement1 = """            # Carica immagine ENTRATA
            try:
                entrata_path = os.path.join(self.base_path, "immagini", "ENTRATA.png")
                if os.path.exists(entrata_path):
                    from PIL import Image, ImageTk
                    entrata_img = Image.open(entrata_path)
                    entrata_img = entrata_img.resize((40, 40), Image.Resampling.LANCZOS)
                    entrata_photo = ImageTk.PhotoImage(entrata_img)
                    if not hasattr(self, 'selector_images'): 
                        self.selector_images = {}
                    self.selector_images['entrata'] = entrata_photo
                    porta_label = tk.Label(icon_frame, image=entrata_photo, bg=config['bg_color'])
                else:
                    porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                         bg=config['bg_color'], fg=config['icon_color'])
            except Exception as e:
                print(f"⚠️ Errore caricamento ENTRATA: {e}")
                porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                     bg=config['bg_color'], fg=config['icon_color'])
            porta_label.pack(side='left', padx=(0,6))"""
    
    # Applica la prima sostituzione
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE | re.DOTALL)
    
    # Pattern per il secondo emoji (USCITA) - quello alla fine
    pattern2 = r"""            porta_label = tk\.Label\(icon_frame,
                                 text='[^']*',
                                 font=\('Segoe UI Emoji', 26\),
                                 bg=config\['bg_color'\],
                                 fg=config\['icon_color'\]\)
            porta_label\.pack\(side='left', padx=\(0,0\)\)"""
    
    # Sostituzione per USCITA  
    replacement2 = """            # Carica immagine USCITA
            try:
                uscita_path = os.path.join(self.base_path, "immagini", "USCITA.png")
                if os.path.exists(uscita_path):
                    from PIL import Image, ImageTk
                    uscita_img = Image.open(uscita_path)
                    uscita_img = uscita_img.resize((40, 40), Image.Resampling.LANCZOS)
                    uscita_photo = ImageTk.PhotoImage(uscita_img)
                    if not hasattr(self, 'selector_images'): 
                        self.selector_images = {}
                    self.selector_images['uscita'] = uscita_photo
                    porta_label = tk.Label(icon_frame, image=uscita_photo, bg=config['bg_color'])
                else:
                    porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                         bg=config['bg_color'], fg=config['icon_color'])
            except Exception as e:
                print(f"⚠️ Errore caricamento USCITA: {e}")
                porta_label = tk.Label(icon_frame, text='🚪', font=('Segoe UI Emoji', 26), 
                                     bg=config['bg_color'], fg=config['icon_color'])
            porta_label.pack(side='left', padx=(0,0))"""
    
    # Applica la seconda sostituzione
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE | re.DOTALL)
    
    # Scrivi il file aggiornato
    with open('tigota_elite_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Selettori aggiornati con successo!")
    print("📁 Le immagini ENTRATA.png e USCITA.png saranno usate al posto degli emoji")

if __name__ == "__main__":
    update_selectors()
