#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wizard touch per abbinare dipendenti e badge NFC:
1) Codice dipendente → 2) Nominativo →    def _render_step_codice(self):
        print(f"[DEBUG] _render_step_codice chiamato")
            tk.Label(self.container, text="Codice dipendente", font=('Segoe UI', self._s(24), 'bold'), bg='#FFFFFF', fg='#333').pack(anchor='w', pady=(0, self._s(4)))) Badge NFC (con pulsante Abilita Lettura)
Requisiti: pulsante Annulla solo in alto a destra; Annulla chiude subito.
"""

import tkinter as tk
import winsound
import os
import time
import sys
import subprocess
try:
    import winreg  # Windows registry for touch keyboard settings
except Exception:  # pragma: no cover
    winreg = None
import ctypes
from ctypes import wintypes
from database_sqlite import get_database_manager
from nfc_manager import NFCReader


class AbbinamentoWizard(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Abbinamento Dipendente ↔ Badge")
        self.configure(bg="#FFFFFF")
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        # Stato/servizi
        self.db = get_database_manager()
        self.nfc_reader = None
        self.step = 1
        self.codice_var = tk.StringVar()
        self.nome_var = tk.StringVar()
        self.cognome_var = tk.StringVar()
        self.badge_var = tk.StringVar()
        self._entry_badge = None
        self._active_text_var = None
        self._osk_uppercase = True
        self._osk_frame = None
        self._kb_spacer = None  # spacer in basso per non coprire i campi con la tastiera
        self._kb_opening = False  # flag per evitare chiamate multiple

        # Fullscreen + scorciatoie
        try:
            self._is_fullscreen = True
            self.attributes('-fullscreen', True)
        except Exception:
            try:
                self.state('zoomed')
            except Exception:
                pass
        self.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.bind('<Escape>', lambda e: self._cancel())

        # Scaling per tablet (baseline 1280x800)
        try:
            vw = self.winfo_screenwidth()
            vh = self.winfo_screenheight()
        except Exception:
            vw, vh = 1280, 800
        base_w, base_h = 1280, 800
        self._scale = max(1.0, min(3.0, min(vw / base_w, vh / base_h)))
        def _s(v: int) -> int:
            return max(1, int(round(v * self._scale)))
        self._s = _s
        self._vw, self._vh = vw, vh
        # Modalità compatta per tablet 1280x800 o più piccoli
        self._compact = (vh <= 800)
        # Tastiera virtuale Windows
        self._touch_kb_enabled = sys.platform.startswith('win')
        self._kb_last_try_ok = False

    def _open_virtual_keyboard(self):
        """Apre la tastiera virtuale di Windows"""
        try:
            subprocess.Popen(['cmd', '/c', 'start', 'ms-inputapp:'], shell=True)
        except Exception:
            pass

        # Build UI e schema
        self._build_ui()
        self._ensure_schema()
        try:
            self.grab_set()
        except Exception:
            pass

    def _build_ui(self):
        pad = self._s(14)
        # Titolo (padding ridotto per alzare i contenuti)
        tk.Label(
            self,
            text="Abbinamento dipendente",
            font=('Segoe UI', self._s(24), 'bold'),
            fg='#5FA8AF',
            bg='#FFFFFF'
        ).pack(pady=(self._s(6), self._s(2)))

        # Header con Annulla (solo in alto a destra) con padding minimo
        header_actions = tk.Frame(self, bg='#FFFFFF')
        header_actions.pack(fill='x', padx=pad*2, pady=(0, self._s(2)))
        tk.Button(
            header_actions,
            text='Annulla',
            font=('Segoe UI', self._s(14), 'bold'),
            bg='#F3F4F6',
            fg='#333',
            relief='ridge',
            command=self._cancel
        ).pack(side='right', ipadx=self._s(12), ipady=self._s(8))

        # Status (padding verticale ridotto)
        self.status = tk.Label(self, text="Step 1 di 3", font=('Segoe UI', self._s(12)), fg='#5FA8AF', bg='#FFFFFF')
        self.status.pack(pady=(0, self._s(2)))

        # Container principale (padding top molto ridotto)
        self.container = tk.Frame(self, bg='#FFFFFF')
        self.container.pack(fill='both', expand=True, padx=pad*2, pady=(self._s(2), self._s(6)))
        self._render_step()

    def _clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _render_step(self):
        print(f"[DEBUG] _render_step chiamato, step={self.step}")
        self._clear_container()
        if self.step == 1:
            self.status.config(text="Step 1 di 3 · Inserisci codice dipendente")
            self._render_step_codice()
        elif self.step == 2:
            self.status.config(text="Step 2 di 3 · Inserisci nominativo")
            self._render_step_nominativo()
        else:
            self.status.config(text="Step 3 di 3 · Abbina badge NFC")
            self._render_step_badge()

    # --- Step 1 ---
    def _render_step_codice(self):
            tk.Label(self.container, text="Codice dipendente (max 10 cifre)", font=('Segoe UI', self._s(24), 'bold'), bg='#FFFFFF', fg='#333').pack(anchor='w', pady=(0, self._s(6)))
            entry = tk.Entry(self.container, textvariable=self.codice_var, font=('Consolas', self._s(28)), 
                           bd=3, relief='solid', highlightthickness=2, highlightcolor='#20B2AA', 
                           highlightbackground='#CCCCCC', insertbackground='#333333')
            entry.pack(fill='x', ipady=self._s(16))
            entry.focus_set()
            entry.bind('<Return>', lambda e: self._go_step2())
            # Filtra automaticamente caratteri non numerici
            try:
                entry.bind('<KeyRelease>', lambda e: self.codice_var.set(''.join(ch for ch in self.codice_var.get() if ch.isdigit())[:10]))
                entry.bind('<Button-1>', lambda e: self._open_virtual_keyboard())
            except Exception:
                pass

            self._error_lbl = tk.Label(self.container, text="", font=('Segoe UI', self._s(12)), fg='#E91E63', bg='#FFFFFF')
            self._error_lbl.pack(pady=(self._s(4), 0))

            tk.Button(self.container, text="Avanti ›", font=('Segoe UI', self._s(22), 'bold'), bg='#20B2AA', fg='white', command=self._go_step2).pack(pady=(self._s(20), 0), ipadx=self._s(28), ipady=self._s(14))
            tk.Frame(self.container, bg='#FFFFFF').pack(pady=(self._s(6), 0), fill='x')

    # --- Step 2 ---
    def _render_step_nominativo(self):
            tk.Label(self.container, text="Nome", font=('Segoe UI', self._s(24), 'bold'), bg='#FFFFFF', fg='#333').pack(anchor='w', pady=(0, self._s(4)))
            entry_nome = tk.Entry(self.container, textvariable=self.nome_var, font=('Segoe UI', self._s(26)), 
                                bd=3, relief='solid', highlightthickness=2, highlightcolor='#20B2AA', 
                                highlightbackground='#CCCCCC', insertbackground='#333333')
            entry_nome.pack(fill='x', ipady=self._s(16))
            entry_nome.focus_set()
            entry_nome.bind('<Return>', lambda e: self._save_anagrafica())
            entry_nome.bind('<FocusIn>', lambda e: self._set_active_var(self.nome_var))
            entry_nome.bind('<Button-1>', lambda e: self._open_virtual_keyboard())

            tk.Label(self.container, text="Cognome (opzionale)", font=('Segoe UI', self._s(24), 'bold'), bg='#FFFFFF', fg='#333').pack(anchor='w', pady=(self._s(8), self._s(4)))
            entry_cognome = tk.Entry(self.container, textvariable=self.cognome_var, font=('Segoe UI', self._s(26)), 
                                   bd=3, relief='solid', highlightthickness=2, highlightcolor='#20B2AA', 
                                   highlightbackground='#CCCCCC', insertbackground='#333333')
            entry_cognome.pack(fill='x', ipady=self._s(16))
            entry_cognome.bind('<FocusIn>', lambda e: self._set_active_var(self.cognome_var))
            entry_cognome.bind('<Button-1>', lambda e: self._open_virtual_keyboard())

            self._active_text_var = self.nome_var
            # Su Windows usa la tastiera di sistema; altrove mostra l'OSK interno
            if not self._touch_kb_enabled:
                self._osk_frame = self._make_osk(self.container)
                self._osk_frame.pack(pady=self._s(12))

            pad = tk.Frame(self.container, bg='#FFFFFF')
            pad.pack(pady=self._s(6))
            tk.Button(pad, text="‹ Indietro", font=('Segoe UI', self._s(20), 'bold'), command=self._go_step1).pack(side='left', ipadx=self._s(16), ipady=self._s(10))
            tk.Button(pad, text="Avanti ›", font=('Segoe UI', self._s(20), 'bold'), bg='#20B2AA', fg='white', command=self._save_anagrafica).pack(side='right', ipadx=self._s(26), ipady=self._s(12))

    def _set_active_var(self, var: tk.StringVar):
        self._active_text_var = var

    # --- Step 3 ---
    def _render_step_badge(self):
            tk.Label(self.container, text="Badge NFC", font=('Segoe UI', self._s(20), 'bold'), bg='#FFFFFF', fg='#333').pack(anchor='w', pady=(0, self._s(4)))
            tk.Label(self.container, text="Premi ‘Abilita Lettura’ e avvicina il badge al lettore", font=('Segoe UI', self._s(16)), bg='#FFFFFF', fg='#5FA8AF').pack(anchor='w', pady=(0, self._s(8)))

            row = tk.Frame(self.container, bg='#FFFFFF')
            row.pack(fill='x')
            entry_badge = tk.Entry(row, textvariable=self.badge_var, font=('Consolas', self._s(28)), 
                                 bd=3, relief='solid', highlightthickness=2, highlightcolor='#20B2AA', 
                                 highlightbackground='#CCCCCC', insertbackground='#333333')
            entry_badge.pack(side='left', fill='x', expand=True, ipady=self._s(16))
            self._entry_badge = entry_badge
            entry_badge.bind('<Return>', lambda e: self._on_badge(self.badge_var.get().strip()))
            entry_badge.bind('<Button-1>', lambda e: self._open_virtual_keyboard())

            tk.Button(row, text="Abilita Lettura", font=('Segoe UI', self._s(20), 'bold'), bg='#E91E63', fg='white', command=self._start_reading).pack(side='left', padx=self._s(10), ipadx=self._s(18), ipady=self._s(12))

            pad = tk.Frame(self.container, bg='#FFFFFF')
            pad.pack(pady=self._s(6))
            tk.Button(pad, text="‹ Indietro", font=('Segoe UI', self._s(20), 'bold'), command=self._go_step2).pack(side='left', ipadx=self._s(16), ipady=self._s(10))
            tk.Button(pad, text="Salva Abbinamento", font=('Segoe UI', self._s(20), 'bold'), bg='#20B2AA', fg='white', command=self._save_badge).pack(side='right', ipadx=self._s(26), ipady=self._s(12))

            self.hint = tk.Label(self.container, text="In attesa…", font=('Segoe UI', self._s(16)), fg='#9CA3AF', bg='#FFFFFF')
            self.hint.pack(anchor='w', pady=(self._s(6), 0))

    # Navigazione
    def _go_step1(self):
        self.step = 1
        self._render_step()

    def _go_step2(self):
        code = (self.codice_var.get() or '').strip()
        if not code or not code.isdigit() or len(code) > 10:
            if getattr(self, '_error_lbl', None):
                self._error_lbl.config(text='Inserisci un codice numerico (max 10 cifre)')
            self._beep(); return
        self.step = 2
        self._render_step()

    def _save_anagrafica(self):
        self.nome_var.set(self.nome_var.get().strip().title())
        self.cognome_var.set(self.cognome_var.get().strip().title())
        if not self.nome_var.get().strip():
            self._beep(); return
        if self.db.upsert_dipendente(self.codice_var.get(), self.nome_var.get(), self.cognome_var.get() or None):
            self.step = 3
            self._render_step()
        else:
            self._beep()

    # NFC
    def _start_reading(self):
        try:
            self.hint.config(text="Lettura attiva: avvicina il badge…", fg='#20B2AA')
        except Exception:
            pass
        try:
            self.badge_var.set('')
            if self._entry_badge and self._entry_badge.winfo_exists():
                self._entry_badge.focus_set()
        except Exception:
            pass
        try:
            if self.nfc_reader:
                self.nfc_reader.stop_reading()
        except Exception:
            pass
        self.nfc_reader = NFCReader(callback=self._on_badge)
        self.nfc_reader.start_reading()

    def _on_badge(self, badge_id: str):
        def ui():
            self.badge_var.set(badge_id)
            self.hint.config(text=f"Badge letto: {badge_id}", fg='#5FA8AF')
            self._beep()
            try:
                if self.nfc_reader:
                    self.nfc_reader.stop_reading()
            except Exception:
                pass
        self.after(0, ui)

    def _save_badge(self):
        badge = self.badge_var.get().strip()
        if not badge:
            self._show_status("Leggi un badge per continuare", error=True)
            self._beep(); return
        ok = self.db.abbina_badge_a_dipendente(self.codice_var.get(), badge)
        if ok:
            try:
                self._show_message('info', 'Salvato', 'Abbinamento salvato')
            except Exception:
                self._show_status("Abbinamento salvato", error=False)
            self.after(0, self._cancel)
        else:
            try:
                self._show_message('error', 'Errore', 'Errore salvataggio')
            except Exception:
                self._show_status("Errore salvataggio", error=True)
            self._beep()

    def _show_status(self, msg: str, error: bool = False):
        try:
            self.hint.config(text=msg, fg='#E91E63' if error else '#20B2AA')
        except Exception:
            pass

    # --- Dialoghi modali touch-friendly in stile TIGOTÀ ---
    def _show_message(self, kind: str, title: str, text: str):
        try:
            self.update_idletasks()
        except Exception:
            pass
        try:
            dlg = tk.Toplevel(self)
            try:
                dlg.transient(self)
                dlg.attributes('-topmost', True)
                dlg.resizable(False, False)
            except Exception:
                pass
            dlg.configure(bg='#FFFFFF')

            brand = '#5FA8AF'
            ok_bg = '#20B2AA'
            warn = '#F59E0B'
            err = '#EF4444'
            header_bg = brand if kind == 'info' else (warn if kind == 'warning' else err)
            btn_bg = ok_bg if kind == 'info' else header_bg

            s = getattr(self, '_s', lambda v: v)
            vw = getattr(self, '_vw', 800) or 800
            width = max(360, min(640, int(vw * 0.48)))

            header = tk.Frame(dlg, bg=header_bg)
            header.pack(fill='x')
            tk.Label(header, text=title, font=('Segoe UI', s(22)), fg='#FFFFFF', bg=header_bg, padx=s(16), pady=s(10)).pack(anchor='w')

            body = tk.Frame(dlg, bg='#FFFFFF')
            body.pack(fill='both', expand=True, padx=s(18), pady=s(16))
            tk.Label(body, text=text, font=('Segoe UI', s(16)), fg='#374151', bg='#FFFFFF', justify='left', wraplength=width - s(36)).pack(anchor='w')

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

            try:
                dlg.update_idletasks()
                dw = max(width, dlg.winfo_width())
                dh = dlg.winfo_height()
                pw = max(800, self.winfo_width())
                ph = max(600, self.winfo_height())
                px = self.winfo_rootx(); py = self.winfo_rooty()
                x = px + (pw - dw) // 2
                y = py + (ph - dh) // 2
                dlg.geometry(f"{dw}x{dh}+{max(0,x)}+{max(0,y)}")
            except Exception:
                pass

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
            # Fallback minimale
            try:
                tk.messagebox.showinfo(title, text, parent=self)
            except Exception:
                pass

    # Utility
    def _make_keypad(self, parent, target_var: tk.StringVar):
        frame = tk.Frame(parent, bg='#FFFFFF')
        buttons = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['◀', '0', 'C']]
        # Dimensioni responsive
        font_sz = self._s(30 if not self._compact else 26)
        pad_x = self._s(20 if not self._compact else 14)
        pad_y = self._s(20 if not self._compact else 14)
        cell_w = self._s(140 if not self._compact else 110)
        cell_h = self._s(110 if not self._compact else 90)
        gap = self._s(10 if not self._compact else 8)
        for r, row in enumerate(buttons):
            for c, val in enumerate(row):
                tk.Button(
                    frame,
                    text=val,
                    font=('Segoe UI', font_sz, 'bold'),
                    relief='raised',
                    bd=2,
                    padx=pad_x,
                    pady=pad_y,
                    command=lambda v=val: self._keypad_press(v, target_var)
                ).grid(row=r, column=c, padx=gap, pady=gap, sticky='nsew')
        # Target touch ampi ma compatibili con 800px di altezza
        for c in range(3):
            frame.grid_columnconfigure(c, weight=1, minsize=cell_w)
        for r in range(4):
            frame.grid_rowconfigure(r, weight=1, minsize=cell_h)
        return frame

    def _keypad_press(self, value: str, var: tk.StringVar):
        s = var.get()
        if value == 'C':
            var.set('')
        elif value == '◀':
            var.set(s[:-1])
        else:
            var.set(s + value)

    def _make_osk(self, parent):
        frame = tk.Frame(parent, bg='#FFFFFF')
        upper = self._osk_uppercase
        rows = [
            list("QWERTYUIOP" if upper else "qwertyuiop"),
            list("ASDFGHJKL" if upper else "asdfghjkl"),
            list("ZXCVBNM" if upper else "zxcvbnm"),
            list("ÀÈÉÌÒÙ" if upper else "àèéìòù")
        ]
        # Dimensioni responsive per OSK
        key_font = self._s(28 if not self._compact else 24)
        key_pad = self._s(14 if not self._compact else 10)
        key_gap_x = self._s(8 if not self._compact else 6)
        key_gap_y = self._s(6 if not self._compact else 4)
        cmd_font = self._s(28 if not self._compact else 24)
        space_font = self._s(24 if not self._compact else 20)
        space_pad_y = self._s(18 if not self._compact else 12)

        for letters in rows:
            rowf = tk.Frame(frame, bg='#FFFFFF')
            rowf.pack(pady=key_gap_y)
            for ch in letters:
                tk.Button(
                    rowf,
                    text=ch,
                    font=('Segoe UI', key_font, 'bold'),
                    relief='raised',
                    bd=2,
                    padx=key_pad,
                    pady=key_pad,
                    command=lambda v=ch: self._osk_press(v)
                ).pack(side='left', padx=key_gap_x, pady=self._s(2))
        # Comandi OSK
        cmd = tk.Frame(frame, bg='#FFFFFF')
        cmd.pack(pady=self._s(8 if not self._compact else 6), fill='x')
        tk.Button(cmd, text='⇧', font=('Segoe UI', cmd_font, 'bold'), relief='raised', bd=2, padx=key_pad, pady=key_pad, command=self._toggle_osk_case).pack(side='left', padx=key_gap_x)
        tk.Button(cmd, text="'", font=('Segoe UI', cmd_font, 'bold'), relief='raised', bd=2, padx=key_pad, pady=key_pad, command=lambda: self._osk_press("'")) .pack(side='left', padx=key_gap_x)
        tk.Button(cmd, text='Spazio', font=('Segoe UI', space_font, 'bold'), relief='raised', bd=2, pady=space_pad_y, command=lambda: self._osk_press(' ')).pack(side='left', padx=self._s(10 if not self._compact else 8), fill='x', expand=True)
        tk.Button(cmd, text='-', font=('Segoe UI', cmd_font, 'bold'), relief='raised', bd=2, padx=key_pad, pady=key_pad, command=lambda: self._osk_press('-')).pack(side='left', padx=key_gap_x)
        tk.Button(cmd, text='◀', font=('Segoe UI', cmd_font, 'bold'), relief='raised', bd=2, padx=key_pad, pady=key_pad, command=lambda: self._osk_press('◀')).pack(side='left', padx=key_gap_x)
        tk.Button(cmd, text='Canc', font=('Segoe UI', space_font, 'bold'), relief='raised', bd=2, padx=self._s(20 if not self._compact else 16), pady=key_pad, command=lambda: self._osk_press('{CLEAR}')).pack(side='left', padx=key_gap_x)
        return frame

    def _toggle_osk_case(self):
        try:
            self._osk_uppercase = not self._osk_uppercase
            if self._osk_frame and self._osk_frame.winfo_exists():
                self._osk_frame.destroy()
            self._osk_frame = self._make_osk(self.container)
            self._osk_frame.pack(pady=self._s(12))
        except Exception:
            pass

    def _osk_press(self, value: str):
        var = self._active_text_var
        if not isinstance(var, tk.StringVar):
            return
        s = var.get()
        if value == '{CLEAR}':
            var.set('')
        elif value == '◀':
            var.set(s[:-1])
        else:
            var.set(s + value)

    def _toggle_fullscreen(self):
        try:
            self._is_fullscreen = not self._is_fullscreen
            self.attributes('-fullscreen', self._is_fullscreen)
        except Exception:
            pass

    def _cancel(self):
        # Chiudi la tastiera touch se aperta (Windows)
        try:
            self._close_touch_keyboard()
        except Exception:
            pass
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            if self.nfc_reader:
                self.nfc_reader.stop_reading()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
        # cleanup spacer
        try:
            self._release_keyboard_space()
        except Exception:
            pass

    def _beep(self):
        try:
            winsound.Beep(880, 120)
        except Exception:
            try:
                winsound.MessageBeep()
            except Exception:
                pass

    def _ensure_schema(self):
        try:
            with self.db._get_db_connection() as conn:
                conn.executescript(
                    """
