# -*- coding: utf-8 -*-
"""
Configurazione App TIGOTÀ Ultra Moderna per Tablet
Design avanzato con gradiente e animazioni
"""

# COLORI TIGOTÀ ULTRA MODERNI
COLORS = {
    # Colori primari brand
    'tigota_pink': '#E91E63',        # Rosa TIGOTÀ principale
    'tigota_light': '#F8BBD9',       # Rosa TIGOTÀ chiaro
    'tigota_dark': '#AD1457',        # Rosa TIGOTÀ scuro
    
    # Sfondo e struttura
    'background': '#FFFFFF',          # Bianco puro
    'card_bg': '#FEFEFE',            # Bianco caldo per card
    'overlay_bg': '#FCFCFC',         # Bianco per overlay
    
    # Bordi e ombre
    'border': '#E8E8E8',             # Bordo sottile
    'shadow': '#E0E0E0',             # Ombra card
    'shadow_light': '#F0F0F0',       # Ombra leggera
    
    # Testi
    'text': '#2C2C2C',               # Testo principale scuro
    'text_light': '#666666',         # Testo secondario
    'text_dark': '#1A1A1A',          # Testo molto scuro
    
    # Status e feedback
    'success': '#4CAF50',            # Verde successo
    'warning': '#FF9800',            # Arancione warning
    'error': '#F44336',              # Rosso errore
    'info': '#2196F3',               # Blu info
    
    # NFC States
    'nfc_active': '#4CAF50',         # Verde NFC attivo
    'nfc_reading': '#FF9800',        # Arancione lettura
    'nfc_error': '#F44336',          # Rosso errore NFC
    
    # Accenti e decorazioni
    'accent_gold': '#FFD700',        # Oro per accenti
    'accent_silver': '#C0C0C0',      # Argento per dettagli
    'gradient_start': '#FFFFFF',     # Inizio gradiente
    'gradient_end': '#FCE4EC',       # Fine gradiente (rosa chiarissimo)
}

# TESTI E CONTENUTI
TEXTS = {
    # Branding
    'logo_principale': 'TIGOTÀ',
    'slogan': 'Belli, Puliti, Profumati',
    'subtitle_negozio': 'Sistema Timbrature Negozio',
    
    # NFC Section
    'nfc_title': 'AVVICINA IL BADGE',
    'nfc_subtitle': 'Posiziona il badge vicino al sensore NFC per registrare la timbratura',
    'nfc_active': '🟢 Sensore Attivo',
    'nfc_reading': '🟡 Lettura in corso...',
    'nfc_waiting': '⚪ In attesa...',
    
    # Feedback messaggi
    'success_msg': 'Timbratura Registrata!',
    'error_msg': 'Errore nella registrazione',
    'welcome_msg': 'Benvenuto/a!',
    'goodbye_msg': 'Arrivederci!',
    
    # Info sistema
    'software_name': 'TIGOTÀ Time',
    'software_version': 'v2.0',
    'copyright': '© 2024 TIGOTÀ',
    
    # Istruzioni
    'instructions_1': '1. Avvicina il badge al sensore NFC',
    'instructions_2': '2. Attendi la conferma visiva',
    'instructions_3': '3. La timbratura viene salvata automaticamente',
}

# FONT SISTEMA ULTRA MODERNI
FONTS = {
    # Header e titoli principali
    'logo': ('Segoe UI', 48, 'bold'),
    'slogan': ('Segoe UI Light', 16, 'italic'),
    'page_title': ('Segoe UI', 32, 'bold'),
    
    # Data e ora
    'date': ('Segoe UI', 24, 'normal'),
    'time': ('Segoe UI', 72, 'bold'),
    'time_seconds': ('Segoe UI', 32, 'normal'),
    
    # NFC area
    'nfc_title': ('Segoe UI', 22, 'bold'),
    'nfc_subtitle': ('Segoe UI', 14, 'normal'),
    'nfc_status': ('Segoe UI', 12, 'bold'),
    
    # Feedback e messaggi
    'feedback_large': ('Segoe UI', 36, 'bold'),    # Movimento ENTRATA/USCITA
    'feedback_medium': ('Segoe UI', 18, 'bold'),   # Messaggi successo
    'feedback_small': ('Segoe UI', 14, 'normal'),  # Info aggiuntive
    
    # Dettagli timbratura
    'badge_id': ('Segoe UI', 16, 'normal'),
    'timestamp': ('Segoe UI', 20, 'bold'),
    'employee_name': ('Segoe UI', 18, 'bold'),
    
    # Status e info sistema
    'status_text': ('Segoe UI', 12, 'normal'),
    'info_text': ('Segoe UI', 10, 'normal'),
    'footer_text': ('Segoe UI', 10, 'italic'),
}

