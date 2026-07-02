import base64
import io
import re
import wave
import queue
import threading
from typing import Optional, Tuple, Callable

import certifi
import httpx
import numpy as np
from openai import APIConnectionError, OpenAI

import config
from llm_project.coding_detector import is_coding_question
from llm_project.response_parser import (
    ParsedResponse,
    parse_structured_response,
    parse_vision_response,
)

_client_instance: OpenAI | None = None
_ssl_bootstrapped = False
_use_local_fallback_directly = getattr(config, "USE_LOCAL_LLM", False)


def close_client() -> None:
    """Close active HTTP connections during application shutdown."""
    global _client_instance
    client = _client_instance
    _client_instance = None
    if client is not None:
        client.close()


def _init_ssl() -> None:
    """Use OS trust store on Windows (fixes CERTIFICATE_VERIFY_FAILED)."""
    global _ssl_bootstrapped
    if _ssl_bootstrapped:
        return
    _ssl_bootstrapped = True
    if not config.SSL_VERIFY or config.SSL_CA_FILE:
        return
    if config.IS_WINDOWS:
        try:
            import truststore

            truststore.inject_into_ssl()
        except ImportError:
            pass

SYSTEM_PROMPT = """You are an interview copilot helping a candidate during a live technical/behavioral interview.

Rules:
- Give concise, speakable answers (2-4 short paragraphs max).
- For behavioral questions use STAR format briefly.
- For technical (non-coding) questions: clear explanation first, then example if useful.
- Sound natural — the candidate will paraphrase, not read verbatim.
- If the input is unclear or not a question, say "Waiting for a clear question..." in one line.
- Never mention that you are an AI assistant.

Candidate background:
{resume}

Target role: {role}
{job_desc}
"""

CODING_PROMPT = """You are a live coding interview copilot. The candidate is solving on CoderPad, HackerRank, LeetCode, or similar.

They need:
1) What to SAY while thinking (short bullets, conversational)
2) Copy-paste ready code in {lang} that runs on the platform
3) Time/space complexity
4) Edge cases to mention

Output EXACTLY these sections (headers must match):

===APPROACH===
- Restate the problem in one line
- 3-5 bullets: brute force idea → optimal approach → why it works
- What to say before typing ("I'll start with...")

===COMPLEXITY===
Time: O(...) — one line why
Space: O(...) — one line why

===CODE===
```{lang}
# Complete solution: correct imports, function signature, handles edge cases.
# Prefer clean, interview-standard style (not over-engineered).
# Add brief inline comments only on tricky lines.
```

===EDGE_CASES===
- bullet list of tests to mention or run

Rules:
- If problem is ambiguous, pick the most common LeetCode interpretation and note it.
- Use {lang} only in CODE section.
- For trees/graphs include standard definition helpers if needed.
- Do not include markdown outside the section format.

Candidate background (for style only, not fake experience):
{resume}

Target role: {role}
{job_desc}
"""

VISION_SCREEN_PROMPT = """You are reading a screenshot from a LIVE CODING interview.

Platforms include: LeetCode, HackerRank, CoderPad, Codility, **White-box Learning**,
Replit, CodeSignal, or any split-screen page with:
- LEFT: problem statement (description, examples, constraints)
- RIGHT: code editor with a function stub (e.g. `def classify_temperature(...): pass`)

CRITICAL RULES:
1) Read ALL problem text from the left panel AND the function signature from the editor.
2) If you see ANY problem statement OR a `def` function stub to implement → this IS a coding problem.
3) Only output NO_PROBLEM if the screen is clearly NOT coding (email, slides, blank desktop).

If coding problem, output EXACTLY these sections (headers must match):

===PROBLEM===
Copy the full problem: title, description, examples, constraints, function signature.

===APPROACH===
What the candidate should SAY out loud (bullets): restate problem → approach → before typing.

===COMPLEXITY===
Time: O(...) — one line
Space: O(...) — one line

===CODE===
```{lang}
# Complete working solution matching the on-screen function signature.
# Use only {lang}. Handle all examples and constraints.
```

===EDGE_CASES===
- bullets of tests to mention

Language: {lang}
Match the exact function name and parameters shown in the editor (e.g. classify_temperature).
Never mention AI. Ignore semi-transparent overlay windows.
"""


def format_api_error(exc: Exception) -> str:
    """User-friendly message for OpenAI / network errors."""
    text = str(exc).lower()
    if "certificate verify failed" in text or "ssl" in text:
        return (
            "SSL certificate error — run .\\scripts\\run.ps1 from interview-copilot, "
            "then: pip install certifi. Or set SSL_VERIFY=false in .env (last resort)."
        )
    if isinstance(exc, APIConnectionError):
        return f"Cannot reach OpenAI — check internet/VPN. ({exc})"
    return str(exc)


