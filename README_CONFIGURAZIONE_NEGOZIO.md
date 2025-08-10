# 🏪 TIGOTÀ Elite - Configurazione Negozio

## 📝 Come Configurare il Numero del Negozio

Il sistema TIGOTÀ Elite supporta ora la configurazione personalizzata del numero di negozio che viene mostrato nell'header dell'applicazione.

### 🔧 File di Configurazione

Il file `config_negozio.ini` contiene tutte le impostazioni del negozio:

```ini
[NEGOZIO]
# Numero identificativo del negozio (es: 001, 042, 123)
numero = 001

# Nome del negozio (opzionale)
nome = TIGOTÀ Store

# Città del negozio (opzionale)
citta = Milano

[DISPLAY]
# Mostra il numero del negozio nell'header (true/false)
mostra_numero = true

# Formato visualizzazione: "numero", "nome", "completo"
formato = numero
```

### 🎯 Opzioni di Configurazione

#### Numero Negozio
- **Campo**: `numero`
- **Esempio**: `001`, `042`, `123`
- **Descrizione**: Identificativo univoco del negozio

#### Nome Negozio (Opzionale)
- **Campo**: `nome`
- **Esempio**: `TIGOTÀ Milano Centro`
- **Descrizione**: Nome descrittivo del negozio

#### Città (Opzionale)
- **Campo**: `citta`
- **Esempio**: `Milano`, `Roma`, `Torino`

#### Visualizzazione
- **Campo**: `mostra_numero`
- **Valori**: `true` / `false`
- **Descrizione**: Abilita/disabilita la visualizzazione nell'header

#### Formato Display
- **Campo**: `formato`
- **Opzioni**:
  - `numero` → Mostra: "Store 001"
  - `nome` → Mostra: "TIGOTÀ Store"
  - `completo` → Mostra: "TIGOTÀ Store - Store 001"

## 🚀 Esempi di Configurazione

### Esempio 1 - Solo Numero
```ini
[NEGOZIO]
numero = 042
[DISPLAY]
mostra_numero = true
formato = numero
```
**Risultato**: `Store 042`

### Esempio 2 - Nome Completo
```ini
[NEGOZIO]
numero = 001
nome = TIGOTÀ Milano Centro
[DISPLAY]
mostra_numero = true
formato = completo
```
**Risultato**: `TIGOTÀ Milano Centro - Store 001`

### Esempio 3 - Nascosto
```ini
[DISPLAY]
mostra_numero = false
```
**Risultato**: Nessuna visualizzazione nell'header

## 📁 Posizione File

### Durante Sviluppo
Il file deve essere nella stessa cartella dell'applicazione:
```
E:\Progetti\ProgettoSmartTIM\config_negozio.ini
```

### Con Eseguibile
Il file deve essere nella stessa cartella dell'eseguibile:
```
TIGOTA_Elite_Store_v12.exe
config_negozio.ini
```

## 🔄 Aggiornamento Configurazione

1. **Modifica il file** `config_negozio.ini`
2. **Salva le modifiche**
3. **Riavvia l'applicazione**
4. **Verifica** che il nuovo numero appaia nell'header

## ⚠️ Note Importanti

- Se il file non esiste, viene usata la configurazione di default (Store 001)
- I cambiamenti richiedono il riavvio dell'applicazione
- Il file deve essere in formato UTF-8
- Non usare caratteri speciali nel numero del negozio

## 🛠️ Troubleshooting

### File Non Trovato
Se vedi: `⚠️ File configurazione non trovato`
- Verifica che `config_negozio.ini` sia nella cartella corretta
- Controlla che il nome file sia scritto correttamente

### Numero Non Visualizzato
- Verifica che `mostra_numero = true`
- Controlla la sintassi del file INI
- Riavvia l'applicazione

### Caratteri Strani
- Salva il file in formato UTF-8
- Evita caratteri speciali nel numero

## 📋 Configurazioni Predefinite per Catena

Per facilitare il deployment su più negozi, ecco alcuni template:

### Template Store Piccolo
```ini
[NEGOZIO]
numero = XXX
nome = TIGOTÀ Express
[DISPLAY]
formato = numero
```

### Template Store Grande
```ini
[NEGOZIO]
numero = XXX
nome = TIGOTÀ Superstore
citta = CITTÀ
[DISPLAY]
formato = completo
```

---

**TIGOTÀ Elite v12** - Configurazione Negozio Personalizzabile! 🏪
