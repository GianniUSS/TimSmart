"""
Tastiera virtuale COMPATTA per TIGOTA Elite Dashboard
"""
import tkinter as tk


class VirtualKeyboard(tk.Toplevel):
    """Tastiera COMPATTA - più larga, meno alta"""

    def __init__(self, parent, target_widget=None, dock_bottom=True):
        super().__init__(parent)
        self.parent = parent
        self.target_widget = target_widget
        self.is_visible = False
        self.dock_bottom = dock_bottom
        self._top_guard_job = None
        self._last_focus_widget = None  # Traccia l'ultimo widget attivo

        self.title("📱 SmartTIM Tastiera COMPATTA")
        self.configure(bg='#F8F9FA')
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.hide_keyboard)
        self.withdraw()

        self.is_caps = False
        self.create_keyboard()
        
        # Debug: stampa info del widget target
        if target_widget:
            print(f"[KEYBOARD] Widget target impostato: {target_widget} (tipo: {type(target_widget)})")
        else:
            print("[KEYBOARD] Nessun widget target specificato")

    def create_keyboard(self):
        """Crea tastiera COMPATTA con binding corretto dei pulsanti"""
        main_frame = tk.Frame(self, bg='#F8F9FA', padx=10, pady=8)
        main_frame.pack(fill='both', expand=True)

        # Numeri - height=2 per compattezza
        num_frame = tk.Frame(main_frame, bg='#F8F9FA')
        num_frame.pack(fill='x', pady=2)
        for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            btn = tk.Button(
                num_frame, text=key, width=8, height=2,
                font=('Arial', 13, 'bold'), bg='#FFFFFF', relief='raised', bd=2,
                takefocus=False  # Evita di rubare il focus
            )
            # Usa partial per binding corretto invece di lambda
            from functools import partial
            btn.config(command=partial(self._insert_text, key))
            btn.pack(side='left', padx=2, pady=2)

        # QWERTY
        qwerty_frame = tk.Frame(main_frame, bg='#F8F9FA')
        qwerty_frame.pack(fill='x', pady=2)
        for key in ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P']:
            btn = tk.Button(
                qwerty_frame, text=key, width=8, height=2,
                font=('Arial', 13, 'bold'), bg='#FFFFFF', relief='raised', bd=2,
                takefocus=False  # Evita di rubare il focus
            )
            btn.config(command=partial(self._insert_text, key))
            btn.pack(side='left', padx=2, pady=2)

        # ASDF
        asdf_frame = tk.Frame(main_frame, bg='#F8F9FA')
        asdf_frame.pack(fill='x', pady=2)
        for key in ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L']:
            btn = tk.Button(
                asdf_frame, text=key, width=8, height=2,
                font=('Arial', 13, 'bold'), bg='#FFFFFF', relief='raised', bd=2,
                takefocus=False  # Evita di rubare il focus
            )
            btn.config(command=partial(self._insert_text, key))
            btn.pack(side='left', padx=2, pady=2)

        # ZXCV
        zxcv_frame = tk.Frame(main_frame, bg='#F8F9FA')
        zxcv_frame.pack(fill='x', pady=2)
        for key in ['Z', 'X', 'C', 'V', 'B', 'N', 'M']:
            btn = tk.Button(
                zxcv_frame, text=key, width=8, height=2,
                font=('Arial', 13, 'bold'), bg='#FFFFFF', relief='raised', bd=2,
                takefocus=False  # Evita di rubare il focus
            )
            btn.config(command=partial(self._insert_text, key))
            btn.pack(side='left', padx=2, pady=2)

        # Simboli
        symbols_frame = tk.Frame(main_frame, bg='#F8F9FA')
        symbols_frame.pack(fill='x', pady=2)
        for key in ['@', '.', '-', '_', '/', ':', ';', ',', '?', '!']:
            btn = tk.Button(
                symbols_frame, text=key, width=8, height=2,
                font=('Arial', 13, 'bold'), bg='#FFFFFF', relief='raised', bd=2,
                takefocus=False  # Evita di rubare il focus
            )
            btn.config(command=partial(self._insert_text, key))
            btn.pack(side='left', padx=2, pady=2)

        # Controlli COMPATTI
        control_frame = tk.Frame(main_frame, bg='#F8F9FA', pady=3)
        control_frame.pack(fill='x')

        # CAPS
        caps_btn = tk.Button(
            control_frame, text='CAPS', width=10, height=2,
            font=('Arial', 13, 'bold'), bg='#E9ECEF', command=self._toggle_caps,
            takefocus=False  # Evita di rubare il focus
        )
        caps_btn.pack(side='left', padx=2, pady=2)

        # SPAZIO
        space_btn = tk.Button(
            control_frame, text='SPAZIO', width=25, height=2,
            font=('Arial', 13, 'bold'), bg='#E9ECEF',
            takefocus=False  # Evita di rubare il focus
        )
        space_btn.config(command=partial(self._insert_text, ' '))
        space_btn.pack(side='left', padx=2, pady=2)

        # BACKSPACE
        back_btn = tk.Button(
            control_frame, text='⌫ CANC', width=12, height=2,
            font=('Arial', 13, 'bold'), bg='#E9ECEF', command=self._backspace,
            takefocus=False  # Evita di rubare il focus
        )
        back_btn.pack(side='left', padx=2, pady=2)

        # OK
        ok_btn = tk.Button(
            control_frame, text='✓ OK', width=10, height=2,
            font=('Arial', 13, 'bold'), bg='#28A745', fg='white', command=self.hide_keyboard,
            takefocus=False  # Evita di rubare il focus
        )
        ok_btn.pack(side='right', padx=2, pady=2)

        # CHIUDI
        close_btn = tk.Button(
            control_frame, text='✕ Chiudi', width=10, height=2,
            font=('Arial', 13, 'bold'), bg='#DC3545', fg='white', command=self.hide_keyboard,
            takefocus=False  # Evita di rubare il focus
        )
        close_btn.pack(side='right', padx=2, pady=2)

    def _insert_text(self, char):
        """Inserisce testo nel widget target con metodi multipli per garantire il funzionamento"""
        widget_to_use = None
        
        # 1. Prova con il target_widget specificato
        if self.target_widget:
            try:
                # Verifica che il widget esista ancora
                if self.target_widget.winfo_exists():
                    widget_to_use = self.target_widget
                    print(f"[KEYBOARD] Usando target_widget: {widget_to_use}")
                else:
                    print("[KEYBOARD] Target widget non esiste più")
            except:
                print("[KEYBOARD] Errore nel controllo target_widget")
        
        # 2. Se non c'è target_widget, trova il widget attualmente in focus
        if not widget_to_use:
            try:
                focused = self.parent.focus_get()
                if focused and hasattr(focused, 'insert') and hasattr(focused, 'get'):
                    widget_to_use = focused
                    self._last_focus_widget = focused
                    print(f"[KEYBOARD] Usando widget in focus: {widget_to_use}")
                elif self._last_focus_widget:
                    try:
                        if self._last_focus_widget.winfo_exists():
                            widget_to_use = self._last_focus_widget
                            print(f"[KEYBOARD] Usando ultimo widget focus: {widget_to_use}")
                    except:
                        pass
            except Exception as e:
                print(f"[KEYBOARD] Errore nel trovare widget focus: {e}")
        
        # 3. Inserisci il testo se abbiamo un widget valido
        if widget_to_use:
            try:
                # Assicura focus al widget
                widget_to_use.focus_set()
                self.after(10, lambda: self._do_insert_text(widget_to_use, char))
                return True
            except Exception as e:
                print(f"[KEYBOARD] Errore nel dare focus: {e}")
        
        print(f"[KEYBOARD] ❌ NESSUN WIDGET VALIDO per inserire '{char}'")
        return False
    
    def _do_insert_text(self, widget, char):
        """Esegue effettivamente l'inserimento del testo"""
        try:
            # Gestione CAPS
            if self.is_caps and char.isalpha():
                char = char.upper()
            
            # Metodo 1: Inserimento alla posizione del cursore
            try:
                current_pos = widget.index(tk.INSERT)
                widget.insert(current_pos, char)
                print(f"[KEYBOARD] ✅ Inserito '{char}' alla posizione {current_pos}")
            except:
                # Metodo 2: Inserimento alla fine
                try:
                    widget.insert(tk.END, char)
                    print(f"[KEYBOARD] ✅ Inserito '{char}' alla fine")
                except:
                    # Metodo 3: Sostituzione completa (ultima risorsa)
                    current_text = widget.get()
                    widget.delete(0, tk.END)
                    widget.insert(0, current_text + char)
                    print(f"[KEYBOARD] ✅ Inserito '{char}' con sostituzione completa")
            
            # Triggera eventi per validazione
            try:
                widget.event_generate('<KeyRelease>')
                widget.event_generate('<Key>')
            except:
                pass
                
        except Exception as e:
            print(f"[KEYBOARD] ❌ ERRORE inserimento testo '{char}': {e}")

    def _backspace(self):
        """Cancella l'ultimo carattere con metodi multipli per garantire il funzionamento"""
        widget_to_use = None
        
        # Trova il widget target usando la stessa logica di _insert_text
        if self.target_widget:
            try:
                if self.target_widget.winfo_exists():
                    widget_to_use = self.target_widget
            except:
                pass
        
        if not widget_to_use:
            try:
                focused = self.parent.focus_get()
                if focused and hasattr(focused, 'delete') and hasattr(focused, 'get'):
                    widget_to_use = focused
                elif self._last_focus_widget:
                    try:
                        if self._last_focus_widget.winfo_exists():
                            widget_to_use = self._last_focus_widget
                    except:
                        pass
            except:
                pass
        
        if widget_to_use:
            try:
                widget_to_use.focus_set()
                self.after(10, lambda: self._do_backspace(widget_to_use))
            except Exception as e:
                print(f"[KEYBOARD] Errore nel backspace: {e}")
        else:
            print("[KEYBOARD] ❌ NESSUN WIDGET per backspace")
    
    def _do_backspace(self, widget):
        """Esegue effettivamente il backspace"""
        try:
            # Metodo 1: Cancellazione dalla posizione del cursore
            try:
                current_pos = widget.index(tk.INSERT)
                if current_pos > 0:
                    widget.delete(current_pos - 1, current_pos)
                    print(f"[KEYBOARD] ✅ Backspace dalla posizione {current_pos}")
                else:
                    print("[KEYBOARD] Niente da cancellare (inizio)")
            except:
                # Metodo 2: Cancellazione dall'ultimo carattere
                try:
                    content = widget.get()
                    if content:
                        widget.delete(0, tk.END)
                        widget.insert(0, content[:-1])
                        print(f"[KEYBOARD] ✅ Backspace con sostituzione completa")
                    else:
                        print("[KEYBOARD] Campo già vuoto")
                except Exception as e:
                    print(f"[KEYBOARD] Errore nel metodo alternativo: {e}")
            
            # Triggera eventi per validazione
            try:
                widget.event_generate('<KeyRelease>')
            except:
                pass
                
        except Exception as e:
            print(f"[KEYBOARD] ❌ ERRORE backspace: {e}")

    def set_target_widget(self, widget):
        """Aggiorna il widget target e verifica che sia valido"""
        self.target_widget = widget
        self._last_focus_widget = widget
        if widget:
            print(f"[KEYBOARD] Nuovo target widget impostato: {widget}")
            try:
                widget.focus_set()
            except:
                print("[KEYBOARD] Errore nel dare focus al nuovo target")
        else:
            print("[KEYBOARD] Target widget rimosso")

    def _toggle_caps(self):
        self.is_caps = not self.is_caps
        print(f"[KEYBOARD] CAPS {'ON' if self.is_caps else 'OFF'}")

    def show_keyboard(self):
        try:
            if not self.is_visible:
                self.deiconify()
                self.is_visible = True
                if self.dock_bottom:
                    self._dock_to_bottom()
                self.lift()
                self.attributes('-topmost', True)
                self._start_topmost_guardian()
                print("[KEYBOARD] ✨ TASTIERA COMPATTA MOSTRATA!")
        except Exception as e:
            print(f"[KEYBOARD] Errore show: {e}")

    def hide_keyboard(self):
        try:
            if self.is_visible:
                self.withdraw()
                self.is_visible = False
                self._stop_topmost_guardian()
                print("[KEYBOARD] Tastiera COMPATTA nascosta!")
                
                # **FIX WIZARD**: Chiamata callback di chiusura se esiste
                if hasattr(self, '_wizard_close_callback') and callable(self._wizard_close_callback):
                    try:
                        self._wizard_close_callback()
                        print("[KEYBOARD] Callback chiusura wizard eseguito")
                    except Exception as e:
                        print(f"[KEYBOARD] Errore nel callback chiusura: {e}")
                        
        except Exception as e:
            print(f"[KEYBOARD] Errore hide: {e}")

    def _dock_to_bottom(self):
        """VERSIONE COMPATTA - Più larga, meno alta"""
        try:
            self.update_idletasks()
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            
            # DIMENSIONI COMPATTE
            width = min(screen_w - 40, 1300)  # PIÙ LARGA
            req_h = self.winfo_reqheight()
            height = min(max(req_h, 280), 350)  # PIÙ BASSA
            
            x = max(20, (screen_w - width) // 2)
            y = screen_h - height - 40
            
            self.geometry(f"{width}x{height}+{x}+{y}")
            print(f"[KEYBOARD] 🎯 TASTIERA COMPATTA: {width}x{height} at {x},{y}")
        except Exception as e:
            self.geometry("1300x320+60+400")

    def _start_topmost_guardian(self):
        self._stop_topmost_guardian()
        if self.is_visible:
            self._top_guard_job = self.after(500, self._ensure_topmost_loop)

    def _stop_topmost_guardian(self):
        if self._top_guard_job:
            self.after_cancel(self._top_guard_job)
            self._top_guard_job = None

    def _ensure_topmost_loop(self):
        if self.is_visible:
            try:
                self.lift()
                self.attributes('-topmost', True)
                self._top_guard_job = self.after(500, self._ensure_topmost_loop)
            except: pass


class KeyboardManager:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.keyboard = None
        print("[KEYBOARD] Manager COMPATTO inizializzato")
    
    def show(self, target_widget=None):
        try:
            print(f"[KEYBOARD] 🚀 Richiesta di mostrare tastiera per widget: {target_widget}")
            
            # Se non c'è target_widget, prova a trovare quello in focus
            if not target_widget:
                try:
                    target_widget = self.parent.focus_get()
                    if target_widget:
                        print(f"[KEYBOARD] Widget focus trovato automaticamente: {target_widget}")
                except:
                    pass
            
            # Ricreo sempre per assicurare nuove dimensioni e target corretto
            if self.keyboard:
                self.keyboard.hide_keyboard()
                try: 
                    self.keyboard.destroy()
                except: 
                    pass
            
            # Crea nuova istanza con target specifico
            self.keyboard = VirtualKeyboard(self.parent, target_widget, dock_bottom=True)
            
            # Assicurati che il target sia impostato correttamente
            if target_widget:
                self.keyboard.set_target_widget(target_widget)
            
            # Mostra la tastiera
            self.keyboard.show_keyboard()
            
            print(f"[KEYBOARD] 🎯 Manager: tastiera mostrata per {target_widget}")
            
        except Exception as e:
            print(f"[KEYBOARD] ❌ Errore Manager.show(): {e}")
            import traceback
            traceback.print_exc()
    
    def hide(self):
        try:
            if self.keyboard:
                self.keyboard.hide_keyboard()
        except: pass
    
    def bring_to_front(self):
        """Porta la tastiera in primo piano - compatibilità con le impostazioni"""
        try:
            if self.keyboard and self.keyboard.is_visible:
                self.keyboard.lift()
                self.keyboard.attributes('-topmost', True)
                self.keyboard.focus_force()
                print("[KEYBOARD] Tastiera portata in primo piano")
        except Exception as e:
            print(f"[KEYBOARD] Errore bring_to_front: {e}")
    
    def close_keyboard(self):
        """Alias per hide_keyboard - compatibilità con wizard"""
        if self.keyboard:
            self.keyboard.hide_keyboard()
    
    def is_visible(self):
        try:
            return self.keyboard and self.keyboard.is_visible
        except:
            return False
