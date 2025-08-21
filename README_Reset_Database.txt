# AzzeraDatabase.exe - Tool per Reset Database SmartTIM

## Descrizione
Utility per azzerare il database di SmartTIM/TIGOTA Elite Dashboard.

## Utilizzo

### Opzione 1: Interfaccia Guidata (Raccomandato)
Esegui il file batch per un'interfaccia user-friendly:
```
reset_database.bat
```

### Opzione 2: Linea di Comando

#### Reset Completo (cancella tutto)
```
AzzeraDatabase.exe
```
⚠️ **ATTENZIONE**: Cancella tutti i dipendenti e le timbrature!

#### Mantieni Anagrafica (cancella solo timbrature)
```
AzzeraDatabase.exe --mantieni-anagrafica
```
✅ Mantiene i dipendenti ma rimuove badge e timbrature

#### Visualizza Aiuto
```
AzzeraDatabase.exe --help
```

## File Inclusi
- `AzzeraDatabase.exe` - Eseguibile principale
- `reset_database.bat` - Interfaccia guidata con menu
- `README_Reset_Database.txt` - Questo file di istruzioni

## Note Tecniche
- L'exe è standalone e non richiede Python installato
- Crea automaticamente le directory necessarie
- Registra le operazioni nei log di sistema
- Supporta Windows 10/11

## Supporto
Per problemi o domande, contattare l'amministratore del sistema SmartTIM.
