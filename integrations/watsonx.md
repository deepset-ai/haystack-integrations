---
layout: integration
name: IBM Watsonx
description: Use IBM’s watsonx models with Haystack for chat and embedding tasks via the new Watsonx SDK integration.
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
  - name: Divya
    socials:
      github: divyaruhil
pypi: https://pypi.org/project/watsonx-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/watsonx
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/watsonx.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Chat Generation with `granite-3-2b-instruct`](#chat-generation-with-granite-3-2b-instruct)
  - [Streaming Chat Generation](#streaming-chat-generation)
  - [Document Embedding](#document-embedding)
  - [Text Embedding](#text-embedding)

## Overview

[IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai) provides access to IBM’s foundation models for enterprise AI. This integration allows you to use powerful models like `granite-3-2b-instruct` and `slate-125m-english-rtrvr` with Haystack for chat and embedding tasks.

## Installation

Install the IBM Watsonx integration:

```bash
pip install watsonx-haystack
```

## Usage

Once installed, you will have access to the Haystack Chat components:
- [`WatsonxChatGenerator`](https://docs.haystack.deepset.ai/docs/watsonxchatgenerator): Use this component with IBM watsonx models like `granite-3-2b-instruct` for chat generation.
- [`WatsonxGenerator`](https://docs.haystack.deepset.ai/docs/watsonxgenerator): Use this component with IBM watsonx models like `granite-3-2b-instruct` for simple text generation tasks.
- [`WatsonxDocumentEmbedder`](https://docs.haystack.deepset.ai/docs/watsonxdocumentembedder): Use this component with IBM watsonx models like `slate-125m-english-rtrvr` for generating document embeddings.
- [`WatsonxTextEmbedder`](https://docs.haystack.deepset.ai/docs/watsonxtextembedder): Use this component with IBM watsonx models like `slate-125m-english-rtrvr` for generating text embeddings and retrieval.

To use the Watsonx integration, you must provide your `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` via environment variables or as an init argument. If neither is set, you won't be able to use the generator.

To get an API key, you can follow the sign-up process for [watsonx.ai](https://www.ibm.com/products/watsonx-ai).


### Chat Generation with `granite-3-2b-instruct`

To use Watsonx models for chat generation, set the `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` environment variable and then initialize a `WatsonxChatGenerator` with `"ibm/granite-3-2b-instruct"`:

```python
import os
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.generators.watsonx.chat.chat_generator import WatsonxChatGenerator

os.environ["WATSONX_API_KEY"] = "your_watsonx_api_key"
os.environ["WATSONX_PROJECT_ID"] = "your_watsonx_project_id"

generator = WatsonxChatGenerator(
    api_key=Secret.from_env_var("WATSONX_API_KEY"),
    project_id=Secret.from_env_var("WATSONX_PROJECT_ID"),
    model="ibm/granite-3-2b-instruct"
)

messages = [
    ChatMessage.from_system("You are a helpful assistant."),
    ChatMessage.from_user("Explain quantum computing in simple terms.")
]

response = generator.run(messages=messages)
print(response["replies"][0].text)
```

Output:

```shell
Quantum computing is a type of computing that uses the principles of quantum mechanics to process information. ...
```

### Streaming Chat Generation

For real-time streaming responses, you can use the streaming callback functionality:

```python
import os
from haystack.dataclasses import ChatMessage, StreamingChunk
from haystack.utils import Secret
from haystack_integrations.components.generators.watsonx.chat.chat_generator import WatsonxChatGenerator

os.environ["WATSONX_API_KEY"] = "your_watsonx_api_key"
os.environ["WATSONX_PROJECT_ID"] = "your_watsonx_project_id"

def print_streaming_chunk(chunk: StreamingChunk):
    print(chunk.content, end="", flush=True)

# Initialize with streaming callback
generator = WatsonxChatGenerator(
    api_key=Secret.from_env_var("WATSONX_API_KEY"),
    project_id=Secret.from_env_var("WATSONX_PROJECT_ID"),
    model="ibm/granite-3-2b-instruct",
    streaming_callback=print_streaming_chunk
)

# Generate a streaming response
messages = [ChatMessage.from_user("Write a short poem about artificial intelligence.")]
generator.run(messages=messages)
# Text will stream in real-time via the callback
```

### Document Embedding

To use Watsonx models for document embedding, set the `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` environment variable and then initialize a `WatsonxDocumentEmbedder` with `"ibm/slate-125m-english-rtrvr"`:

```python
import os
from haystack import Document
from haystack.utils import Secret
from haystack_integrations.components.embedders.watsonx.document_embedder import WatsonxDocumentEmbedder

os.environ["WATSONX_API_KEY"] = "your_watsonx_api_key"
os.environ["WATSONX_PROJECT_ID"] = "your_watsonx_project_id"

document_embedder = WatsonxDocumentEmbedder(
    model="ibm/slate-125m-english-rtrvr",
    api_key=Secret.from_env_var("WATSONX_API_KEY"),
    project_id=Secret.from_env_var("WATSONX_PROJECT_ID"),
    api_base_url="https://us-south.ml.cloud.ibm.com"
)

documents = [Document(content="Germany has many big cities.")]
docs_with_embeddings = document_embedder.run(documents)["documents"]
print(docs_with_embeddings)
```

Output:

```shell
[Document(id=..., content: 'Germany has many big cities.', embedding: vector of size 768)]
```

### Text Embedding

To use Watsonx models for text embedding, set the `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` environment variable and then initialize a `WatsonxTextEmbedder` with `"ibm/slate-125m-english-rtrvr"`:

```python
import os
from haystack.utils import Secret
from haystack_integrations.components.embedders.watsonx.text_embedder import WatsonxTextEmbedder

os.environ["WATSONX_API_KEY"] = "your_watsonx_api_key"
os.environ["WATSONX_PROJECT_ID"] = "your_watsonx_project_id"

text_embedder = WatsonxTextEmbedder(
    model="ibm/slate-125m-english-rtrvr",
    api_key=Secret.from_env_var("WATSONX_API_KEY"),
    project_id=Secret.from_env_var("WATSONX_PROJECT_ID"),
    api_base_url="https://us-south.ml.cloud.ibm.com"
)

text = "I love pizza!"
result = text_embedder.run(text=text)
print(result)
```

Output:

```shell
{'embedding': [0.123, -0.456, 0.789, ...], 
'meta': {'model': 'ibm/slate-125m-english-rtrvr', 'truncated_input_tokens': None}}
```