def _ssl_verify_setting() -> bool | str:
    if not config.SSL_VERIFY:
        return False
    if config.SSL_CA_FILE:
        return config.SSL_CA_FILE
    if config.IS_WINDOWS:
        return True
    return certifi.where()


def check_ssl_connectivity() -> tuple[bool, str]:
    """Quick probe before interview — returns (ok, message)."""
    _init_ssl()
    try:
        with httpx.Client(verify=_ssl_verify_setting(), timeout=15.0) as client:
            client.get("https://api.openai.com")
        return True, "SSL OK"
    except Exception as exc:
        text = str(exc).lower()
        if "certificate verify failed" in text or "ssl" in text:
            return False, (
                "SSL failed — run: .\\venv\\Scripts\\pip install truststore "
                "then restart. Or set SSL_VERIFY=false in .env (last resort)."
            )
        return False, f"Network: {exc}"


def _client() -> OpenAI:
    global _client_instance
    _init_ssl()
    if _client_instance is not None:
        return _client_instance
    if not config.openai_key_configured():
        raise ValueError(
            "OPENAI_API_KEY missing in interview-copilot/.env only (must start with sk-)"
        )
    http_client = httpx.Client(verify=_ssl_verify_setting(), timeout=120.0)
    _client_instance = OpenAI(
        api_key=config.OPENAI_API_KEY,
        http_client=http_client,
    )
    return _client_instance


def _audio_to_wav_bytes(samples: np.ndarray, sample_rate: int) -> bytes:
    audio = np.clip(samples, -1.0, 1.0)
    pcm = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    buf.seek(0)
    return buf.read()


def transcribe(samples: np.ndarray, sample_rate: int) -> str:
    client = _client()
    wav_bytes = _audio_to_wav_bytes(samples, sample_rate)
    bio = io.BytesIO(wav_bytes)
    bio.name = "chunk.wav"
    result = client.audio.transcriptions.create(
        model=config.OPENAI_TRANSCRIBE_MODEL,
        file=bio,
        language="en",
    )
    return (result.text or "").strip()


def should_use_coding_mode(question: str, force_coding: bool = False) -> bool:
    if force_coding:
        return True
    if config.CODING_MODE == "always":
        return True
    return False


