# TIGOTÀ Sistema di Timbratura - Manuale Produzione

## 🚀 SETUP RAPIDO PRODUZIONE

### 1. INSTALLAZIONE
```bash
# Clona o copia i file del progetto
# Esegui installer automatico
python installer.py
```

### 2. AVVIO PRODUZIONE
```bash
# Avvio normale
python production_launcher.py

# Avvio con monitoring
python production_launcher.py --monitor

# Avvio come servizio (Windows)
sc create "TIGOTA" binPath="C:\Python\python.exe C:\Program Files\TIGOTA_Timbratura\production_launcher.py"
```

## 📋 CHECKLIST DEPLOYMENT

### Hardware Necessario
- [ ] **Tablet/PC touch** (min 10", risoluzione 1280x800)
- [ ] **Lettore NFC/RFID** USB compatibile
- [ ] **Badge NFC** per dipendenti
- [ ] **Supporto fisso** per tablet
- [ ] **Alimentazione permanente**
- [ ] **Connessione WiFi** stabile

### Software Necessario
- [ ] **Python 3.8+** installato
- [ ] **Dipendenze** installate (`pip install -r requirements.txt`)
- [ ] **Driver NFC** configurati
- [ ] **Antivirus** configurato (esclusioni per app)
- [ ] **Windows Updates** disabilitati (opzionale)

### Configurazione Sistema
- [ ] **Avvio automatico** configurato
- [ ] **Screensaver** disabilitato
- [ ] **Sleep mode** disabilitato
- [ ] **Firewall** configurato
- [ ] **Backup automatico** attivo

## 🔧 CONFIGURAZIONE HARDWARE

### Lettori NFC/RFID Supportati
```python
# Nel file nfc_manager.py configurare:

# OPZIONE A: Lettore USB seriale
LETTORE_TIPO = "USB_SERIAL"
LETTORE_PORT = "COM3"  # Windows
LETTORE_PORT = "/dev/ttyUSB0"  # Linux

# OPZIONE B: Lettore NFC standard
LETTORE_TIPO = "NFC_STANDARD"
LETTORE_LIBRARY = "pynfc"

# OPZIONE C: Lettore RFID Mifare
LETTORE_TIPO = "RFID_MIFARE"
LETTORE_LIBRARY = "mfrc522"
```

### Badge Configuration
```json
{
    "badge_types": {
        "dipendenti": {
            "format": "BADGE{:03d}",
            "range": [1, 999],
            "permissions": ["timbratura"]
        },
        "admin": {
            "format": "ADMIN{:02d}",
            "range": [1, 10],
            "permissions": ["timbratura", "admin"]
        }
    }
}
```

## 📊 MONITORING E LOGGING

### Log Files Locazione
```
C:/ProgramData/TIGOTA_Timbratura/logs/
├── tigota.log          # Log applicazione principale
├── launcher.log        # Log launcher produzione
├── nfc.log            # Log lettore NFC
├── database.log       # Log database operations
└── error.log          # Log errori critici
```

### Monitoring Parametri
```python
# Nel file production_launcher.py
MONITORING = {
    "check_interval": 30,      # Secondi tra controlli
    "max_memory_mb": 512,      # Memoria massima MB
    "max_cpu_percent": 80,     # CPU massima %
    "auto_restart": True,      # Riavvio automatico
    "max_restarts": 5          # Riavvii massimi
}
```

## 🗄️ DATABASE E BACKUP

### Database Structure
```sql
-- Tabella timbrature
CREATE TABLE timbrature (
    id INTEGER PRIMARY KEY,
    badge_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_movimento TEXT CHECK(tipo_movimento IN ('ENTRATA','USCITA')),
    location TEXT DEFAULT 'TIGOTA_STORE',
    sync_status INTEGER DEFAULT 0
);

-- Tabella dipendenti  
CREATE TABLE dipendenti (
    badge_id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    reparto TEXT,
    attivo INTEGER DEFAULT 1
);
```

### Backup Automatico
```python
# Configurazione backup nel file production.json
"database": {
    "backup_enabled": true,
    "backup_interval": 3600,    # Ogni ora
    "backup_path": "C:/ProgramData/TIGOTA_Timbratura/backup",
    "retention_days": 30,       # Mantieni 30 giorni
    "export_format": ["json", "excel"]
}
```

## 🔒 SICUREZZA

### Password Admin
```python
# Default: tigota2025
# Cambiare in production.json
"security": {
    "admin_password": "LA_TUA_PASSWORD_SICURA",
    "encryption_enabled": true,
    "session_timeout": 300
}
```

### Backup Encryption
```python
# Backup cifrati automaticamente
"backup_encryption": {
    "enabled": true,
    "algorithm": "AES-256",
    "key_file": "C:/ProgramData/TIGOTA_Timbratura/keys/backup.key"
}
```

## 🌐 INTEGRAZIONE API

### Export Dati
```python
# API endpoint per esportazione dati
def export_timbrature(start_date, end_date, format="json"):
    """
    Esporta timbrature in vari formati
    Supporta: JSON, Excel, CSV
    """
    pass

# Esempio usage
python -c "
from tigota_api import export_timbrature
export_timbrature('2025-08-01', '2025-08-31', 'excel')
"
```

### Sincronizzazione Cloud (Opzionale)
```python
# Configurazione sync cloud
"cloud_sync": {
    "enabled": false,
    "provider": "aws|azure|gcp",
    "endpoint": "https://api.tigota.cloud/v1/",
    "api_key": "YOUR_API_KEY",
    "sync_interval": 3600
}
```

## 🚨 TROUBLESHOOTING

### Problemi Comuni

**App non si avvia:**
```bash
# Verifica Python
python --version

# Verifica dipendenze
pip check

# Verifica permissions
icacls "C:\Program Files\TIGOTA_Timbratura" /grant Users:F

# Log dettagliato
python tigota_elite_dashboard.py --debug
```

**Lettore NFC non funziona:**
```bash
# Lista porte seriali
python -m serial.tools.list_ports

# Test lettore
python test_nfc.py

# Driver update
# Scaricare driver dal produttore lettore
```

**Performance issues:**
```bash
# Monitor risorse
python production_launcher.py --monitor --verbose

# Ottimizza memoria
# Nel config: max_memory_mb: 256

# Disabilita animazioni
# Nel config: animations_enabled: false
```

## 📞 SUPPORTO

### Contatti Tecnici
- **Email**: support@tigota.it
- **Telefono**: +39 XXX XXXXXXX
- **Orari**: Lun-Ven 9:00-18:00

### Documentazione
- **Manuale Utente**: `docs/user_manual.pdf`
- **API Documentation**: `docs/api_docs.html`
- **Video Tutorials**: `https://support.tigota.it/videos`

### Remote Support
```bash
# Abilita accesso remoto (solo per troubleshooting)
python remote_support.py --enable --duration 3600

# Genera report diagnostico
python diagnostic_tool.py --full-report
```

## 📈 MANUTENZIONE

### Giornaliera
- [ ] Verifica log errori
- [ ] Controllo spazio disco
- [ ] Test lettura badge

### Settimanale  
- [ ] Backup manuale
- [ ] Pulizia log vecchi
- [ ] Update badge database

### Mensile
- [ ] Analisi performance
- [ ] Review sicurezza
- [ ] Update software

---

**Versione Documento**: 1.0  
**Ultimo Aggiornamento**: 07/08/2025  
**Compatibilità**: TIGOTÀ v3.1.0 Elite
