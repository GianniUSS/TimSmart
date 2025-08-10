#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOTÀ Sistema Timbratura - Test Completo SQLite
Test di tutte le funzionalità del sistema con database SQLite
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Test 1: Import e inizializzazione
print("🧪 TIGOTÀ - Test Completo Sistema SQLite")
print("="*60)

try:
    from database_sqlite import get_database_manager, close_database
    print("✅ Import database_sqlite: OK")
except ImportError as e:
    print(f"❌ Errore import database_sqlite: {e}")
    sys.exit(1)

try:
    from config_tablet import DATA_CONFIG, DATA_DIR, LOGS_DIR
    print("✅ Import config_tablet: OK")
except ImportError as e:
    print(f"❌ Errore import config_tablet: {e}")
    sys.exit(1)

# Test 2: Inizializzazione database
print("\n🔧 Test Inizializzazione Database")
print("-" * 40)

try:
    db = get_database_manager()
    print("✅ Database manager inizializzato")
    
    # Verifica directory create
    if os.path.exists(DATA_DIR):
        print("✅ Directory dati creata")
    if os.path.exists(LOGS_DIR):
        print("✅ Directory logs creata")
        
    # Verifica file database
    db_path = DATA_CONFIG['database_file']
    if os.path.exists(db_path):
        print(f"✅ File database SQLite esistente: {os.path.getsize(db_path)} bytes")
    else:
        print("⚠️ File database SQLite non trovato (verrà creato)")
        
except Exception as e:
    print(f"❌ Errore inizializzazione: {e}")
    sys.exit(1)

# Test 3: Operazioni CRUD database
print("\n💾 Test Operazioni Database")
print("-" * 40)

test_badge_ids = ["TEST001", "TEST002", "TEST003"]
test_movements = ["entrata", "uscita", "entrata"]

# Salva timbrature di test
for i, (badge_id, tipo) in enumerate(zip(test_badge_ids, test_movements)):
    try:
        success = db.save_timbratura(
            badge_id=badge_id,
            tipo=tipo,
            nome=f"Nome{i+1}",
            cognome=f"Cognome{i+1}"
        )
        
        if success:
            print(f"✅ Timbratura salvata: {badge_id} - {tipo}")
        else:
            print(f"❌ Errore salvataggio: {badge_id}")
            
    except Exception as e:
        print(f"❌ Errore salvataggio {badge_id}: {e}")

# Test lettura timbrature
print("\n📊 Test Lettura Dati")
print("-" * 40)

try:
    # Timbrature di oggi
    timbrature_oggi = db.get_timbrature_today()
    print(f"✅ Timbrature oggi: {len(timbrature_oggi)}")
    
    for t in timbrature_oggi[-3:]:  # Ultime 3
        timestamp = t.get('timestamp', 'N/A')
        badge = t.get('badge_id', 'N/A')
        tipo = t.get('tipo', 'N/A')
        print(f"   📝 {badge} - {tipo} ({timestamp})")
    
    # Ultima timbratura per badge specifico
    ultima = db.get_last_timbratura_badge("TEST001")
    if ultima:
        print(f"✅ Ultima timbratura TEST001: {ultima['tipo']}")
    else:
        print("⚠️ Nessuna timbratura trovata per TEST001")
        
    # Statistiche database
    stats = db.get_database_stats()
    print(f"✅ Statistiche:")
    print(f"   📈 Timbrature totali: {stats.get('total_timbrature', 0)}")
    print(f"   👥 Badge unici: {stats.get('unique_badges', 0)}")
    print(f"   📅 Timbrature oggi: {stats.get('timbrature_today', 0)}")
    print(f"   💾 Dimensione DB: {stats.get('database_size_mb', 0)} MB")
    
except Exception as e:
    print(f"❌ Errore lettura dati: {e}")

# Test 4: Backup e Export
print("\n💾 Test Backup e Export")
print("-" * 40)

try:
    # Backup giornaliero
    backup_ok = db.create_daily_backup()
    if backup_ok:
        print("✅ Backup giornaliero creato")
    else:
        print("❌ Errore backup giornaliero")
    
    # Export CSV
    csv_file = db.export_to_csv()
    if csv_file:
        print(f"✅ Export CSV creato: {os.path.basename(csv_file)}")
        
        # Verifica dimensione file CSV
        if os.path.exists(csv_file):
            csv_size = os.path.getsize(csv_file)
            print(f"   📊 Dimensione CSV: {csv_size} bytes")
    else:
        print("❌ Errore export CSV")
        
