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
    Lettore NFC per TIGOTÀ - MODALITÀ PRODUZIONE
    
    HARDWARE REALE: Sistema configurato per lettori NFC fisici
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
            print("   ⚠️ MODALITÀ SIMULAZIONE DISABILITATA")
            print("   🔌 Sistema configurato per hardware reale")
            print("   � Test temporaneo: crea file 'current_badge.txt'")
        else:
            print("   🔌 MODALITÀ HARDWARE REALE ATTIVA")
            print("   📡 Avvicina badge NFC al lettore")
            print("   📁 Test alternativo: file 'current_badge.txt'")
        
    def start_reading(self):
        """Avvia la lettura NFC in background"""
        if not self.is_reading:
            self.is_reading = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            
            if self.simulation_mode:
                print("🔄 Lettore NFC avviato (hardware disabilitato)")
                print("   � Collega lettore hardware per funzionamento")
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
                    # MODALITÀ SIMULAZIONE DISABILITATA - NO DEMO AUTOMATICHE
                    time.sleep(1)
                    # RIMOSSO: Nessuna simulazione automatica
                    # Il sistema attende solo letture hardware reali
                            
                else:
                    # MODALITÀ HARDWARE REALE - lettura continua
                    badge_data = self._read_nfc_hardware()
                    if badge_data and self.callback:
                        print(f"✅ Badge NFC reale rilevato: {badge_data}")
                        self.callback(badge_data)
                        
                        # Pausa dopo lettura per evitare duplicati
                        time.sleep(2)
                    else:
                        # Attesa breve se nessun badge rilevato
                        time.sleep(0.5)
                    
        except Exception as e:
            print(f"❌ Errore nel loop NFC: {e}")
    
    def simulate_badge_read(self, badge_id=None):
        """
        SIMULAZIONE DISABILITATA - MODALITÀ PRODUZIONE
        Questo metodo è disabilitato per evitare dati falsi
        """
        print("⚠️ SIMULAZIONE DISABILITATA - Usa solo lettore NFC hardware reale")
        print("   Per test temporaneo, usa il file current_badge.txt")
        return False
    
    def test_multiple_badges(self, count=3):
        """FUNZIONE DISABILITATA - Solo dati reali"""
        print("⚠️ Test automatici disabilitati - Solo letture hardware reali")
    
    def _read_nfc_hardware(self):
        """
        Implementazione lettura hardware NFC reale
        SUPPORTO LETTORE ID CARD USB (modalità tastiera)
        """
        try:
            # OPZIONE 1: Lettore ID Card USB (modalità tastiera) - ATTIVA
            # Il lettore "ID Card Reader" integrato funziona come tastiera
            # Legge il badge e "digita" l'ID seguito da ENTER
            
            # Controlla se c'è input in coda dalla tastiera (dal lettore badge)
            badge_data = self._read_keyboard_input()
            if badge_data:
                print(f"🔌 Badge ID Card letto: {badge_data}")
                return badge_data
            
            # OPZIONE 2: Lettore NFC seriale/USB 
            # import serial
            # try:
            #     ser = serial.Serial('COM3', 9600, timeout=1)
            #     if ser.is_open:
            #         data = ser.readline().decode('utf-8').strip()
            #         ser.close()
            #         if data and len(data) > 4:  # ID badge valido
            #             print(f"🔌 Badge NFC letto: {data}")
            #             return data
            # except serial.SerialException as e:
            #     print(f"❌ Errore lettore seriale: {e}")
            
            # OPZIONE 3: Test con file (backup)
            # Per test con file fisico quando il lettore non è disponibile
            badge_file = "current_badge.txt"
            if os.path.exists(badge_file):
                try:
                    # Prova prima con UTF-8
                    with open(badge_file, 'r', encoding='utf-8') as f:
                        badge_data = f.read().strip()
                except UnicodeDecodeError:
                    try:
                        # Se fallisce, prova con UTF-16
                        with open(badge_file, 'r', encoding='utf-16') as f:
                            badge_data = f.read().strip()
                    except UnicodeDecodeError:
                        # Ultimo tentativo con latin-1
                        with open(badge_file, 'r', encoding='latin-1') as f:
                            badge_data = f.read().strip()
                
                # Rimuovi file dopo lettura (simula lettura singola)
                os.remove(badge_file)
                
                # Pulisci caratteri strani
                if badge_data:
                    # Rimuovi BOM e caratteri di controllo
                    badge_data = badge_data.replace('\ufeff', '').replace('\x00', '').strip()
                    if badge_data and len(badge_data) >= 3:  # ID badge valido
                        print(f"🔌 Badge letto da file di test: {badge_data}")
                        return badge_data
            
            return None
            
        except Exception as e:
            print(f"❌ Errore lettura hardware NFC: {e}")
            return None
    
    def _read_keyboard_input(self):
        """
        Legge input da lettore badge USB (modalità tastiera)
        METODO ALTERNATIVO: Usa un campo di input invisibile in tkinter
        """
        try:
            # Per lettori USB che funzionano come tastiera, 
            # la soluzione migliore è catturare eventi keyboard in tkinter
            # Questo sarà gestito direttamente nell'app principale
            
            # Verifica file temporaneo creato dall'app principale
            temp_badge_file = "temp_badge_input.txt"
            if os.path.exists(temp_badge_file):
                with open(temp_badge_file, 'r') as f:
                    badge_data = f.read().strip()
                # Rimuovi file dopo lettura
                os.remove(temp_badge_file)
                if badge_data:
                    print(f"⌨️ Badge da input tastiera: {badge_data}")
                    return badge_data
            
            return None
            
        except Exception as e:
            print(f"❌ Errore lettura tastiera: {e}")
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
