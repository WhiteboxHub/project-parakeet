import asyncio
import os
import threading
from deepgram import DeepgramClient
from deepgram.listen.v1.socket_client import EventType
from .base import STTProvider


class DeepgramProvider(STTProvider):
    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("DEEPGRAM_API_KEY")
        # v7.3.1: api_key must be a keyword argument
        self.deepgram = DeepgramClient(api_key=key)

    async def process_audio_stream(
        self,
        audio_queue: asyncio.Queue,
        handler_callback
    ):
        loop = asyncio.get_running_loop()

        try:
            with self.deepgram.listen.v1.connect(
                model="nova-3",
                smart_format=True,   # Maximum formatting/punctuation accuracy
                encoding="linear16", # Tells Deepgram we stream raw PCM
                sample_rate=16000,
                channels=1,
                interim_results=False,
                endpointing=250,
                language="en",
                keyterm=["LangChain", "LangGraph", "land graph", "Landra", "MilvusDB", "BM25", "Agentic AI", "Agentic", "RAG", "Prometheus", "Grafana", "CloudWatch"]
            ) as connection:

                def on_message(*args, **kwargs):
                    # Handler receives (self, message) or just (message,)
                    message = args[1] if len(args) > 1 else args[0]
                    try:
                        if hasattr(message, "channel") and hasattr(message.channel, "alternatives"):
                            sentence = message.channel.alternatives[0].transcript
                            if sentence and sentence.strip():
                                print(f"Deepgram raw text: {sentence}")
                                asyncio.run_coroutine_threadsafe(
                                    handler_callback(sentence), loop
                                )
                    except Exception as e:
                        print(f"Deepgram message parse error: {e}")

                def on_error(*args, **kwargs):
                    error = args[1] if len(args) > 1 else args[0]
                    print(f"Deepgram Error: {error}")

                connection.on(EventType.MESSAGE, on_message)
                connection.on(EventType.ERROR, on_error)

                # start_listening() is blocking — run in a thread
                listen_thread = threading.Thread(
                    target=connection.start_listening, daemon=True
                )
                listen_thread.start()

                # Send initial keepalive immediately to prevent early timeout
                try:
                    connection.send_keep_alive()
                except Exception as e:
                    print(f"Failed to send initial keepalive: {e}", flush=True)

                # Stream audio chunks to Deepgram
                while True:
                    try:
                        try:
                            chunk = await asyncio.wait_for(audio_queue.get(), timeout=2.0)
                        except asyncio.TimeoutError:
                            # Send KeepAlive to prevent Deepgram timeout
                            try:
                                connection.send_keep_alive()
                            except Exception:
                                pass
                            continue

                        if chunk is None:  # EOF / sender disconnected
                            break

                        connection.send_media(chunk)

                    except Exception as e:
                        print(f"Error sending audio to Deepgram: {e}", flush=True)
                        break

                listen_thread.join(timeout=3.0)
                print("Deepgram streaming finished.")

        except Exception as e:
            print(f"Could not open Deepgram socket: {e}")
