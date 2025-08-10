"""
Script per aggiornare i selettori con le nuove immagini ENTRATA.png e USCITA.png
"""

def update_selector_function():
    return '''    def create_selector_button(self, parent, config, row, col):
        """Crea bottoni identici all'immagine - design minimale e preciso"""
        # Container principale
        container = tk.Frame(parent, bg='#FFFFFF')
        container.grid(row=row, column=col, padx=25, pady=20, sticky='ew')
        
        # Bottone con dimensioni più grandi e bordi più evidenti
        button = tk.Frame(container,
                         bg=config['bg_color'],
                         relief='solid',
                         bd=3,
                         highlightbackground='#1565C0',
                         highlightthickness=0,
                         width=180,
                         height=100)
        button.pack_propagate(False)
        button.pack()

        content = tk.Frame(button, bg=config['bg_color'])
        content.pack(expand=True, fill='both', padx=0, pady=0)

        icon_frame = tk.Frame(content, bg=config['bg_color'])
        icon_frame.pack(expand=True, pady=(8,0))

        # Carica le immagini ENTRATA e USCITA
        if config['value'] == 'entrata':
            # Carica immagine ENTRATA
            try:
                entrata_path = os.path.join(self.base_path, "immagini", "ENTRATA.png")
                if os.path.exists(entrata_path):
                    from PIL import Image, ImageTk
                    entrata_img = Image.open(entrata_path)
                    entrata_img = entrata_img.resize((40, 40), Image.Resampling.LANCZOS)
                    entrata_photo = ImageTk.PhotoImage(entrata_img)
                    
                    # Salva riferimento per evitare garbage collection
                    if not hasattr(self, 'selector_images'):
                        self.selector_images = {}
                    self.selector_images['entrata'] = entrata_photo
                    
                    porta_label = tk.Label(icon_frame,
                                         image=entrata_photo,
                                         bg=config['bg_color'])
                    porta_label.pack(side='left', padx=(0,6))
                else:
                    # Fallback all'emoji se l'immagine non esiste
                    porta_label = tk.Label(icon_frame,
                                         text='🚪',
                                         font=('Segoe UI Emoji', 26),
                                         bg=config['bg_color'],
                                         fg=config['icon_color'])
                    porta_label.pack(side='left', padx=(0,6))
            except Exception as e:
                print(f"⚠️ Errore caricamento immagine ENTRATA: {e}")
                # Fallback all'emoji in caso di errore
                porta_label = tk.Label(icon_frame,
                                     text='🚪',
                                     font=('Segoe UI Emoji', 26),
                                     bg=config['bg_color'],
                                     fg=config['icon_color'])
                porta_label.pack(side='left', padx=(0,6))
                
            freccia_label = tk.Label(icon_frame,
                                   text='➤',
                                   font=('Arial', 26, 'bold'),
                                   bg=config['bg_color'],
                                   fg='#000000')
            freccia_label.pack(side='left', padx=(0,0))
        else:
            freccia_label = tk.Label(icon_frame,
                                   text='⬅',
                                   font=('Arial', 26, 'bold'),
                                   bg=config['bg_color'],
                                   fg='#000000')
            freccia_label.pack(side='left', padx=(0,6))
            
            # Carica immagine USCITA
            try:
                uscita_path = os.path.join(self.base_path, "immagini", "USCITA.png")
                if os.path.exists(uscita_path):
                    from PIL import Image, ImageTk
                    uscita_img = Image.open(uscita_path)
                    uscita_img = uscita_img.resize((40, 40), Image.Resampling.LANCZOS)
                    uscita_photo = ImageTk.PhotoImage(uscita_img)
                    
                    # Salva riferimento per evitare garbage collection
                    if not hasattr(self, 'selector_images'):
                        self.selector_images = {}
                    self.selector_images['uscita'] = uscita_photo
                    
                    porta_label = tk.Label(icon_frame,
                                         image=uscita_photo,
                                         bg=config['bg_color'])
                    porta_label.pack(side='left', padx=(0,0))
                else:
                    # Fallback all'emoji se l'immagine non esiste
                    porta_label = tk.Label(icon_frame,
                                         text='🚪',
                                         font=('Segoe UI Emoji', 26),
                                         bg=config['bg_color'],
                                         fg=config['icon_color'])
                    porta_label.pack(side='left', padx=(0,0))
            except Exception as e:
                print(f"⚠️ Errore caricamento immagine USCITA: {e}")
                # Fallback all'emoji in caso di errore
                porta_label = tk.Label(icon_frame,
                                     text='🚪',
                                     font=('Segoe UI Emoji', 26),
                                     bg=config['bg_color'],
                                     fg=config['icon_color'])
                porta_label.pack(side='left', padx=(0,0))

        text_label = tk.Label(content,
                             text=config['text'],
                             font=('Arial', 15, 'bold'),
                             bg=config['bg_color'],
                             fg=config['text_color'])
        text_label.pack(pady=(6, 0))
        
        # Click handler
        def on_click(event):
            self.select_timbratura_type(config['value'])
        
        # Hover effects per feedback chiaro
        def on_enter(event):
            button.configure(highlightthickness=3, highlightbackground='#1565C0', bg='#E3F2FD')

        def on_leave(event):
            if config['value'] != self.timbratura_type.get():
                button.configure(highlightthickness=3, highlightbackground='#000000', bg=config['bg_color'])

        widgets = [button, content, icon_frame, text_label, porta_label, freccia_label]
        for widget in widgets:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.configure(cursor='hand2')
        
        # Salva riferimenti
        self.selector_buttons[config['value']] = {
            'container': container,
            'button': button,
            'config': config,
            'porta_label': porta_label,
            'freccia_label': freccia_label,
            'text_label': text_label
        }'''

if __name__ == "__main__":
    print("Script di aggiornamento selettori pronto")
