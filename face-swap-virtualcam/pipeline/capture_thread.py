import cv2
import threading
import queue
import time
import logging
from core.config import AppConfig

logger = logging.getLogger("CaptureThread")

class CaptureThread(threading.Thread):
    def __init__(self, config: AppConfig, output_queue: queue.Queue):
        super().__init__(daemon=True, name="CaptureThread")
        self.config = config
        self.output_queue = output_queue
        self.running = False
        self.cap = None

    def start_capture(self):
        self.running = True
        self.start()

    def stop_capture(self):
        self.running = False

    def _initialize_camera(self) -> bool:
        """Inizializzazione con priorità a DirectShow per evitare il lag di MSMF."""
        test_ids = list(dict.fromkeys([self.config.webcam_id, 0, 1]))
        
        for cam_id in test_ids:
            # 1. Prova prima DirectShow (Velocissimo su Windows per molte webcam)
            start_t = time.time()
            logger.info(f"[{cam_id}] Tentativo apertura con DirectShow (DSHOW)...")
            self.cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
            
            if self.cap and self.cap.isOpened():
                logger.info(f"[{cam_id}] DSHOW aperto in {time.time() - start_t:.2f}s")
                return True
            
            # 2. Fallback su MSMF solo se DSHOW fallisce
            start_t = time.time()
            logger.info(f"[{cam_id}] Fallback su Media Foundation (MSMF)...")
            self.cap = cv2.VideoCapture(cam_id, cv2.CAP_MSMF)
            if self.cap and self.cap.isOpened():
                logger.info(f"[{cam_id}] MSMF aperto in {time.time() - start_t:.2f}s")
                return True
                
        return False

    def run(self):
        try:
            if not self._initialize_camera():
                logger.error("Impossibile aprire alcuna webcam.")
                self.running = False
                return

            # Configurazione iper-veloce delle proprietà
            # IMPORTANTE: Impostiamo MJPG e Risoluzione PRIMA di qualsiasi lettura
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.virtual_cam_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.virtual_cam_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.virtual_cam_fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # Verifica specifiche reali
            actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"WEBCAM LIVE: {actual_w:.0f}x{actual_h:.0f} @ {actual_fps:.0f} FPS")

            while self.running:
                try:
                    # Usiamo grab() e retrieve() separati, è più stabile in caso di errori di bus
                    if not self.cap.grab():
                        continue
                        
                    ret, frame = self.cap.retrieve()
                    
                    if not ret or frame is None or frame.size == 0:
                        continue
                    
                    # Svuota buffer se pieno
                    if self.output_queue.full():
                        try:
                            self.output_queue.get_nowait()
                        except queue.Empty:
                            pass
                    
                    self.output_queue.put(frame)
                    
                except cv2.error as e:
                    logger.debug(f"Recupero da errore OpenCV momentaneo: {e}")
                    continue

        except Exception as e:
            logger.error(f"Errore fatale nel CaptureThread: {e}", exc_info=True)
        finally:
            if self.cap:
                self.cap.release()
            logger.info("CaptureThread arrestato.")
