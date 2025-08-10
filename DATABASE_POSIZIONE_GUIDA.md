# 🗄️ TIGOTÀ Elite - Posizione Database

## 📍 Dove si trova il Database

Quando copi l'eseguibile su un tablet, il database viene automaticamente creato in:

### 🖥️ Windows (Desktop/Tablet)
```
C:\ProgramData\TIGOTA_Timbratura\data\timbrature.db
```

### 📁 Struttura Directory Completa
```
C:\ProgramData\TIGOTA_Timbratura\
├── data\
│   ├── timbrature.db          (Database principale)
│   └── timbrature_backup_*.db (Backup automatici)
├── logs\
│   └── sistema.log           (Log applicazione)
├── backup\
│   └── backup_*.zip          (Backup compressi)
└── export\
    └── esportazioni_*.xlsx   (Export dati)
```

## 🔄 Backup Automatici

L'applicazione crea automaticamente:
- **Backup giornalieri** nella cartella `backup\`
- **Backup prima della chiusura** dell'applicazione
- **Log di sistema** per tracciare le operazioni

## 📱 Copiare su Tablet

### Procedura Completa:

1. **Copia l'eseguibile:**
   ```
   TIGOTA_Elite_Tablet_Final_v11.exe
   ```

2. **Il database viene creato automaticamente** al primo avvio in:
   ```
   C:\ProgramData\TIGOTA_Timbratura\data\
   ```

3. **Non serve copiare il database** - viene inizializzato automaticamente

## 🔒 Permessi

L'applicazione potrebbe richiedere permessi di amministratore per:
- Creare la cartella in `C:\ProgramData\`
- Scrivere il database SQLite
- Creare i file di backup

## 📊 Visualizzare il Database

Per ispezionare il database puoi usare:
- **DB Browser for SQLite** (gratuito)
- **DBeaver** (gratuito)
- Qualsiasi client SQLite

## 🚀 Migrazione Dati

### Da un tablet all'altro:
1. Copia il file `timbrature.db` dal tablet sorgente
2. Sostituisci il file nel tablet destinazione
3. Riavvia l'applicazione

### Percorsi completi:
```
Sorgente: C:\ProgramData\TIGOTA_Timbratura\data\timbrature.db
Destinazione: C:\ProgramData\TIGOTA_Timbratura\data\timbrature.db
```

## ⚠️ Note Importanti

- **Il database è portatile** - funziona su qualsiasi Windows
- **I backup sono automatici** - non perdere mai i dati
- **L'applicazione è autosufficiente** - non serve installazione
- **I dati sono persistenti** - rimangono anche dopo riavvio

## 🛠️ Troubleshooting

### Se l'applicazione non trova il database:
1. Controlla i permessi della cartella `C:\ProgramData\`
2. Esegui come amministratore la prima volta
3. Verifica che non ci siano antivirus che bloccano la scrittura

### Se vuoi cambiare percorso:
Il percorso è hardcoded per sicurezza, ma puoi:
1. Creare un link simbolico
2. Modificare il codice sorgente
3. Usare variabili d'ambiente

---
**TIGOTÀ Elite v11** - Database sempre al sicuro! 🛡️
