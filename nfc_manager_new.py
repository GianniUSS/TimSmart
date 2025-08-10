#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo per la gestione delle letture NFC con simulazione tastiera
SmartTIM - Sistema di Timbratura TIGOTÀ
"""

import threading
import time
from datetime import datetime
import json
import os
import random

class NFCReader:
    """
    Lettore NFC con supporto simulazione per test
    
    MODALITÀ TEST: Premi SPAZIO per simulare lettura badge
    MODALITÀ PRODUZIONE: Collegare lettore NFC reale
    """
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_reading = False
        self.reader_thread = None
        
        # Modalità simulazione per test (da config)
        from config_tablet import NFC_CONFIG
        self.simulation_mode = NFC_CONFIG.get('simulation_mode', True)
        self.last_simulation_time = 0
        
        print("🔧 NFCReader inizializzato")
        if self.simulation_mode:
            print("   📱 MODALITÀ SIMULAZIONE ATTIVA")
            print("   ⌨️  Premi SPAZIO per simulare lettura badge")
            print("   🎯 Il sistema genererà automaticamente ID badge di test")
        else:
            print("   🔌 MODALITÀ HARDWARE REALE")
            print("   📡 Avvicina badge NFC al lettore")
        
    def start_reading(self):
        """Avvia la lettura NFC in background"""
        if not self.is_reading:
            self.is_reading = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            
            if self.simulation_mode:
                print("🔄 Lettore NFC avviato (modalità simulazione)")
                print("   👆 Usa SPAZIO per simulare badge")
            else:
                print("🔄 Lettore NFC hardware avviato")
            
    def stop_reading(self):
        """Ferma la lettura NFC"""
        self.is_reading = False
        if self.reader_thread:
            self.reader_thread.join(timeout=1)
        print("🔒 Lettore NFC fermato")
            
    def _read_loop(self):
        """Loop principale per la lettura NFC"""
        try:
            while self.is_reading:
                if self.simulation_mode:
                    # In modalità simulazione, attesa breve
                    time.sleep(0.5)
                    
                    # Simulazione automatica occasionale per demo (molto rara)
                    if random.random() < 0.0005:  # 0.05% probabilità
                        badge_id = f"AUTO{random.randint(100,999):03d}"
                        print(f"🎲 Demo automatica: {badge_id}")
                        if self.callback:
                            self.callback(badge_id)
                            
                else:
                    # Modalità hardware reale - implementare qui la logica NFC
                    time.sleep(1)
                    
                    # TODO: Implementare lettura hardware NFC
                    # Esempio con pynfc, pyserial, o altra libreria
                    # badge_data = self._read_nfc_hardware()
                    # if badge_data and self.callback:
                    #     self.callback(badge_data)
                    
        except Exception as e:
            print(f"❌ Errore nel loop NFC: {e}")
    
    def simulate_badge_read(self, badge_id=None):
        """
        Simula lettura badge (chiamata da binding tastiera)
        Questo metodo viene chiamato quando l'utente preme SPAZIO
        """
        if not badge_id:
            # Genera badge di test con pattern realistico
            badge_types = ["TIGOTA", "EMPL", "VISIT", "ADMIN", "MNGR"]
            badge_type = random.choice(badge_types)
            badge_number = random.randint(100, 999)
            badge_id = f"{badge_type}{badge_number:03d}"
        
        current_time = time.time()
        
        # Previeni letture troppo ravvicinate (debounce)
        if current_time - self.last_simulation_time < 1.5:
            print("⚠️ Attendi almeno 1.5 secondi tra le simulazioni")
            return False
            
        self.last_simulation_time = current_time
        
        print(f"🎯 SIMULAZIONE BADGE: {badge_id}")
        print(f"   📅 Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        
        if self.callback:
            self.callback(badge_id)
            return True
        else:
            print("⚠️ Nessun callback configurato per NFC")
            return False
    
    def test_multiple_badges(self, count=3):
        """Test con simulazione di più badge in sequenza"""
        print(f"🧪 Test simulazione {count} badge...")
        
        test_badges = [
            "TIGOTA001", "TIGOTA002", "TIGOTA003",
            "EMPL001", "EMPL002", "ADMIN001"
        ]
        
        for i in range(count):
            badge_id = test_badges[i % len(test_badges)]
            print(f"   {i+1}/{count}: {badge_id}")
            
            if self.callback:
                self.callback(badge_id)
            
            # Pausa tra simulazioni
            time.sleep(2)
    
    def _read_nfc_hardware(self):
        """
        Implementazione lettura hardware NFC reale
        DA IMPLEMENTARE quando si collega hardware
        """
        # Placeholder per hardware reale
        # 
        # Esempi di implementazione:
        #
        # OPZIONE 1: Lettore seriale/USB
        # import serial
        # ser = serial.Serial('COM3', 9600)
        # data = ser.readline().decode().strip()
        # return data if data else None
        #
        # OPZIONE 2: Lettore NFC standard
        # import nfc
        # clf = nfc.ContactlessFrontend('usb')
        # tag = clf.connect(rdwr={'on-connect': lambda tag: False})
        # return tag.identifier.hex() if tag else None
        #
        # OPZIONE 3: Lettore RFID specifico
        # from mfrc522 import SimpleMFRC522
        # reader = SimpleMFRC522()
        # id, text = reader.read()
        # return str(id) if id else None
        
        return None
    
    def enable_hardware_mode(self):
        """Attiva modalità hardware reale"""
        self.simulation_mode = False
        print("🔌 Modalità hardware NFC attivata")
    
    def enable_simulation_mode(self):
        """Attiva modalità simulazione"""
        self.simulation_mode = True
        print("📱 Modalità simulazione NFC attivata")


# Compatibility: mantieni la vecchia classe per retrocompatibilità
class TimbratureManager:
    """
    Classe obsoleta - ora utilizziamo database_sqlite.py
    Mantenuta per compatibilità
    """
    
    def __init__(self, data_file="timbrature.json"):
        print("⚠️ TimbratureManager è obsoleto - usa database_sqlite.py")
        self.data_file = data_file
        
    def registra_timbratura(self, badge_id):
        print(f"⚠️ Usa database_sqlite per salvare timbratura: {badge_id}")
        return {
            'badge_id': badge_id,
            'timestamp': datetime.now(),
            'tipo_movimento': 'entrata'  # Placeholder
        }


# Test del modulo NFC
if __name__ == "__main__":
    print("🧪 Test Modulo NFC TIGOTÀ")
    print("="*40)
    
    def test_callback(badge_id):
        print(f"✅ Callback ricevuto: {badge_id}")
    
    # Test lettore NFC
    reader = NFCReader(callback=test_callback)
    reader.start_reading()
    
    # Test simulazioni
    print("\n🎯 Test simulazioni...")
    reader.simulate_badge_read("TEST001")
    time.sleep(2)
    reader.simulate_badge_read("TEST002")
    
    # Test automatico
    print("\n🧪 Test automatico 3 badge...")
    reader.test_multiple_badges(3)
    
    reader.stop_reading()
    print("\n✅ Test NFC completato!")