# CONFIGURAZIONE TABLET ULTRA MODERNA
TABLET_CONFIG = {
    # Dimensioni schermo
    'screen_width': 1280,
    'screen_height': 800,
    'dpi_scale': 1.25,              # Scaling per alta DPI
    
    # Layout spacing
    'margin_large': 40,             # Margini esterni
    'margin_medium': 24,            # Margini medi
    'margin_small': 16,             # Margini piccoli
    'padding': 20,                  # Padding interno
    
    # Dimensioni touch target
    'touch_min_size': 60,           # Dimensione minima area touch
    'button_width': 200,            # Larghezza pulsanti
    'button_height': 80,            # Altezza pulsanti
    
    # Bordi e angoli
    'border_radius': 12,            # Raggio bordi arrotondati
    'shadow_offset': 4,             # Offset ombra
    'shadow_blur': 8,               # Blur ombra
    
    # Animazioni
    'animation_speed': 300,         # Velocità animazioni (ms)
    'feedback_duration': 4000,      # Durata feedback (ms)
    'pulse_interval': 2000,         # Intervallo pulse NFC (ms)
    
    # Card dimensions
    'card_datetime_width': 700,     # Larghezza card data/ora
    'card_nfc_width': 460,          # Larghezza card NFC
    'card_height': 400,             # Altezza card standard
    'card_spacing': 40,             # Spazio tra card
    
    # NFC area
    'nfc_circle_size': 140,         # Diametro cerchio NFC
    'nfc_pulse_size': 160,          # Dimensione pulse massima
    'nfc_icon_size': 48,            # Dimensione icona NFC
    
    # Header e footer
    'header_height': 120,           # Altezza header
    'footer_height': 60,            # Altezza footer
    
    # Gradiente background
    'gradient_steps': 150,          # Passi gradiente
    'gradient_intensity': 0.1,      # Intensità gradiente
    
    # Touch feedback
    'touch_ripple_size': 100,       # Dimensione effetto ripple
    'touch_feedback_duration': 600, # Durata feedback touch
}

# CONFIGURAZIONE NFC AVANZATA
NFC_CONFIG = {
    # Simulazione per sviluppo
    'simulation_mode': True,
    'simulation_badges': [
        'CARD001', 'CARD002', 'CARD003', 'CARD004', 'CARD005'
    ],
    'simulation_interval': 10,      # Secondi tra simulazioni auto
    
    # Lettura hardware
    'read_timeout': 5,              # Timeout lettura badge
    'retry_attempts': 3,            # Tentativi di rilettura
    'debounce_time': 2,             # Tempo anti-rimbalzo (secondi)
    
    # Area di lettura
    'detection_distance': 5,        # Distanza rilevamento (cm)
    'read_power': 'high',           # Potenza lettore: low, medium, high
    
    # Audio feedback
    'beep_success': True,           # Beep successo
    'beep_error': True,             # Beep errore
    'volume': 0.7,                  # Volume audio (0.0 - 1.0)
}

# CONFIGURAZIONE FINESTRA
WINDOW_CONFIG = {
    'title': 'TIGOTÀ - Sistema Timbrature Ultra',
    'geometry': '1280x800',
    'fullscreen': True,
    'hide_cursor': False,           # Nasconde cursore in produzione
    'always_on_top': True,          # Sempre in primo piano
    'disable_alt_tab': True,        # Disabilita Alt+Tab
    'kiosk_mode': True,             # Modalità chiosco
}

# CONFIGURAZIONE DATABASE
DATABASE_CONFIG = {
    'file_path': 'data/timbrature_ultra.json',
    'backup_enabled': True,
    'backup_interval': 3600,        # Backup ogni ora
    'max_records': 10000,           # Massimo record in memoria
    'compression': True,            # Compressione dati
    'encryption': False,            # Crittografia (future)
}

# CONFIGURAZIONE LOGGING
LOGGING_CONFIG = {
    'level': 'INFO',                # DEBUG, INFO, WARNING, ERROR
    'file_path': 'logs/tigota_ultra.log',
    'max_size': '10MB',             # Dimensione massima log
    'backup_count': 5,              # Numero file backup
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# CONFIGURAZIONE RETE (per versioni future)
NETWORK_CONFIG = {
    'api_enabled': False,           # API REST per sincronizzazione
    'api_url': 'https://api.tigota.com',
    'sync_interval': 300,           # Sync ogni 5 minuti
    'offline_mode': True,           # Funzionamento offline
    'retry_sync': True,             # Riprova sync in caso di errore
}

# CONFIGURAZIONE SICUREZZA
SECURITY_CONFIG = {
    'admin_badge': 'ADMIN001',      # Badge amministratore
    'maintenance_mode': False,      # Modalità manutenzione
    'auto_lock': True,              # Blocco automatico
    'lock_timeout': 3600,           # Timeout blocco (secondi)
    'reset_daily': True,            # Reset giornaliero contatori
}

# TEMI PERSONALIZZABILI (per future versioni)
THEMES = {
    'ultra_modern': {
        'name': 'Ultra Moderno TIGOTÀ',
        'description': 'Design avanzato con gradiente e animazioni',
        'primary_color': '#E91E63',
        'gradient_enabled': True,
        'animations_enabled': True,
        'shadow_enabled': True,
    },
    'classic': {
        'name': 'Classico TIGOTÀ',
        'description': 'Design tradizionale semplice',
        'primary_color': '#E91E63',
        'gradient_enabled': False,
        'animations_enabled': False,
        'shadow_enabled': False,
    }
}

# CONFIGURAZIONE CURRENT THEME
CURRENT_THEME = 'ultra_modern'
