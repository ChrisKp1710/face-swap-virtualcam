# Real-Time Face-Swap Virtual Cam

Il progetto mira a sviluppare un'applicazione desktop professionale per il face-swap in tempo reale, leggendo dalla webcam fisica, applicando il modello AI in tempo reale, ed esponendo il flusso tramite una webcam virtuale per poter interagire con software di terze parti come OBS, Discord o Google Meet. Il software deve essere ottimizzato per hardware AMD.

Poiché il tuo sistema operativo è **Windows**, ci affideremo a **DirectML** (`onnxruntime-directml`) per l'accelerazione hardware AMD sulla tua RX 7900 XTX. Questo garantirà prestazioni massime senza dover installare ROCm, che è più orientato a Linux.

L'architettura sarà altamente scalabile e modulare, divisa in layer separati: GUI, Pipeline a Thread Multipli, e Motore d'Inferenza AI.

## User Review Required

> [!IMPORTANT]
> - Poiché l'OS è Windows, l'approccio principale per sfruttare nativamente l'accelerazione AMD sarà usare il pacchetto `onnxruntime-directml`. Sei d'accordo con l'impostare l'ambiente primario su DirectML?
> - Per l'esecuzione dei modelli *InsightFace*, c'è attualmente una libreria specifica che useremo o dobbiamo gestire chiamate dirette tramite `onnxruntime`? Il wrapper ufficiale di `insightface` fa in genere fatica a riconoscere DirectML senza patch, quindi in futuro potremmo dover estrarre la logica in chiamate pure ONNX se le performance non dovessero soddifare.
> - Vuoi che procediamo con la creazione dello scheletro completo della struttura delle directory descritta (fase 1-2) per impostare il template del repository?

## Proposed Changes

Sarà rispettata esattamente la struttura che hai ipotizzato, rendendo il codice elegante, modulabile e pronto alla produzione.

### Struttura Base del Repository
Inizializzazione delle directory principali per garantire la separazione delle competenze.

#### [NEW] [config.json](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/config.json)
Template con i percorsi dei modelli e delle impostazioni di base.
#### [NEW] [requirements.txt](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/requirements.txt)
Dipendenze necessarie, configurate per Windows AMD (`onnxruntime-directml`, `opencv-python`, ecc.)
#### [NEW] [main.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/main.py)
Entry-point generale dell'applicazione.

---

### Core (Logica AI e Modelli ONNX)
La logica di inferenza, isolata dal resto dell'app.

#### [NEW] [core/onnx_session.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/core/onnx_session.py)
Gestore dell'inizializzazione dei provider ONNX (DmlExecutionProvider, CPUExecutionProvider).
#### [NEW] [core/face_analyser.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/core/face_analyser.py)
Rilevamento del volto e calcolo dell'embedding.
#### [NEW] [core/face_swapper.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/core/face_swapper.py)
Logica di inferenza Inswapper 128 e Temporal Smoothing base.
#### [NEW] [core/face_enhancer.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/core/face_enhancer.py)
Costrutto per l'eventuale integrazione di CodeFormer.
#### [NEW] [core/face_masker.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/core/face_masker.py)
Logica per le maschere e i bordi.
#### [NEW] [core/color_transfer.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/core/color_transfer.py)
Implementazione di Reinhard Color Transfer.

---

### Pipeline (Acquisizione, Processamento, Output)
Thread manager per mantenere 30 fps fluidi usando le queue.

#### [NEW] [pipeline/capture_thread.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/pipeline/capture_thread.py)
Cattura webcam con OpenCV (Thread 1).
#### [NEW] [pipeline/process_thread.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/pipeline/process_thread.py)
Coda di inferenza AI che processa i frame (Thread 2).
#### [NEW] [pipeline/output_thread.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/pipeline/output_thread.py)
Passaggio dei frame virtual camera via `pyvirtualcam` (Thread 3).

---

### UI (Interfaccia Grafica)
Pannello utente basato su `customtkinter`.

#### [NEW] [ui/app.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/ui/app.py)
Creazione layout a due colonne (`CustomTkinter`).
#### [NEW] [ui/preview_panel.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/ui/preview_panel.py)
Widget e callback aggiornamento preview a schermo.
#### [NEW] [ui/settings_panel.py](file:///C:/Users/chris/Documents/Epicode/tool/face-swap-virtualcam/ui/settings_panel.py)
Tasti, slider parametri, selettore webcam.


## Fasi e Approccio

Seguiremo esattamente le sette fasi dettate nel documento:
1. **Fondamenta**: Inizializzare la UI con CustomTkinter.
2. **Idraulica**: Creare i 3 thread per far scorrere i frame video dalla webcam fisica a quella virtuale.
3. **Analisi AI (Iniziale)**: Logica per inserire una foto target, validarne la dimensione ed estrarre l'embedding del volto.
4. **Core AI + Enhancement**: Integrazione dell'accelerazione hardware e step 4.5 (CodeFormer).
5. **Ottimizzazione (Color Transfer)**: Poisson blending e color matching via `scikit-image`.
6. **Selezione Foto (Quality Gate)**: Fornire score della foto in input.
7. **Refining Multi-Hardware**.

## Open Questions

- Assumendo che creerò la base di tutti questi file per implementare lo scheletro in base al Documento di Progetto... Sei d'accordo ad usare l'installazione di **OBS Virtual Cam** lato tuo o similari quando arriveremo alla fase di test del software?
- Vuoi scaricare autonomamente i pesi `.onnx` come da te indicato nel documento e inserirli nella cartella creata non appena avrò finalizzato l'ossatura del progetto?

## Verification Plan

### Automated Checks
- Verificare che il programma si avvii senza crash e formi correttamente i thread, loggando i frame rates.
- Esecuzione base e parsing di un'immagine input.

### Manual Verification
- Testare con la RX 7900 XTX tramite i pannelli diagnostici l'occupazione della GPU e l'fps target in uscita su OBS.
- Conferma visiva da parte tua che l'interfaccia UI si allinei col design che hai in mente.