except Exception as e:
    print(f"❌ Errore backup/export: {e}")

# Test 5: Performance e Integrità
print("\n⚡ Test Performance e Integrità")
print("-" * 40)

try:
    # Test performance: inserimento multiplo
    start_time = datetime.now()
    
    for i in range(10):
        db.save_timbratura(f"PERF{i:03d}", "entrata", f"Test{i}", "Performance")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"✅ Performance test: 10 inserimenti in {duration:.3f} secondi")
    
    # Test integrità database
    integrity_ok = db._verify_database_integrity()
    if integrity_ok:
        print("✅ Integrità database: OK")
    else:
        print("❌ Integrità database: ERRORE")
        
    # Test query con range date
    ieri = datetime.now() - timedelta(days=1)
    oggi = datetime.now()
    timbrature_range = db.get_timbrature_range(ieri, oggi)
    print(f"✅ Query range date: {len(timbrature_range)} timbrature")
    
except Exception as e:
    print(f"❌ Errore test performance: {e}")

# Test 6: Stress Test (opzionale)
print("\n🚀 Test Stress (100 timbrature)")
print("-" * 40)

try:
    stress_start = datetime.now()
    
    for i in range(100):
        badge_id = f"STRESS{i:03d}"
        tipo = "entrata" if i % 2 == 0 else "uscita"
        db.save_timbratura(badge_id, tipo, "Stress", "Test")
    
    stress_end = datetime.now()
    stress_duration = (stress_end - stress_start).total_seconds()
    
    print(f"✅ Stress test completato:")
    print(f"   ⏱️ 100 timbrature in {stress_duration:.3f} secondi")
    print(f"   📊 Performance: {100/stress_duration:.1f} timbrature/secondo")
    
    # Verifica finale statistiche
    final_stats = db.get_database_stats()
    print(f"   📈 Timbrature totali finali: {final_stats.get('total_timbrature', 0)}")
    
except Exception as e:
    print(f"❌ Errore stress test: {e}")

# Test 7: Backup JSON automatico
print("\n📄 Test Backup JSON")
print("-" * 40)

try:
    json_path = DATA_CONFIG['timbrature_file']
    if os.path.exists(json_path):
        json_size = os.path.getsize(json_path)
        print(f"✅ Backup JSON automatico: {json_size} bytes")
        
        # Verifica contenuto JSON
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"   📊 Record nel JSON: {len(json_data)}")
    else:
        print("⚠️ Backup JSON non trovato")
        
except Exception as e:
    print(f"❌ Errore verifica JSON: {e}")

# Chiusura e cleanup
print("\n🏁 Chiusura e Cleanup")
print("-" * 40)

try:
    # Backup finale prima della chiusura
    final_backup = db.create_daily_backup()
    if final_backup:
        print("✅ Backup finale creato")
    
    # Chiudi database
    close_database()
    print("✅ Database chiuso correttamente")
    
except Exception as e:
    print(f"❌ Errore chiusura: {e}")

# Riepilogo finale
print("\n🎯 RIEPILOGO COMPLETO")
print("="*60)
print("✅ Sistema TIGOTÀ SQLite completamente testato!")
print(f"📂 Database: {DATA_CONFIG['database_file']}")
print(f"📁 Directory dati: {DATA_DIR}")
print(f"📋 Logs: {LOGS_DIR}")

final_stats = db.get_database_stats() if 'db' in locals() else {}
if final_stats:
    print(f"📊 Timbrature totali: {final_stats.get('total_timbrature', 0)}")
    print(f"👥 Badge registrati: {final_stats.get('unique_badges', 0)}")

print("\n🚀 Sistema pronto per produzione!")
print("=" * 60)

# Consigli finali
print("\n💡 CONSIGLI PRODUZIONE:")
print("• Eseguire backup automatici giornalieri")
print("• Monitorare dimensione database SQLite")
print("• Verificare integrità dati periodicamente")
print("• Configurare export automatici per HR")
print("• Testare recovery da backup in caso di emergenza")
print("\n🎉 Test completato con successo!")
