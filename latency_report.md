# Latency Analysis Report

*Last updated: 2026-07-02 12:12:19*

## Summary Statistics

| Metric | Average Latency | Count |
| :--- | :--- | :--- |
| **Speech-to-Text (STT)** | 99.35 s (99347.5 ms) | 13 |
| **LLM Time-to-First-Token (TTFT)** | 1.49 s (1486.2 ms) | 7 |
| **LLM Total Generation Time (TGT)** | 9.10 s (9096.9 ms) | 7 |

## Detailed Logs

### Speech-to-Text (STT) Transcription Latencies

| Timestamp | Transcript | Latency |
| :--- | :--- | :--- |
| 12:12:09 | `strategies that you have used for the racks?` | 224.77 s (224766.0 ms) |
| 12:12:08 | `Apart from chunking, what are the` | 223.58 s (223578.0 ms) |
| 12:11:17 | `mismatch problem when using recursive character splitting?` | 173.25 s (173250.0 ms) |
| 12:11:14 | `How can you solve the context` | 170.05 s (170047.0 ms) |
| 12:09:57 | `It's okay. It's okay. It's fine.` | 92.59 s (92594.0 ms) |
| 12:09:43 | `we can use it for authentication. Right?` | 78.88 s (78875.0 ms) |
| 12:09:40 | `This token can be reached for subject to` | 75.27 s (75266.0 ms) |
| 12:09:22 | `returning it?` | 57.86 s (57859.0 ms) |
| 12:09:21 | `Why do we raise x raise HTTP exceptions instead of` | 56.80 s (56797.0 ms) |
| 12:09:16 | `Ask any other` | 51.75 s (51750.0 ms) |
| 12:09:05 | `that part.` | 41.06 s (41063.0 ms) |
| 12:09:02 | `We have paid. We have` | 38.09 s (38094.0 ms) |
| 12:08:32 | `Explain me the contents of a JWT token.` | 7.58 s (7578.0 ms) |

### LLM Answering Latencies

| Timestamp | Question Prompt | Time-to-First-Token (TTFT) | Total Generation Time (TGT) |
| :--- | :--- | :--- | :--- |
| 12:12:19 | `mismatch problem when using recursive character splitting?
F...` | 1.06 s (1060.3 ms) | 10.09 s (10085.7 ms) |
| 12:11:28 | `mismatch problem when using recursive character splitting?...` | 0.84 s (842.5 ms) | 10.29 s (10290.3 ms) |
| 12:10:04 | `returning it?
Follow-up: This token can be reached for subje...` | 0.81 s (814.4 ms) | 7.38 s (7384.6 ms) |
| 12:09:50 | `returning it?
Follow-up: This token can be reached for subje...` | 0.65 s (649.2 ms) | 7.18 s (7176.6 ms) |
| 12:09:34 | `returning it?...` | 3.14 s (3141.9 ms) | 11.88 s (11882.8 ms) |
| 12:09:12 | `that part....` | 1.08 s (1084.6 ms) | 6.49 s (6485.2 ms) |
| 12:08:42 | `Explain me the contents of a JWT token....` | 2.81 s (2810.5 ms) | 10.37 s (10373.1 ms) |