CREATE TABLE IF NOT EXISTS dipendenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    cognome TEXT,
    badge_id TEXT UNIQUE,
    attivo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_dipendenti_codice ON dipendenti(codice);
CREATE INDEX IF NOT EXISTS idx_dipendenti_badge ON dipendenti(badge_id);
                    """
                )
                conn.commit()
        except Exception:
            pass

    # --- Touch keyboard helpers (Windows) ---
    def _open_virtual_keyboard(self):
        """Apre la tastiera virtuale solo quando l'utente clicca su un campo."""
        if not self._touch_kb_enabled:
            return
            
        # Evita aperture multiple ravvicinate
        now = time.time()
        if hasattr(self, '_last_keyboard_open') and now - self._last_keyboard_open < 1.0:
            return
        self._last_keyboard_open = now
        
        print("[DEBUG] Apertura tastiera virtuale su richiesta utente...")
        
        try:
            import subprocess
            # Metodo diretto e affidabile
            subprocess.Popen(['cmd', '/c', 'start', '', 'ms-inputapp:'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                           creationflags=0x08000000)
            print("[DEBUG] Tastiera virtuale aperta")
        except Exception as e:
            print(f"[DEBUG] Errore apertura tastiera: {e}")
            # Fallback a TabTip.exe
            try:
                subprocess.Popen(['tabtip.exe'], stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL, creationflags=0x08000000)
                print("[DEBUG] Fallback TabTip.exe riuscito")
            except:
                pass
        if not self._touch_kb_enabled:
            return
        try:
            # 1) Abilita auto-invoke tastiera dal registro quando possibile
            try:
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

            # 2) Assicura servizi IME/ctf attivi
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

            # 3) Tentativo moderno via protocollo ms-inputapp (Windows 11)
            started = False
            try:
                subprocess.Popen(['cmd', '/c', 'start', '', 'ms-inputapp:'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                started = True
            except Exception:
                try:
                    subprocess.Popen(['explorer.exe', 'ms-inputapp:'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    started = True
                except Exception:
                    pass

            # 4) Fallback a TabTip.exe classico
            paths = [
                os.path.join(os.environ.get('ProgramFiles', r'C\\Program Files'), 'Common Files', 'microsoft shared', 'ink', 'TabTip.exe'),
                os.path.join(os.environ.get('ProgramFiles(x86)', r'C\\Program Files (x86)'), 'Common Files', 'microsoft shared', 'ink', 'TabTip.exe'),
            ]
            for p in paths:
                if os.path.exists(p):
                    try:
                        os.startfile(p)  # type: ignore[attr-defined]
                        started = True
                        break
                    except Exception:
                        try:
                            subprocess.Popen([p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x00000008)
                            started = True
                            break
                        except Exception:
                            continue
            if not started:
                try:
                    subprocess.Popen(['osk.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x00000008)
                    started = True
                except Exception:
                    pass
            self._kb_last_try_ok = started
        except Exception:
            self._kb_last_try_ok = False
        # riserva spazio poco dopo l'avvio della tastiera (e un secondo tentativo)
        try:
            self.after(200, self._reserve_keyboard_space)
            self.after(1000, self._reserve_keyboard_space)
        except Exception:
            pass

    def _get_keyboard_rect(self):
        """Ritorna (left, top, right, bottom) della tastiera (TabTip/OSK) se visibile, altrimenti None."""
        if not self._touch_kb_enabled:
            return None
        try:
            classes = ['IPTip_Main_Window', 'OSKMainClass']
            user32 = ctypes.windll.user32
            rect = wintypes.RECT()
            for cls in classes:
                hwnd = user32.FindWindowW(cls, None)
                if hwnd and user32.IsWindowVisible(hwnd):
                    if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                        return (rect.left, rect.top, rect.right, rect.bottom)
            return None
        except Exception:
            return None

    def _reserve_keyboard_space(self):
        """Inserisce/aggiorna uno spacer in basso pari all'altezza della tastiera.
        Se non rilevabile, usa una stima per tablet.
        """
        try:
            kb_rect = self._get_keyboard_rect()
            vh = self._vh if hasattr(self, '_vh') else self.winfo_screenheight()
            height = 0
            if kb_rect:
                height = max(0, kb_rect[3] - kb_rect[1])
                # applica solo se la tastiera è nella metà bassa dello schermo
                if kb_rect[1] <= (vh * 0.45):
                    height = 0
            elif self._kb_last_try_ok:
                # fallback stimato
                height = int(vh * 0.34)
            self._apply_keyboard_spacer(height)
        except Exception:
            pass

    def _apply_keyboard_spacer(self, height: int):
        try:
            height = max(0, int(height))
            if height == 0:
                self._release_keyboard_space()
                return
            if self._kb_spacer is None or not self._kb_spacer.winfo_exists():
                self._kb_spacer = tk.Frame(self, bg='#FFFFFF', height=height)
                try:
                    self._kb_spacer.pack_propagate(False)
                except Exception:
                    pass
                self._kb_spacer.pack(side='bottom', fill='x')
            else:
                self._kb_spacer.configure(height=height)
        except Exception:
            pass

    def _release_keyboard_space(self):
        try:
            if self._kb_spacer and self._kb_spacer.winfo_exists():
                self._kb_spacer.pack_forget()
        except Exception:
            pass

    def _close_touch_keyboard(self):
        """Chiude/nasconde la tastiera di sistema se presente (TabTip/OSK) e rilascia lo spacer."""
        if not self._touch_kb_enabled:
            return
            
        print("[DEBUG] Chiusura tastiera virtuale sicura...")
        
        try:
            # Cancella operazioni pending
            if hasattr(self, '_kb_pending_job'):
                self.after_cancel(self._kb_pending_job)
            self._kb_opening = False  # Reset flag
        except:
            pass
            
        try:
            import subprocess
            # Metodo gentile - chiude TabTip senza forzare
            subprocess.run(['taskkill', '/IM', 'TabTip.exe', '/F'], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            print("[DEBUG] TabTip chiuso")
        except Exception as e:
            print(f"[DEBUG] Errore chiusura TabTip: {e}")
            
        try:
            # Chiusura classica per OSK se presente
            user32 = ctypes.windll.user32
            WM_CLOSE = 0x0010
            classes = ['IPTip_Main_Window', 'OSKMainClass']
            for cls in classes:
                try:
                    hwnd = user32.FindWindowW(cls, None)
                    if hwnd:
                        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                except Exception:
                    pass
        except Exception as e:
            print(f"[DEBUG] Errore chiusura finestre tastiera: {e}")
            
        # Rilascia spazio keyboard con delay
        try:
            self._kb_last_try_ok = False
            self.after(100, self._release_keyboard_space)
        except Exception:
            pass


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    AbbinamentoWizard(root)
    root.mainloop()
