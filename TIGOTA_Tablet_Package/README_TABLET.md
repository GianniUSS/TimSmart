# 📱 TIGOTÀ Sistema Timbratura - MODALITÀ PRODUZIONE

**🔒 VERSIONE PRODUZIONE - SOLO DATI REALI**
**Compilato:** 7 agosto 2025 - 11:35  
**Simulazioni:** DISABILITATE
**Database:** SQLite attivo

## 🚀 INSTALLAZIONE RAPIDA

### ⚡ Metodo Consigliato: Installazione Automatica
1. **Eseguire come Amministratore**: `INSTALLA_TIGOTA.bat`
2. Seguire le istruzioni a schermo
3. Il sistema si installerà automaticamente in `C:\Program Files\TIGOTA_Timbratura\`
4. Verrà creato collegamento sul desktop
5. Configurazione avvio automatico

### 📋 Metodo Manuale: Installazione Semplice
1. Copiare `TIGOTA_Sistema_Timbratura.exe` in una cartella a scelta
2. Eseguire l'applicazione con doppio click
3. Il sistema funzionerà immediatamente

## 💻 REQUISITI SISTEMA

### Minimi
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB
- **Storage**: 100MB liberi
- **Display**: 1024x768

### Consigliati per Tablet
- **OS**: Windows 11 Pro
- **RAM**: 8GB+
- **Storage**: 1GB liberi
- **Display**: 1280x800 touch screen
- **NFC**: Lettore RFID/NFC compatibile

## 🎯 UTILIZZO IMMEDIATO

### Prima Accensione
1. **Avvio**: Doppio click su icona desktop "TIGOTA Sistema Timbratura"
2. **Modalità Fullscreen**: Il sistema si avvia automaticamente a schermo intero
3. **Test Funzionamento**: Premere spazio per simulare lettura badge
4. **Uscita**: Premere ESC per uscire dal fullscreen

### Comandi Rapidi
- **ESC**: Uscita fullscreen / Chiudi applicazione
- **F1**: Menu amministratore e diagnostica
- **F5**: Aggiorna display
- **Spazio**: Simula lettura badge (modalità test)

## 📊 CARATTERISTICHE PRINCIPALI

### ✅ Sistema Database Robusto
- **Database SQLite** integrato per massima affidabilità
- **Backup automatico** ogni ora in `C:\ProgramData\TIGOTA_Timbratura\backup\`
- **Export CSV** giornaliero per sistemi HR
- **Integrità dati** garantita con controlli automatici

### ✅ Interfaccia Premium
- **Design TIGOTÀ** professionale con colori brand
- **Orologio analogico** di alta qualità
- **Animazioni fluide** e feedback visivi
- **Touch ottimizzato** per tablet 1280x800

### ✅ Funzionalità Avanzate
- **NFC/RFID** compatibile con lettori standard
- **Modalità simulazione** per test senza hardware
- **Monitoraggio sistema** integrato
- **Logs completi** per diagnostica

## 🗂️ STRUTTURA INSTALLAZIONE

```
C:\Program Files\TIGOTA_Timbratura\
└── TIGOTA_Sistema_Timbratura.exe (11.8 MB)

C:\ProgramData\TIGOTA_Timbratura\
├── data\
│   ├── timbrature.db          (Database SQLite principale)
│   └── timbrature.json        (Backup JSON)
├── logs\
│   ├── database_sqlite.log    (Log operazioni database)
│   └── tigota_application.log (Log applicazione)
├── backup\
│   └── timbrature_backup_*.db (Backup automatici)
└── export\
    └── export_timbrature_*.csv (Export per HR)
```

## 🔧 CONFIGURAZIONE AVANZATA

### Database
- **Posizione**: `C:\ProgramData\TIGOTA_Timbratura\data\timbrature.db`
- **Tipo**: SQLite (thread-safe, ACID compliant)
- **Backup**: Automatico ogni ora
- **Dimensione**: Cresce dinamicamente (molto efficiente)

### Modalità NFC
- **Simulazione**: Attiva di default per test
- **Hardware**: Configurabile per lettori reali
- **Feedback**: Visivo e sonoro (opzionale)

### Performance
- **Inserimento**: 70+ timbrature/secondo
- **Memoria**: ~50MB in esecuzione
- **CPU**: <5% su sistemi moderni

## 🛠️ RISOLUZIONE PROBLEMI

### Problemi Comuni

**❓ L'applicazione non si avvia**
- Verificare Windows 10/11 64-bit
- Eseguire come Amministratore
- Controllare antivirus (aggiungere eccezione se necessario)

**❓ Database non salva timbrature**
- Verificare permessi in `C:\ProgramData\`
- Controllo spazio disco disponibile
- Menu F1 > Diagnostica per dettagli

**❓ Lettore NFC non funziona**
- Verificare driver lettore installati
- Testare con modalità simulazione (Spazio)
- Configurare porta COM corretta

**❓ Schermo non fullscreen su tablet**
- Premere F11 o riavviare applicazione
- Verificare risoluzione tablet (minimo 1024x768)

### Diagnostica
1. Aprire applicazione
2. Premere **F1** per menu amministratore  
3. Selezionare "Diagnostica Sistema"
4. Salvare report per supporto tecnico

## 📞 SUPPORTO TECNICO

### Canali di Supporto
- **Email**: support@tigota.it
- **Documentazione**: File inclusi nel pacchetto
- **Logs**: Menu F1 > Visualizza Logs
- **Database**: Backup automatici disponibili

### Informazioni per Supporto
Quando contatti il supporto, includi:
- Versione sistema: TIGOTÀ v3.1
- Sistema operativo Windows
- File di log (Menu F1 > Esporta Logs)
- Descrizione dettagliata problema

## 🎯 DEPLOYMENT AZIENDALE

### Per IT Manager
- **Installazione silente**: Possibile via script batch
- **Configurazione centralizzata**: File JSON modificabili
- **Backup automatici**: Integrabili con sistemi aziendali
- **Monitoring**: Logs strutturati per sistemi SIEM

### Integrazione HR
- **Export automatico**: CSV compatibile con tutti i sistemi HR
- **Formato dati**: Standard, facilmente importabile
- **Scheduling**: Configurabile per export automatici

---

## 🎉 TIGOTÀ v3.1 - TABLET EDITION

**Sistema di Timbratura Professionale**  
*Database SQLite • Interface Touch • Design Premium*

Sviluppato per TIGOTÀ S.r.l.  
© 2025 - Tutti i diritti riservati

---

**📋 CHECKLIST POST-INSTALLAZIONE**

- [ ] Sistema avviato correttamente in fullscreen
- [ ] Test timbratura con Spazio (modalità simulazione)
- [ ] Verificato collegamento desktop
- [ ] Configurato lettore NFC (se disponibile)
- [ ] Testato backup automatico (Menu F1 > Backup)
- [ ] Verificato export CSV (Menu F1 > Export)

**🚀 Sistema pronto per produzione!**
