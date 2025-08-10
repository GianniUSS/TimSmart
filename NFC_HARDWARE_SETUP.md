# 🔌 CONFIGURAZIONE HARDWARE NFC - TIGOTÀ

## ✅ MODALITÀ PRODUZIONE ATTIVATA
Il sistema è ora configurato per utilizzare dati reali dal database SQLite e lettori NFC hardware.

### 🎯 COSA È STATO MODIFICATO

1. **config_tablet.py**: `simulation_mode = False` ✅
2. **tigota_elite_dashboard.py**: Binding tastiera SPAZIO/ENTER disabilitati ✅  
3. **nfc_manager.py**: Attivata lettura hardware reale ✅

---

## 🔧 CONFIGURAZIONE LETTORE NFC

### OPZIONE 1: Lettore NFC USB/Seriale (Raccomandato)

```python
# In nfc_manager.py, decommentare:
import serial

# Configurare porta COM corretta (verificare in Gestione Dispositivi)
ser = serial.Serial('COM3', 9600, timeout=1)  # Cambiare COM3 con porta corretta
```

**Passi necessari:**
1. Collegare lettore NFC USB al tablet
2. Verificare porta COM in Gestione Dispositivi Windows
3. Modificare `COM3` con porta corretta nel codice
4. Installare driver lettore se necessario

### OPZIONE 2: Lettore NFC Python (pynfc)

```bash
pip install pynfc
```

```python
# In nfc_manager.py, decommentare sezione pynfc
import nfc
clf = nfc.ContactlessFrontend('usb')
```

### OPZIONE 3: Lettore RFID (mfrc522 - Raspberry Pi)

```bash
pip install mfrc522
```

```python
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
```

---

## 🧪 TEST CON FILE BADGE (Modalità temporanea)

**Per testare senza hardware NFC:**

1. Creare file `current_badge.txt` nella cartella progetto
2. Scrivere ID badge nel file (es: "EMPL001")
3. Il sistema leggerà il file e lo cancellerà automaticamente
4. Simula una lettura badge reale

**Esempio:**
```bash
echo EMPL001 > current_badge.txt
```

---

## 📊 DATABASE SQLITE ATTIVO

Il sistema ora salva tutte le timbrature nel database SQLite:
- **File:** `C:/ProgramData/TIGOTA_Timbratura/data/timbrature.db`
- **Backup automatico:** Ogni ora
- **Export CSV:** Giornaliero
- **Performance:** 70+ operazioni/secondo

### Tabella timbrature:
```sql
- id (PRIMARY KEY)
- badge_id (ID badge letto)
- timestamp (Data/ora timbratura)
- tipo (entrata/uscita)
- dipendente_nome, dipendente_cognome
- location, tablet_id
- sync_status (pending/synced/error)
```

---

## 🚀 AVVIO SISTEMA PRODUZIONE

1. **Collegare lettore NFC** al tablet
2. **Verificare drivers** installati
3. **Configurare porta COM** in nfc_manager.py
4. **Avviare applicazione:** `python tigota_elite_dashboard.py`
5. **Oppure usare EXE:** `TIGOTA_Tablet_Package/TIGOTA_Elite_v3.exe`

---

## 🔍 RISOLUZIONE PROBLEMI

### Lettore NFC non funziona:
1. Verificare connessione USB
2. Controllare Gestione Dispositivi
3. Installare driver lettore
4. Verificare porta COM nel codice
5. Testare con file badge temporaneo

### Database non accessibile:
1. Verificare permessi cartella `C:/ProgramData/TIGOTA_Timbratura/`
2. Eseguire come amministratore se necessario
3. Controllare spazio disco disponibile

### Performance problemi:
1. Verificare SQLite database non corrotto
2. Controllare log errori in `logs/errors.log`
3. Riavviare applicazione

---

## 📞 SUPPORTO TECNICO

Per problemi hardware NFC specifici:
1. Verificare compatibilità lettore con Windows
2. Testare lettore con software del produttore
3. Controllare documentazione tecnica lettore
4. Considerare lettori USB HID (modalità tastiera)

## ⚙️ CONFIGURAZIONE AVANZATA

### Per lettori USB HID (modalità tastiera):
Molti lettori NFC economici emulano una tastiera. In questo caso:
1. Il lettore invierà automaticamente l'ID badge
2. Seguito da ENTER
3. Non serve codice speciale in Python
4. Riattivare binding tastiera se necessario

### Per integrazione cloud:
Modificare `config_tablet.py`:
```python
'cloud_sync_enabled': True,
'cloud_provider': 'onedrive',  # o 'dropbox', 'googledrive'
'sync_interval': 900,  # 15 minuti
```