def generate_answer(
    question: str,
    conversation: list[dict],
    force_coding: bool = False,
    on_chunk: Callable[[ParsedResponse], None] = None,
    is_cancelled: Callable[[], bool] = None,
) -> ParsedResponse:
    coding = should_use_coding_mode(question, force_coding)
    client = _client()
    resume = config.load_resume_context() or "(No resume loaded — add resume_context.txt)"
    job_desc = ""
    if config.JOB_DESCRIPTION.strip():
        job_desc = f"Job focus:\n{config.JOB_DESCRIPTION.strip()}"

    if coding:
        lang = config.CODE_LANGUAGE
        system = CODING_PROMPT.format(
            lang=lang,
            resume=resume,
            role=config.JOB_ROLE,
            job_desc=job_desc,
        )
        user_msg = (
            f"Coding interview problem (from interviewer):\n{question}\n\n"
            "Give the full structured response for the candidate."
        )
        max_tokens = config.CODING_MAX_TOKENS
        temperature = 0.2
    else:
        system = SYSTEM_PROMPT.format(
            resume=resume,
            role=config.JOB_ROLE,
            job_desc=job_desc,
        )
        user_msg = f"Interviewer asked:\n{question}"
        max_tokens = 800
        temperature = 0.4

    messages = [{"role": "system", "content": system}]
    for turn in conversation[-6:]:
        messages.append(turn)
    messages.append({"role": "user", "content": user_msg})

    winner_provider = None
    winner_lock = threading.Lock()
    final_raw_text = ""
    result_queue = queue.Queue()
    errors = []
    errors_lock = threading.Lock()

    def run_stream(provider_name, client_obj, model_name):
        nonlocal winner_provider, final_raw_text
        try:
            print(f"[openai_service] Racing: {provider_name} call started...", flush=True)
            if is_cancelled and is_cancelled():
                result_queue.put(None)
                return

            resp = client_obj.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            accumulated_text = ""
            for chunk in resp:
                if is_cancelled and is_cancelled():
                    result_queue.put(None)
                    return

                if not chunk.choices or not chunk.choices[0].delta.content:
                    continue

                content = chunk.choices[0].delta.content
                accumulated_text += content

                with winner_lock:
                    if winner_provider is None:
                        winner_provider = provider_name
                        print(f"[openai_service] Racing: {provider_name} won the race!", flush=True)

                    if winner_provider != provider_name:
                        result_queue.put(None)
                        return  # lost race, abort

                # If we won, notify on_chunk and update final text
                final_raw_text = accumulated_text
                if on_chunk:
                    parsed = parse_structured_response(accumulated_text, coding)
                    on_chunk(parsed)

            result_queue.put((provider_name, final_raw_text))
            print(f"[openai_service] Racing: {provider_name} completed streaming successfully!", flush=True)
        except Exception as e:
            print(f"[openai_service] Racing: {provider_name} error: {e}", flush=True)
            if provider_name == "openai":
                err_str = str(e).lower()
                if "quota" in err_str or "limit" in err_str or "429" in err_str or "insufficient" in err_str:
                    global _use_local_fallback_directly
                    _use_local_fallback_directly = True
                    print("[openai_service] OpenAI quota limit hit. Caching local fallback direct.", flush=True)
            with errors_lock:
                errors.append((provider_name, e))

            with winner_lock:
                # If the current winner failed before completing, let the other one win
                if winner_provider == provider_name:
                    winner_provider = None

            result_queue.put(None)

    def run_openai():
        run_stream("openai", client, config.OPENAI_CHAT_MODEL)

    def run_local():
        fallback_model = "qwen3:8b"
        try:
            r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=2.0)
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                qwen_models = [m for m in models if "qwen" in m]
                if qwen_models:
                    preferred = ["qwen3:8b", "qwen3:14b", "qwen3:30b", "qwen3", "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:3b", "qwen2.5"]
                    found = False
                    for pref in preferred:
                        if pref in qwen_models:
                            fallback_model = pref
                            found = True
                            break
                    if not found:
                        fallback_model = qwen_models[0]
        except Exception:
            pass

        local_client = OpenAI(
            base_url="http://127.0.0.1:11434/v1",
            api_key="ollama",
        )
        run_stream("local", local_client, fallback_model)

    global _use_local_fallback_directly
    use_local = getattr(config, "USE_LOCAL_LLM", False)

    if use_local:
        if _use_local_fallback_directly:
            print("[openai_service] Local fallback active. Running local only.", flush=True)
            run_local()
            res = result_queue.get()
            if res is not None:
                raw = res[1]
            else:
                print("[openai_service] Local failed, trying OpenAI as last resort...", flush=True)
                run_openai()
                res = result_queue.get()
                if res is not None:
                    raw = res[1]
                else:
                    raise errors[0][1]
        else:
            t_openai = threading.Thread(target=run_openai, daemon=True)
            t_local = threading.Thread(target=run_local, daemon=True)
            t_openai.start()
            t_local.start()

            # Wait for the winner to finish
            res = result_queue.get()
            if res is not None:
                raw = res[1]
            else:
                # Try the other provider if one failed
                res = result_queue.get()
                if res is not None:
                    raw = res[1]
                else:
                    with errors_lock:
                        raise RuntimeError(f"Both OpenAI and Local LLM failed. Errors: {errors}")
    else:
        run_openai()
        res = result_queue.get()
        if res is not None:
            raw = res[1]
        else:
            with errors_lock:
                if errors:
                    raise errors[0][1]
            raw = ""

    return parse_structured_response(raw, coding)


