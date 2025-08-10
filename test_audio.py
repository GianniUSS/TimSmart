#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Audio per TIGOTÀ - Verifica funzionamento suoni
"""

import winsound
import time

def test_audio_systems():
    """Testa diversi sistemi audio disponibili"""
    print("🔊 Test sistemi audio TIGOTÀ...")
    
    try:
        print("1. Test MessageBeep MB_OK...")
        winsound.MessageBeep(winsound.MB_OK)
        time.sleep(1)
        print("✅ MessageBeep MB_OK completato")
    except Exception as e:
        print(f"❌ Errore MessageBeep MB_OK: {e}")
    
    try:
        print("2. Test MessageBeep MB_ICONHAND...")
        winsound.MessageBeep(winsound.MB_ICONHAND)
        time.sleep(1)
        print("✅ MessageBeep MB_ICONHAND completato")
    except Exception as e:
        print(f"❌ Errore MessageBeep MB_ICONHAND: {e}")
    
    try:
        print("3. Test MessageBeep MB_ICONQUESTION...")
        winsound.MessageBeep(winsound.MB_ICONQUESTION)
        time.sleep(1)
        print("✅ MessageBeep MB_ICONQUESTION completato")
    except Exception as e:
        print(f"❌ Errore MessageBeep MB_ICONQUESTION: {e}")
    
    try:
        print("4. Test MessageBeep MB_ICONASTERISK...")
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        time.sleep(1)
        print("✅ MessageBeep MB_ICONASTERISK completato")
    except Exception as e:
        print(f"❌ Errore MessageBeep MB_ICONASTERISK: {e}")
    
    try:
        print("5. Test Beep base (500Hz, 500ms)...")
        winsound.Beep(500, 500)
        time.sleep(0.5)
        print("✅ Beep base completato")
    except Exception as e:
        print(f"❌ Errore Beep base: {e}")
    
    try:
        print("6. Test Beep alto (1000Hz, 300ms)...")
        winsound.Beep(1000, 300)
        time.sleep(0.3)
        print("✅ Beep alto completato")
    except Exception as e:
        print(f"❌ Errore Beep alto: {e}")
    
    print("🎯 Test audio completato!")

if __name__ == "__main__":
    test_audio_systems()
