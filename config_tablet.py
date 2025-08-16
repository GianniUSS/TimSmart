# Configurazione App Timbratura TIGOTÀ - Tablet Touch

# Colori TIGOTÀ Brand (aggiornati per tablet)
COLORS = {
    'background': '#FFFFFF',          # Bianco pulito
    'primary': '#E91E63',             # Rosa TIGOTÀ principale
    'secondary': '#F8BBD9',           # Rosa molto chiaro
    'accent': '#AD1457',              # Rosa scuro per contrasto
    'text': '#212121',                # Grigio molto scuro
    'text_light': '#757575',          # Grigio medio
    'highlight': '#E91E63',           # Rosa per highlights
    'card_bg': '#FAFAFA',             # Bianco sporco per card
    'border': '#E0E0E0',              # Grigio chiaro bordi
    'success': '#4CAF50',             # Verde successo
    'warning': '#FF9800',             # Arancione warning
    'error': '#F44336',               # Rosso errore
    'gradient_start': '#E91E63',      # Gradiente rosa
    'gradient_end': '#F8BBD9',        # Gradiente rosa chiaro
    'tigota_pink': '#E91E63',         # Pink principale TIGOTÀ
    'tigota_light': '#FCE4EC',        # Rosa chiarissimo - SOLO DATI REALI
    'shadow': '#E0E0E0',              # Grigio per ombra (invece di trasparente)
    'nfc_active': '#00E676',          # Verde NFC attivo
    'button_hover': '#C2185B'         # Rosa hover pulsanti
}

# Configurazione testi per tablet
TEXTS = {
    'app_title': 'TIGOTÀ - Timbratura Dipendenti',
    'logo_principale': 'TIGOTÀ',
    'slogan': '',  # Slogan rimosso
    'software_name': 'SmartTIM',
    'software_version': 'v3.0 Tablet',
    'nfc_title': 'AVVICINA IL BADGE',
    'nfc_subtitle': 'Posiziona il badge NFC vicino al tablet',
    'nfc_active': 'Sistema Pronto',
    'nfc_reading': 'Lettura in corso...',
    'nfc_error': 'Errore di lettura',
    'entrata': 'ENTRATA',
    'uscita': 'USCITA',
    'welcome_msg': 'Benvenuto/a',
    'goodbye_msg': 'Arrivederci',
    'success_msg': 'Timbratura registrata!',
    'touch_instruction': 'Tocca per continuare',
    'admin_access': 'Accesso Amministratore'
}

# Font ottimizzati per tablet (più grandi)
FONTS = {
    'logo_main': ('Segoe UI', 48, 'bold'),           # Logo principale
    'date': ('Segoe UI', 28, 'normal'),              # Data ridotta per evitare troncamenti
    'time': ('Consolas', 72, 'bold'),                # Ora grande
    'nfc_title': ('Segoe UI', 24, 'bold'),           # Titolo NFC
    'nfc_subtitle': ('Segoe UI', 16, 'normal'),      # Sottotitolo NFC
    'feedback_large': ('Segoe UI', 36, 'bold'),      # Feedback grande
    'feedback_medium': ('Segoe UI', 24, 'normal'),   # Feedback medio
    'button_text': ('Segoe UI', 18, 'bold'),         # Testo pulsanti
    'status_text': ('Segoe UI', 14, 'normal'),       # Status
    'slogan': ('Segoe UI', 18, 'italic'),            # Slogan ridotto
    'badge_id': ('Consolas', 18, 'bold'),            # Badge ID
    'timestamp': ('Consolas', 16, 'normal')          # Timestamp
}

# Configurazione tablet touch
TABLET_CONFIG = {
    'screen_width': 1280,        # Larghezza tablet standard
    'screen_height': 800,        # Altezza tablet standard  
    'touch_target_size': 80,     # Dimensione minima touch target
    'animation_speed': 300,      # Velocità animazioni (ms)
    'feedback_duration': 4000,   # Durata feedback visivo (ms)
    'auto_return_home': 10000,   # Ritorno automatico home (ms)
    'button_padding': 20,        # Padding pulsanti
    'card_elevation': 8,         # Elevazione card (shadow)
    'border_radius': 12          # Raggio bordi arrotondati
}

# Configurazione NFC per tablet
NFC_CONFIG = {
    'simulation_mode': False,     # MODALITÀ PRODUZIONE - NFC REALE
    'read_interval': 1,           # Intervallo lettura più veloce
    'feedback_duration': 4000,    # Feedback più lungo
    'pulse_animation': True,      # Animazione pulse attiva
    'sound_feedback': False,      # Audio feedback (opzionale)
    'vibration_feedback': False   # Vibrazione (se supportata)
}

