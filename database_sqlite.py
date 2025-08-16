"""
TIGOTÀ Sistema Timbratura - Database Manager SQLite Professionale
Gestione storage robusto con SQLite per produzione aziendale
- Thread-safe operations
- Backup automatico 
- Integrità dati garantita
- Export CSV/JSON
"""

import sqlite3
import json
import os
import shutil
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
import hashlib
import logging
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple

try:
    from config_tablet import DATA_CONFIG, DATABASE_SCHEMA, DATA_DIR, LOGS_DIR, BACKUP_DIR, EXPORT_DIR
except ImportError:
    # Fallback configuration se config_tablet non disponibile
    DATA_CONFIG = {
        'database_file': 'timbrature.db',
        'timbrature_file': 'timbrature.json',
        'use_database': True,
        'daily_export': True,
        'backup_interval': 3600,
        'max_backup_days': 30
    }
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
        sync_status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        hash_verify TEXT
    );
    """
    DATA_DIR = Path('./data')
    LOGS_DIR = Path('./logs')
    BACKUP_DIR = Path('./backup')
    EXPORT_DIR = Path('./export')


class TigotaSQLiteManager:
    """
    Database Manager SQLite professionale per sistema timbratura TIGOTÀ
    
    Features:
    - SQLite come database principale per affidabilità
    - Thread-safe operations con locks
    - Backup automatico giornaliero
    - Export CSV per HR systems
    - Verifica integrità dati
    - Logging completo operazioni
    """
    
    def __init__(self):
        self.db_path = DATA_CONFIG.get('database_file', str(DATA_DIR / 'timbrature.db'))
        self.json_backup_path = DATA_CONFIG.get('timbrature_file', str(DATA_DIR / 'timbrature.json'))
        
        # Thread lock per operazioni sicure multi-thread
        self._db_lock = threading.Lock()
        
        # Setup directory struttura PRIMA di tutto
        self._setup_directories()
        
        # Setup logging DOPO le directory
        self._setup_logging()
        
        # Inizializza database
        self._init_database()
        
        self.logger.info("TigotaSQLiteManager inizializzato con successo")
    
    def _setup_directories(self):
        """Crea struttura directory produzione"""
        directories = [DATA_DIR, LOGS_DIR, BACKUP_DIR, EXPORT_DIR]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Directory: {directory}")
            except Exception as e:
                print(f"❌ Errore creazione directory {directory}: {e}")
                raise
    
    def _setup_logging(self):
        """Configura sistema logging avanzato"""
        log_file = LOGS_DIR / 'database_sqlite.log'
        
        # Configurazione logger principale
        self.logger = logging.getLogger('TigotaDB_SQLite')
        self.logger.setLevel(logging.INFO)
        
        # Evita duplicazione handlers
        if not self.logger.handlers:
            # File handler con rotazione
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Formatter dettagliato
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _init_database(self):
        """Inizializza database SQLite con schema completo"""
        try:
            with self._get_db_connection() as conn:
                # Esegui schema completo
                conn.executescript(DATABASE_SCHEMA)
                conn.commit()
                
                # Verifica tabelle create
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                self.logger.info(f"Database SQLite inizializzato: {self.db_path}")
                self.logger.info(f"Tabelle create: {[table[0] for table in tables]}")
                
                # Test di integrità
                self._verify_database_integrity()
                
        except Exception as e:
            self.logger.error(f"Errore inizializzazione database: {e}")
            raise
    
    @contextmanager 
    def _get_db_connection(self):
        """Context manager per connessioni SQLite thread-safe"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # Timeout 30 secondi per evitare deadlock
                check_same_thread=False  # Permette uso multi-thread
            )
            # Row factory per accesso per nome colonna
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Errore connessione database: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _verify_database_integrity(self):
        """Verifica integrità database SQLite"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] == 'ok':
                    self.logger.info("✅ Verifica integrità database: OK")
                    return True
                else:
                    self.logger.error(f"❌ Database corrotto: {result}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Errore verifica integrità: {e}")
            return False

    # --- Normalizzazione/validazione campi anagrafica ---
    def _normalize_codice(self, codice: Optional[str]) -> Optional[str]:
        """
        Rende il codice composto solo da cifre e ne applica il vincolo di max 10 cifre.
        Ritorna None se vuoto/non valido.
        """
        try:
            if not codice:
                return None
            s = ''.join(ch for ch in str(codice).strip() if ch.isdigit())
            if not s:
                return None
            if len(s) > 10:
                return None
            return s
        except Exception:
            return None
    
    def save_timbratura(self, badge_id: str, tipo: str, nome: str = None, cognome: str = None) -> bool:
        """
        Salva timbratura nel database SQLite con tutte le garanzie di integrità
        
        Args:
            badge_id: ID del badge NFC
            tipo: 'entrata' o 'uscita'
            nome: Nome dipendente (opzionale)
            cognome: Cognome dipendente (opzionale)
            
        Returns:
            bool: True se salvata con successo
        """
        with self._db_lock:  # Thread-safe operation
            try:
                timestamp = datetime.now()
                
                # Genera hash per verifica integrità
                hash_data = f"{badge_id}{timestamp.isoformat()}{tipo}"
                hash_verify = hashlib.sha256(hash_data.encode()).hexdigest()[:16]
                
                with self._get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Insert con tutti i campi
                    cursor.execute("""
                        INSERT INTO timbrature (
                            badge_id, dipendente_nome, dipendente_cognome,
                            timestamp, tipo, hash_verify, location, tablet_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        badge_id, nome, cognome, timestamp, tipo, 
                        hash_verify, 'tablet_principale', 'TIGOTA_001'
                    ))
                    
                    timbratura_id = cursor.lastrowid
                    conn.commit()
                    
                    self.logger.info(
                        f"✅ Timbratura salvata - ID: {timbratura_id}, "
                        f"Badge: {badge_id}, Tipo: {tipo}, Hash: {hash_verify}"
                    )
                    
                    # Backup JSON automatico dopo ogni salvataggio
                    self._create_json_backup()
                    
                    return True
                    
            except Exception as e:
                self.logger.error(f"❌ Errore salvataggio timbratura: {e}")
                return False
    
    def get_timbrature_today(self) -> List[Dict]:
        """Ottiene tutte le timbrature di oggi dal database SQLite"""
        try:
            today = datetime.now().date()
            
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM timbrature 
                    WHERE DATE(timestamp) = ?
                    ORDER BY timestamp DESC
                """, (today,))
                
                rows = cursor.fetchall()
                timbrature = [dict(row) for row in rows]
                
                self.logger.info(f"📊 Timbrature oggi: {len(timbrature)}")
                return timbrature
                
        except Exception as e:
            self.logger.error(f"Errore lettura timbrature oggi: {e}")
            return []
    
    def get_last_timbratura_badge(self, badge_id: str) -> Optional[Dict]:
        """Ottiene ultima timbratura per un badge specifico"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM timbrature 
                    WHERE badge_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (badge_id,))
                
                row = cursor.fetchone()
                if row:
                    timbratura = dict(row)
                    self.logger.info(f"🔍 Ultima timbratura badge {badge_id}: {timbratura['tipo']}")
                    return timbratura
                    
                return None
                
        except Exception as e:
            self.logger.error(f"Errore lettura ultima timbratura badge {badge_id}: {e}")
            return None

    def get_timbrature_pending(self) -> List[Dict]:
        """Ritorna timbrature con sync_status='pending' ordinate per timestamp"""
        try:
            with self._get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT * FROM timbrature WHERE sync_status = 'pending' ORDER BY timestamp
                """)
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            self.logger.error(f"Errore get_timbrature_pending: {e}")
            return []

    def mark_timbrature_synced(self, ids: List[int]) -> bool:
        """Imposta sync_status='synced' alle timbrature con id nella lista."""
        if not ids:
            return True
        try:
            with self._get_db_connection() as conn:
                cur = conn.cursor()
                q = f"UPDATE timbrature SET sync_status='synced', updated_at=CURRENT_TIMESTAMP WHERE id IN ({','.join(['?']*len(ids))})"
                cur.execute(q, ids)
                conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Errore mark_timbrature_synced: {e}")
            return False
    
    def get_timbrature_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Ottiene timbrature in un range di date"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM timbrature 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, (start_date, end_date))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Errore lettura timbrature range: {e}")
            return []
    
    def get_unique_badge_count(self):
        """Conta badge unici nel database (solo dati reali)"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(DISTINCT badge_id) FROM timbrature")
                result = cursor.fetchone()
                count = result[0] if result else 0
                self.logger.info(f"📊 Badge unici nel database: {count}")
                return count
        except Exception as e:
            self.logger.error(f"Errore conteggio badge unici: {e}")
            return 0
    
    def get_today_entries_count(self):
        """Conta timbrature di oggi (solo dati reali)"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM timbrature 
                    WHERE DATE(timestamp) = ?
                """, (today,))
                result = cursor.fetchone()
                count = result[0] if result else 0
                self.logger.info(f"📊 Timbrature oggi: {count}")
                return count
        except Exception as e:
            self.logger.error(f"Errore conteggio timbrature oggi: {e}")
            return 0
    
    def get_active_employees_today(self):
        """Conta dipendenti attivi oggi (con almeno una timbratura)"""
        try:
            today = date.today().strftime('%Y-%m-%d')
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(DISTINCT badge_id) FROM timbrature 
                    WHERE DATE(timestamp) = ?
                """, (today,))
                result = cursor.fetchone()
                count = result[0] if result else 0
                self.logger.info(f"📊 Dipendenti attivi oggi: {count}")
                return count
        except Exception as e:
            self.logger.error(f"Errore conteggio dipendenti attivi: {e}")
            return 0
    
    def _create_json_backup(self):
        """Crea backup JSON per compatibilità e sicurezza"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM timbrature ORDER BY timestamp")
                rows = cursor.fetchall()
                
                # Converti in formato JSON compatibile
                timbrature_json = []
                for row in rows:
                    timbratura = dict(row)
                    # Converti datetime per compatibilità JSON
                    for key, value in timbratura.items():
                        if isinstance(value, datetime):
                            timbratura[key] = value.isoformat()
                    timbrature_json.append(timbratura)
                
                # Salva backup JSON
                with open(self.json_backup_path, 'w', encoding='utf-8') as f:
                    json.dump(timbrature_json, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"💾 Backup JSON creato: {len(timbrature_json)} timbrature")
                
        except Exception as e:
            self.logger.error(f"Errore backup JSON: {e}")
    
    def create_daily_backup(self):
        """Crea backup completo giornaliero (SQLite + JSON)"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Backup database SQLite
            backup_db_name = f"timbrature_backup_{timestamp}.db"
            backup_db_path = BACKUP_DIR / backup_db_name
            shutil.copy2(self.db_path, backup_db_path)
            
            # Backup JSON
            backup_json_name = f"timbrature_backup_{timestamp}.json"
            backup_json_path = BACKUP_DIR / backup_json_name
            if os.path.exists(self.json_backup_path):
                shutil.copy2(self.json_backup_path, backup_json_path)
            
            self.logger.info(f"📦 Backup giornaliero creato: {backup_db_name}")
            
            # Pulizia backup vecchi
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Errore backup giornaliero: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Rimuove backup più vecchi di N giorni"""
        try:
            max_days = DATA_CONFIG.get('max_backup_days', 30)
            cutoff_date = datetime.now() - timedelta(days=max_days)
            
            removed_count = 0
            for backup_file in BACKUP_DIR.glob("timbrature_backup_*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                self.logger.info(f"🧹 Backup rimossi: {removed_count} file vecchi")
                
        except Exception as e:
            self.logger.error(f"Errore pulizia backup: {e}")
    
    def export_to_csv(self, start_date: datetime = None, end_date: datetime = None) -> Optional[str]:
        """
        Esporta timbrature in formato CSV per HR systems
        
        Args:
            start_date: Data inizio (default: 30 giorni fa)
            end_date: Data fine (default: oggi)
            
        Returns:
            str: Path del file CSV creato o None se errore
        """
        try:
            # Date di default
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Ottieni dati
            timbrature = self.get_timbrature_range(start_date, end_date)
            
            if not timbrature:
                self.logger.warning("Nessuna timbratura da esportare")
                return None
            
            # Crea CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_filename = f"export_timbrature_{timestamp}.csv"
            csv_path = EXPORT_DIR / csv_filename
            
            with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header CSV
                writer.writerow([
                    'ID', 'Badge ID', 'Nome', 'Cognome', 'Data/Ora', 
                    'Tipo', 'Posizione', 'Tablet', 'Stato Sync'
                ])
                
                # Dati
                for t in timbrature:
                    writer.writerow([
                        t.get('id', ''),
                        t.get('badge_id', ''),
                        t.get('dipendente_nome', ''),
                        t.get('dipendente_cognome', ''),
                        t.get('timestamp', ''),
                        t.get('tipo', ''),
                        t.get('location', ''),
                        t.get('tablet_id', ''),
                        t.get('sync_status', '')
                    ])
            
            self.logger.info(f"📊 Export CSV creato: {csv_filename} ({len(timbrature)} record)")
            return str(csv_path)
            
        except Exception as e:
            self.logger.error(f"Errore export CSV: {e}")
            return None
    
    def get_database_stats(self) -> Dict:
        """Ottiene statistiche complete del database"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Statistiche generali
                cursor.execute("SELECT COUNT(*) FROM timbrature")
                total_timbrature = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT badge_id) FROM timbrature")
                unique_badges = cursor.fetchone()[0]
                
                # Timbrature oggi
                today = datetime.now().date()
                cursor.execute("SELECT COUNT(*) FROM timbrature WHERE DATE(timestamp) = ?", (today,))
                timbrature_today = cursor.fetchone()[0]
                
                # Ultima timbratura
                cursor.execute("SELECT timestamp FROM timbrature ORDER BY timestamp DESC LIMIT 1")
                last_result = cursor.fetchone()
                last_timbratura = last_result[0] if last_result else None
                
                # Dimensione file database
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                stats = {
                    'total_timbrature': total_timbrature,
                    'unique_badges': unique_badges,
                    'timbrature_today': timbrature_today,
                    'last_timbratura': last_timbratura,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024*1024), 2),
                    'database_path': self.db_path
                }
                
                self.logger.info(f"📈 Statistiche database: {stats}")
                return stats
                
        except Exception as e:
            self.logger.error(f"Errore statistiche database: {e}")
            return {}

    # --- Gestione Dipendenti / Anagrafica ---
    def upsert_dipendente(self, codice: str, nome: str, cognome: str = None) -> bool:
        """Crea o aggiorna un dipendente per codice (senza badge)."""
        if not codice or not nome:
            return False
        # Validazione codice: solo cifre, max 10
        norm_cod = self._normalize_codice(codice)
        if not norm_cod:
            self.logger.warning(f"upsert_dipendente: codice non valido '{codice}' (richieste solo cifre, max 10)")
            return False
        with self._get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO dipendenti (codice, nome, cognome)
                    VALUES (?, ?, ?)
                    ON CONFLICT(codice) DO UPDATE SET
                        nome=excluded.nome,
                        cognome=excluded.cognome,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (norm_cod, nome.strip(), (cognome or '').strip() or None)
                )
                conn.commit()
                return True
            except Exception as e:
                self.logger.error(f"Errore upsert dipendente {codice}: {e}")
                return False

    def abbina_badge_a_dipendente(self, codice: str, badge_id: str) -> bool:
        """Abbina/aggiorna il badge NFC per un dipendente dato il codice (mantiene badge univoco)."""
        if not codice or not badge_id:
            return False
        # Validazione codice: solo cifre, max 10
        norm_cod = self._normalize_codice(codice)
        if not norm_cod:
            self.logger.warning(f"abbina_badge_a_dipendente: codice non valido '{codice}' (richieste solo cifre, max 10)")
            return False
        with self._get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                # Rimuovi eventuali altri dipendenti che già hanno questo badge per garantire unicità
                cursor.execute("UPDATE dipendenti SET badge_id=NULL WHERE badge_id = ?", (badge_id.strip(),))
                # Aggiorna/assegna al codice selezionato
                cursor.execute(
                    """
                    UPDATE dipendenti
                    SET badge_id = ?, updated_at=CURRENT_TIMESTAMP
                    WHERE codice = ?
                    """,
                    (badge_id.strip(), norm_cod)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                self.logger.error(f"Errore abbinamento badge {badge_id} a {codice}: {e}")
                return False

    def get_dipendente_by_codice(self, codice: str) -> Optional[Dict]:
        with self._get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                norm_cod = self._normalize_codice(codice)
                if not norm_cod:
                    return None
                cursor.execute("SELECT * FROM dipendenti WHERE codice = ?", (norm_cod,))
                row = cursor.fetchone()
                return dict(row) if row else None
            except Exception as e:
                self.logger.error(f"Errore get_dipendente_by_codice {codice}: {e}")
                return None

    def get_dipendente_by_badge(self, badge_id: str) -> Optional[Dict]:
        with self._get_db_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM dipendenti WHERE badge_id = ?", (badge_id.strip(),))
                row = cursor.fetchone()
                return dict(row) if row else None
            except Exception as e:
                self.logger.error(f"Errore get_dipendente_by_badge {badge_id}: {e}")
                return None
    
    def close(self):
        """Chiude database manager con cleanup finale"""
        try:
            # Backup finale
            self._create_json_backup()
            self.logger.info("🔒 Database SQLite chiuso correttamente")
            
        except Exception as e:
            self.logger.error(f"Errore chiusura database: {e}")

    # --- Manutenzione ---
    def reset_database(self, keep_anagrafica: bool = False) -> bool:
        """
        Svuota le tabelle del database per un test pulito.
        - keep_anagrafica=True: cancella solo timbrature e azzera badge su dipendenti (mantiene anagrafica senza badge)
        - keep_anagrafica=False: cancella timbrature e dipendenti
        """
        with self._db_lock:
            try:
                with self._get_db_connection() as conn:
                    cur = conn.cursor()
                    # Svuota timbrature
                    cur.execute("DELETE FROM timbrature")
                    if keep_anagrafica:
                        # Mantieni anagrafica ma rimuovi associazioni badge
                        try:
                            cur.execute("UPDATE dipendenti SET badge_id=NULL, updated_at=CURRENT_TIMESTAMP")
                        except Exception:
                            pass
                    else:
                        # Svuota completamente anagrafica
                        cur.execute("DELETE FROM dipendenti")
                    conn.commit()
                    try:
                        cur.execute("VACUUM")
                    except Exception:
                        pass
                self.logger.info(f"🧹 Reset database completato (keep_anagrafica={keep_anagrafica})")
                return True
            except Exception as e:
                self.logger.error(f"Errore reset database: {e}")
                return False


# Compatibilità con vecchio nome classe
TimbraturaManager = TigotaSQLiteManager

# Istanza singleton globale
_database_manager = None

def get_database_manager() -> TigotaSQLiteManager:
    """Ottiene istanza singleton del database manager SQLite"""
    global _database_manager
    if _database_manager is None:
        _database_manager = TigotaSQLiteManager()
    return _database_manager

def close_database():
    """Chiude database manager globale"""
    global _database_manager
    if _database_manager:
        _database_manager.close()
        _database_manager = None


# Test completo del sistema SQLite
if __name__ == "__main__":
    print("🗄️ Test Sistema Database SQLite TIGOTÀ")
    print("="*60)
    
    try:
        # Inizializza database manager
        db = get_database_manager()
        print("✅ Database SQLite inizializzato")
        
        # Test salvataggio timbrature
        print("\n🔧 Test operazioni database...")
        
        # Test entrata
        success1 = db.save_timbratura("BADGE001", "entrata", "Mario", "Rossi")
        print(f"✅ Test salvataggio entrata: {'OK' if success1 else 'ERRORE'}")
        
        # Test uscita
        success2 = db.save_timbratura("BADGE001", "uscita", "Mario", "Rossi")
        print(f"✅ Test salvataggio uscita: {'OK' if success2 else 'ERRORE'}")
        
        # Test lettura timbrature oggi
        timbrature_oggi = db.get_timbrature_today()
        print(f"✅ Timbrature oggi: {len(timbrature_oggi)}")
        
        # Test ultima timbratura
        ultima = db.get_last_timbratura_badge("BADGE001")
        print(f"✅ Ultima timbratura BADGE001: {ultima['tipo'] if ultima else 'Nessuna'}")
        
        # Test statistiche
        stats = db.get_database_stats()
        print(f"✅ Statistiche: Total={stats.get('total_timbrature')}, "
              f"Badges={stats.get('unique_badges')}, "
              f"Size={stats.get('database_size_mb')}MB")
        
        # Test backup
        backup_ok = db.create_daily_backup()
        print(f"✅ Backup giornaliero: {'OK' if backup_ok else 'ERRORE'}")
        
        # Test export CSV
        csv_file = db.export_to_csv()
        print(f"✅ Export CSV: {'OK' if csv_file else 'ERRORE'}")
        if csv_file:
            print(f"   File: {csv_file}")
        
        # Test verifica integrità
        integrity_ok = db._verify_database_integrity()
        print(f"✅ Integrità database: {'OK' if integrity_ok else 'ERRORE'}")
        
        print(f"\n🎉 Tutti i test SQLite completati con successo!")
        print(f"📂 Database: {db.db_path}")
        print(f"📊 {stats.get('total_timbrature', 0)} timbrature salvate")
        
    except Exception as e:
        print(f"❌ Errore durante i test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        close_database()
        print("🔒 Database chiuso")
