import threading
import queue
import logging
import cv2
import time
from typing import Callable, Optional
from core.config import AppConfig

logger = logging.getLogger("OutputThread")

class OutputThread(threading.Thread):
    def __init__(self, config: AppConfig, result_queue: queue.Queue, ui_callback: Callable):
        super().__init__(daemon=True, name="OutputThread")
        self.config = config
        self.result_queue = result_queue
        self.ui_callback = ui_callback
        self.running = False

    def start_output(self):
        self.running = True
        self.start()

    def stop_output(self):
        self.running = False

    def run(self):
        logger.info("Avviando OutputThread (PyVirtualCam)")
        
        try:
            import pyvirtualcam
        except ImportError:
            logger.error("pyvirtualcam non installato. Fallback solo GUI.")
            self._run_fallback()
            return

        # Calcolo precisione frame-time per mantenere i 30fps costanti
        target_frame_time = 1.0 / self.config.virtual_cam_fps
        
        try:
            with pyvirtualcam.Camera(
                width=self.config.virtual_cam_width, 
                height=self.config.virtual_cam_height, 
                fps=self.config.virtual_cam_fps
            ) as cam:
                logger.info(f"Virtual Camera attiva su: {cam.device}")
                
                frame_idx = 0
                while self.running:
                    try:
                        loop_start = time.time()
                        frame = self.result_queue.get(timeout=0.1)
                        
                        if frame is not None:
                            # 1. Conversione BGR -> RGB (Richiesta da VirtualCam e PIL)
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            
                            # 2. Resize se necessario (Evitiamo di farlo se già corretto)
                            h, w = rgb_frame.shape[:2]
                            if w != self.config.virtual_cam_width or h != self.config.virtual_cam_height:
                                rgb_frame = cv2.resize(rgb_frame, (self.config.virtual_cam_width, self.config.virtual_cam_height))
                                
                            # 3. Invio a Virtual Camera
                            cam.send(rgb_frame)
                            
                            # 4. Aggiornamento UI (Ogni 2 frame per non sovraccaricare il main thread)
                            frame_idx += 1
                            if frame_idx % 2 == 0:
                                self.ui_callback(rgb_frame)
                            
                            # 5. Sincronizzazione FPS per evitare jitter
                            elapsed = time.time() - loop_start
                            wait = target_frame_time - elapsed
                            if wait > 0:
                                time.sleep(wait)
                                
                    except queue.Empty:
                        continue
        except Exception as e:
            logger.error(f"Errore critico VirtualCam: {e}")
            self._run_fallback()

    def _run_fallback(self):
        """Loop di emergenza che aggiorna solo la preview GUI se la virtual cam fallisce."""
        logger.warning("Esecuzione in modalità Fallback (Solo GUI Preview)")
        while self.running:
            try:
                frame = self.result_queue.get(timeout=0.1)
                if frame is not None:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.ui_callback(rgb_frame)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Errore nel fallback: {e}")
                time.sleep(0.1)
        
        logger.info("OutputThread terminato.")
