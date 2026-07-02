# Interview Copilot Workspace

This workspace has been reorganized into three separate, modular project sub-folders, with the application entry point [main.py](file:///c:/Users/Jashuva/Desktop/interview-copilot/main.py) located at the workspace root:

1. **[copilot_app](file:///c:/Users/Jashuva/Desktop/interview-copilot/copilot_app)**: Contains PyQt6 overlay window components, GUI styling (`glass_theme.py`, `glass_effect.py`), screen watcher/capture scripts, configuration (`.env`, `resume_context.txt`), and dependencies (`venv`).
2. **[audio_processing](file:///c:/Users/Jashuva/Desktop/interview-copilot/audio_processing)**: Contains the audio recorder, loopback, local/enterprise audio-to-text pipeline dependencies (`audio_stt`), and the `audio_processing_backend` sub-service.
3. **[llm_project](file:///c:/Users/Jashuva/Desktop/interview-copilot/llm_project)**: Contains the LLM response service (`openai_service.py`), code detector, and output parser.

## How to Run

You can run the application directly from this workspace root by:
1. Double-clicking the root-level [run.bat](file:///c:/Users/Jashuva/Desktop/interview-copilot/run.bat) file (runs startup checks, syncs dependencies, and launches).
2. Running `python main.py` directly (if you have activated the virtual environment: `.\copilot_app\venv\Scripts\Activate.ps1`).

For more detailed information about each module, refer to the READMEs in their respective directories.
