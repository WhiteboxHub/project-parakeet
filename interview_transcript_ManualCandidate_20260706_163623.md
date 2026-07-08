# Interview Transcript & Roleplay Log

*Last updated: 2026-07-06 16:59:00*

| Timestamp | Role | Transcript |
| :--- | :--- | :--- |
| 16:50:09 | **Interviewer** | Just before we begin. Take up all your dose. How's your day been so far? |
| 16:50:13 | **Interviewer** | Identities and added to that. Hello. It's your daddy. It's good. |
| 16:50:21 | **Interviewer** | Glad to hear that. This will be a fifteen to twenty minute conversation to assess |
| 16:50:26 | **Interviewer** | your hard skills based on your experience. If you're ready for the interview, |
| 16:50:27 | **Interviewer** | please begin by introducing yourself. |
| 16:50:32 | **Interviewer** | Oh, hello. |
| 16:50:34 | **Interviewer** | I'm Shweta Shweta Margeti. |
| 16:50:41 | **Interviewer** | Based on your resume, do you have research and |
| 16:50:45 | **Interviewer** | experience in AI engineering, MLPs, |
| 16:50:49 | **Interviewer** | and back end development. Are there any other core areas of expertise you would add? |
| 16:50:54 | **Interviewer** | Any |
| 16:50:54 | **Interviewer** | No. |
| 16:51:03 | **Interviewer** | Please check your time. Are there any additional |
| 16:51:11 | **Interviewer** | areas of expertise beyond AI engineering MLOPs, and back end development that you would highlight from your |
| 16:51:38 | **Interviewer** | I know AWS Docker, |
| 16:51:39 | **Interviewer** | Kubernetes, |
| 16:51:44 | **Interviewer** | Background. |
| 16:51:46 | **Interviewer** | Thank you for clarifying. |
| 16:51:50 | **Interviewer** | And of these, which do you consider your strongest domain? |
| 16:51:54 | **Interviewer** | AWS. |
| 16:52:01 | **Interviewer** | To clarify, on AI engineering, |
| 16:52:04 | **Interviewer** | MLLPs, back end development, |
| 16:52:09 | **Interviewer** | AWS, and Docker. Which area do you consider your |
| 16:52:11 | **Interviewer** | strongest domain of expertise? |
| 16:52:23 | **Interviewer** | AI engineering. |
| 16:52:31 | **Interviewer** | You. I'd like to ask a few focused questions to better understand your experience in AI and |
| 16:52:39 | **Interviewer** | You mentioned designing a generic AI using a retrieval augmented generation |
| 16:52:42 | **Interviewer** | Can you describe your specific role in the |
| 16:52:46 | **Interviewer** | experimental design and implementation of this |
| 16:52:49 | **Interviewer** | system, what technical tools and methodologies did you personally use throughout the process? |
| 16:53:12 | **Interviewer** | I started with the POC. |
| 16:53:17 | **Interviewer** | With with RAG RAG |
| 16:53:23 | **Interviewer** | and I created an AI assistant AI assistant. |
| 16:53:26 | **Interviewer** | After that, I worked on |
| 16:53:31 | **Interviewer** | AI assistant AI assistant platform |
| 16:53:34 | **Interviewer** | platform in which |
| 16:53:38 | **Interviewer** | they had a two two phases. In phase one, |
| 16:53:41 | **Interviewer** | which was in production right now, and the phase one is a RAG system, |
| 16:53:46 | **Interviewer** | in which we |
| 16:53:51 | **Interviewer** | the phase one. They have two parts in phase one. |
| 16:53:56 | **Interviewer** | Integration pipeline, query pipeline. We worked with |
| 16:54:00 | **Interviewer** | data. I did I did data cleaning. |
| 16:54:04 | **Interviewer** | And and processing preprocessing using doc |
| 16:54:09 | **Interviewer** | link for chunking and embedding. I use dock link and |
| 16:54:14 | **Interviewer** | sentence transformers. I use LangChain for orchestration. |
| 16:54:19 | **Interviewer** | Prompt templating, chaining, |
| 16:54:22 | **Interviewer** | q and a. I implemented a hybrid trivia |
| 16:54:25 | **Interviewer** | semantic semantic plus keyword. |
| 16:54:32 | **Interviewer** | Thank you for your answer. I I use Clarify. |
| 16:54:37 | **Interviewer** | Could you explain the core scientific or technical |
| 16:54:40 | **Interviewer** | principles behind retrieval augmented generation, RAG, |
| 16:54:43 | **Interviewer** | and how you ensured the system retrieve the most relevant information for use |
| 16:54:44 | **Interviewer** | your |
| 16:55:04 | **Interviewer** | We had the semantic plus keyword |
| 16:55:07 | **Interviewer** | based based hybrid retrieval. |
| 16:55:12 | **Interviewer** | That that can that can get the |
| 16:55:17 | **Interviewer** | that can get that can get the correct |
| 16:55:20 | **Interviewer** | that can, that can correct the chunks from the |
| 16:55:24 | **Interviewer** | from the, database, and they can set the |
| 16:55:28 | **Interviewer** | LLM LLM, and before that before to the LLM, |
| 16:55:31 | **Interviewer** | we have the |
| 16:55:34 | **Interviewer** | we have the re ranker |
| 16:55:40 | **Interviewer** | So we can we can re rank |
| 16:55:43 | **Interviewer** | rerank the, result. |
| 16:55:48 | **Interviewer** | Result and send to the |
| 16:55:49 | **Interviewer** | sent to the LLM. |
| 16:55:54 | **Interviewer** | So we will we so we will get the correct |
| 16:55:59 | **Interviewer** | To confirm your hands on experience, when you were building the retrieval and re ranking |
| 16:56:04 | **Interviewer** | pipelines, which specific tools or frameworks |
| 16:56:07 | **Interviewer** | did you personally use for embedding generation, vector storage, and re ranking? |
| 16:56:11 | **Interviewer** | Please be as specific as possible about your direct involvement. |
| 16:56:19 | **Interviewer** | I implemented a hybrid retriever |
| 16:56:23 | **Interviewer** | semantic plus keyword. I use LangGraph |
| 16:56:26 | **Interviewer** | Chain for orchestration, prompt templating, |
| 16:56:30 | **Interviewer** | training, q and q and a, |
| 16:56:39 | **Interviewer** | I use Milvus as a vector database. For generation, I used AWS Bedrock for Cloud Cloud Sonat. |
| 16:56:40 | **Interviewer** | I also worked |
| 16:56:46 | **Interviewer** | worked on retrieval evaluation and generation AI, evaluation |
| 16:56:48 | **Interviewer** | I used cross |
| 16:56:51 | **Interviewer** | encoder as a re ranker. |
| 16:56:59 | **Interviewer** | You for clarifying your tool usage. Let's move to an applied reasoning |
| 16:57:00 | **Interviewer** | scenario. |
| 16:57:05 | **Interviewer** | Suppose you have deployed your RAG based AI assistant in a production environment. |
| 16:57:10 | **Interviewer** | After several weeks, users report the |
| 16:57:13 | **Interviewer** | sometimes returns outdated or irrelevant information |
| 16:57:17 | **Interviewer** | even though the source documents have been updated in your data pipeline. |
| 16:57:21 | **Interviewer** | You have limited downtime available for troubleshooting, and the system must remain |
| 16:57:21 | **Interviewer** | operational. |
| 16:57:26 | **Interviewer** | Please walk me through step by step how you would have |
| 16:57:30 | **Interviewer** | approach diagnosing and resolving this issue. |
| 16:57:33 | **Interviewer** | Explain your reasoning at each stage, state any assumptions you are making, |
| 16:57:35 | **Interviewer** | and describe which tools or methods you would use. |
| 16:58:03 | **Interviewer** | I will I will, I will |
| 16:58:08 | **Interviewer** | do to see the issue first. Are we getting the correct chunks |
| 16:58:13 | **Interviewer** | at the first place? So so it will be like |
| 16:58:17 | **Interviewer** | retriever first, add, then |
| 16:58:20 | **Interviewer** | then I will go back to the chunks and then the embeddings. |
| 16:58:22 | **Interviewer** | And the LLM. |
| 16:58:27 | **Interviewer** | And now I also check if |
| 16:58:29 | **Interviewer** | we have a |
| 16:58:34 | **Interviewer** | we have any, failures in the |
| 16:58:35 | **Interviewer** | retriever. |
| 16:58:38 | **Interviewer** | Or the LLM. |
| 16:58:42 | **Interviewer** | Or any no any noise data |
| 16:58:47 | **Interviewer** | A data noise data coming in, we can analyze |
| 16:58:51 | **Interviewer** | analyze the issues. |
| 16:59:00 | **Interviewer** | Thank you. Please elaborate on how you would prioritize which component |
