# Latency Analysis Report

*Last updated: 2026-07-06 13:48:48*

## Summary Statistics

| Metric | Average Latency | Count |
| :--- | :--- | :--- |
| **Speech-to-Text (STT)** | 93.85 s (93849.6 ms) | 21 |
| **LLM Time-to-First-Token (TTFT)** | 1.03 s (1033.6 ms) | 11 |
| **LLM Total Generation Time (TGT)** | 3.58 s (3584.0 ms) | 11 |

## Detailed Logs

### Speech-to-Text (STT) Transcription Latencies

| Timestamp | Transcript | Latency |
| :--- | :--- | :--- |
| 13:48:45 | `Take care, and if you ever need to chat again, I'll be here.` | 152.30 s (152297.0 ms) |
| 13:48:44 | `Bye.` | 150.86 s (150859.0 ms) |
| 13:48:39 | `of your day. Goodbye.` | 145.86 s (145859.0 ms) |
| 13:48:37 | `You're very welcome. Take care, and have a great rest` | 144.41 s (144406.0 ms) |
| 13:48:32 | `You ever wanna put this up again or explore something new, just let me know.` | 139.42 s (139422.0 ms) |
| 13:48:30 | `Absolutely. No problem at all. I'm glad we got to dive into those topics.` | 137.19 s (137187.0 ms) |
| 13:48:22 | `I'm all ears.` | 129.17 s (129172.0 ms) |
| 13:48:21 | `you'd like to discuss, whether it's RAG refinements, other projects, or just broader AI topics,` | 128.06 s (128062.0 ms) |
| 13:48:18 | `You're welcome, and if you have any other area` | 124.61 s (124609.0 ms) |
| 13:48:13 | `Of core` | 119.55 s (119547.0 ms) |
| 13:48:08 | `and the semantic quality of the responses.` | 114.81 s (114812.0 ms) |
| 13:48:06 | `and user feedback. It sounds like you got a really good balance between precision,` | 113.16 s (113156.0 ms) |
| 13:48:02 | `That's fantastic. I love how you combine both quantitative metric` | 108.83 s (108828.0 ms) |
| 13:47:15 | `metrics or methods you used to make sure the answers were actually helpful to the users?` | 61.62 s (61625.0 ms) |
| 13:47:11 | `If you don't mind, can you also share how you evaluated the accuracy or relevance of the retrievals? Like,` | 57.67 s (57672.0 ms) |
| 13:47:07 | `Got it. That sounds really robust.` | 53.50 s (53500.0 ms) |
| 13:47:02 | `That's` | 48.48 s (48484.0 ms) |
| 13:46:27 | `the retrieval steps, how you evaluated the results.` | 13.97 s (13969.0 ms) |
| 13:46:26 | `project? I'm especially interested in how you handled the indexing,` | 12.75 s (12750.0 ms) |
| 13:46:22 | `Can you walk me through a scenario where you implemented a RAG pipeline in a row` | 9.33 s (9328.0 ms) |
| 13:46:18 | `Ah, perfect. So thinking about RAG, retrieval augmented generation.` | 5.30 s (5297.0 ms) |

### LLM Answering Latencies

| Timestamp | Question Prompt | Time-to-First-Token (TTFT) | Total Generation Time (TGT) |
| :--- | :--- | :--- | :--- |
| 13:48:48 | `Absolutely. No problem at all. I'm glad we got to dive into ...` | 1.01 s (1008.3 ms) | 3.11 s (3106.6 ms) |
| 13:48:42 | `Absolutely. No problem at all. I'm glad we got to dive into ...` | 0.76 s (760.4 ms) | 2.74 s (2742.6 ms) |
| 13:48:37 | `Absolutely. No problem at all. I'm glad we got to dive into ...` | 2.21 s (2212.6 ms) | 4.46 s (4455.0 ms) |
| 13:48:26 | `That's fantastic. I love how you combine both quantitative m...` | 1.23 s (1228.3 ms) | 3.97 s (3967.1 ms) |
| 13:48:15 | `That's fantastic. I love how you combine both quantitative m...` | 0.72 s (718.6 ms) | 2.85 s (2845.8 ms) |
| 13:48:11 | `That's fantastic. I love how you combine both quantitative m...` | 0.81 s (810.3 ms) | 3.22 s (3218.0 ms) |
| 13:48:06 | `That's fantastic. I love how you combine both quantitative m...` | 1.12 s (1119.6 ms) | 3.84 s (3844.7 ms) |
| 13:47:18 | `That's Got it. That sounds really robust. If you don't mind,...` | 0.92 s (916.9 ms) | 3.05 s (3052.7 ms) |
| 13:47:15 | `That's Got it. That sounds really robust. If you don't mind,...` | 0.74 s (739.0 ms) | 3.94 s (3942.4 ms) |
| 13:47:05 | `That's...` | 0.78 s (780.6 ms) | 3.76 s (3763.1 ms) |
| 13:46:32 | `Ah, perfect. So thinking about RAG, retrieval augmented gene...` | 1.07 s (1074.7 ms) | 4.49 s (4486.0 ms) |
