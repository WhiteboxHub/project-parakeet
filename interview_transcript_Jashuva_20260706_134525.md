# Interview Transcript & Roleplay Log

*Last updated: 2026-07-06 13:48:45*

| Timestamp | Role | Transcript |
| :--- | :--- | :--- |
| 13:46:18 | **Interviewer** | Ah, perfect. So thinking about RAG, retrieval augmented generation. |
| 13:46:22 | **Interviewer** | Can you walk me through a scenario where you implemented a RAG pipeline in a row |
| 13:46:26 | **Interviewer** | project? I'm especially interested in how you handled the indexing, |
| 13:46:27 | **Interviewer** | the retrieval steps, how you evaluated the results. |
| 13:46:32 | **Candidate** | Yeah. I've implemented a RAG pipeline for customer care assistant. |
| 13:46:37 | **Candidate** | Focusing on documentization, indexing, and retrieval and evaluation. |
| 13:46:41 | **Candidate** | So I created ingestion using unstructured data, PDF, the case. |
| 13:46:42 | **Candidate** | And |
| 13:46:47 | **Candidate** | I've used the AWS extract, clean and |
| 13:46:49 | **Candidate** | chunk the data using doc link, generated embeddings using sentence transformer, |
| 13:46:54 | **Candidate** | and stored in Milvus for efficient retrieval. |
| 13:46:58 | **Candidate** | I implemented hybrid retrieval system, a |
| 13:47:00 | **Candidate** | Symantec Milvus and Keyword BM25. |
| 13:47:02 | **Interviewer** | That's |
| 13:47:03 | **Candidate** | Yes. That's it. |
| 13:47:07 | **Interviewer** | Got it. That sounds really robust. |
| 13:47:11 | **Interviewer** | If you don't mind, can you also share how you evaluated the accuracy or relevance of the retrievals? Like, |
| 13:47:15 | **Interviewer** | metrics or methods you used to make sure the answers were actually helpful to the users? |
| 13:47:17 | **Candidate** | So I evaluate |
| 13:47:21 | **Candidate** | the accuracy, the retrieval relevance using position at k. Recall it |
| 13:47:23 | **Candidate** | k, bird score. |
| 13:47:28 | **Candidate** | And user feedback to ensure answers are helpful. Precision |
| 13:47:31 | **Candidate** | came that measures the ratio of relevant documents in the top quizzes. |
| 13:47:36 | **Candidate** | And Recall eight k assesses the number of relevant documents |
| 13:47:38 | **Candidate** | retrieved |
| 13:47:43 | **Candidate** | compared to the total relevant documents. Okay? And the bird |
| 13:47:47 | **Candidate** | score analyzes semantic similarity between retrieved answers and |
| 13:47:48 | **Candidate** | ground truth. |
| 13:47:49 | **Candidate** | So I also implemented |
| 13:47:54 | **Candidate** | automated evaluation script here using the CICD pipelines. |
| 13:47:56 | **Candidate** | Allowing real time performance tracking. |
| 13:48:02 | **Interviewer** | That's fantastic. I love how you combine both quantitative metric |
| 13:48:06 | **Interviewer** | and user feedback. It sounds like you got a really good balance between precision, |
| 13:48:08 | **Interviewer** | and the semantic quality of the responses. |
| 13:48:12 | **Candidate** | Thank you. |
| 13:48:13 | **Interviewer** | Of core |
| 13:48:18 | **Interviewer** | You're welcome, and if you have any other area |
| 13:48:21 | **Interviewer** | you'd like to discuss, whether it's RAG refinements, other projects, or just broader AI topics, |
| 13:48:22 | **Interviewer** | I'm all ears. |
| 13:48:25 | **Candidate** | Now let's end this here. |
| 13:48:30 | **Interviewer** | Absolutely. No problem at all. I'm glad we got to dive into those topics. |
| 13:48:33 | **Interviewer** | You ever wanna put this up again or explore something new, just let me know. |
| 13:48:34 | **Candidate** | Thank you. Bye bye. |
| 13:48:37 | **Interviewer** | You're very welcome. Take care, and have a great rest |
| 13:48:39 | **Interviewer** | of your day. Goodbye. |
| 13:48:40 | **Candidate** | You too. Bye. |
| 13:48:44 | **Interviewer** | Bye. |
| 13:48:45 | **Interviewer** | Take care, and if you ever need to chat again, I'll be here. |
