#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test dei suoni di SmartTIM per verificare che funzionino correttamente."""

import winsound
import time

def test_suoni():
    print("🔊 Test dei suoni di SmartTIM")
    print("=" * 40)
    
    print("\n1. ✅ Suono timbratura RIUSCITA (badge riconosciuto)")
    print("   - Beep acuto 1000Hz per 150ms")
    try:
        winsound.Beep(1000, 150)
        print("   ✅ Suono primario OK")
    except Exception as e:
        print(f"   ❌ Errore suono primario: {e}")
        try:
            winsound.MessageBeep()
            print("   ✅ Fallback OK")
        except Exception as e2:
            print(f"   ❌ Errore fallback: {e2}")
    
    time.sleep(1)
    
    print("\n2. ❌ Suono badge NON RICONOSCIUTO")
    print("   - Beep grave 440Hz per 220ms")
    try:
        winsound.Beep(440, 220)
        print("   ✅ Suono primario OK")
    except Exception as e:
        print(f"   ❌ Errore suono primario: {e}")
        try:
            winsound.MessageBeep(winsound.MB_ICONHAND)
            print("   ✅ Fallback OK")
        except Exception as e2:
            print(f"   ❌ Errore fallback: {e2}")
    
    time.sleep(1)
    
    print("\n3. 🔊 Suoni di CONTROLLO (usati nel wizard/impostazioni)")
    print("   - Beep errore 800Hz per 200ms")
    try:
        winsound.Beep(800, 200)
        print("   ✅ Suono errore breve OK")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    time.sleep(1)
    
    print("   - Beep errore grave 800Hz per 500ms")
    try:
        winsound.Beep(800, 500)
        print("   ✅ Suono errore lungo OK")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    time.sleep(1)
    
    print("   - Beep successo 800Hz per 300ms")
    try:
        winsound.Beep(800, 300)
        print("   ✅ Suono successo OK")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    
    print("\n🎵 Test completato!")
    print("Se hai sentito tutti i suoni, il sistema audio è funzionante.")

if __name__ == "__main__":
    test_suoni()
