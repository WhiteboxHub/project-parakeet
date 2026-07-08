# Latency Analysis Report

*Last updated: 2026-07-06 16:59:00*

## Summary Statistics

| Metric | Average Latency | Count |
| :--- | :--- | :--- |
| **Speech-to-Text (STT)** | 282.15 s (282146.7 ms) | 107 |
| **LLM Time-to-First-Token (TTFT)** | 1.50 s (1498.6 ms) | 8 |
| **LLM Total Generation Time (TGT)** | 3.56 s (3558.6 ms) | 8 |

## Detailed Logs

### Speech-to-Text (STT) Transcription Latencies

| Timestamp | Transcript | Latency |
| :--- | :--- | :--- |
| 16:59:00 | `Thank you. Please elaborate on how you would prioritize which component` | 535.30 s (535297.0 ms) |
| 16:58:51 | `analyze the issues.` | 526.42 s (526422.0 ms) |
| 16:58:47 | `A data noise data coming in, we can analyze` | 522.80 s (522797.0 ms) |
| 16:58:42 | `Or any no any noise data` | 517.80 s (517797.0 ms) |
| 16:58:38 | `Or the LLM.` | 513.38 s (513375.0 ms) |
| 16:58:35 | `retriever.` | 510.55 s (510547.0 ms) |
| 16:58:34 | `we have any, failures in the` | 509.11 s (509110.0 ms) |
| 16:58:29 | `we have a` | 504.14 s (504141.0 ms) |
| 16:58:27 | `And now I also check if` | 502.80 s (502797.0 ms) |
| 16:58:22 | `And the LLM.` | 497.84 s (497844.0 ms) |
| 16:58:20 | `then I will go back to the chunks and then the embeddings.` | 495.77 s (495766.0 ms) |
| 16:58:17 | `retriever first, add, then` | 492.50 s (492500.0 ms) |
| 16:58:13 | `at the first place? So so it will be like` | 488.17 s (488172.0 ms) |
| 16:58:08 | `do to see the issue first. Are we getting the correct chunks` | 483.12 s (483125.0 ms) |
| 16:58:03 | `I will I will, I will` | 478.69 s (478688.0 ms) |
| 16:57:35 | `and describe which tools or methods you would use.` | 450.44 s (450438.0 ms) |
| 16:57:33 | `Explain your reasoning at each stage, state any assumptions you are making,` | 448.31 s (448313.0 ms) |
| 16:57:30 | `approach diagnosing and resolving this issue.` | 445.28 s (445282.0 ms) |
| 16:57:26 | `Please walk me through step by step how you would have` | 441.45 s (441454.0 ms) |
| 16:57:21 | `operational.` | 436.41 s (436407.0 ms) |
| 16:57:21 | `You have limited downtime available for troubleshooting, and the system must remain` | 436.03 s (436032.0 ms) |
| 16:57:17 | `even though the source documents have been updated in your data pipeline.` | 432.27 s (432266.0 ms) |
| 16:57:13 | `sometimes returns outdated or irrelevant information` | 428.33 s (428329.0 ms) |
| 16:57:10 | `After several weeks, users report the` | 425.14 s (425141.0 ms) |
| 16:57:05 | `Suppose you have deployed your RAG based AI assistant in a production environment.` | 420.12 s (420125.0 ms) |
| 16:57:00 | `scenario.` | 415.30 s (415297.0 ms) |
| 16:56:59 | `You for clarifying your tool usage. Let's move to an applied reasoning` | 414.89 s (414891.0 ms) |
| 16:56:51 | `encoder as a re ranker.` | 406.49 s (406485.0 ms) |
| 16:56:48 | `I used cross` | 403.45 s (403454.0 ms) |
| 16:56:46 | `worked on retrieval evaluation and generation AI, evaluation` | 400.91 s (400907.0 ms) |
| 16:56:40 | `I also worked` | 395.84 s (395844.0 ms) |
| 16:56:39 | `I use Milvus as a vector database. For generation, I used AWS Bedrock for Cloud Cloud Sonat.` | 394.28 s (394282.0 ms) |
| 16:56:30 | `training, q and q and a,` | 385.77 s (385766.0 ms) |
| 16:56:26 | `Chain for orchestration, prompt templating,` | 381.88 s (381875.0 ms) |
| 16:56:23 | `semantic plus keyword. I use LangGraph` | 377.91 s (377907.0 ms) |
| 16:56:19 | `I implemented a hybrid retriever` | 374.52 s (374516.0 ms) |
| 16:56:11 | `Please be as specific as possible about your direct involvement.` | 366.44 s (366438.0 ms) |
| 16:56:07 | `did you personally use for embedding generation, vector storage, and re ranking?` | 362.81 s (362813.0 ms) |
| 16:56:04 | `pipelines, which specific tools or frameworks` | 359.34 s (359344.0 ms) |
| 16:55:59 | `To confirm your hands on experience, when you were building the retrieval and re ranking` | 354.34 s (354344.0 ms) |
| 16:55:54 | `So we will we so we will get the correct` | 349.66 s (349657.0 ms) |
| 16:55:49 | `sent to the LLM.` | 344.61 s (344610.0 ms) |
| 16:55:48 | `Result and send to the` | 343.72 s (343719.0 ms) |
| 16:55:43 | `rerank the, result.` | 338.70 s (338704.0 ms) |
| 16:55:40 | `So we can we can re rank` | 335.83 s (335829.0 ms) |
| 16:55:34 | `we have the re ranker` | 329.58 s (329579.0 ms) |
| 16:55:31 | `we have the` | 326.11 s (326110.0 ms) |
| 16:55:28 | `LLM LLM, and before that before to the LLM,` | 323.62 s (323625.0 ms) |
| 16:55:24 | `from the, database, and they can set the` | 319.19 s (319188.0 ms) |
| 16:55:20 | `that can, that can correct the chunks from the` | 315.24 s (315235.0 ms) |
| 16:55:17 | `that can get that can get the correct` | 312.14 s (312141.0 ms) |
| 16:55:12 | `That that can that can get the` | 307.17 s (307172.0 ms) |
| 16:55:07 | `based based hybrid retrieval.` | 302.17 s (302172.0 ms) |
| 16:55:04 | `We had the semantic plus keyword` | 299.78 s (299782.0 ms) |
| 16:54:44 | `your` | 278.95 s (278954.0 ms) |
| 16:54:43 | `and how you ensured the system retrieve the most relevant information for use` | 278.45 s (278454.0 ms) |
| 16:54:40 | `principles behind retrieval augmented generation, RAG,` | 275.14 s (275141.0 ms) |
| 16:54:37 | `Could you explain the core scientific or technical` | 272.14 s (272141.0 ms) |
| 16:54:32 | `Thank you for your answer. I I use Clarify.` | 267.17 s (267172.0 ms) |
| 16:54:25 | `semantic semantic plus keyword.` | 260.41 s (260407.0 ms) |
| 16:54:22 | `q and a. I implemented a hybrid trivia` | 257.62 s (257625.0 ms) |
| 16:54:19 | `Prompt templating, chaining,` | 253.95 s (253954.0 ms) |
| 16:54:14 | `sentence transformers. I use LangChain for orchestration.` | 249.02 s (249016.0 ms) |
| 16:54:09 | `link for chunking and embedding. I use dock link and` | 244.05 s (244047.0 ms) |
| 16:54:04 | `And and processing preprocessing using doc` | 239.36 s (239360.0 ms) |
| 16:54:00 | `data. I did I did data cleaning.` | 235.19 s (235188.0 ms) |
| 16:53:56 | `Integration pipeline, query pipeline. We worked with` | 231.00 s (231000.0 ms) |
| 16:53:51 | `the phase one. They have two parts in phase one.` | 226.11 s (226110.0 ms) |
| 16:53:46 | `in which we` | 221.64 s (221641.0 ms) |
| 16:53:41 | `which was in production right now, and the phase one is a RAG system,` | 216.69 s (216688.0 ms) |
| 16:53:38 | `they had a two two phases. In phase one,` | 213.42 s (213422.0 ms) |
| 16:53:34 | `platform in which` | 209.74 s (209735.0 ms) |
| 16:53:31 | `AI assistant AI assistant platform` | 206.36 s (206360.0 ms) |
| 16:53:26 | `After that, I worked on` | 201.28 s (201282.0 ms) |
| 16:53:23 | `and I created an AI assistant AI assistant.` | 198.03 s (198032.0 ms) |
| 16:53:17 | `With with RAG RAG` | 192.55 s (192547.0 ms) |
| 16:53:12 | `I started with the POC.` | 187.55 s (187547.0 ms) |
| 16:52:49 | `system, what technical tools and methodologies did you personally use throughout the process?` | 164.78 s (164782.0 ms) |
| 16:52:46 | `experimental design and implementation of this` | 161.45 s (161454.0 ms) |
| 16:52:42 | `Can you describe your specific role in the` | 157.74 s (157735.0 ms) |
| 16:52:39 | `You mentioned designing a generic AI using a retrieval augmented generation` | 154.77 s (154766.0 ms) |
| 16:52:31 | `You. I'd like to ask a few focused questions to better understand your experience in AI and` | 146.50 s (146500.0 ms) |
| 16:52:23 | `AI engineering.` | 138.17 s (138172.0 ms) |
| 16:52:11 | `strongest domain of expertise?` | 126.78 s (126782.0 ms) |
| 16:52:09 | `AWS, and Docker. Which area do you consider your` | 124.66 s (124657.0 ms) |
| 16:52:04 | `MLLPs, back end development,` | 119.67 s (119672.0 ms) |
| 16:52:01 | `To clarify, on AI engineering,` | 116.80 s (116797.0 ms) |
| 16:51:54 | `AWS.` | 109.58 s (109579.0 ms) |
| 16:51:50 | `And of these, which do you consider your strongest domain?` | 105.06 s (105063.0 ms) |
| 16:51:46 | `Thank you for clarifying.` | 100.92 s (100922.0 ms) |
| 16:51:44 | `Background.` | 99.80 s (99797.0 ms) |
| 16:51:39 | `Kubernetes,` | 94.75 s (94750.0 ms) |
| 16:51:38 | `I know AWS Docker,` | 93.11 s (93110.0 ms) |
| 16:51:11 | `areas of expertise beyond AI engineering MLOPs, and back end development that you would highlight from your` | 65.98 s (65985.0 ms) |
| 16:51:03 | `Please check your time. Are there any additional` | 58.67 s (58672.0 ms) |
| 16:50:54 | `No.` | 49.66 s (49657.0 ms) |
| 16:50:54 | `Any` | 49.42 s (49422.0 ms) |
| 16:50:49 | `and back end development. Are there any other core areas of expertise you would add?` | 44.47 s (44469.0 ms) |
| 16:50:45 | `experience in AI engineering, MLPs,` | 40.53 s (40532.0 ms) |
| 16:50:41 | `Based on your resume, do you have research and` | 36.11 s (36110.0 ms) |
| 16:50:34 | `I'm Shweta Shweta Margeti.` | 29.38 s (29375.0 ms) |
| 16:50:32 | `Oh, hello.` | 27.66 s (27657.0 ms) |
| 16:50:27 | `please begin by introducing yourself.` | 22.67 s (22672.0 ms) |
| 16:50:26 | `your hard skills based on your experience. If you're ready for the interview,` | 21.23 s (21235.0 ms) |
| 16:50:21 | `Glad to hear that. This will be a fifteen to twenty minute conversation to assess` | 16.36 s (16360.0 ms) |
| 16:50:13 | `Identities and added to that. Hello. It's your daddy. It's good.` | 8.80 s (8797.0 ms) |
| 16:50:09 | `Just before we begin. Take up all your dose. How's your day been so far?` | 4.55 s (4547.0 ms) |

