# TIGOTÀ Elite Dashboard v11 - Eseguibile Produzione

## 📁 File Presenti

### Eseguibili
- **`TIGOTA_Elite_Dashboard_v11.exe`** - Versione produzione (senza console)
- **`TIGOTA_Elite_Dashboard_v11_Debug.exe`** - Versione debug (con console per troubleshooting)

### Launcher
- **`Avvia_TIGOTA_Elite_v11.bat`** - Launcher batch user-friendly

## 🚀 Come Utilizzare

### Metodo 1: Doppio click sull'eseguibile
Semplicemente fare doppio click su `TIGOTA_Elite_Dashboard_v11.exe`

### Metodo 2: Launcher batch (Consigliato)
Fare doppio click su `Avvia_TIGOTA_Elite_v11.bat` per un avvio più user-friendly

## ⚙️ Funzionalità Integrate

### Sistema di Timbratura
- ✅ Lettore NFC hardware supportato
- ✅ Lettore USB ID Card (modalità tastiera) supportato
- ✅ 4 tipi di timbratura: Inizio Giornata, Fine Giornata, Inizio Pausa, Fine Pausa
- ✅ Freccia indicatrice gigante per localizzare il lettore hardware

### Database
- ✅ SQLite integrato e automaticamente configurato
- ✅ Percorso database: `C:\ProgramData\TIGOTA_Timbratura\data\timbrature.db`
- ✅ Backup automatici giornalieri
- ✅ Export dati supportato

### Interfaccia
- ✅ Dashboard a schermo intero (Escape per uscire)
- ✅ Orologio analogico e digitale
- ✅ Contatori dipendenti con dati reali
- ✅ Feedback audio e visivo per conferma timbratura
- ✅ Icona badge NFC personalizzata caricata

## 🔧 Controlli

| Tasto | Azione |
|-------|---------|
| **ESC** | Esci dalla modalità fullscreen |
| **F1** | Pannello amministratore |
| **F5** | Aggiorna dashboard |

## 📊 Configurazione Automatica

L'eseguibile si occupa automaticamente di:
- Creazione directory sistema in `C:\ProgramData\TIGOTA_Timbratura\`
- Inizializzazione database SQLite
- Configurazione lettore NFC
- Caricamento immagine badge personalizzata
- Impostazione tema Elite

## 🛠️ Troubleshooting

### Se l'applicazione non si avvia:
1. Usare la versione debug: `TIGOTA_Elite_Dashboard_v11_Debug.exe`
2. Controllare l'output nella console per eventuali errori
3. Verificare che il file sia eseguito come Amministratore se necessario

### Se il lettore NFC non funziona:
1. Verificare che il dispositivo sia connesso
2. L'applicazione supporta anche lettori USB ID Card in modalità tastiera
3. Per test, creare un file `current_badge.txt` con un ID badge

## 📋 Specifiche Tecniche

- **Dimensione**: ~35 MB (include tutte le dipendenze)
- **Sistema Operativo**: Windows 10/11 (64-bit)
- **Framework**: Python 3.11 + tkinter
- **Database**: SQLite integrato
- **Audio**: winsound + feedback visivo

## 📱 Ottimizzato Per Tablet

L'interfaccia è ottimizzata per:
- Touchscreen
- Schermo intero
- Font grandi e leggibili
- Pulsanti touch-friendly
- Feedback visivo prominente

---
**TIGOTÀ Elite Dashboard v11** - Sistema di Timbratura Aziendale Professionale
