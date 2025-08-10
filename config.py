# Configurazione App Timbratura SmartTIM - TIGOTA Brand

# Colori TIGOTA Brand (basati sul sito ufficiale)
COLORS = {
    'background': '#FFFFFF',          # Bianco pulito TIGOTA
    'primary': '#E91E63',             # Rosa/Magenta TIGOTA principale
    'secondary': '#F8F9FA',           # Grigio chiarissimo
    'accent': '#FF6B9D',              # Rosa accento più chiaro
    'text': '#2C3E50',                # Grigio scuro per testi
    'highlight': '#E91E63',           # Rosa TIGOTA per evidenziare
    'card_bg': '#FFFFFF',             # Bianco per le card
    'border': '#E1E8ED',              # Grigio chiaro per bordi
    'success': '#27AE60',             # Verde per successo
    'warning': '#F39C12',             # Arancione per avvisi
    'error': '#E74C3C',               # Rosso per errori
    'gradient_start': '#E91E63',      # Gradiente rosa TIGOTA
    'gradient_end': '#FF6B9D',        # Gradiente rosa chiaro
    'tigota_pink': '#E91E63',         # Colore distintivo TIGOTA
    'tigota_light': '#FCE4EC'         # Rosa molto chiaro per sfondi
}

# Configurazione testi - Design moderno TIGOTA
TEXTS = {
    'app_title': 'TIGOTÀ - Sistema di Timbratura',
    'logo_cliente': 'TIGOTÀ',
    'software_name': '⚡ SmartTIM by TIGOTÀ',
    'software_version': 'v2.0 TIGOTÀ Edition',
    'nfc_label': '📱',
    'nfc_instruction': 'Avvicina il tuo badge',
    'nfc_active': '🟢 Sistema Attivo',
    'nfc_error': '❌ ERRORE LETTURA',
    'entrata': 'ENTRATA',
    'uscita': 'USCITA',
    'welcome': 'Benvenuto in TIGOTÀ!',
    'goodbye': 'Arrivederci da TIGOTÀ!',
    'processing': '⏳ Elaborazione...',
    'slogan': 'Belli, Puliti, Profumati'
}

# Font configurabili - Design moderno
FONTS = {
    'logo_cliente': ('Segoe UI', 28, 'bold'),
    'date': ('Segoe UI', 42, 'normal'),
    'time': ('Consolas', 84, 'bold'),  # Font monospace per l'ora
    'nfc_icon': ('Segoe UI Emoji', 32, 'normal'),
    'nfc_text': ('Segoe UI', 16, 'normal'),
    'nfc_status': ('Segoe UI', 14, 'bold'),
    'software_name': ('Segoe UI', 18, 'bold'),
    'software_version': ('Segoe UI', 12, 'normal'),
    'badge_feedback': ('Segoe UI', 20, 'bold'),
    'movement_type': ('Segoe UI', 24, 'bold')
}

# Configurazione NFC
NFC_CONFIG = {
    'simulation_mode': True,  # Imposta False per NFC reale
    'read_interval': 2,       # Secondi tra letture simulate
    'feedback_duration': 3000 # Millisecondi per mostrare feedback
}

# Configurazione finestra
WINDOW_CONFIG = {
    'fullscreen': True,
    'title': TEXTS['app_title'],
    'geometry': '1920x1080',  # Fallback se non fullscreen
    'resizable': False
}

# File di configurazione
DATA_CONFIG = {
    'timbrature_file': 'timbrature.json',
    'log_file': 'app.log',
    'config_file': 'config.json'
}