### LLM Answering Latencies

| Timestamp | Question Prompt | Time-to-First-Token (TTFT) | Total Generation Time (TGT) |
| :--- | :--- | :--- | :--- |
| 16:50:57 | `Based on your resume, do you have research and experience in...` | 0.79 s (786.8 ms) | 3.09 s (3094.4 ms) |
| 16:50:53 | `Based on your resume, do you have research and experience in...` | 0.81 s (814.3 ms) | 4.01 s (4010.9 ms) |
| 16:50:48 | `Based on your resume, do you have research and experience in...` | 1.12 s (1118.0 ms) | 2.87 s (2871.0 ms) |
| 16:50:43 | `Based on your resume, do you have research and...` | 0.80 s (795.2 ms) | 2.64 s (2640.7 ms) |
| 16:50:39 | `Glad to hear that. This will be a fifteen to twenty minute c...` | 2.79 s (2793.7 ms) | 4.61 s (4612.1 ms) |
| 16:50:30 | `Glad to hear that. This will be a fifteen to twenty minute c...` | 0.72 s (720.0 ms) | 2.47 s (2471.8 ms) |
| 16:50:18 | `Just before we begin. Take up all your dose. How's your day ...` | 1.94 s (1941.2 ms) | 4.78 s (4784.4 ms) |
| 16:50:13 | `Just before we begin. Take up all your dose. How's your day ...` | 3.02 s (3019.6 ms) | 3.98 s (3983.4 ms) |
