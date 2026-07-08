# LLM Session Token & Cost Tracking Report

Generated on: 2026-07-06 13:48:47

Target Job Role: **AI enginner**

## Transaction Summary

| # | Timestamp | Provider | Model | Prompt Tokens | Output Tokens | Total Tokens | Estimated Cost ($) |
|---|---|---|---|---|---|---|---|
| 1 | 13:46:32 | Openai | gpt-4o-mini | 4909 | 280 | 5189 | $0.000904 |
| 2 | 13:47:05 | Openai | gpt-4o-mini | 4844 | 336 | 5180 | $0.000928 |
| 3 | 13:47:15 | Openai | gpt-4o-mini | 4879 | 316 | 5195 | $0.000921 |
| 4 | 13:47:18 | Openai | gpt-4o-mini | 4901 | 231 | 5132 | $0.000874 |
| 5 | 13:48:06 | Openai | gpt-4o-mini | 4858 | 263 | 5121 | $0.000886 |
| 6 | 13:48:11 | Openai | gpt-4o-mini | 4890 | 240 | 5130 | $0.000878 |
| 7 | 13:48:15 | Openai | gpt-4o-mini | 4892 | 231 | 5123 | $0.000872 |
| 8 | 13:48:26 | Openai | gpt-4o-mini | 4931 | 207 | 5138 | $0.000864 |
| 9 | 13:48:37 | Openai | gpt-4o-mini | 4880 | 193 | 5073 | $0.000848 |
| 10 | 13:48:42 | Openai | gpt-4o-mini | 4899 | 188 | 5087 | $0.000848 |

## Totals

- **Total Input/Prompt Tokens**: 48883
- **Total Output/Response Tokens**: 2485
- **Total Tokens Utilized**: 51368
- **Estimated Session Cost**: **$0.0088**

## Conversation & Candidate Transcript Logs

### Q1 Dialogue Block
- **Question**: Ah, perfect. So thinking about RAG, retrieval augmented generation. Can you walk me through a scenario where you implemented a RAG pipeline in a row project? I'm especially interested in how you handled the indexing, the retrieval steps, how you evaluated the results.
- **LLM (Openai) Answer**: 1. **Short Answer**  
Implemented a RAG pipeline for a customer care AI assistant, focusing on document ingestion, indexing, retrieval, and evaluation.

2. **Detailed Explanation**  
- **Indexing**: Ingested unstructured data (PDFs, wikis) using Apache Tika and AWS Textract. Cleaned and chunked data with Docling, generating embeddings with Sentence Transformers, stored in Milvus for efficient retrieval.
- **Retrieval**: Implemented a hybrid retrieval system combining semantic search (Milvus) and keyword search (BM25). Queries were processed to create embeddings, and results were reranked using a cross-encoder model.
- **Evaluation**: Used metrics like Precision@K, Recall@K, and BERTScore to assess retrieval quality. Regular evaluations ensured system reliability and reduced hallucinations.

3. **Architecture**  
```plaintext
User → FastAPI → Query Validation → Embedding Generation → Hybrid Retrieval (Semantic + BM25) → Milvus → Reranking → AWS Bedrock LLM
```

4. **Internal Working**  
- **Indexing**: Document ingestion → Data cleaning → Chunking → Embedding generation → Storage in Milvus.  
- **Retr
- **Candidate Spoken Answer**: Yeah. I've implemented a RAG pipeline for customer care assistant. Focusing on documentization, indexing, and retrieval and evaluation. So I created ingestion using unstructured data, PDF, the case. And I've used the AWS extract, clean and chunk the data using doc link, generated embeddings using sentence transformer, and stored in Milvus for efficient retrieval. I implemented hybrid retrieval system, a Symantec Milvus and Keyword BM25. Yes. That's it.

------------------------------

### Q2 Dialogue Block
- **Question**: That's
- **LLM (Openai) Answer**: 1. **Short Answer**  
I implemented a hybrid retrieval system combining semantic search in Milvus with keyword-based BM25 for improved accuracy.

2. **Detailed Explanation**  
The hybrid retrieval system leverages Milvus for semantic embeddings while integrating traditional keyword search to enhance the retrieval quality. This dual approach allows for better context understanding and precise results, addressing the limitations of keyword-only searches.

3. **Architecture**  
- **User Query** → FastAPI → Query Validation → Embedding Generation → Hybrid Retrieval (Semantic + BM25) → Milvus → Response Generation.

4. **Internal Working**  
- Queries are embedded and processed through both semantic and keyword retrieval paths. Results are merged and reranked for final output.

5. **Implementation**  
- Utilized Sentence Transformers for embeddings and configured Milvus for vector storage. Integrated BM25 for keyword search.

6. **Best Practices**  
- Regularly evaluate retrieval effectiveness using metrics like precision and recall. Implement fallback mechanisms for low-confidence results.

