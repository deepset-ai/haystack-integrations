---
layout: integration
name: Ragas
description: Use the Ragas evaluation framework to calculate model-based metrics 
authors:
    - name: Siddharth Sahu
      socials:
        github: sahusiddharth
pypi: https://pypi.org/project/ragas-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/ragas
type: Evaluation Framework
report_issue: https://github.com/explodinggradients/ragas/issues
logo: /logos/ragas.png
version: Haystack 2.0
toc: true
---

### Table of Contents

1. [Overview](#overview)  
2. [Installation](#installation)  
3. [Usage](#usage)  
   - 3.1 [Evaluation with Integrated RagasEvaluator Component](#evaluation-with-integrated-ragasevaluator-component)  
     - 3.1.1 [Importing Required Libraries and Setting Up Environment](#importing-required-libraries-and-setting-up-environment)  
     - 3.1.2 [Getting the Dataset](#getting-the-dataset)  
     - 3.1.3 [Initializing RAG Pipeline Components](#initializing-rag-pipeline-components)  
     - 3.1.4 [Configuring RagasEvaluator Component](#configuring-ragasevaluator-component)  
     - 3.1.5 [Building and Connecting the RAG Pipeline](#building-and-connecting-the-rag-pipeline)  
     - 3.1.6 [Running the Pipeline](#running-the-pipeline)  
   - 3.2 [Standalone Evaluation of the RAG Pipeline](#standalone-evaluation-of-the-rag-pipeline)  
     - 3.2.1 [Setting Up a Basic RAG Pipeline](#setting-up-a-basic-rag-pipeline)  
     - 3.2.2 [Extracting Outputs for Evaluation](#extracting-outputs-for-evaluation)  
     - 3.2.3 [Evaluating the Pipeline Using Ragas EvaluationDataset](#evaluating-the-pipeline-using-ragas-evaluationdataset)

## Overview

[Ragas](https://docs.ragas.io/) is an open source framework for model-based evaluation to evaluate your LLM applications by quantifying their performance on aspects such as correctness, tonality, hallucination, fluency, etc. More information can be found on the [documentation page](https://docs.haystack.deepset.ai/docs/ragasevaluator).

This tutorial demonstrates how to integrate Ragas with a Retrieval-Augmented Generation (RAG) pipeline built using Haystack, evaluating it both with and without the RagasEvaluator component.
## Installation

Install the `ragas-haystack` integration package
```bash
pip install ragas-haystack
```

## Usage

### Evaluation with Integrated RagasEvaluator Component
This section focuses on using the RagasEvaluator component for performing evaluations within a Haystack RAG pipeline.

#### Importing Required Libraries and Setting Up Environment
We begin by importing the required libraries and configuring the environment. 

```py
import os
from getpass import getpass

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("Enter OpenAI API key:")

from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from haystack.components.generators import OpenAIGenerator
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.builders import AnswerBuilder
from haystack_integrations.components.evaluators.ragas import RagasEvaluator

from ragas.llms import HaystackLLMWrapper
from ragas.metrics import AnswerRelevancy, ContextPrecision, Faithfulness
```

#### Getting the Dataset
In this section we create a sample dataset containing information about AI companies and their language models. This dataset serves as the context for retrieving relevant data during pipeline execution.
```py
dataset = [
    "OpenAI is one of the most recognized names in the large language model space, known for its GPT series of models. These models excel at generating human-like text and performing tasks like creative writing, answering questions, and summarizing content. GPT-4, their latest release, has set benchmarks in understanding context and delivering detailed responses.",
    "Anthropic is well-known for its Claude series of language models, designed with a strong focus on safety and ethical AI behavior. Claude is particularly praised for its ability to follow complex instructions and generate text that aligns closely with user intent.",
    "DeepMind, a division of Google, is recognized for its cutting-edge Gemini models, which are integrated into various Google products like Bard and Workspace tools. These models are renowned for their conversational abilities and their capacity to handle complex, multi-turn dialogues.",
    "Meta AI is best known for its LLaMA (Large Language Model Meta AI) series, which has been made open-source for researchers and developers. LLaMA models are praised for their ability to support innovation and experimentation due to their accessibility and strong performance.",
    "Meta AI with it's LLaMA models aims to democratize AI development by making high-quality models available for free, fostering collaboration across industries. Their open-source approach has been a game-changer for researchers without access to expensive resources.",
    "Microsoft’s Azure AI platform is famous for integrating OpenAI’s GPT models, enabling businesses to use these advanced models in a scalable and secure cloud environment. Azure AI powers applications like Copilot in Office 365, helping users draft emails, generate summaries, and more.",
    "Amazon’s Bedrock platform is recognized for providing access to various language models, including its own models and third-party ones like Anthropic’s Claude and AI21’s Jurassic. Bedrock is especially valued for its flexibility, allowing users to choose models based on their specific needs.",
    "Cohere is well-known for its language models tailored for business use, excelling in tasks like search, summarization, and customer support. Their models are recognized for being efficient, cost-effective, and easy to integrate into workflows.",
    "AI21 Labs is famous for its Jurassic series of language models, which are highly versatile and capable of handling tasks like content creation and code generation. The Jurassic models stand out for their natural language understanding and ability to generate detailed and coherent responses.",
    "In the rapidly advancing field of artificial intelligence, several companies have made significant contributions with their large language models. Notable players include OpenAI, known for its GPT Series (including GPT-4); Anthropic, which offers the Claude Series; Google DeepMind with its Gemini Models; Meta AI, recognized for its LLaMA Series; Microsoft Azure AI, which integrates OpenAI’s GPT Models; Amazon AWS (Bedrock), providing access to various models including Claude (Anthropic) and Jurassic (AI21 Labs); Cohere, which offers its own models tailored for business use; and AI21 Labs, known for its Jurassic Series. These companies are shaping the landscape of AI by providing powerful models with diverse capabilities.",
]
```
#### Initializing RAG Pipeline Components

This section sets up the essential components required to build a Retrieval-Augmented Generation (RAG) pipeline. These components include a Document Store for managing and storing documents, an Embedder for generating embeddings to enable similarity-based retrieval, and a Retriever for fetching relevant documents. Additionally, a Prompt Template is designed to structure the pipeline's input, while a Chat Generator handles response generation. Together, these components form the backbone of the RAG pipeline, ensuring smooth integration between document retrieval and response generation.

```python
# Sets up an in-memory store to hold documents
document_store = InMemoryDocumentStore()
docs = [Document(content=doc) for doc in dataset]

# Embeds the documents using OpenAI's embedding models to enable similarity search.
document_embedder = OpenAIDocumentEmbedder(model="text-embedding-3-small")
text_embedder = OpenAITextEmbedder(model="text-embedding-3-small")

docs_with_embeddings = document_embedder.run(docs)
document_store.write_documents(docs_with_embeddings["documents"])

# Configures a retriever to fetch relevant documents based on embeddings
retriever = InMemoryEmbeddingRetriever(document_store, top_k=2)

# Defines a template for prompting the LLM with a user query and the retrieved documents
template = [
    ChatMessage.from_user(
        """
Given the following information, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
    )
]

# Sets up an LLM-based generator to create responses
prompt_builder = ChatPromptBuilder(template=template)
chat_generator = OpenAIChatGenerator(model="gpt-4o-mini")
```
#### Configuring RagasEvaluator Component

Pass all the Ragas metrics you want to use for evaluation, ensuring that all the necessary information to calculate each selected metric is provided.

For example:

- **AnswerRelevancy**: requires both the **query** and the **response**.
- **ContextPrecision**: requires the **query**, **retrieved documents**, and the **reference**.
- **Faithfulness**: requires the **query**, **retrieved documents**, and the **response**.

Make sure to include all relevant data for each metric to ensure accurate evaluation.

```py
llm = OpenAIGenerator(model="gpt-4o-mini")
evaluator_llm = HaystackLLMWrapper(llm)

ragas_evaluator = RagasEvaluator(
    ragas_metrics=[AnswerRelevancy(), ContextPrecision(), Faithfulness()],
    evaluator_llm=evaluator_llm,
)
```

#### Building and Connecting the RAG Pipeline
Here we add and connect the initialized components to form a RAG Haystack pipeline.
```py
# Creating the Pipeline
rag_pipeline = Pipeline()

# Adding the components
rag_pipeline.add_component("text_embedder", text_embedder)
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", chat_generator)
rag_pipeline.add_component("answer_builder", AnswerBuilder())
rag_pipeline.add_component("ragas_evaluator", ragas_evaluator)

# Connecting the components
rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever", "prompt_builder")
rag_pipeline.connect("prompt_builder.prompt", "llm.messages")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("retriever", "answer_builder.documents")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("retriever", "answer_builder.documents")
rag_pipeline.connect("retriever", "ragas_evaluator.documents")
rag_pipeline.connect("llm.replies", "ragas_evaluator.response")
```

#### Running the Pipeline
In this section, we execute the pipeline with a sample query and evaluate its performance using the configured RagasEvaluator.

```py
question = "What makes Meta AI’s LLaMA models stand out?"

reference = "Meta AI’s LLaMA models stand out for being open-source, supporting innovation and experimentation due to their accessibility and strong performance."


result = rag_pipeline.run(
    {
        "text_embedder": {"text": question},
        "prompt_builder": {"question": question},
        "answer_builder": {"query": question},
        "ragas_evaluator": {"query": question, "reference": reference},
        # Each metric expects a specific set of parameters as input. Refer to the
        # Ragas class' documentation for more details.
    }
)

print(result['answer_builder']['answers'][0].data, '\n')
print(result['ragas_evaluator']['result'])
```
Output
```
Evaluating: 100%|██████████| 3/3 [00:14<00:00,  4.72s/it]

Meta AI's LLaMA models stand out due to their open-source nature, which allows researchers and developers easy access to high-quality language models without the need for expensive resources. This accessibility fosters innovation and experimentation, enabling collaboration across various industries. Moreover, the strong performance of the LLaMA models further enhances their appeal, making them valuable tools for advancing AI development. 

{'answer_relevancy': 0.9782, 'context_precision': 1.0000, 'faithfulness': 1.0000}
```

### Standalone Evaluation of the RAG Pipeline

This section explores an alternative approach to evaluating a RAG pipeline without using the `RagasEvaluator` component. It emphasizes manual extraction of outputs and organizing them for evaluation.

You can use any existing Haystack pipeline for this purpose. For demonstration, we will create a simple RAG pipeline similar to the one described earlier, but without including the `RagasEvaluator` component.

#### Setting Up a Basic RAG Pipeline
We construct a simple RAG pipeline similar to the approach above but without the RagasEvaluator component. 

```py
# Initialize components for RAG pipeline
document_store = InMemoryDocumentStore()
docs = [Document(content=doc) for doc in dataset]

document_embedder = OpenAIDocumentEmbedder(model="text-embedding-3-small")
text_embedder = OpenAITextEmbedder(model="text-embedding-3-small")

docs_with_embeddings = document_embedder.run(docs)
document_store.write_documents(docs_with_embeddings["documents"])

retriever = InMemoryEmbeddingRetriever(document_store, top_k=2)

template = [
    ChatMessage.from_user(
        """
Given the following information, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""
    )
]

prompt_builder = ChatPromptBuilder(template=template)
chat_generator = OpenAIChatGenerator(model="gpt-4o-mini")

# Creating the Pipeline
rag_pipeline = Pipeline()

# Adding the components
rag_pipeline.add_component("text_embedder", text_embedder)
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", chat_generator)
rag_pipeline.add_component("answer_builder", AnswerBuilder())

# Connecting the components
rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipeline.connect("retriever", "prompt_builder")
rag_pipeline.connect("prompt_builder.prompt", "llm.messages")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("retriever", "answer_builder.documents")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("retriever", "answer_builder.documents")
```

#### Extracting Outputs for Evaluation
After building the pipeline, we use it to generate the necessary outputs, such as retrieved documents and responses. These outputs are then structured into a dataset for evaluation.

```py
questions = [
    "Who are the major players in the large language model space?",
    "What is Microsoft’s Azure AI platform known for?",
    "What kind of models does Cohere provide?",
]

references = [
    "The major players include OpenAI (GPT Series), Anthropic (Claude Series), Google DeepMind (Gemini Models), Meta AI (LLaMA Series), Microsoft Azure AI (integrating GPT Models), Amazon AWS (Bedrock with Claude and Jurassic), Cohere (business-focused models), and AI21 Labs (Jurassic Series).",
    "Microsoft’s Azure AI platform is known for integrating OpenAI’s GPT models, enabling businesses to use these models in a scalable and secure cloud environment.",
    "Cohere provides language models tailored for business use, excelling in tasks like search, summarization, and customer support.",
]


evals_list = []

for que_idx in range(len(questions)):

    single_turn = {}
    single_turn['user_input'] = questions[que_idx]
    single_turn['reference'] = references[que_idx]

    # Running the pipeline
    response = rag_pipeline.run(
        {
            "text_embedder": {"text": questions[que_idx]},
            "prompt_builder": {"question": questions[que_idx]},
            "answer_builder": {"query": questions[que_idx]},
        }
    )

    # the response of the pipeline
    single_turn['response'] = response["answer_builder"]["answers"][0].data

    haystack_documents = response["answer_builder"]["answers"][0].documents
    # extracting context from haystack documents 
    # retrieved durring answer generation process
    single_turn['retrieved_contexts'] = [doc.content for doc in haystack_documents]

    evals_list.append(single_turn)
```
> When constructing the `evals_list`, it is important to align the keys in the single_turn dictionary with the attributes defined in the Ragas [SingleTurnSample](https://docs.ragas.io/en/stable/references/evaluation_schema/#ragas.dataset_schema.SingleTurnSample). This ensures compatibility with the Ragas evaluation framework. Use the retrieved documents and pipeline outputs to populate these fields accurately, as demonstrated in the provided code snippet.

#### Evaluating the pipeline using Ragas EvaluationDataset
The extracted dataset is converted into a Ragas [EvaluationDataset](https://docs.ragas.io/en/stable/references/evaluation_schema/#ragas.dataset_schema.EvaluationDataset).

```py
from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset

evaluation_dataset = EvaluationDataset.from_list(evals_list)

llm = OpenAIGenerator(model="gpt-4o-mini")
evaluator_llm = HaystackLLMWrapper(llm)

result = evaluate(
    dataset=evaluation_dataset,
    metrics=[AnswerRelevancy(), ContextPrecision(), Faithfulness()],
    llm=evaluator_llm,
)

print(result)
result.to_pandas()
```

Output
```
Evaluating: 100%|██████████| 9/9 [00:21<00:00,  2.35s/it]

{'answer_relevancy': 0.9715, 'context_precision': 1.0000, 'faithfulness': 1.0000}
```

<div class="styled-table">

| user_input | retrieved_contexts | response | reference | answer_relevancy | context_precision | faithfulness |
| --- | --- | --- | --- | --- | --- | -- |
| Who are the major players in the large languag... | [In the rapidly advancing field of artificial ... | The major players in the large language model ... | The major players include OpenAI (GPT Series),... | 1.000000 | 1.0 | 1.0 |
| What is Microsoft’s Azure AI platform known for? | [Microsoft’s Azure AI platform is famous for i... | Microsoft’s Azure AI platform is known for int... | Microsoft’s Azure AI platform is known for int... | 1.000000 | 1.0 | 1.0 |
| What kind of models does Cohere provide? | [Cohere is well-known for its language models ... | Cohere provides language models tailored for b.. | Cohere provides language models tailored for b.. | 0.914599 | 1.0 | 1.0 |
</div>