# Configurazione finestra per tablet
WINDOW_CONFIG = {
    'fullscreen': True,
    'title': TEXTS['app_title'],
    'geometry': f"{TABLET_CONFIG['screen_width']}x{TABLET_CONFIG['screen_height']}",
    'resizable': False,
    'touch_mode': True,
    'hide_cursor': True           # Nasconde cursor su tablet
}

# File di configurazione - PRODUZIONE
import os
from pathlib import Path

# Directory produzione (Windows ProgramData)
PRODUCTION_DIR = Path("C:/ProgramData/TIGOTA_Timbratura")
DATA_DIR = PRODUCTION_DIR / "data"
LOGS_DIR = PRODUCTION_DIR / "logs" 
BACKUP_DIR = PRODUCTION_DIR / "backup"
EXPORT_DIR = PRODUCTION_DIR / "export"
CONFIG_DIR = PRODUCTION_DIR / "config"

# Configurazione storage multi-layer
DATA_CONFIG = {
    # Database principale (SQLite per produzione)
    'database_file': str(DATA_DIR / 'timbrature.db'),
    'use_database': True,  # True per produzione, False per sviluppo
    
    # File JSON per compatibilità/backup
    'timbrature_file': str(DATA_DIR / 'timbrature.json'),
    'daily_export_dir': str(EXPORT_DIR),
    
    # Logging
    'log_file': str(LOGS_DIR / 'tigota_application.log'),
    'sync_log': str(LOGS_DIR / 'sync.log'),
    'error_log': str(LOGS_DIR / 'errors.log'),
    
    # Configurazioni
    'config_file': str(CONFIG_DIR / 'tigota_config.json'),
    'database_config': str(CONFIG_DIR / 'database.ini'),
    'sync_config': str(CONFIG_DIR / 'sync_settings.json'),
    
    # Backup e sicurezza
    'backup_dir': str(BACKUP_DIR),
    'backup_interval': 3600,      # Backup ogni ora
    'daily_export': True,         # Export giornaliero automatico
    'compress_backups': True,     # Compressione backup
    'max_backup_days': 30,        # Retention backup (30 giorni)
    
    # Sync cloud (opzionale)
    'cloud_sync_enabled': False,  # Da attivare se necessario
    'cloud_provider': 'onedrive', # onedrive, dropbox, googledrive
    'sync_interval': 900,         # Sync ogni 15 minuti
    
    # Sicurezza
    'encrypt_data': False,        # Crittografia dati (opzionale)
    'data_integrity_check': True, # Controllo integrità dati
    'audit_trail': True           # Log accessi e modifiche
}

# Schema database produzione
DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS timbrature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_id TEXT NOT NULL,
    dipendente_nome TEXT,
    dipendente_cognome TEXT,
    timestamp DATETIME NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('entrata', 'uscita')),
    location TEXT DEFAULT 'tablet_principale',
    tablet_id TEXT DEFAULT 'TIGOTA_001',
    sync_status TEXT DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'error')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    hash_verify TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_badge_timestamp ON timbrature(badge_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_status ON timbrature(sync_status);
CREATE INDEX IF NOT EXISTS idx_date ON timbrature(DATE(timestamp));

-- Anagrafica dipendenti con abbinamento badge NFC
CREATE TABLE IF NOT EXISTS dipendenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice TEXT NOT NULL UNIQUE,                     -- Codice dipendente (univoco)
    nome TEXT NOT NULL,                              -- Nome
    cognome TEXT,                                    -- Cognome facoltativo
    badge_id TEXT UNIQUE,                            -- Codice badge NFC (univoco, può essere NULL fino ad abbinamento)
    attivo INTEGER DEFAULT 1,                        -- Flag attivo
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dipendenti_codice ON dipendenti(codice);
CREATE INDEX IF NOT EXISTS idx_dipendenti_badge ON dipendenti(badge_id);
"""

# Configurazione per diversi ambienti
ENVIRONMENT_CONFIG = {
    'development': {
        'use_database': False,
        'data_dir': './data',
        'cloud_sync_enabled': False,
        'encrypt_data': False
    },
    'production': {
        'use_database': True,
        'data_dir': str(DATA_DIR),
        'cloud_sync_enabled': False,  # Configurabile
        'encrypt_data': False         # Configurabile
    },
    'enterprise': {
        'use_database': True,
        'data_dir': str(DATA_DIR),
        'cloud_sync_enabled': True,
        'encrypt_data': True,
        'api_integration': True
    }
}

# Environment attuale (cambiare per deployment)
CURRENT_ENVIRONMENT = 'production'
ACTIVE_CONFIG = ENVIRONMENT_CONFIG[CURRENT_ENVIRONMENT]
