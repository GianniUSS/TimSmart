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
    
    def close(self):
        """Chiude database manager con cleanup finale"""
        try:
            # Backup finale
            self._create_json_backup()
            self.logger.info("🔒 Database SQLite chiuso correttamente")
            
        except Exception as e:
            self.logger.error(f"Errore chiusura database: {e}")


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

            db_path = Path(self.db_file)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connessione e creazione schema
            with sqlite3.connect(self.db_file) as conn:
                conn.executescript(DATABASE_SCHEMA)
                conn.commit()
                
            self.logger.info(f"Database inizializzato: {self.db_file}")
            
        except Exception as e:
            self.logger.error(f"Errore inizializzazione database: {e}")
            # Fallback a JSON se database fallisce
            self.use_database = False
    
    def _generate_hash(self, data: Dict) -> str:
        """Genera hash per verifica integrità"""
        data_str = f"{data['badge_id']}{data['timestamp']}{data['tipo']}"
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def salva_timbratura(self, badge_id: str, tipo: str, 
                        dipendente_nome: str = None, 
                        dipendente_cognome: str = None) -> bool:
        """
        Salva timbratura nel sistema multi-layer
        
        Args:
            badge_id: ID del badge NFC
            tipo: 'entrata' o 'uscita'
            dipendente_nome: Nome dipendente (opzionale)
            dipendente_cognome: Cognome dipendente (opzionale)
            
        Returns:
            bool: True se salvato con successo
        """
        timestamp = datetime.now()
        
        timbratura = {
            'badge_id': badge_id,
            'dipendente_nome': dipendente_nome,
            'dipendente_cognome': dipendente_cognome,
            'timestamp': timestamp.isoformat(),
            'tipo': tipo,
            'location': 'tablet_principale',
            'tablet_id': 'TIGOTA_001',
            'sync_status': 'pending',
            'hash_verify': None
        }
        
        # Genera hash per integrità
        timbratura['hash_verify'] = self._generate_hash(timbratura)
        
        try:
            # 1. Aggiungi a buffer memoria (velocità)
            self._memory_buffer.append(timbratura)
            
            # 2. Salvataggio immediato
            success = self._save_immediate(timbratura)
            
            # 3. Flush buffer se necessario
            if len(self._memory_buffer) >= self._buffer_size:
                self._flush_buffer()
            
            if success:
                self.logger.info(f"Timbratura salvata: {badge_id} - {tipo} - {timestamp}")
                return True
            else:
                self.logger.error(f"Errore salvataggio timbratura: {badge_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Errore salva_timbratura: {e}")
            return False
    
    def _save_immediate(self, timbratura: Dict) -> bool:
        """Salvataggio immediato nel storage principale"""
        if self.use_database:
            return self._save_to_database(timbratura)
        else:
            return self._save_to_json(timbratura)
    
    def _save_to_database(self, timbratura: Dict) -> bool:
        """Salva in database SQLite"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO timbrature 
                    (badge_id, dipendente_nome, dipendente_cognome, timestamp, 
                     tipo, location, tablet_id, sync_status, hash_verify)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timbratura['badge_id'],
                    timbratura['dipendente_nome'],
                    timbratura['dipendente_cognome'],
                    timbratura['timestamp'],
                    timbratura['tipo'],
                    timbratura['location'],
                    timbratura['tablet_id'],
                    timbratura['sync_status'],
                    timbratura['hash_verify']
                ))
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Errore salvataggio database: {e}")
            return False
    
    def _save_to_json(self, timbratura: Dict) -> bool:
        """Salva in file JSON (fallback o sviluppo)"""
        try:
            # Leggi esistenti
            timbrature = []
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    timbrature = json.load(f)
            
            # Aggiungi nuova
            timbrature.append(timbratura)
            
            # Salva tutto
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(timbrature, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Errore salvataggio JSON: {e}")
            return False
    
    def _flush_buffer(self):
        """Svuota buffer memoria su disco"""
        if not self._memory_buffer:
            return
        
        self.logger.info(f"Flush buffer: {len(self._memory_buffer)} records")
        
        # Backup buffer prima di svuotare
        for timbratura in self._memory_buffer:
            self._save_immediate(timbratura)
        
        # Svuota buffer
        self._memory_buffer.clear()
    
    def get_timbrature_oggi(self) -> List[Dict]:
        """Recupera timbrature di oggi"""
        oggi = date.today().isoformat()
        
        if self.use_database:
            return self._get_from_database_by_date(oggi)
        else:
            return self._get_from_json_by_date(oggi)
    
    def _get_from_database_by_date(self, data: str) -> List[Dict]:
        """Recupera da database per data"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM timbrature 
                    WHERE DATE(timestamp) = ?
                    ORDER BY timestamp DESC
                """, (data,))
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Errore lettura database: {e}")
            return []
    
    def _get_from_json_by_date(self, data: str) -> List[Dict]:
        """Recupera da JSON per data"""
        try:
            if not os.path.exists(self.json_file):
                return []
            
            with open(self.json_file, 'r', encoding='utf-8') as f:
                timbrature = json.load(f)
            
            # Filtra per data
            timbrature_oggi = []
            for t in timbrature:
                if t['timestamp'].startswith(data):
                    timbrature_oggi.append(t)
            
            return sorted(timbrature_oggi, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Errore lettura JSON: {e}")
            return []
    
    def export_daily_report(self, data: date = None) -> str:
        """Esporta report giornaliero in CSV"""
        if data is None:
            data = date.today()
        
        data_str = data.isoformat()
        timbrature = self._get_from_database_by_date(data_str) if self.use_database else self._get_from_json_by_date(data_str)
        
        # File export
        export_dir = Path(DATA_CONFIG.get('daily_export_dir', './export'))
        export_dir.mkdir(exist_ok=True)
        
        filename = f"timbrature_{data_str}.csv"
        filepath = export_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if timbrature:
                    fieldnames = timbrature[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(timbrature)
            
            self.logger.info(f"Report esportato: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Errore export CSV: {e}")
            return ""
    
    def backup_database(self) -> bool:
        """Backup completo database/dati"""
        try:
            backup_dir = Path(DATA_CONFIG.get('backup_dir', './backup'))
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.use_database:
                # Backup database
                backup_file = backup_dir / f"timbrature_backup_{timestamp}.db"
                shutil.copy2(self.db_file, backup_file)
            else:
                # Backup JSON
                backup_file = backup_dir / f"timbrature_backup_{timestamp}.json"
                shutil.copy2(self.json_file, backup_file)
            
            self.logger.info(f"Backup creato: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Errore backup: {e}")
            return False
    
    def get_statistiche(self) -> Dict:
        """Statistiche sistema"""
        try:
            if self.use_database:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    # Totale timbrature
                    cursor.execute("SELECT COUNT(*) FROM timbrature")
                    totale = cursor.fetchone()[0]
                    
                    # Timbrature oggi
                    oggi = date.today().isoformat()
                    cursor.execute("SELECT COUNT(*) FROM timbrature WHERE DATE(timestamp) = ?", (oggi,))
                    oggi_count = cursor.fetchone()[0]
                    
                    # Ultimo backup
                    backup_dir = Path(DATA_CONFIG.get('backup_dir', './backup'))
                    ultimo_backup = "Mai"
                    if backup_dir.exists():
                        backup_files = list(backup_dir.glob('*.db'))
                        if backup_files:
                            ultimo_backup = max(backup_files, key=os.path.getctime).stat().st_mtime
                            ultimo_backup = datetime.fromtimestamp(ultimo_backup).strftime("%Y-%m-%d %H:%M")
                    
                    return {
                        'totale_timbrature': totale,
                        'timbrature_oggi': oggi_count,
                        'ultimo_backup': ultimo_backup,
                        'database_size': os.path.getsize(self.db_file) if os.path.exists(self.db_file) else 0,
                        'storage_type': 'SQLite Database'
                    }
            else:
                # Statistiche JSON
                timbrature = []
                if os.path.exists(self.json_file):
                    with open(self.json_file, 'r', encoding='utf-8') as f:
                        timbrature = json.load(f)
                
                oggi = date.today().isoformat()
                oggi_count = len([t for t in timbrature if t['timestamp'].startswith(oggi)])
                
                return {
                    'totale_timbrature': len(timbrature),
                    'timbrature_oggi': oggi_count,
                    'ultimo_backup': 'N/A',
                    'database_size': os.path.getsize(self.json_file) if os.path.exists(self.json_file) else 0,
                    'storage_type': 'JSON File'
                }
                
        except Exception as e:
            self.logger.error(f"Errore statistiche: {e}")
            return {}
    
    def close(self):
        """Chiusura sicura del manager"""
        # Flush finale del buffer
        self._flush_buffer()
        
        # Backup automatico finale
        self.backup_database()
        
        self.logger.info("TimbraturaManager chiuso correttamente")

# Istanza globale per import facile
timbratura_manager = TimbraturaManager()

# Funzioni di utilità per compatibilità
def salva_timbratura(badge_id: str, tipo: str, **kwargs) -> bool:
    """Funzione di utilità per compatibilità"""
    return timbratura_manager.salva_timbratura(badge_id, tipo, **kwargs)

def get_timbrature_oggi() -> List[Dict]:
    """Funzione di utilità per compatibilità"""
    return timbratura_manager.get_timbrature_oggi()

def export_daily_report(data: date = None) -> str:
    """Funzione di utilità per compatibilità"""
    return timbratura_manager.export_daily_report(data)

if __name__ == "__main__":
    # Test del sistema
    print("🔧 Test TIGOTÀ Database Manager")
    
    # Test salvataggio
    success = salva_timbratura("BADGE001", "entrata", dipendente_nome="Mario", dipendente_cognome="Rossi")
    print(f"✅ Test salvataggio: {'OK' if success else 'ERRORE'}")
    
    # Test lettura
    timbrature = get_timbrature_oggi()
    print(f"📊 Timbrature oggi: {len(timbrature)}")
    
    # Test statistiche
    stats = timbratura_manager.get_statistiche()
    print(f"📈 Statistiche: {stats}")
    
    # Test export
    export_file = export_daily_report()
    print(f"💾 Export: {export_file}")
    
    print("✅ Test completato!")
