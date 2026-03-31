# Progress Report - StreamSwapper VCam

## 🛠 Lavoro Svolto (Refactoring & Optimization)

### 1. Backend & Configurazione
- **AppConfig**: Creata classe `core/config.py` con `AppConfig` (dataclass) per gestione tipizzata dei parametri.
- **Main Engine**: Refactoring di `main.py` con logging professionale e gestione eccezioni.
- **Pipeline Threads**: Ottimizzazione dei thread di Capture, Process e Output per minimizzare la latenza.

### 2. Hardware (Webcam)
- **Lag Fix**: Ridotto avvio webcam da **11s a <1s** invertendo i backend (DSHOW come primario).
- **High Resolution**: Supporto stabile per **1920x1080 @ 50/60 FPS** via MJPG.
- **Robustness**: Implementato `grab()/retrieve()` per evitare crash `cv2.error`.

### 3. UI/UX (Interfaccia)
- **Asymmetric Layout**: Webcam (60%) | Arrow (10%) | Source (30%).
- **Smart Crop (Fill)**: Eliminazione barre nere tramite ritaglio centrale proporzionale.
- **Modern Design**: Card arrotondate (Radius 30) con blocco della propagazione (`pack_propagate(False)`).
- **Zero-Stretching**: Il video si adatta al contenitore senza mai deformarsi.

---

## 📍 Stato Attuale
Il "guscio" del software è pronto, ultra-veloce e professionale. La pipeline di streaming funziona perfettamente a 1080p. Il motore di elaborazione (`ProcessThread`) è pronto a ricevere la logica AI.

---

## 🚀 Prossimi Passi (AI Engine)
1. **InsightFace Integration**: Caricamento modelli `buffalo_l` per detection e landmarks.
2. **Inswapper Core**: Implementazione della logica di swapping dei volti tramite ONNX.
3. **Hardware Acceleration**: Configurazione di `onnxruntime-directml` per sfruttare la GPU.
4. **Face Enhancement**: Filtro per migliorare la nitidezza del volto swappato.