7. **Trade-offs**  
- Balancing complexity of hybrid retrieval with performance; requires careful tuning of both retrieval methods.

8. **Common Mistakes**  
- Over-relying on one retrieval method can lead to poor performance. Ensure both
- **Candidate Spoken Answer**: (Candidate did not speak for this question)

------------------------------

### Q3 Dialogue Block
- **Question**: That's Got it. That sounds really robust. If you don't mind, can you also share how you evaluated the accuracy or relevance of the retrievals? Like,
- **LLM (Openai) Answer**: 1. **Short Answer**  
We evaluated retrieval accuracy using metrics like Precision@K, Recall@K, and BERTScore, alongside user feedback for relevance assessment.

2. **Detailed Explanation**  
- **Precision@K** measures the proportion of relevant documents in the top K results.  
- **Recall@K** assesses how many relevant documents are retrieved out of the total relevant documents.  
- **BERTScore** evaluates the semantic similarity between retrieved results and ground truth using contextual embeddings.

3. **Architecture**  
- Evaluation Pipeline: Retrieved Results → Metric Calculation (Precision@K, Recall@K, BERTScore) → User Feedback → Iterative Improvement.

4. **Internal Working**  
- Metrics are computed post-retrieval to quantify effectiveness, guiding adjustments in the retrieval strategy.

5. **Implementation**  
- Integrated evaluation scripts in the CI/CD pipeline to automate performance tracking and reporting.

6. **Best Practices**  
- Regularly update evaluation datasets and involve domain experts for qualitative assessments.

7. **Trade-offs**  
- Balancing automated metrics with human feedback for comprehensive evaluation.

8. **Common Mistakes**  
- Neglecting user feedback can lead to misalignment with real-world relevance.

9
- **Candidate Spoken Answer**: So I evaluate

------------------------------

### Q4 Dialogue Block
- **Question**: That's Got it. That sounds really robust. If you don't mind, can you also share how you evaluated the accuracy or relevance of the retrievals? Like, metrics or methods you used to make sure the answers were actually helpful to the users?
- **LLM (Openai) Answer**: 1. **Short Answer**  
We evaluated retrieval relevance using Precision@K, Recall@K, BERTScore, and user feedback to ensure answers were helpful.

2. **Detailed Explanation**  
- **Precision@K**: Measures the ratio of relevant documents in the top K results.  
- **Recall@K**: Assesses the number of relevant documents retrieved compared to the total relevant documents.  
- **BERTScore**: Analyzes semantic similarity between retrieved answers and ground truth, ensuring contextual relevance.

3. **Implementation**  
- Integrated automated evaluation scripts in the CI/CD pipeline, allowing real-time performance tracking and adjustments based on metrics.

4. **Best Practices**  
- Regularly update evaluation datasets and incorporate user feedback for continuous improvement.

5. **Common Mistakes**  
- Relying solely on quantitative metrics without qualitative user feedback can lead to misalignment with user needs.
- **Candidate Spoken Answer**: the accuracy, the retrieval relevance using position at k. Recall it k, bird score. And user feedback to ensure answers are helpful. Precision came that measures the ratio of relevant documents in the top quizzes. And Recall eight k assesses the number of relevant documents retrieved compared to the total relevant documents. Okay? And the bird score analyzes semantic similarity between retrieved answers and ground truth. So I also implemented automated evaluation script here using the CICD pipelines. Allowing real time performance tracking.

------------------------------

### Q5 Dialogue Block
- **Question**: That's fantastic. I love how you combine both quantitative metric
- **LLM (Openai) Answer**: 1. **Short Answer**  
   I utilized quantitative metrics like Precision@K and Recall@K to evaluate retrieval accuracy, alongside qualitative assessments through user feedback and safety metrics.

2. **Detailed Explanation**  
   - **Quantitative Metrics**: Precision@K measures the relevance of the top K retrieved documents, while Recall@K assesses how many relevant documents were retrieved from the total available. These metrics provide a clear performance benchmark.
   - **Qualitative Metrics**: User feedback and safety metrics help gauge the system's effectiveness and compliance, ensuring that responses are not only accurate but also safe and contextually appropriate.

3. **Best Practices**  
   - Regularly review and update evaluation metrics based on user needs.
   - Implement A/B testing to compare different model versions.

4. **Production Considerations**  
   - Ensure metrics are integrated into the CI/CD pipeline for continuous monitoring.
   - Use automated tools for real-time evaluation to quickly identify and rectify issues.
- **Candidate Spoken Answer**: (Candidate did not speak for this question)

------------------------------

### Q6 Dialogue Block
- **Question**: That's fantastic. I love how you combine both quantitative metric and user feedback. It sounds like you got a really good balance between precision, and the semantic quality of the responses.
- **LLM (Openai) Answer**: 1. **Short Answer**  
   Thank you! Balancing quantitative metrics with user feedback ensures that our system not only retrieves accurate information but also meets user expectations for relevance and context.

