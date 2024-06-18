---
layout: integration
name: llamafile
description: Run LLMs locally with llamafile
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai
pypi: https://pypi.org/project/haystack-ai/
repo: https://github.com/deepset-ai/haystack
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack/issues
logo: /logos/llamafile.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Download and run the model](#download-and-run-the-model)
- [Usage](#usage)

## Overview

[llamafile](https://github.com/Mozilla-Ocho/llamafile) is a project that aims to make open LLMs accessible to developers and users.

To run LLMs locally, simply download a single-file executable ("llamafile") that contains both the model and the inference engine and runs locally on most computers.

llamafile can be used on its own to chat with these models, but below we will see how to integrate it with Haystack, to build LLM applications.

## Download and run models
### Generative models
Several models are available. You can find some in the [llamafile repository](https://github.com/Mozilla-Ocho/llamafile) or search for them in the [Hugging Face Hub](https://huggingface.co/models?library=llamafile).

Let's see for example how to download the `Mistral-7B-Instruct` model and start an OpenAI-compatible server:

```bash
wget https://huggingface.co/Mozilla/Mistral-7B-Instruct-v0.2-llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_0.llamafile

chmod +x mistral-7b-instruct-v0.2.Q4_0.llamafile

./mistral-7b-instruct-v0.2.Q4_0.llamafile --server --nobrowser
```

This will start a server on `http://localhost:8000` that can be used to interact with the model.

If you encounter issues or need information on GPU support, refer to the [llamafile repository](https://github.com/Mozilla-Ocho/llamafile).

### Embedding models
Some embedding models are also available.

For example, to download and run the `mxbai-embed-large-v1` model:

```bash
wget https://huggingface.co/Mozilla/mxbai-embed-large-v1-llamafile/resolve/main/mxbai-embed-large-v1-f16.llamafile

chmod +x mxbai-embed-large-v1-f16.llamafile

./mxbai-embed-large-v1-f16.llamafile --server --nobrowser --embedding --port 8081
```

This will start an OpenAI-compatible server on `http://localhost:8081`.


## Usage with Haystack

Since llamafile runs OpenAI-compatible servers, you can use it with Haystack components that interact with OpenAI models:
[OpenAITextEmbedder](https://docs.haystack.deepset.ai/docs/openaitextembedder), [OpenAIDocumentEmbedder](https://docs.haystack.deepset.ai/docs/openaidocumentembedder), [OpenAIGenerator](https://docs.haystack.deepset.ai/docs/openaigenerator), and [OpenAIChatGenerator](https://docs.haystack.deepset.ai/docs/openaichatgenerator).


Let's start with an **indexing pipeline** that uses an embedding model.
You should have the `mxbai-embed-large-v1` model running as described above.

```python
from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import OpenAIDocumentEmbedder

document_store = InMemoryDocumentStore()

documents = [Document(content="My name is Wolfgang and I live in Berlin"),
             Document(content="I saw a black horse running"),
             Document(content="Germany has many big cities")]

indexing_pipeline = Pipeline()
indexing_pipeline.add_component("embedder",
                                OpenAIDocumentEmbedder(
                                    api_key=Secret.from_token("sk-no-key-required"),  # for compatibility with the OpenAI API
                                    model="LLaMA_CPP",
                                    api_base_url="http://localhost:8081/v1")
                                )
indexing_pipeline.add_component("writer", DocumentWriter(document_store=document_store))
indexing_pipeline.connect("embedder", "writer")

indexing_pipeline.run({"embedder": {"documents": documents}})
```

Now let's build a **RAG pipeline**, that uses both an embedding model and a generative model.
You should have the `mxbai-embed-large-v1` and `Mistral-7B-Instruct` models running as described above.

```python
from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.components.writers import DocumentWriter
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.embedders import OpenAITextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder


prompt_template = """<s>[INST]
Given these documents, answer the question.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{question}} [/INST]
Answer:
"""

rag_pipe = Pipeline()
rag_pipe.add_component("text_embedder", 
                        OpenAITextEmbedder(
                            api_key=Secret.from_token("sk-no-key-required"),  # for compatibility with the OpenAI API
                            model="LLaMA_CPP",
                            api_base_url="http://localhost:8081/v1")
                        )
rag_pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
rag_pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
rag_pipe.add_component("generator",
                        OpenAIGenerator(
                            api_key=Secret.from_token("sk-no-key-required"),  # for compatibility with the OpenAI API
                            model="LLaMA_CPP",
                            api_base_url="http://localhost:8080/v1")
                        )

rag_pipe.connect("text_embedder.embedding", "retriever.query_embedding")
rag_pipe.connect("retriever.documents", "prompt_builder.documents")
rag_pipe.connect("prompt_builder", "generator")

query = "Who lives in Berlin?"

result = rag_pipe.run({"text_embedder":{"text": query}})
print(result["generator"]["replies"][0])

# Wolfang
```