"""
Interview Copilot — Windows + macOS.
Isolated project: uses only interview-copilot/.env and interview-copilot/venv.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Inject reorganized codebase package directories into Python sys.path
_ROOT = Path(__file__).resolve().parent
for _p in (_ROOT, _ROOT / "copilot_app", _ROOT / "audio_processing", _ROOT / "llm_project"):
    _p_str = str(_p.resolve())
    if _p_str not in sys.path:
        sys.path.insert(0, _p_str)

# Bootstrap before config (venv + .env checks)
from project_bootstrap import bootstrap

bootstrap()

import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

import config
from audio_processing.audio_stt import AudioEvent, AudioSTTConfig, AudioToTextPipeline, EventKind
from audio_processing.audio_capture import AudioChunk, SpeechRecorder
from llm_project.openai_service import (
    close_client,
    format_api_error,
    generate_answer,
    solve_from_screenshot,
    transcribe,
)
from overlay import OverlayWindow
from screen_capture import capture_screen_jpeg
from screen_watcher import ScreenWatcher


class WorkerBridge(QObject):
    status = pyqtSignal(str)
    question = pyqtSignal(str)
    answer = pyqtSignal(object)
    error = pyqtSignal(str)
    jpeg_ready = pyqtSignal(bytes, str)
    watch_jpeg_ready = pyqtSignal(bytes, bool)
    coding_busy = pyqtSignal(bool)
    transcript = pyqtSignal(str, bool, float)
    candidate_transcript = pyqtSignal(str, bool)
    listening_state = pyqtSignal(bool)




class InterviewApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Interview Copilot")
        self.window = OverlayWindow()
        self.bridge = WorkerBridge()
        self.executor = ThreadPoolExecutor(max_workers=max(4, config.MAX_WORKERS))
        self.recorder: SpeechRecorder | None = None
        self.audio_pipeline: AudioToTextPipeline | None = None
        self.candidate_pipeline: AudioToTextPipeline | None = None
        self._pipeline_warmup_thread: threading.Thread | None = None
        self._generation_lock = threading.Lock()
        self._generation_request_id = 0
        self._last_partial_submit_time = 0.0
        self._last_submitted_text = ""
        self.backend_process = None
        self.conversation: list[dict] = []
        self._busy = False
        self._last_final_question = ""
        self._force_next_coding = False
        self._pending_scan_detail = "high"
        self._watch_capture_pending = False
        self._shutting_down = False

        self._watcher = ScreenWatcher(on_change=lambda _: None)
        self._watch_timer = QTimer()
        self._watch_timer.timeout.connect(self._watch_tick_start)

        self.bridge.status.connect(self.window.status_changed.emit)
        self.bridge.question.connect(self.window.set_question)
        self.bridge.answer.connect(self.window.answer_ready.emit)
        self.bridge.error.connect(self._on_error)
        self.bridge.jpeg_ready.connect(self._on_scan_jpeg_ready)
        self.bridge.watch_jpeg_ready.connect(self._on_watch_jpeg_ready)
        self.bridge.coding_busy.connect(self.window.set_coding_busy)
        self.bridge.transcript.connect(self._on_audio_transcript)
        self.bridge.candidate_transcript.connect(self._on_candidate_transcript)
        self.bridge.listening_state.connect(self.window.set_listening_state)

        self.window.listening_toggled.connect(self._on_listen_toggle)
        self.window.force_coding_requested.connect(self._on_force_coding)
        self.window.scan_screen_requested.connect(self._on_scan_screen)
        self.window.watch_screen_toggled.connect(self._on_watch_toggle)
        self.app.aboutToQuit.connect(self._shutdown)

        if config.SCREEN_WATCH_ENABLED:
            self._watcher.enabled = True
            self._watch_timer.start(config.SCREEN_WATCH_INTERVAL_SEC * 1000)

        if config.ENTERPRISE_AUDIO:
            self._start_pipeline_warmup()

    def _on_error(self, msg: str) -> None:
        self._busy = False
        self.window.status_changed.emit(f"Error: {msg}")

    def _on_force_coding(self) -> None:
        if self._busy:
            self.window.status_changed.emit("Already generating — please wait...")
            return
        q = self.window.get_last_question().strip()
        if q:
            self.window.status_changed.emit("Regenerating coding solution...")
            self.window.set_coding_busy(True)
            self._busy = True
            # A forced retry only needs the current problem. Sending previous
            # code answers again adds a large prompt and noticeably increases
            # latency without improving the result.
            self._generation_request_id += 1
            self.executor.submit(
                self._generate_for_question,
                q,
                True,
                self._generation_request_id,
                True,
                False,
            )
        else:
            self._force_next_coding = True
            self.window.status_changed.emit("Coding mode armed for next question")

    def _on_scan_screen(self) -> None:
        if self._busy or self._watch_capture_pending:
            self.window.status_changed.emit("Busy — please wait...")
            return
        self._busy = True
        self._pending_scan_detail = "high"
        self.window.status_changed.emit("Capturing screen...")
        self.window.hide_for_screenshot()
        QTimer.singleShot(120, self._scan_step_capture)

    def _scan_step_capture(self) -> None:
        self.executor.submit(self._worker_capture_jpeg, self._pending_scan_detail)

    def _worker_capture_jpeg(self, detail: str) -> None:
        try:
            max_w = 1920 if detail == "high" else None
            quality = 88 if detail == "high" else None
            jpeg = capture_screen_jpeg(max_width=max_w, quality=quality)
            self.bridge.jpeg_ready.emit(jpeg, detail)
        except Exception as e:
            self.bridge.jpeg_ready.emit(b"", detail)
            self.bridge.error.emit(format_api_error(e))
            traceback.print_exc()

    def _on_scan_jpeg_ready(self, jpeg: bytes, detail: str) -> None:
        self.window.restore_after_screenshot()
        if not jpeg:
            return
        self.window.status_changed.emit("Reading problem (AI vision)...")
        self._generation_request_id += 1
        self.executor.submit(self._worker_solve_jpeg, jpeg, detail)

    def _worker_solve_jpeg(self, jpeg: bytes, detail: str) -> None:
        with self._generation_lock:
            self._busy = True
            try:
                problem, response = solve_from_screenshot(jpeg, detail=detail)
                question = problem or response.problem_text or "(from screenshot)"
                self.bridge.question.emit(question)
                self.conversation.append(
                    {"role": "user", "content": f"[Screen problem]\n{question}"}
                )
                self.conversation.append(
                    {"role": "assistant", "content": response.full_text}
                )
                self.bridge.answer.emit(response)
                if response.is_coding and response.code:
                    self.bridge.status.emit("Coding solution ready — Ctrl+Shift+S to rescan")
                else:
                    self.bridge.status.emit("Ready — Ctrl+Shift+S to rescan")
            except Exception as e:
                self.bridge.error.emit(format_api_error(e))
                traceback.print_exc()
            finally:
                self._busy = False

    def _on_watch_toggle(self, enabled: bool) -> None:
        self._watcher.enabled = enabled
        if enabled:
            self._watcher.reset()
            self._watch_timer.start(config.SCREEN_WATCH_INTERVAL_SEC * 1000)
            self.window.status_changed.emit(
                f"Watch on (every {config.SCREEN_WATCH_INTERVAL_SEC}s)"
            )
        else:
            self._watch_timer.stop()
            if self._watch_capture_pending:
                self._watch_capture_pending = False
                self.window.restore_after_screenshot()
            self.window.status_changed.emit("Watch off")

    def _watch_tick_start(self) -> None:
        if self._busy or self._watch_capture_pending or not self._watcher.enabled:
            return
        self._watch_capture_pending = True
        self.window.hide_for_screenshot()
        QTimer.singleShot(120, self._watch_step_capture)

    def _watch_step_capture(self) -> None:
        if not self._watcher.enabled:
            self._watch_capture_pending = False
            self.window.restore_after_screenshot()
            return
        self.executor.submit(self._worker_watch_capture)

    def _worker_watch_capture(self) -> None:
        try:
            changed, jpeg = self._watcher.capture_and_check()
            self.bridge.watch_jpeg_ready.emit(jpeg, changed)
        except Exception as e:
            self.bridge.watch_jpeg_ready.emit(b"", False)
            traceback.print_exc()

    def _on_watch_jpeg_ready(self, jpeg: bytes, changed: bool) -> None:
        self._watch_capture_pending = False
        self.window.restore_after_screenshot()
        if changed and jpeg and not self._busy:
            self._busy = True
            self.window.status_changed.emit("Screen changed — analyzing...")
            self.executor.submit(self._worker_solve_jpeg, jpeg, "low")

    def _on_listen_toggle(self, listening: bool) -> None:
        if listening:
            self._start_listening()
        else:
            self._stop_listening()

    def _start_listening(self) -> None:
        if not config.AUDIO_ALLOW_OPENAI_STT and not config.ENTERPRISE_AUDIO:
            self.window.status_changed.emit(
                "Local STT only is enabled. Set ENTERPRISE_AUDIO=true in .env."
            )
            self.window.set_listening_state(False)
            return
        if config.ENTERPRISE_AUDIO:
            self._start_enterprise_audio()
            return
        if not config.openai_key_configured():
            self.window.status_changed.emit(
                "OpenAI key missing in interview-copilot/.env (OPENAI_API_KEY=sk-...)"
            )
            self.window.set_listening_state(False)
            return

        def on_chunk(chunk: AudioChunk) -> None:
            self.executor.submit(self._worker_process_audio, chunk)

        def on_status(msg: str) -> None:
            self.bridge.status.emit(msg)

        self.recorder = SpeechRecorder(on_chunk=on_chunk, on_status=on_status)
        try:
            self.recorder.start()
        except Exception as e:
            self.bridge.error.emit(format_api_error(e))
            self.window.set_listening_state(False)
            return
        label = getattr(self.recorder, "_device_label", "")
        mode = "system audio" if self.recorder and self.recorder._loopback else "microphone"
        self.window.status_changed.emit(
            f"Listening ({mode}) — {label[:50]} — click Stop when done"
        )

    def _start_pipeline_warmup(self) -> None:
        self._pipeline_warmup_thread = threading.Thread(
            target=self._warm_up_pipeline,
            name="audio-pipeline-warmup",
            daemon=True,
        )
        self._pipeline_warmup_thread.start()

    def _warm_up_pipeline(self) -> None:
        try:
            settings = AudioSTTConfig(
                stt_provider=config.AUDIO_STT_PROVIDER,
                stt_model=config.AUDIO_STT_MODEL,
                language=config.AUDIO_LANGUAGE,
                vad_model_path=config.AUDIO_VAD_MODEL_PATH,
                allow_component_fallback=config.AUDIO_ALLOW_FALLBACK,
                allow_openai_stt=config.AUDIO_ALLOW_OPENAI_STT,
                dhwani_server_url=config.DHWANI_SERVER_URL,
                dhwani_provider=config.DHWANI_PROVIDER,
                dhwani_openai_key=config.DHWANI_OPENAI_KEY or config.OPENAI_API_KEY,
                dhwani_deepgram_key=config.DHWANI_DEEPGRAM_KEY,
                disable_llm_cleaning=config.DISABLE_LLM_CLEANING,
            )

            # 1. System/Interviewer pipeline (loopback)
            from audio_capture import _find_loopback_device
            from audio_stt.capture import RobustMicrophoneSource
            
            loopback_id = _find_loopback_device()
            sys_source = RobustMicrophoneSource(settings, device=loopback_id)
            pipeline = AudioToTextPipeline(settings, source=sys_source)

            def on_event(event: AudioEvent) -> None:
                if event.kind in (
                    EventKind.PARTIAL_TRANSCRIPT,
                    EventKind.FINAL_TRANSCRIPT,
                ) and event.transcript is not None:
                    self.bridge.transcript.emit(
                        event.transcript.text,
                        event.transcript.is_final,
                        event.transcript.latency_ms or 0.0,
                    )
                elif event.kind == EventKind.DEVICE_CHANGED:
                    self.bridge.status.emit(f"Interviewer mic: {event.message}")
                elif event.kind in (EventKind.WARNING, EventKind.ERROR):
                    self.bridge.status.emit(f"Audio error: {event.message}")

            pipeline.subscribe(on_event)
            self.audio_pipeline = pipeline

            # 2. Candidate pipeline (local microphone)
            mic_source = RobustMicrophoneSource(settings, device=None)
            candidate_pipeline = AudioToTextPipeline(settings, source=mic_source)

            def on_candidate_event(event: AudioEvent) -> None:
                if event.kind in (
                    EventKind.PARTIAL_TRANSCRIPT,
                    EventKind.FINAL_TRANSCRIPT,
                ) and event.transcript is not None:
                    self.bridge.candidate_transcript.emit(
                        event.transcript.text,
                        event.transcript.is_final,
                    )
                elif event.kind == EventKind.DEVICE_CHANGED:
                    self.bridge.status.emit(f"Candidate mic: {event.message}")
                elif event.kind in (EventKind.WARNING, EventKind.ERROR):
                    self.bridge.status.emit(f"Candidate audio error: {event.message}")

            candidate_pipeline.subscribe(on_candidate_event)
            self.candidate_pipeline = candidate_pipeline

        except Exception as exc:
            traceback.print_exc()

    def _wait_and_start_pipeline(self) -> None:
        if self._pipeline_warmup_thread:
            self._pipeline_warmup_thread.join()
        if self.audio_pipeline is not None and self.candidate_pipeline is not None:
            self._worker_start_enterprise_audio()
        else:
            self.bridge.error.emit("Failed to load speech models in background")
            self.bridge.listening_state.emit(False)

    def _init_and_start_pipeline(self) -> None:
        try:
            settings = AudioSTTConfig(
                stt_provider=config.AUDIO_STT_PROVIDER,
                stt_model=config.AUDIO_STT_MODEL,
                language=config.AUDIO_LANGUAGE,
                vad_model_path=config.AUDIO_VAD_MODEL_PATH,
                allow_component_fallback=config.AUDIO_ALLOW_FALLBACK,
                allow_openai_stt=config.AUDIO_ALLOW_OPENAI_STT,
                dhwani_server_url=config.DHWANI_SERVER_URL,
                dhwani_provider=config.DHWANI_PROVIDER,
                dhwani_openai_key=config.DHWANI_OPENAI_KEY or config.OPENAI_API_KEY,
                dhwani_deepgram_key=config.DHWANI_DEEPGRAM_KEY,
                disable_llm_cleaning=config.DISABLE_LLM_CLEANING,
            )

            # 1. System/Interviewer pipeline (loopback)
            from audio_capture import _find_loopback_device
            from audio_stt.capture import RobustMicrophoneSource
            
            loopback_id = _find_loopback_device()
            sys_source = RobustMicrophoneSource(settings, device=loopback_id)
            pipeline = AudioToTextPipeline(settings, source=sys_source)

            def on_event(event: AudioEvent) -> None:
                if event.kind in (
                    EventKind.PARTIAL_TRANSCRIPT,
                    EventKind.FINAL_TRANSCRIPT,
                ) and event.transcript is not None:
                    self.bridge.transcript.emit(
                        event.transcript.text,
                        event.transcript.is_final,
                        event.transcript.latency_ms or 0.0,
                    )
                elif event.kind == EventKind.DEVICE_CHANGED:
                    self.bridge.status.emit(f"Interviewer mic: {event.message}")
                elif event.kind in (EventKind.WARNING, EventKind.ERROR):
                    self.bridge.status.emit(f"Audio error: {event.message}")

            pipeline.subscribe(on_event)
            self.audio_pipeline = pipeline

            # 2. Candidate pipeline (local microphone)
            mic_source = RobustMicrophoneSource(settings, device=None)
            candidate_pipeline = AudioToTextPipeline(settings, source=mic_source)

            def on_candidate_event(event: AudioEvent) -> None:
                if event.kind in (
                    EventKind.PARTIAL_TRANSCRIPT,
                    EventKind.FINAL_TRANSCRIPT,
                ) and event.transcript is not None:
                    self.bridge.candidate_transcript.emit(
                        event.transcript.text,
                        event.transcript.is_final,
                    )
                elif event.kind == EventKind.DEVICE_CHANGED:
                    self.bridge.status.emit(f"Candidate mic: {event.message}")
                elif event.kind in (EventKind.WARNING, EventKind.ERROR):
                    self.bridge.status.emit(f"Candidate audio error: {event.message}")

            candidate_pipeline.subscribe(on_candidate_event)
            self.candidate_pipeline = candidate_pipeline

            self._worker_start_enterprise_audio()
        except Exception as exc:
            self.bridge.error.emit(format_api_error(exc))
            self.bridge.listening_state.emit(False)

    def _start_enterprise_audio(self) -> None:
        if self.audio_pipeline is not None and self.candidate_pipeline is not None:
            self.window.status_changed.emit("Starting role-based listening...")
            self.executor.submit(self._worker_start_enterprise_audio)
            return

        if self._pipeline_warmup_thread and self._pipeline_warmup_thread.is_alive():
            self.window.status_changed.emit("Speech models are still loading in background...")
            self.executor.submit(self._wait_and_start_pipeline)
            return

        self.window.status_changed.emit("Loading speech models...")
        self.executor.submit(self._init_and_start_pipeline)

    def _worker_start_enterprise_audio(self) -> None:
        try:
            if self.audio_pipeline is not None:
                self.audio_pipeline.start()
            if self.candidate_pipeline is not None:
                self.candidate_pipeline.start()
        except Exception as exc:
            if self.audio_pipeline is not None:
                self.audio_pipeline.stop()
            if self.candidate_pipeline is not None:
                self.candidate_pipeline.stop()
            self.bridge.error.emit(format_api_error(exc))
            self.bridge.listening_state.emit(False)
            return
        self.bridge.status.emit("Role-based audio listening started")

    def _on_audio_transcript(self, text: str, is_final: bool, latency_ms: float = 0.0) -> None:
        text = text.strip()
        if not text:
            return

        if is_final:
            from latency_tracker import tracker
            tracker.record_stt(text, is_final, latency_ms)
            tracker.record_dialogue("Interviewer", text)

        if self._busy and self._last_final_question:
            display_text = f"{self._last_final_question}\nFollow-up: {text}"
        else:
            display_text = text
            if is_final:
                self._last_final_question = text

        if is_final and self._busy:
            self._last_final_question = display_text

        self.window.set_question(display_text)

        now = time.time()
        is_partial = not is_final
        if is_partial:
            # Word count check
            words = text.split()
            if len(words) < 3:
                self.window.status_changed.emit(f"Hearing: {text[-90:]}")
                return
            # Check if we have added at least 2 words since last submitted partial text
            last_words = self._last_submitted_text.split()
            if len(words) - len(last_words) < 2:
                self.window.status_changed.emit(f"Hearing: {text[-90:]}")
                return
            # Throttle to at most once every 600ms
            if now - self._last_partial_submit_time < 0.6:
                self.window.status_changed.emit(f"Hearing: {text[-90:]}")
                return

            self._last_partial_submit_time = now
            self._last_submitted_text = text
            self.window.status_changed.emit(f"Hearing: {text[-90:]}")
        else:
            self._last_submitted_text = ""
            self._last_partial_submit_time = 0.0

        force = self._force_next_coding
        if is_final:
            self._force_next_coding = False

        self._generation_request_id += 1
        self.executor.submit(
            self._generate_for_question,
            display_text,
            force,
            self._generation_request_id,
            is_final,
        )

    def _on_candidate_transcript(self, text: str, is_final: bool) -> None:
        text = text.strip()
        if not text:
            return
        self.window.status_changed.emit(f"You said: {text[-90:]}")

        if not is_final:
            return

        from latency_tracker import tracker
        tracker.record_dialogue("Candidate", text)

        with self._generation_lock:
            self.conversation.append({"role": "assistant", "content": text})
            print(f"[candidate] answer saved to history: '{text}'", flush=True)

    def _stop_listening(self) -> None:
        if self.audio_pipeline is not None:
            self.audio_pipeline.stop()
        if self.candidate_pipeline is not None:
            self.candidate_pipeline.stop()
        if self.recorder:
            self.recorder.stop()
            self.recorder = None
        self.window.status_changed.emit("Stopped listening")

    def _shutdown(self) -> None:
        if self._shutting_down:
            return
        self._shutting_down = True

        if config.EMAIL_RECEIVER:
            try:
                from email_service import send_transcript_email
                t = threading.Thread(target=send_transcript_email, name="email-transcript-thread", daemon=False)
                t.start()
            except Exception as e:
                print(f"Error launching email thread: {e}")

        self._watch_timer.stop()
        self._watcher.enabled = False

        if self.audio_pipeline is not None:
            self.audio_pipeline.stop()
            self.audio_pipeline = None
        if self.candidate_pipeline is not None:
            self.candidate_pipeline.stop()
            self.candidate_pipeline = None
        if self.recorder is not None:
            try:
                self.recorder.stop()
            except Exception:
                traceback.print_exc()
            self.recorder = None
        try:
            close_client()
        finally:
            self.executor.shutdown(wait=False, cancel_futures=True)

    def _worker_process_audio(self, chunk: AudioChunk) -> None:
        try:
            self.bridge.status.emit("Transcribing interviewer audio...")
            text = transcribe(chunk.samples, chunk.sample_rate)
            if not text:
                self.bridge.status.emit(
                    "Could not hear speech — turn up Meet volume / use speakers"
                )
                return
            if len(text.split()) < 2:
                self.bridge.status.emit(f"Heard: \"{text}\" — waiting for full question...")
                return
            force = self._force_next_coding
            self._force_next_coding = False
            self._generation_request_id += 1
            self._generate_for_question(text, force, self._generation_request_id, True)
        except Exception as e:
            self.bridge.error.emit(format_api_error(e))
            traceback.print_exc()

    def _generate_for_question(
        self,
        text: str,
        force_coding: bool,
        request_id: int,
        is_final: bool,
        include_history: bool = True,
    ) -> None:
        if request_id < self._generation_request_id:
            return

        if is_final and include_history:
            # Safely copy conversation under lock
            with self._generation_lock:
                temp_conv = list(self.conversation)
            if temp_conv:
                from llm_project.openai_service import is_question_linked
                is_linked = is_question_linked(text, temp_conv)
                if not is_linked:
                    with self._generation_lock:
                        if request_id == self._generation_request_id:
                            print("[main] Context mismatch detected. Starting a new context (clearing history).", flush=True)
                            self.conversation = []

        with self._generation_lock:
            if request_id < self._generation_request_id:
                return

            self._busy = True
            self.bridge.question.emit(text)
            history = list(self.conversation) if include_history else []


        try:
            from openai_service import should_use_coding_mode

            force_coding = force_coding or text.strip().startswith("[Screen problem]")
            coding = should_use_coding_mode(text, force_coding)
            self.bridge.status.emit(
                f"Generating {'coding solution' if coding else 'answer'}..."
            )

            if request_id < self._generation_request_id:
                return

            start_time = time.perf_counter()
            ttft_ms = None

            def is_cancelled():
                return request_id < self._generation_request_id

            def on_chunk(parsed_resp):
                nonlocal ttft_ms
                if is_cancelled():
                    return
                if ttft_ms is None:
                    ttft_ms = (time.perf_counter() - start_time) * 1000
                self.bridge.answer.emit(parsed_resp)

            response = generate_answer(
                text,
                history,
                force_coding,
                on_chunk=on_chunk,
                is_cancelled=is_cancelled,
            )

            tgt_ms = (time.perf_counter() - start_time) * 1000

            with self._generation_lock:
                if request_id < self._generation_request_id:
                     return

                if is_final:
                    self.conversation.append({"role": "user", "content": text})
                    self.conversation.append(
                        {"role": "assistant", "content": response.full_text}
                    )
                    from latency_tracker import tracker
                    tracker.record_llm(text, ttft_ms or tgt_ms, tgt_ms)

                self.bridge.answer.emit(response)
                self.bridge.status.emit("Ready — listening...")
        except Exception as e:
            self.bridge.error.emit(format_api_error(e))
            traceback.print_exc()
        finally:
            self._busy = False
            if force_coding:
                self.bridge.coding_busy.emit(False)

    def run(self) -> int:
        plat = "macOS" if config.IS_MAC else "Windows"
        self.window.show()
        self.window.move(80, 80)
        self.window.raise_()
        if not config.STEALTH_FOCUS:
            self.window.activateWindow()
        QTimer.singleShot(300, self.window._apply_exclude_once)
        msg = f"Ready ({plat})"
        if config.openai_key_configured():
            msg += " · API key OK"
        else:
            msg += " · set OPENAI_API_KEY in interview-copilot/.env"
        if config.use_transparent_overlay():
            msg += " · transparent"
        else:
            msg += " · opaque"
        if config.INVISIBLE_IN_SHARE:
            msg += " · share-hide on"
        if config.LIGHTWEIGHT_MODE:
            msg += " · lightweight"
        if config.STEALTH_FOCUS:
            msg += " · stealth (hover+scroll)"
        if config.load_resume_context():
            msg += " · resume loaded"
        self.window.status_changed.emit(msg)
        if self._watcher.enabled:
            self.window.set_watch_checked(True)
        return self.app.exec()


def main() -> None:
    app = InterviewApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
