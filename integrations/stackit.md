---
layout: integration
name: STACKIT
description: Use the STACKIT API for text generation models.
authors:
    - name: deepset 
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/stackit-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/stackit
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/stackit.svg
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
[STACKIT](https://www.stackit.de/en/) provides access to Large Language Models via an API.
This Haystack integration introduces a [`STACKITChatGenerator`](https://docs.haystack.deepset.ai/docs/stackitchatgenerator) component to use that API and the chat completion models served by STACKIT, such as `neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8`.
In order to follow along with this guide, you'll need a STACKIT API key. Add it as an environment variable, `STACKIT_API_KEY`.

## Installation

```bash
pip install stackit-haystack
```

## Usage
### STACKITChatGenerator as a single component
```python
import os
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.stackit import STACKITChatGenerator

os.environ["STACKIT_API_KEY"] = "YOUR_STACKITL_API_KEY"


generator = STACKITChatGenerator(model="neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8")

result = generator.run([ChatMessage.from_user("Tell me a joke.")])
print(result)
```
```bash
{'replies': [ChatMessage(_role=<ChatRole.ASSISTANT: 'assistant'>, _content=[TextContent(text='A man walked into a library and asked the librarian, "Do you have any books on Pavlov\'s dogs and Schrödinger\'s cat?" \n\nThe librarian replied, "It rings a bell, but I\'m not sure if it\'s here or not."')], _name=None, _meta={'model': 'neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8', 'index': 0, 'finish_reason': 'stop', 'usage': {'completion_tokens': 55, 'prompt_tokens': 40, 'total_tokens': 95, 'completion_tokens_details': None, 'prompt_tokens_details': None}})]}
```
STACKIT also supports streaming responses if you pass a callback into the `STACKITChatGenerator` like so:

```python
import os

from haystack.components.generators.utils import print_streaming_chunk
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.generators.stackit import STACKITChatGenerator

os.environ["STACKIT_API_KEY"] = "YOUR_STACKIT_API_KEY"

client = STACKITChatGenerator(
    model="neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8",
    streaming_callback=print_streaming_chunk
)

response = client.run(
    messages=[ChatMessage.from_user("Tell me a joke.")]
)
print(response)
```

### `STACKITChatGenerator` in a pipeline

Use the `STACKITChatGenerator` in a pipeline with a `ChatPromptBuilder`:

```python
import os

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.generators.stackit import STACKITChatGenerator

os.environ["STACKIT_API_KEY"] = "YOUR_STACKIT_API_KEY"

prompt_builder = ChatPromptBuilder()
llm = STACKITChatGenerator(model="neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8")

messages = [ChatMessage.from_user("Question: {{question}} \\n")]

pipeline = Pipeline()
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("llm", llm)

pipeline.connect("prompt_builder.prompt", "llm.messages")

result = pipeline.run({"prompt_builder": {"template_variables": {"question": "Tell me a joke."}, "template": messages}})

print(result)
```

### `STACKITChatGenerator` in a RAG pipeline with streaming
To run this example, the HTMLToDocument requires an additional dependency to be installed via `pip install trafilatura`.
Use the `STACKITChatGenerator` in a RAG pipeline that streams chat replies to the console:

```python
import os

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import HTMLToDocument
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.generators.utils import print_streaming_chunk
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore

from haystack_integrations.components.generators.stackit import STACKITChatGenerator

os.environ["STACKIT_API_KEY"] = "YOUR_STACKIT_API_KEY"

document_store = InMemoryDocumentStore()
fetcher = LinkContentFetcher()
converter = HTMLToDocument()
chunker = DocumentSplitter()
writer = DocumentWriter(document_store=document_store)

indexing = Pipeline()

indexing.add_component(name="fetcher", instance=fetcher)
indexing.add_component(name="converter", instance=converter)
indexing.add_component(name="chunker", instance=chunker)
indexing.add_component(name="writer", instance=writer)

indexing.connect("fetcher", "converter")
indexing.connect("converter", "chunker")
indexing.connect("chunker", "writer")

indexing.run(data={"fetcher": {"urls": ["https://www.stackit.de/en/"]}})

retriever = InMemoryBM25Retriever(document_store=document_store)
prompt_builder = ChatPromptBuilder(variables=["documents"])
llm = STACKITChatGenerator(model="neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8", streaming_callback=print_streaming_chunk)

messages = [ChatMessage.from_user("Here are some of the documents: {{documents}} \\n Question: {{query}} \\n Answer:")]

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)

rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

question = "What does STACKIT offer?"

result = rag_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"template_variables": {"query": question}, "template": messages},
        "llm": {"generation_kwargs": {"max_tokens": 165}},
    }
)

print(result)
```

### License

`stackit-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
