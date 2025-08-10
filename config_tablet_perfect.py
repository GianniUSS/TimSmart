# -*- coding: utf-8 -*-
"""
Configurazione perfetta per tablet TIGOTÀ
Layout ottimizzato con dimensioni garantite
"""

# Colori brand TIGOTÀ ottimizzati
COLORS = {
    # Colori principali
    'background': '#F8F9FA',          # Grigio chiaro moderno
    'card_bg': '#FFFFFF',             # Bianco pulito per card
    'secondary': '#F1F3F4',           # Grigio secondario
    
    # Brand TIGOTÀ
    'tigota_pink': '#E91E63',         # Rosa TIGOTÀ principale
    'tigota_light': '#FCE4EC',        # Rosa chiaro per header
    'tigota_dark': '#AD1457',         # Rosa scuro per accenti
    
    # Testi
    'text': '#212121',                # Testo principale scuro
    'text_light': '#757575',          # Testo secondario
    'text_white': '#FFFFFF',          # Testo bianco
    
    # Stati
    'success': '#4CAF50',             # Verde successo
    'warning': '#FF9800',             # Arancione attenzione
    'error': '#F44336',               # Rosso errore
    'info': '#2196F3',                # Blu informazioni
    
    # Effetti
    'shadow': '#E0E0E0',              # Ombra leggera
    'hover': '#F5F5F5',               # Stato hover
    'active': '#EEEEEE'               # Stato attivo
}

# Font ottimizzati per tablet
FONTS = {
    'logo_large': ('Segoe UI', 56, 'bold'),       # Logo TIGOTÀ
    'title': ('Segoe UI', 22, 'bold'),            # Titoli sezioni
    'subtitle': ('Segoe UI', 18, 'normal'),       # Sottotitoli
    'body': ('Segoe UI', 14, 'normal'),           # Testo normale
    'body_bold': ('Segoe UI', 14, 'bold'),        # Testo enfatizzato
    'date': ('Segoe UI', 26, 'normal'),           # Data - dimensione ridotta
    'time': ('Consolas', 68, 'bold'),             # Ora - monospace grande
    'slogan': ('Segoe UI', 16, 'italic'),         # Slogan
    'status': ('Segoe UI', 12, 'bold'),           # Status
    'badge': ('Segoe UI', 20, 'bold'),            # Badge ID
    'icon': ('Apple Color Emoji', 80),            # Icone emoji
    'small': ('Segoe UI', 10, 'normal')           # Testo piccolo
}

# Testi interfaccia
TEXTS = {
    'app_title': 'TIGOTÀ - Sistema di Timbratura',
    'header_title': 'TIGOTÀ',
    'header_subtitle': 'Sistema di Timbratura',
    'nfc_title': 'AVVICINA IL BADGE',
    'nfc_instructions': 'Posiziona il badge\nvicino al sensore',
    'nfc_ready': '🟢 Sistema Pronto',
    'status_active': 'ATTIVO',
    'slogan': '',  # Slogan rimosso
    'software_version': 'SmartTIM v3.0 Tablet',
    'entrata': 'ENTRATA',
    'uscita': 'USCITA',
    'error_read': '❌ Errore Lettura',
    'feedback_success': 'Timbratura registrata!'
}

# Configurazione finestra tablet
WINDOW_CONFIG = {
    'title': 'TIGOTÀ - Sistema di Timbratura Tablet',
    'width': 1280,          # Larghezza tablet standard
    'height': 800,          # Altezza tablet standard
    'fullscreen': True,     # Modalità fullscreen
    'resizable': False,     # Non ridimensionabile
    'topmost': True,        # Sempre in primo piano
}

# Layout tablet ottimizzato
TABLET_CONFIG = {
    # Dimensioni container principali
    'header_height': 120,           # Altezza fissa header
    'footer_height': 60,            # Altezza fissa footer
    'main_padding': 30,             # Padding principale
    'card_padding': 40,             # Padding interno card
    
    # Dimensioni card
    'datetime_ratio': 0.6,          # 60% larghezza per data/ora
    'nfc_ratio': 0.4,               # 40% larghezza per NFC
    'card_margin': 15,              # Margine tra card
    'card_spacing': 10,             # Spaziatura card
    
    # Dimensioni testo con wrap garantito
    'date_wraplength': 450,         # Larghezza massima data
    'nfc_wraplength': 200,          # Larghezza massima NFC
    'instructions_wraplength': 180, # Larghezza istruzioni
    'slogan_wraplength': 450,       # Larghezza slogan
    
    # Touch targets (44px minimum per accessibilità)
    'min_touch_size': 44,           # Dimensione minima touch
    'button_height': 60,            # Altezza pulsanti
    'icon_size': 80,                # Dimensione icone
    
    # Animazioni e timing
    'feedback_duration': 3000,      # Durata feedback (ms)
    'error_duration': 2000,         # Durata errore (ms)
    'clock_update': 1000,           # Aggiornamento orologio (ms)
    
    # Layout grid
    'grid_weights': {
        'datetime_col': 6,          # Peso colonna data/ora
        'nfc_col': 4,               # Peso colonna NFC
        'main_row': 1               # Peso riga principale
    }
}

# Configurazione NFC
NFC_CONFIG = {
    'enabled': True,
    'simulation_mode': True,        # Modalità simulazione per test
    'read_timeout': 5000,           # Timeout lettura (ms)
    'retry_attempts': 3,            # Tentativi di lettura
    'feedback_sound': True,         # Suono feedback
    'visual_feedback': True,        # Feedback visivo
    'log_enabled': True,            # Log letture
    
    # Badge simulati per test
    'test_badges': [
        'BADGE001', 'BADGE002', 'BADGE003',
        'ADMIN001', 'TEST001', 'DEMO001'
    ]
}

# Configurazione debugging
DEBUG_CONFIG = {
    'enabled': True,                # Debug abilitato
    'show_fps': False,              # Mostra FPS
    'show_memory': False,           # Mostra uso memoria
    'log_level': 'INFO',            # Livello log
    'admin_key': 'F1',              # Tasto admin panel
    'exit_key': 'Escape',           # Tasto uscita fullscreen
    'reload_key': 'F5',             # Tasto ricarica
}

# Configurazione database
DATABASE_CONFIG = {
    'file': 'timbrature_tablet.json',  # File database
    'backup_enabled': True,             # Backup automatico
    'backup_interval': 3600,            # Intervallo backup (s)
    'max_records': 10000,               # Record massimi
    'auto_cleanup': True,               # Pulizia automatica
}

# Stili personalizzati per widget
WIDGET_STYLES = {
    'main_frame': {
        'bg': COLORS['background'],
        'relief': 'flat',
        'bd': 0
    },
    'card_frame': {
        'bg': COLORS['card_bg'],
        'relief': 'flat',
        'bd': 0
    },
    'header_frame': {
        'bg': COLORS['tigota_light'],
        'relief': 'flat',
        'bd': 0
    },
    'footer_frame': {
        'bg': COLORS['secondary'],
        'relief': 'flat',
        'bd': 0
    }
}

# Export per import semplificato
__all__ = [
    'COLORS', 'FONTS', 'TEXTS', 'WINDOW_CONFIG', 
    'TABLET_CONFIG', 'NFC_CONFIG', 'DEBUG_CONFIG',
    'DATABASE_CONFIG', 'WIDGET_STYLES'
]
