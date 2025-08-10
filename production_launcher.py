#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIGOTÀ Production Launcher
Launcher sicuro per ambiente produzione con monitoring
"""

import os
import sys
import json
import logging
import psutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

class TigotaProductionLauncher:
    def __init__(self):
        self.app_name = "TIGOTÀ Sistema Timbratura"
        self.config_file = Path("C:/ProgramData/TIGOTA_Timbratura/config/production.json")
        self.log_file = Path("C:/ProgramData/TIGOTA_Timbratura/logs/launcher.log")
        self.pid_file = Path("C:/ProgramData/TIGOTA_Timbratura/tigota.pid")
        
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura logging produzione"""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            self.logger = logging.getLogger('TigotaLauncher')
            self.logger.info("=== TIGOTÀ Production Launcher avviato ===")
            
        except Exception as e:
            print(f"Errore setup logging: {e}")
            sys.exit(1)
    
    def load_config(self):
        """Carica configurazione produzione"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info("Configurazione produzione caricata")
            else:
                self.config = self.get_default_config()
                self.logger.warning("Configurazione predefinita utilizzata")
                
        except Exception as e:
            self.logger.error(f"Errore caricamento configurazione: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Configurazione predefinita"""
        return {
            "app": {"debug": False, "auto_restart": True},
            "monitoring": {"enabled": True, "check_interval": 30},
            "performance": {"max_memory_mb": 512, "max_cpu_percent": 80}
        }
    
    def check_system_requirements(self):
        """Verifica requisiti sistema"""
        self.logger.info("Verifica requisiti sistema...")
        
        # Memoria disponibile
        memory = psutil.virtual_memory()
        if memory.available < 1024 * 1024 * 1024:  # 1GB
            self.logger.warning(f"Memoria bassa: {memory.available // (1024*1024)} MB")
        
        # Spazio disco
        disk = psutil.disk_usage('C:/')
        if disk.free < 5 * 1024 * 1024 * 1024:  # 5GB
            self.logger.warning(f"Spazio disco basso: {disk.free // (1024*1024*1024)} GB")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            self.logger.warning(f"CPU usage elevato: {cpu_percent}%")
        
        self.logger.info("✅ Verifica requisiti completata")
    
    def is_app_running(self):
        """Verifica se app è già in esecuzione"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    if 'python' in process.name().lower():
                        return True, pid
                
                # PID file non valido, rimuovi
                self.pid_file.unlink()
            
            return False, None
            
        except Exception as e:
            self.logger.error(f"Errore verifica processo: {e}")
            return False, None
    
    def create_pid_file(self, pid):
        """Crea file PID"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
            self.logger.info(f"PID file creato: {pid}")
        except Exception as e:
            self.logger.error(f"Errore creazione PID file: {e}")
    
    def cleanup_pid_file(self):
        """Rimuove file PID"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                self.logger.info("PID file rimosso")
        except Exception as e:
            self.logger.error(f"Errore rimozione PID file: {e}")
    
    def launch_application(self):
        """Avvia applicazione principale"""
        self.logger.info("Avvio applicazione TIGOTÀ...")
        
        try:
            # Determina quale app avviare
            app_script = "tigota_elite_dashboard.py"
            
            # Verifica esistenza script
            if not Path(app_script).exists():
                self.logger.error(f"Script non trovato: {app_script}")
                return None
            
            # Avvia processo
            process = subprocess.Popen(
                [sys.executable, app_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            
            # Crea PID file
            self.create_pid_file(process.pid)
            
            self.logger.info(f"✅ Applicazione avviata - PID: {process.pid}")
            return process
            
        except Exception as e:
            self.logger.error(f"Errore avvio applicazione: {e}")
            return None
    
    def monitor_application(self, process):
        """Monitora applicazione in esecuzione"""
        self.logger.info("Avvio monitoraggio applicazione...")
        
        check_interval = self.config.get("monitoring", {}).get("check_interval", 30)
        max_memory = self.config.get("performance", {}).get("max_memory_mb", 512) * 1024 * 1024
        max_cpu = self.config.get("performance", {}).get("max_cpu_percent", 80)
        
        restart_count = 0
        max_restarts = 5
        
        try:
            while True:
                time.sleep(check_interval)
                
                # Verifica se processo è ancora attivo
                if process.poll() is not None:
                    self.logger.warning("Processo terminato inaspettatamente")
                    
                    if self.config.get("app", {}).get("auto_restart", True) and restart_count < max_restarts:
                        restart_count += 1
                        self.logger.info(f"Tentativo riavvio {restart_count}/{max_restarts}")
                        
                        process = self.launch_application()
                        if process is None:
                            break
                        continue
                    else:
                        self.logger.error("Troppi riavvii falliti o auto-restart disabilitato")
                        break
                
                # Monitora performance
                try:
                    app_process = psutil.Process(process.pid)
                    
                    # Memoria
                    memory_info = app_process.memory_info()
                    if memory_info.rss > max_memory:
                        self.logger.warning(f"Memoria elevata: {memory_info.rss // (1024*1024)} MB")
                    
                    # CPU
                    cpu_percent = app_process.cpu_percent()
                    if cpu_percent > max_cpu:
                        self.logger.warning(f"CPU elevato: {cpu_percent}%")
                    
                    # Log periodico stato
                    if restart_count == 0:  # Solo se non ci sono stati restart
                        self.logger.info(f"Status OK - Memoria: {memory_info.rss // (1024*1024)}MB, CPU: {cpu_percent:.1f}%")
                    
                except psutil.NoSuchProcess:
                    self.logger.error("Processo non più esistente")
                    break
                
        except KeyboardInterrupt:
            self.logger.info("Monitoraggio interrotto da utente")
        except Exception as e:
            self.logger.error(f"Errore monitoraggio: {e}")
        finally:
            self.cleanup_pid_file()
    
    def graceful_shutdown(self, process):
        """Spegnimento sicuro"""
        self.logger.info("Avvio spegnimento sicuro...")
        
        try:
            if process and process.poll() is None:
                # Termina processo gentilmente
                process.terminate()
                
                # Aspetta terminazione
                try:
                    process.wait(timeout=10)
                    self.logger.info("Processo terminato correttamente")
                except subprocess.TimeoutExpired:
                    # Forza terminazione
                    process.kill()
                    self.logger.warning("Processo forzatamente terminato")
            
            self.cleanup_pid_file()
            
        except Exception as e:
            self.logger.error(f"Errore spegnimento: {e}")
    
    def run(self):
        """Esegue launcher produzione"""
        try:
            self.logger.info(f"🚀 Avvio {self.app_name} - Modalità Produzione")
            
            # Verifica se già in esecuzione
            running, pid = self.is_app_running()
            if running:
                self.logger.warning(f"Applicazione già in esecuzione (PID: {pid})")
                return
            
            # Verifica requisiti
            self.check_system_requirements()
            
            # Avvia applicazione
            process = self.launch_application()
            if process is None:
                self.logger.error("❌ Impossibile avviare applicazione")
                return
            
            # Monitora applicazione
            self.monitor_application(process)
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Interruzione richiesta dall'utente")
        except Exception as e:
            self.logger.error(f"❌ Errore critico: {e}")
        finally:
            if 'process' in locals():
                self.graceful_shutdown(process)
            self.logger.info("=== TIGOTÀ Production Launcher terminato ===")

def main():
    """Main launcher"""
    launcher = TigotaProductionLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
