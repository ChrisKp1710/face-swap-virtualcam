import threading
import queue
import time
import logging
from typing import Optional
import numpy as np
from core.config import AppConfig

logger = logging.getLogger("ProcessThread")

class ProcessThread(threading.Thread):
    def __init__(self, config: AppConfig, input_queue: queue.Queue, output_queue: queue.Queue):
        super().__init__(daemon=True, name="ProcessThread")
        self.config = config
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.running = False
        self.effect_enabled = False
        
        # Performance Tracking
        self.fps = 0.0
        self.frame_times = []
        
        # AI Engine Placeholders
        self.face_analyzer = None 
        self.face_swapper = None
        self.face_enhancer = None

    def start_process(self):
        self.running = True
        self.start()

    def stop_process(self):
        self.running = False

    def toggle_effect(self, state: bool):
        self.effect_enabled = state
        logger.info(f"Effetto Face-Swap {'ATTIVATO' if state else 'DISATTIVATO'}")

    def run(self):
        logger.info("Motore di elaborazione avviato.")
        last_fps_update = time.time()
        
        while self.running:
            try:
                # Prende l'ultimo frame con un timeout corto
                start_time = time.time()
                frame = self.input_queue.get(timeout=0.1)
                
                # --- CORE LOGIC START ---
                if not self.effect_enabled:
                    processed_frame = frame.copy()
                else:
                    # In futuro qui chiameremo:
                    # processed_frame = self.face_swapper.process(frame)
                    processed_frame = frame.copy()
                # --- CORE LOGIC END ---

                # Calcolo FPS (Media mobile su 30 frame)
                self.frame_times.append(time.time() - start_time)
                if len(self.frame_times) > 30:
                    self.frame_times.pop(0)
                
                if time.time() - last_fps_update > 1.0:
                    self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0
                    logger.debug(f"AI Performance: {self.fps:.2f} FPS")
                    last_fps_update = time.time()

                # Gestione coda output (LIFO)
                if self.output_queue.full():
                    try:
                        self.output_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                self.output_queue.put(processed_frame)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Errore critico loop AI: {e}", exc_info=True)

        logger.info("ProcessThread terminato correttamente.")
