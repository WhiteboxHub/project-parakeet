# Latency Analysis Report

*Last updated: 2026-07-06 12:55:08*

## Summary Statistics

| Metric | Average Latency | Count |
| :--- | :--- | :--- |
| **Speech-to-Text (STT)** | 29.37 s (29369.6 ms) | 8 |
| **LLM Time-to-First-Token (TTFT)** | 0.77 s (771.1 ms) | 4 |
| **LLM Total Generation Time (TGT)** | 2.71 s (2714.8 ms) | 4 |

## Detailed Logs

### Speech-to-Text (STT) Transcription Latencies

| Timestamp | Transcript | Latency |
| :--- | :--- | :--- |
| 12:55:05 | `just let me know. I'm always here to continue the conversation when you're ready.` | 54.36 s (54360.0 ms) |
| 12:55:02 | `If there's anything else you want to delve into later,` | 51.36 s (51360.0 ms) |
| 12:54:48 | `scalable and compliant with any regulations or company policies?` | 37.34 s (37344.0 ms) |
| 12:54:46 | `experience when implementing AI systems, how did you ensure they were both` | 35.02 s (35016.0 ms) |
| 12:54:42 | `Certainly. In your PASS` | 31.31 s (31313.0 ms) |
| 12:54:22 | `What was the biggest technical challenge you overcame?` | 11.22 s (11219.0 ms) |
| 12:54:19 | `What was one of the key projects you led?` | 8.33 s (8329.0 ms) |
| 12:54:17 | `Of course, let's start with your most recent role.` | 6.02 s (6016.0 ms) |

### LLM Answering Latencies

| Timestamp | Question Prompt | Time-to-First-Token (TTFT) | Total Generation Time (TGT) |
| :--- | :--- | :--- | :--- |
| 12:55:08 | `If there's anything else you want to delve into later, just ...` | 0.73 s (728.6 ms) | 2.33 s (2329.8 ms) |
| 12:55:05 | `If there's anything else you want to delve into later,...` | 0.78 s (782.4 ms) | 2.41 s (2407.3 ms) |
| 12:54:51 | `Certainly. In your PASS experience when implementing AI syst...` | 0.69 s (694.2 ms) | 2.86 s (2863.4 ms) |
| 12:54:25 | `Of course, let's start with your most recent role. What was ...` | 0.88 s (879.0 ms) | 3.26 s (3258.8 ms) |
