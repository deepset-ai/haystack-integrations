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
  - [Chat Generation with `gemini-2.0-flash`](#chat-generation-with-gemini-20-flash)
  - [Streaming Chat Generation](#streaming-chat-generation)
  - [Function calling](#function-calling)
  - [Document Embedding](#document-embedding)
  - [Text Embedding](#text-embedding)

## Overview

[Google Gen AI](https://ai.google.dev/) provides access to Google's Gemini models through the new Google Gen AI SDK. This integration enables the usage of Google's latest generative models via the updated API interface.

Haystack supports the latest [Gemini models](https://ai.google.dev/models/gemini) like `gemini-2.0-flash` and `text-embedding-004` for tasks such as **chat completion**, **function calling**, **streaming responses** and **embedding generation**.

## Installation

Install the Google Gen AI integration:

```bash
pip install google-genai-haystack
```

## Usage

Once installed, you will have access to the Haystack Chat components:

- [`GoogleGenAIChatGenerator`](https://docs.haystack.deepset.ai/docs/googlegenaichatgenerator): Use this component with [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini#model-variations), such as '**gemini-2.0-flash**' for chat completion and function calling.
- `GoogleGenAIDocumentEmbedder`: Use this component with [Google GenAI models](https://ai.google.dev/gemini-api/docs/embeddings#embeddings-models), such as '**text-embedding-004**' for generating embeddings.
- `GoogleGenAIChatGenerator`: Use this component with [Google GenAI models](https://ai.google.dev/gemini-api/docs/embeddings#embeddings-models), such as '**text-embedding-004**' for generating embeddings.

To use Google Gemini models you need an API key. You can either pass it as init argument or set a `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable. If neither is set you won't be able to use the generator.

To get an API key visit [Google AI Studio](https://aistudio.google.com/).

### Chat Generation with `gemini-2.0-flash`

To use Gemini model for chat generation, set the `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable and then initialize a `GoogleGenAIChatGenerator` with `"gemini-2.0-flash"`:

```python
import os
from haystack.dataclasses.chat_message import ChatMessage
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

# Initialize the chat generator
chat_generator = GoogleGenAIChatGenerator(model="gemini-2.0-flash")

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
    model="gemini-2.0-flash",
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
    model="gemini-2.0-flash",
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

### Document Embedding

To use Google model for embedding generation, set the `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable and then initialize a `GoogleGenAIDocumentEmbedder`:

```python
import os
from haystack import Document
from haystack_integrations.components.embedders.google_genai import GoogleGenAIDocumentEmbedder

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

# Initialize the embedder
embedder = GoogleGenAIDocumentEmbedder()

# Generate a response
doc = Document(content="some text")
docs_w_embeddings = embedder.run(documents=[doc])["documents"]
```

### Text Embedding

To use Google model for embedding generation, set the `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable and then initialize a `GoogleGenAITextEmbedder`:

```python
import os
from haystack_integrations.components.embedders.google_genai import GoogleGenAITextEmbedder

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

text_to_embed = "I love pizza!"

# Initialize the text embedder
text_embedder = GoogleGenAITextEmbedder()

# Generate a response
print(text_embedder.run(text_to_embed))
```

Output:

```shell
{'embedding': [-0.052871075, -0.035282962, ...., -0.04802792], 
'meta': {'model': 'text-embedding-004'}}
```