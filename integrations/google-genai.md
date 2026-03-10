---
layout: integration
name: Google Gen AI
description: Use Google's Gemini models with Haystack via the new Google Gen AI SDK
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
  - name: Gary Badwal
    socials:
      website: garybadwal.com
      github: garybadwal
      twitter: garybadwal_
      linkedin: https://www.linkedin.com/in/garybadwal/
pypi: https://pypi.org/project/google-genai-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/google_genai
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/googleai.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Chat Generation with `gemini-3.1-flash-lite-preview`](#chat-generation-with-gemini-31-flash-lite-preview)
  - [Streaming Chat Generation](#streaming-chat-generation)
  - [Function calling](#function-calling)
  - [Embeddings](#embeddings)
  - [Multimodal Embeddings with `gemini-embedding-2-preview`](#multimodal-embeddings-with-gemini-embedding-2-preview)
- [License](#license)

## Overview

[Google Gen AI](https://ai.google.dev/) provides access to Google's Gemini models through the new Google Gen AI SDK. This integration enables the usage of Google's latest generative models via the updated API interface.
Google Gen AI is compatible with both the Gemini Developer API and the Vertex AI API.

Haystack supports the latest [Gemini models](https://ai.google.dev/models/gemini) for tasks such as **chat completion**, **function calling**, **streaming responses** and **embedding generation**.

**Generative models:** `gemini-3.1-flash-lite-preview`, `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.5-flash-lite`, and the Gemini 2.0 series (e.g. `gemini-2.0-flash`).

**Embedding models:** `gemini-embedding-2-preview` (multimodal, multilingual) and `gemini-embedding-001` (multilingual).

> 🖼️ Learn how to build multimodal search systems using Gemini Embedding 2 to embed text, images, video, audio, and PDFs in [Multimodal Search with Gemini Embedding 2 in Haystack](https://haystack.deepset.ai/blog/multimodal-embeddings-gemini-haystack). 

## Installation

Install the Google Gen AI integration:

```bash
pip install google-genai-haystack
```

## Usage

Once installed, you will have access to the Haystack Chat components:

- [`GoogleGenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/googlegenaichatgenerator): Use this component with [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini#model-variations), such as **gemini-3.1-flash-lite-preview** or **gemini-2.5-pro** for chat completion and function calling.
- [`GoogleGenAIDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/googlegenaidocumentembedder): Use this component with [Google GenAI embedding models](https://ai.google.dev/gemini-api/docs/embeddings#embeddings-models), such as **gemini-embedding-001** for generating embeddings for documents.
- [`GoogleGenAITextEmbedder`](https://docs.haystack.deepset.ai/docs/googlegenaitextembedder): Use this component with [Google GenAI embedding models](https://ai.google.dev/gemini-api/docs/embeddings#embeddings-models), such as **gemini-embedding-001** for generating embeddings for text.
- [`GoogleGenAIMultimodalDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/googlegenaimultimodaldocumentembedder): Use this component with [Google GenAI multimodal embedding models](https://ai.google.dev/gemini-api/docs/embeddings#embeddings-models), such as **gemini-embedding-2-preview** for generating embeddings for text, image, PDF, video and audio.

To use this component with the Gemini Developer API and get an API key, visit [Google AI Studio](https://aistudio.google.com/).
To use this component with the Vertex AI API, visit [Google Cloud > Vertex AI](https://cloud.google.com/vertex-ai).

### Authentication

The following examples show how to use the component with the Gemini Developer API and the Vertex AI API. They are also valid
for the Embedders.

#### Gemini Developer API (API Key Authentication)
```python
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator

# set the environment variable (GOOGLE_API_KEY or GEMINI_API_KEY)
chat_generator = GoogleGenAIChatGenerator()
```

#### Vertex AI (Application Default Credentials)
```python
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator

# Using Application Default Credentials (requires gcloud auth setup)
chat_generator = GoogleGenAIChatGenerator(
    api="vertex",
    vertex_ai_project="my-project",
    vertex_ai_location="us-central1",
)
```

#### Vertex AI (API Key Authentication)
```python
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator

# set the environment variable (GOOGLE_API_KEY or GEMINI_API_KEY)
chat_generator = GoogleGenAIChatGenerator(api="vertex")
```

### Chat Generation with `gemini-3.1-flash-lite-preview`

To use Gemini model for chat generation, set the `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable and then initialize a `GoogleGenAIChatGenerator` with `"gemini-3.1-flash-lite-preview"`:

```python
import os
from haystack.dataclasses.chat_message import ChatMessage
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

# Initialize the chat generator
chat_generator = GoogleGenAIChatGenerator(model="gemini-3.1-flash-lite-preview")

# Generate a response
messages = [ChatMessage.from_user("Tell me about the future of AI")]
response = chat_generator.run(messages=messages)
print(response["replies"][0].text)
```

Output:

```shell
The future of AI is incredibly exciting and multifaceted, with developments spanning multiple domains...
```

### Streaming Chat Generation

For real-time streaming responses, you can use the streaming callback functionality:

```python
import os
from haystack.dataclasses.chat_message import ChatMessage
from haystack.dataclasses import StreamingChunk
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

def streaming_callback(chunk: StreamingChunk):
    print(chunk.content, end='', flush=True)

# Initialize with streaming callback
chat_generator = GoogleGenAIChatGenerator(
    model="gemini-3.1-flash-lite-preview",
    streaming_callback=streaming_callback
)

# Generate a streaming response
messages = [ChatMessage.from_user("Write a short story about robots")]
response = chat_generator.run(messages=messages)
# Text will stream in real-time via the callback
```

### Function calling

When chatting with Gemini models, you can also use function calls for tool integration:

```python
import os
from haystack.dataclasses.chat_message import ChatMessage
from haystack.tools import Tool

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

# Define a simple weather function
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny and 25°C"

# Create a tool from the function
weather_tool = Tool(
    name="get_weather",
    description="Get weather information for a city",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "The city name"}
        },
        "required": ["city"]
    },
    function=get_weather
)

# Initialize chat generator with tools
chat_generator = GoogleGenAIChatGenerator(
    model="gemini-3.1-flash-lite-preview",
    tools=[weather_tool]
)

# Generate response with tool usage
messages = [ChatMessage.from_user("What's the weather like in Paris?")]
response = chat_generator.run(messages=messages)

# The model will call the weather function and provide a natural response
print(response["replies"][0].text)
```

Output:

```shell
The weather in Paris is sunny and 25°C.
``` 

### Embeddings

Embeddings are vector representations of text that capture semantic meaning. They power use cases like **semantic search**, **retrieval-augmented generation (RAG)**, and **similarity comparison** e.g. finding documents or passages that are closest in meaning to a query.

This integration provides three embedder components:

- **`GoogleGenAIDocumentEmbedder`** — Embeds Haystack `Document` objects (text content). Use it when indexing documents into a vector store or when you need to embed multiple documents in one call. The resulting embeddings are stored on the documents and can be used for document retrieval.
- **`GoogleGenAITextEmbedder`** — Embeds a single string. Use it when you need to embed a search query or any standalone text to compare against document embeddings (e.g. in a RAG pipeline for the query side).
- **`GoogleGenAIMultimodalDocumentEmbedder`** — Embeds documents that can contain **images**, **videos**, or **PDFs** (via `meta["file_path"]`). Use the `gemini-embedding-2-preview` model for multimodal retrieval, e.g. searching over mixed media with text or image queries.

For text-only pipelines, use the same model (e.g. `gemini-embedding-001`) for documents and queries so that their embeddings live in the same vector space. For multimodal content, use `gemini-embedding-2-preview` with the appropriate `task_type` in the config.

#### Document Embedding

Use `GoogleGenAIDocumentEmbedder` to create embeddings for documents before storing them in a document store or using them in retrieval:

```python
import os
from haystack import Document
from haystack_integrations.components.embedders.google_genai import GoogleGenAIDocumentEmbedder

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

# Initialize the embedder (uses gemini-embedding-001 by default)
embedder = GoogleGenAIDocumentEmbedder(model="gemini-embedding-001")

# Generate a response
doc = Document(content="some text")
docs_w_embeddings = embedder.run(documents=[doc])["documents"]
```

#### Text Embedding

Use `GoogleGenAITextEmbedder` to embed a single string (e.g. a user query) so you can compare it to document embeddings:

```python
import os
from haystack_integrations.components.embedders.google_genai import GoogleGenAITextEmbedder

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

text_to_embed = "I love pizza!"
# Initialize the text embedder (uses gemini-embedding-001 by default)
text_embedder = GoogleGenAITextEmbedder(model="gemini-embedding-001")

# Generate a response
print(text_embedder.run(text_to_embed))
```

Output:

```shell
{'embedding': [-0.052871075, -0.035282962, ...., -0.04802792], 
'meta': {'model': 'gemini-embedding-001'}}
```

The returned embedding is a list of floats (e.g. 3072 dimensions for `gemini-embedding-001`). In a typical RAG pipeline you would pass this query embedding to a retriever to find the most similar document embeddings from your index.

#### Multimodal Embeddings with `gemini-embedding-2-preview`

`GoogleGenAIMultimodalDocumentEmbedder` embeds documents that reference **text**, **images**, **audios**, **videos**, or **PDFs** via `meta["file_path"]`. It uses the `gemini-embedding-2-preview` model, which produces a unified embedding space for text, images, and other modalities—so you can index mixed media and retrieve with text or image queries.

Set `config={"task_type": "RETRIEVAL_DOCUMENT"}` when embedding documents for indexing, and use `RETRIEVAL_QUERY` when embedding queries. Use the same model and task type pairing so document and query embeddings are comparable.

Example: embedding multiple files (text, audio, video, images, PDF) and writing them to a document store:

```python
import os
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack import Document
from haystack_integrations.components.embedders.google_genai import GoogleGenAIMultimodalDocumentEmbedder

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

document_store = InMemoryDocumentStore()
docs = [
    Document(meta={"file_path": "kangaroo.mp4"}),
    Document(meta={"file_path": "tiger.jpg"}),
    Document(meta={"file_path": "sample.pdf"}),
    Document(meta={"file_path": "dog.jpg"}),
    Document(meta={"file_path": "cat.jpg"}),
]

doc_multimodal_embedder = GoogleGenAIMultimodalDocumentEmbedder(
    model="gemini-embedding-2-preview",
    config={"task_type": "RETRIEVAL_DOCUMENT"},
)
docs_with_embeddings = doc_multimodal_embedder.run(documents=docs)
document_store.write_documents(docs_with_embeddings["documents"])
```

## License
`google-genai-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.