---
layout: integration
name: Google AI
description: Use Google AI Models with Haystack
authors:
  - name: deepset
    socials:
      github: deepset-ai
      twitter: deepset_ai
      linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/google-ai-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/google_ai
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
  - [Multimodality with `gemini-1.5-flash`](#multimodality-with-gemini-1.5-flash)
  - [Function calling](#function-calling)
  - [Code generation](#code-generation)

## Overview

🚧 **This integration uses a deprecated SDK.**

**We recommend switching to the new [Google GenAI](https://haystack.deepset.ai/integrations/google-genai) integration instead.**

[Google AI](https://ai.google.dev/) is a machine learning (ML) platform that lets you train and deploy ML models and AI applications, and customize large language models (LLMs) for use in your AI-powered applications. This integration enables the usage of Google generative models via Google AI Studio.

Haystack supports all the available [multimodal Gemini models](https://ai.google.dev/models/gemini) for tasks such as **text generation**, **function calling**, **visual question answering**, **code generation**, and **image captioning**.

## Installation

Install the Google AI integration:

```bash
pip install google-ai-haystack
```

## Usage

Once installed, you will have access to various Haystack Generators:

- [`GoogleAIGeminiGenerator`](https://docs.haystack.deepset.ai/docs/googleaigeminigenerator): Use this component with [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini#model-variations), such as '**gemini-2.0-flash**', '**gemini-1.5-flash**', '**gemini-1.5-pro**' for text generation and multimodal prompts.
- [`GoogleAIGeminiChatGenerator`](https://docs.haystack.deepset.ai/docs/googleaigeminichatgenerator): Use this component with [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini#model-variations), such as '**gemini-2.0-flash**' and '**gemini-1.5-pro**' for text generation and and function calling in chat completion setting.

To use Google Gemini models you need an API key. You can either pass it as init argument or set a `GOOGLE_API_KEY` environment variable. If neither is set you won't be able to use the generators.

To get an API key visit [Google AI Studio](https://aistudio.google.com/).

**Text Generation with `gemini-1.5-pro`**

To use Gemini model for text generation, set the `GOOGLE_API_KEY` environment variable and then initialize a `GoogleAIGeminiGenerator` with `"gemini-1.5-pro"`:

```python
import os
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

gemini_generator = GoogleAIGeminiGenerator(model="gemini-1.5-pro")
result = gemini_generator.run(parts = ["What is assemblage in art?"])
print(result["replies"][0])
```

Output:

```shell
Assemblage in art refers to the creation of a three-dimensional artwork by combining various found objects...
```

### Multimodality with `gemini-1.5-flash`

To use `gemini-1.5-flash` model for visual question answering, initialize a `GoogleAIGeminiGenerator` with `"gemini-1.5-flash"` and `project_id`. Then, run it with the images as well as the prompt:

```python
import requests
import os
from haystack.dataclasses.byte_stream import ByteStream

from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator

BASE_URL = (
    "https://raw.githubusercontent.com/deepset-ai/haystack-core-integrations"
    "/main/integrations/google_ai/example_assets"
)

URLS = [
    f"{BASE_URL}/robot1.jpg",
    f"{BASE_URL}/robot2.jpg",
    f"{BASE_URL}/robot3.jpg",
    f"{BASE_URL}/robot4.jpg"
]
images = [
    ByteStream(data=requests.get(url).content, mime_type="image/jpeg")
    for url in URLS
]

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

gemini_generator = GoogleAIGeminiGenerator(model="gemini-1.5-flash")
result = gemini_generator.run(parts = ["What can you tell me about these robots?", *images])
for answer in result["replies"]:
    print(answer)
```

Output:

```shell
The first image is of C-3PO and R2-D2 from the Star Wars franchise...
The second image is of Maria from the 1927 film Metropolis...
The third image is of Gort from the 1951 film The Day the Earth Stood Still...
The fourth image is of Marvin from the 1977 film The Hitchhiker's Guide to the Galaxy...
```

### Function calling

When chatting with Gemini we can also use function calls.

```python
from typing import Annotated
from haystack.utils import Secret
from haystack.dataclasses.chat_message import ChatMessage
from haystack.components.tools import ToolInvoker
from haystack.tools import create_tool_from_function

from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator


# example function to get the current weather
def get_current_weather(
    location: Annotated[str, "The city for which to get the weather, e.g. 'San Francisco'"] = "Munich",
    unit: Annotated[str, "The unit for the temperature, e.g. 'celsius'"] = "celsius",
) -> str:
    return f"The weather in {location} is sunny. The temperature is 20 {unit}."

tool = create_tool_from_function(get_current_weather)
tool_invoker = ToolInvoker(tools=[tool])

gemini_chat = GoogleAIGeminiChatGenerator(
    model="gemini-2.0-flash-exp",
    api_key=Secret.from_token("<MY_API_KEY>"),
    tools=[tool],
)
user_message = [ChatMessage.from_user("What is the temperature in celsius in Berlin?")]
replies = gemini_chat.run(messages=user_message)["replies"]
print(replies[0].tool_calls)

# actually invoke the tool
tool_messages = tool_invoker.run(messages=replies)["tool_messages"]
messages = user_message + replies + tool_messages

# transform the tool call result into a human readable message
final_replies = gemini_chat.run(messages=messages)["replies"]
print(final_replies[0].text)
```

Will output:

```
In Berlin, the weather is sunny with a temperature of 20 degrees Celsius.
```

### Code generation

Gemini can also easily generate code, here's an example:

```python
import os
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

gemini_generator = GoogleAIGeminiGenerator(model="gemini-1.5-pro")
result = gemini_generator.run("Write a code for calculating fibonacci numbers in JavaScript")
print(result["replies"][0])
```

Output:

```javascript
// Recursive approach
function fibonacciRecursive(n) {
  if (n <= 1) {
    return n;
  } else {
    return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);
  }
}

// Iterative approach
function fibonacciIterative(n) {
  if (n <= 1) {
    return n;
  }

  let fibSequence = [0, 1];
  while (fibSequence.length < n + 1) {
    let nextNumber =
      fibSequence[fibSequence.length - 1] + fibSequence[fibSequence.length - 2];
    fibSequence.push(nextNumber);
  }

  return fibSequence[n];
}

// Usage
console.log(fibonacciRecursive(7)); // Output: 13
console.log(fibonacciIterative(7)); // Output: 13
```
