import sys
import json
import logging
import os
from ui.app import FaceSwapApp

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FaceSwapMain")

def load_config():
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

def main():
    logger.info("Starting Face Swap Virtual Cam Application...")
    config = load_config()
    
    app = FaceSwapApp(config)
    app.mainloop()

if __name__ == "__main__":
    main()
