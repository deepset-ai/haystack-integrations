---
layout: integration
name: Llama.cpp
description: Use Llama.cpp models with Haystack.
authors:
  - name: Ashwin Mathur
    socials:
      github: awinml
      twitter: awinml
      linkedin: https://www.linkedin.com/in/ashwin-mathur-ds
pypi: https://pypi.org/project/llama-cpp-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/llama_cpp
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
logo: /logos/llama_cpp.png
---

### Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
  - [Using a different compute backend](#using-a-different-compute-backend)
- [Downloading Models](#downloading-models)
- [Usage](#usage)
  - [Passing additional model parameters](#passing-additional-model-parameters)
  - [Passing text generation parameters](#passing-text-generation-parameters)
- [Example: RAG Pipeline](#example-rag-pipeline)

## Introduction

[Llama.cpp](https://github.com/ggerganov/llama.cpp) is a library written in C/C++ for efficient inference of Large Language models. It uses the efficient quantized GGUF format, dramatically reducing memory requirements and accelerating inference. This means it is possible to run LLMs efficiently on standard machines (even without GPUs).

## Installation

Install the `llama-cpp-haystack` package:

```bash
pip install llama-cpp-haystack
```

### Using a different compute backend

The default installation behaviour is to build `llama.cpp` for CPU on Linux and Windows and use Metal on MacOS. To use other compute backends:

1. Follow instructions on the [llama.cpp installation page](https://github.com/abetlen/llama-cpp-python#installation) to install [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) for your preferred compute backend.
2. Install [llama-cpp-haystack](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/llama_cpp) using the command above.

For example, to use `llama-cpp-haystack` with the **cuBLAS backend**, you have to run the following commands:

```bash
export LLAMA_CUBLAS=1
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
pip install llama-cpp-haystack
```

## Downloading Models

Llama.cpp requires the quantized binary of the LLM in GGUF format.

The GGUF versions of popular LLMs can be downloaded from [HuggingFace](https://huggingface.co/models?library=gguf).

For example, to download the GGUF version of [OpenChat3.5](https://huggingface.co/openchat/openchat_3.5), we find the required [GGUF version on HuggingFace](https://huggingface.co/TheBloke/openchat-3.5-1210-GGUF) and then download the file to disk:

```python
import os
import urllib.request

def download_file(file_link, filename):
    # Checks if the file already exists before downloading
    if not os.path.isfile(filename):
        urllib.request.urlretrieve(file_link, filename)
        print("Model file downloaded successfully.")
    else:
        print("Model file already exists.")

# Download GGUF model from HuggingFace
ggml_model_path = (
    "https://huggingface.co/TheBloke/openchat-3.5-1210-GGUF/resolve/main/openchat-3.5-1210.Q3_K_S.gguf"
)
filename = "openchat-3.5-1210.Q3_K_S.gguf"
download_file(ggml_model_path, filename)
```

You could also directly download the file from the command line using Curl:

```bash
curl -L -O "https://huggingface.co/TheBloke/openchat-3.5-1210-GGUF/resolve/main/openchat-3.5-1210.Q3_K_S.gguf"
```

## Usage

You can leverage Llama.cpp to run models by using the `LlamaCppGenerator` component.

Initialize an `LlamaCppGenerator` with the the path to the GGUF file and also specify the required model and text generation parameters:

```python
from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator

generator = LlamaCppGenerator(
    model="/content/openchat-3.5-1210.Q3_K_S.gguf",
    n_ctx=512,
    n_batch=128,
    model_kwargs={"n_gpu_layers": -1},
		generation_kwargs={"max_tokens": 128, "temperature": 0.1},
)
generator.warm_up()
prompt = f"Who is the best American actor?"
result = generator.run(prompt)
```

### Passing additional model parameters

The `model_path`, `n_ctx`, `n_batch` arguments have been exposed for convenience and can be directly passed to the Generator during initialization as keyword arguments.

The `model_kwargs` parameter can be used to pass additional arguments when initializing the model. In case of duplication, these parameters override the `model_path`, `n_ctx`, and `n_batch` initialization parameters.

See [Llama.cpp's LLM documentation](https://llama-cpp-python.readthedocs.io/en/latest/api-reference/#llama_cpp.Llama.__init__) for more information on the available model arguments.

For example, to offload the model to GPU during initialization:

```python
from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator

generator = LlamaCppGenerator(
    model="/content/openchat-3.5-1210.Q3_K_S.gguf",
    n_ctx=512,
    n_batch=128,
    model_kwargs={"n_gpu_layers": -1}
)
generator.warm_up()
prompt = f"Who is the best American actor?"
result = generator.run(prompt, generation_kwargs={"max_tokens": 128})
generated_text = result["replies"][0]
print(generated_text)
```

### Passing text generation parameters

The `generation_kwargs` parameter can be used to pass additional generation arguments like `max_tokens`, `temperature`, `top_k`, `top_p`, etc to the model during inference.

See [Llama.cpp's Completion API documentation](https://llama-cpp-python.readthedocs.io/en/latest/api-reference/#llama_cpp.Llama.create_completion) for more information on the available generation arguments.

For example, to set the `max_tokens` and `temperature`:

```python
from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator

generator = LlamaCppGenerator(
    model="/content/openchat-3.5-1210.Q3_K_S.gguf",
    n_ctx=512,
    n_batch=128,
    generation_kwargs={"max_tokens": 128, "temperature": 0.1},
)
generator.warm_up()
prompt = f"Who is the best American actor?"
result = generator.run(prompt)
```

The `generation_kwargs` can also be passed to the `run` method of the generator directly:

```python
from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator

generator = LlamaCppGenerator(
    model="/content/openchat-3.5-1210.Q3_K_S.gguf",
    n_ctx=512,
    n_batch=128,
)
generator.warm_up()
prompt = f"Who is the best American actor?"
result = generator.run(
    prompt,
    generation_kwargs={"max_tokens": 128, "temperature": 0.1},
)
```

## Example: RAG Pipeline

We use the `LlamaCppGenerator` in a Retrieval Augmented Generation pipeline on the [Simple Wikipedia](https://huggingface.co/datasets/pszemraj/simple_wikipedia) Dataset from HuggingFace and generate answers using the [OpenChat-3.5](https://huggingface.co/openchat/openchat-3.5-1210) LLM.

**Load the dataset:**

```python
# Install HuggingFace Datasets using "pip install datasets"
from datasets import load_dataset
from haystack import Document, Pipeline
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

# Import LlamaCppGenerator
from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator

# Load first 100 rows of the Simple Wikipedia Dataset from HuggingFace
dataset = load_dataset("pszemraj/simple_wikipedia", split="validation[:100]")

docs = [
    Document(
        content=doc["text"],
        meta={
            "title": doc["title"],
            "url": doc["url"],
        },
    )
    for doc in dataset
]
```

**Index the documents to the `InMemoryDocumentStore` using the `SentenceTransformersDocumentEmbedder` and `DocumentWriter`:**

```python
doc_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")

# Indexing Pipeline
indexing_pipeline = Pipeline()
indexing_pipeline.add_component(instance=doc_embedder, name="DocEmbedder")
indexing_pipeline.add_component(instance=DocumentWriter(document_store=doc_store), name="DocWriter")
indexing_pipeline.connect("DocEmbedder", "DocWriter")

indexing_pipeline.run({"DocEmbedder": {"documents": docs}})
```

**Create the Retrieval Augmented Generation (RAG) pipeline and add the `LlamaCppGenerator` to it:**

```python
# Prompt Template for the https://huggingface.co/openchat/openchat-3.5-1210 LLM
prompt_template = """GPT4 Correct User: Answer the question using the provided context.
Question: {{question}}
Context:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
<|end_of_turn|>
GPT4 Correct Assistant:
"""

rag_pipeline = Pipeline()

text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")

# Load the LLM using LlamaCppGenerator
model_path = "openchat-3.5-1210.Q3_K_S.gguf"
generator = LlamaCppGenerator(model=model_path, n_ctx=4096, n_batch=128)

rag_pipeline.add_component(
    instance=text_embedder,
    name="text_embedder",
)
rag_pipeline.add_component(instance=InMemoryEmbeddingRetriever(document_store=doc_store, top_k=3), name="retriever")
rag_pipeline.add_component(instance=PromptBuilder(template=prompt_template), name="prompt_builder")
rag_pipeline.add_component(instance=generator, name="llm")
rag_pipeline.add_component(instance=AnswerBuilder(), name="answer_builder")

rag_pipeline.connect("text_embedder", "retriever")
rag_pipeline.connect("retriever", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm")
rag_pipeline.connect("llm.replies", "answer_builder.replies")
rag_pipeline.connect("retriever", "answer_builder.documents")
```

**Run the pipeline:**

```python
question = "Which year did the Joker movie release?"
result = rag_pipeline.run(
    {
        "text_embedder": {"text": question},
        "prompt_builder": {"question": question},
        "llm": {"generation_kwargs": {"max_tokens": 128, "temperature": 0.1}},
        "answer_builder": {"query": question},
    }
)

generated_answer = result["answer_builder"]["answers"][0]
print(generated_answer.data)
# The Joker movie was released on October 4, 2019.
```
