# Enterprise Audio-to-Text Module

`audio_stt` has one responsibility: convert microphone audio into transcript
events. It does not import interview prompts or perform LLM reasoning.

## Runtime pipeline

```text
PortAudio microphone
  -> 16 kHz mono float frames
  -> WebRTC APM (when native binding is installed)
  -> HPF / AGC / peak protection fallback
  -> bounded ring buffer
  -> Silero VAD
  -> endpoint detector
  -> pluggable STT provider
  -> partial/final AudioEvent callbacks
```

Capture uses `sounddevice`, which supports Windows WASAPI and macOS CoreAudio.
The supervisor polls the selected/default device and reopens it with exponential
backoff when a USB, wired, built-in, or Bluetooth microphone changes.

## Install local speech models

The base application remains usable with its OpenAI final-transcript fallback.
For local Silero and SenseVoice:

```powershell
.\venv\Scripts\pip install -r requirements-audio-enterprise.txt
```

The first SenseVoice start downloads its model. Production deployments should
pre-download and pin model artifacts in an internal cache.

## Configuration

```env
ENTERPRISE_AUDIO=true
AUDIO_STT_PROVIDER=sensevoice
AUDIO_STT_MODEL=iic/SenseVoiceSmall
AUDIO_LANGUAGE=auto
AUDIO_ALLOW_FALLBACK=true
AUDIO_ALLOW_OPENAI_STT=false
```

Set `AUDIO_ALLOW_FALLBACK=false` in controlled deployments to fail fast when a
required native/model component is missing.
Set `AUDIO_ALLOW_OPENAI_STT=false` to guarantee no OpenAI-based STT fallback.

## Public API

```python
from audio_stt import AudioSTTConfig, AudioToTextPipeline, EventKind

pipeline = AudioToTextPipeline(AudioSTTConfig())

def handle(event):
    if event.kind in (EventKind.PARTIAL_TRANSCRIPT, EventKind.FINAL_TRANSCRIPT):
        print(event.transcript.text)

pipeline.subscribe(handle)
pipeline.start()
# ...
pipeline.stop()
```

For real AEC, feed synchronized speaker/render frames through
`pipeline.push_far_end(...)`. Microphone-only input cannot cancel acoustic echo.
If no native WebRTC binding is installed, the module logs the downgrade and
uses its deterministic HPF/AGC/normalization fallback.

## Reliability behavior

- Every real-time queue and audio buffer is bounded.
- Partial inference is shed first under backpressure; final jobs are retained.
- Capture errors trigger automatic device reopening.
- Subscriber failures are isolated from capture and inference threads.
- Metrics are available through `pipeline.metrics()` and emitted periodically.
- Model, capture, DSP, VAD, and STT implementations are independently replaceable.

## Latency note

The event path itself is frame-based and non-blocking. End-to-end partial
latency depends on the selected provider and hardware. SenseVoice snapshot
inference is not guaranteed to remain below 200 ms on every CPU. A strict
sub-200 ms service-level objective requires benchmarking the deployment machine
and, if necessary, plugging a native session-based streaming provider into the
`StreamingSTTProvider` contract.
