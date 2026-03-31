import sys
import logging
import argparse
from pathlib import Path
from core.config import AppConfig
from ui.app import FaceSwapApp

# Configurazione del logging professionale
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("FaceSwapMain")

def parse_args():
    parser = argparse.ArgumentParser(description="Real-Time Face-Swap Virtual Cam")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    logger.info("="*50)
    logger.info("STREAMSAPPER - VIRTUAL CAM EDITION")
    logger.info("Professional AI Face-Swap Engine")
    logger.info("="*50)
    
    # Caricamento configurazione tipizzata
    config = AppConfig.load(args.config)
    
    try:
        app = FaceSwapApp(config)
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Chiusura forzata dall'utente.")
    except Exception as e:
        logger.error(f"Errore critico all'avvio: {e}", exc_info=args.debug)
    finally:
        # Salvataggio impostazioni all'uscita
        config.save(args.config)
        logger.info("Sessione terminata correttamente.")

if __name__ == "__main__":
    main()