2. **Detailed Explanation**  
   - **Precision**: We focus on metrics like Precision@K to quantify the accuracy of our retrieval system, ensuring that the top results are relevant.
   - **User Feedback**: Incorporating user feedback helps us understand the semantic quality of responses, allowing us to fine-tune the model and improve user satisfaction.

3. **Trade-offs**  
   - Relying solely on quantitative metrics can overlook nuances in user intent, while focusing only on feedback may lead to subjective biases. A hybrid approach mitigates these risks.

4. **Production Considerations**  
   - Continuous evaluation and iteration based on both metrics and feedback are crucial for maintaining system effectiveness in a production environment.
- **Candidate Spoken Answer**: Thank you.

------------------------------

### Q7 Dialogue Block
- **Question**: That's fantastic. I love how you combine both quantitative metric and user feedback. It sounds like you got a really good balance between precision, and the semantic quality of the responses. Of core
- **LLM (Openai) Answer**: 1. **Short Answer**  
   Absolutely! By integrating quantitative metrics with user feedback, we achieve a robust evaluation framework that enhances both precision and semantic relevance.

2. **Detailed Explanation**  
   - **Quantitative Metrics**: Metrics like Precision@K and Recall@K provide objective measures of retrieval accuracy, ensuring that the system consistently delivers relevant results.
   - **User Feedback**: Collecting qualitative insights allows us to assess the semantic quality and user satisfaction, enabling continuous improvement of the model's responses.

3. **Best Practices**  
   - Regularly iterate on the model based on feedback and metrics.
   - Use a feedback loop to refine prompts and retrieval strategies.

4. **Production Considerations**  
   - Implement automated monitoring for metrics and feedback to quickly identify areas for improvement and maintain high performance in production.
- **Candidate Spoken Answer**: Now let's end this here.

------------------------------

### Q8 Dialogue Block
- **Question**: That's fantastic. I love how you combine both quantitative metric and user feedback. It sounds like you got a really good balance between precision, and the semantic quality of the responses. Of core You're welcome, and if you have any other area you'd like to discuss, whether it's RAG refinements, other projects, or just broader AI topics, I'm all ears.
- **LLM (Openai) Answer**: 1. **Short Answer**  
   Thank you! I'm open to discussing RAG refinements, multi-agent systems, or any advancements in generative AI.

2. **Detailed Explanation**  
   - **RAG Refinements**: We can explore techniques like improved embedding strategies or advanced reranking methods to enhance retrieval accuracy.
   - **Multi-Agent Systems**: Discussing the orchestration of agents, memory management, and policy validation can provide insights into building robust AI solutions.

3. **Best Practices**  
   - Stay updated on the latest research in AI to incorporate cutting-edge techniques.
   - Foster collaboration among teams to share insights and improve system performance.

4. **Production Considerations**  
   - Ensure that any new refinements or projects align with business goals and user needs for maximum impact.
- **Candidate Spoken Answer**: Thank you. Bye bye.

------------------------------

### Q9 Dialogue Block
- **Question**: Absolutely. No problem at all. I'm glad we got to dive into those topics. You ever wanna put this up again or explore something new, just let me know.
- **LLM (Openai) Answer**: 1. **Short Answer**  
   Thank you! I appreciate the opportunity to discuss these topics and will definitely reach out for further exploration.

2. **Detailed Explanation**  
   - **Future Discussions**: I look forward to delving deeper into advanced AI concepts or sharing insights on ongoing projects.
   - **Continuous Learning**: Staying engaged with the latest trends in AI and machine learning is crucial for driving innovation.

3. **Best Practices**  
   - Maintain open communication for knowledge sharing and collaboration.
   - Regularly review and assess new developments in the field to remain competitive.

4. **Production Considerations**  
   - Ensure that any new initiatives align with organizational goals and user needs for effective implementation.
- **Candidate Spoken Answer**: You too. Bye.

------------------------------

### Q10 Dialogue Block
- **Question**: Absolutely. No problem at all. I'm glad we got to dive into those topics. You ever wanna put this up again or explore something new, just let me know. You're very welcome. Take care, and have a great rest of your day. Goodbye.
- **LLM (Openai) Answer**: 1. **Short Answer**  
   Thank you! I appreciate the conversation and look forward to future discussions. Have a great day!

2. **Detailed Explanation**  
   - **Gratitude**: Expressing appreciation for the opportunity to discuss AI topics is essential for building rapport.
   - **Future Engagement**: Indicating openness to future conversations shows enthusiasm for collaboration and continued learning.

3. **Best Practices**  
   - Always follow up with a thank-you message after interviews to reinforce positive impressions.
   - Keep lines of communication open for networking and professional growth.

4. **Production Considerations**  
   - Maintain a professional demeanor in all interactions to foster lasting relationships in the industry.
- **Candidate Spoken Answer**: (Candidate did not speak for this question)

------------------------------
