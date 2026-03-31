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
        """Prova a inizializzare la webcam con diversi backend, dando priorità a MSMF."""
        # Backend da testare in ordine di modernità/performance su Windows
        backends = [
            (cv2.CAP_MSMF, "Media Foundation (Nativo)"),
            (cv2.CAP_DSHOW, "DirectShow (Legacy)"),
            (None, "Default")
        ]
        
        # Prova prima l'ID preferito, poi quelli standard
        for cam_id in [self.config.webcam_id, 0, 1, 2]:
            for backend, name in backends:
                try:
                    if backend is not None:
                        self.cap = cv2.VideoCapture(cam_id, backend)
                    else:
                        self.cap = cv2.VideoCapture(cam_id)
                        
                    if self.cap and self.cap.isOpened():
                        logger.info(f"Webcam trovata: ID {cam_id} via {name}")
                        return True
                except Exception as e:
                    logger.debug(f"Fallito test ID {cam_id} con {name}: {e}")
        return False

    def run(self):
        if not self._initialize_camera():
            logger.error("Impossibile aprire alcuna webcam.")
            self.running = False
            return

        # Configurazione hardware veloce (MJPG riduce la banda USB e la latenza)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FPS, self.config.virtual_cam_fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Fondamentale per eliminare il lag

        logger.info(f"Streaming avviato a {self.config.virtual_cam_fps} FPS")

        while self.running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.warning("Frame nullo o errore lettura webcam")
                time.sleep(0.01)
                continue
            
            # Svuota buffer se pieno (LIFO pattern)
            if self.output_queue.full():
                try:
                    self.output_queue.get_nowait()
                except queue.Empty:
                    pass
            
            self.output_queue.put(frame)

        if self.cap:
            self.cap.release()
        logger.info("CaptureThread terminato correttamente.")