def solve_from_screenshot(
    image_jpeg: bytes,
    detail: str = "high",
) -> Tuple[str, ParsedResponse]:
    """Read problem from screen image and return coding solution."""
    client = _client()
    lang = config.CODE_LANGUAGE
    resume = config.load_resume_context() or ""
    job_desc = config.JOB_DESCRIPTION.strip()

    b64 = base64.standard_b64encode(image_jpeg).decode("ascii")
    instructions = VISION_SCREEN_PROMPT.format(lang=lang)
    extra = ""
    if resume:
        extra += f"\nCandidate background:\n{resume[:2000]}"
    if job_desc:
        extra += f"\nJob focus:\n{job_desc[:800]}"

    global _use_local_fallback_directly
    try:
        if _use_local_fallback_directly:
            raise Exception("insufficient_quota (cached)")

        response = client.chat.completions.create(
            model=config.OPENAI_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instructions + extra},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                                "detail": detail,
                            },
                        },
                    ],
                }
            ],
            temperature=0.2,
            max_tokens=2500,
        )
        raw = (response.choices[0].message.content or "").strip()
        has_vision = True
    except Exception as exc:
        err_str = str(exc).lower()
        if "quota" in err_str or "limit" in err_str or "429" in err_str or "insufficient" in err_str:
            if getattr(config, "USE_LOCAL_LLM", False):
                _use_local_fallback_directly = True
                print(f"[openai_service] OpenAI quota limit hit during vision scan. Checking local models...", flush=True)
            try:
                fallback_model = "qwen3:8b"
                has_vision = False
                try:
                    r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=2.0)
                    if r.status_code == 200:
                        models = [m["name"] for m in r.json().get("models", [])]
                        vision_keywords = ["llava", "bakllava", "minicpm", "vision", "moondream"]
                        for model in models:
                            if any(k in model.lower() for k in vision_keywords):
                                fallback_model = model
                                has_vision = True
                                break
                        if not has_vision:
                            qwen_models = [m for m in models if "qwen" in m]
                            if qwen_models:
                                preferred = ["qwen3:8b", "qwen3:14b", "qwen3:30b", "qwen3", "qwen2.5:7b", "qwen2.5:14b", "qwen2.5:3b", "qwen2.5"]
                                for pref in preferred:
                                    if pref in qwen_models:
                                        fallback_model = pref
                                        break
                except Exception:
                    pass

                print(f"[openai_service] Falling back to local model: '{fallback_model}' (has_vision={has_vision})", flush=True)
                local_client = OpenAI(
                    base_url="http://127.0.0.1:11434/v1",
                    api_key="ollama",
                )
                
                if has_vision:
                    response = local_client.chat.completions.create(
                        model=fallback_model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": instructions + extra},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{b64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        temperature=0.2,
                        max_tokens=2500
                    )
                    raw = (response.choices[0].message.content or "").strip()
                else:
                    prompt = (
                        "OpenAI Quota Limit Exceeded. A local text-only model is running, "
                        "but screen vision scanning is not available without a local vision model (e.g. llava). "
                        "Generate a template response instructing the candidate to paste the problem description or read it out loud."
                    )
                    response = local_client.chat.completions.create(
                        model=fallback_model,
                        messages=[
                            {"role": "system", "content": "You are a coding interview copilot."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                        max_tokens=1000
                    )
                    raw = (response.choices[0].message.content or "").strip()
            except Exception as local_exc:
                print(f"[openai_service] Local vision fallback failed: {local_exc}", flush=True)
                raise exc
        else:
            raise exc

    problem, parsed = parse_vision_response(raw)
    parsed.is_coding = True

    if not has_vision:
        problem = "OpenAI Quota Exceeded — Local Qwen Active"
        parsed.approach = "Please read the problem description out loud or paste the problem description so that the local Qwen model can solve it."
        parsed.code = "# Screen vision scanning is offline due to OpenAI quota limit.\n# Please speak/transcribe the problem description."
        return problem, parsed

    prob_upper = (problem or "").strip().upper()
    looks_coding = _screen_looks_like_coding(problem, raw)

    if prob_upper == "NO_PROBLEM" and not looks_coding:
        raise ValueError(
            "No coding problem on screen. Open your coding tab (White-box / LeetCode) "
            "and press Scan screen (Ctrl+Shift+S)."
        )

    prob_text = problem if prob_upper != "NO_PROBLEM" else parsed.problem_text
    if not prob_text:
        prob_text = _extract_problem_fallback(raw)

    # Vision sometimes returns problem only — generate solution via chat model
    if (not parsed.code or len(parsed.approach.strip()) < 30) and prob_text:
        parsed = generate_answer(prob_text, [], force_coding=True)
        parsed.is_coding = True
        parsed.problem_text = prob_text
        problem = prob_text

    if not parsed.code and not parsed.approach.strip():
        raise ValueError(
            "Could not read the coding problem. Zoom the problem panel and scan again."
        )

    if not problem and prob_text:
        problem = prob_text

    return problem, parsed


def _screen_looks_like_coding(problem: str, raw: str) -> bool:
    blob = f"{problem}\n{raw}".lower()
    hints = (
        "def ",
        "problem statement",
        "implement",
        "write a function",
        "constraints",
        "examples",
        "classify_",
        "pass #",
        "leetcode",
        "white-box",
        "whitebox",
        "coderpad",
        "hackerrank",
    )
    return any(h in blob for h in hints)


def _extract_problem_fallback(raw: str) -> str:
    m = re.search(
        r"===\s*PROBLEM\s*===\s*(.+?)(?====\s*(?:APPROACH|CODE|COMPLEXITY)|\Z)",
        raw,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        text = m.group(1).strip()
        if text.upper() != "NO_PROBLEM":
            return text
    return ""
