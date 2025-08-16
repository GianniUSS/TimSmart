#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility per azzerare il database di SmartTIM/TIGOTÀ.
Opzioni:
- Senza argomenti: cancella timbrature e dipendenti (reset completo).
- --mantieni-anagrafica: cancella solo timbrature e rimuove badge dai dipendenti.
"""
import argparse
from database_sqlite import get_database_manager


def main():
    parser = argparse.ArgumentParser(description="Azzera il database")
    parser.add_argument("--mantieni-anagrafica", action="store_true", help="Non cancellare i dipendenti, rimuovi solo i badge")
    args = parser.parse_args()

    db = get_database_manager()
    ok = db.reset_database(keep_anagrafica=args.mantieni_anagrafica)
    if ok:
        print("✅ Database azzerato con successo")
    else:
        print("❌ Errore durante l'azzeramento del database")


if __name__ == "__main__":
    main()
