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

[Google AI](https://ai.google.dev/) is a machine learning (ML) platform that lets you train and deploy ML models and AI applications, and customize large language models (LLMs) for use in your AI-powered applications. This integration enables the usage of Google generative models via their Makersuite REST API.

Haystack supports all the available [multimodal Gemini models](https://ai.google.dev/models/gemini) for tasks such as **text generation**, **function calling**, **visual question answering**, **code generation**, and **image captioning**.

## Installation

Install the Google AI integration:

```bash
pip install google-ai-haystack
```

## Usage

Once installed, you will have access to various Haystack Generators:

- [`GoogleAIGeminiGenerator`](https://docs.haystack.deepset.ai/docs/googleaigeminigenerator): Use this component with Gemini models '**gemini-pro**', '**gemini-1.5-flash**', '**gemini-1.5-pro**' for text generation and multimodal prompts.
- [`GoogleAIGeminiChatGenerator`](https://docs.haystack.deepset.ai/docs/googleaigeminichatgenerator): Use this component with Gemini models '**gemini-pro**', '**gemini-1.5-flash**' and '**gemini-1.5-pro**' for text generation, multimodal prompts and function calling in chat completion setting.

To use Google Gemini models you need an API key. You can either pass it as init argument or set a `GOOGLE_API_KEY` environment variable. If neither is set you won't be able to use the generators.

To get an API key visit [Google Makersuite](https://makersuite.google.com).

**Text Generation with `gemini-pro`**

To use Gemini model for text generation, set the `GOOGLE_API_KEY` environment variable and then initialize a `GoogleAIGeminiGenerator` with `"gemini-pro"`:

```python
import os
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

gemini_generator = GoogleAIGeminiGenerator(model="gemini-pro")
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
import os
import json
from google.ai.generativelanguage import FunctionDeclaration, Tool
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.generators.google_ai import GoogleAIGeminiChatGenerator

# Define a function that return always some nice weather
def get_current_weather(location: str, unit: str = "celsius"):
    return {"weather": "sunny", "temperature": 21.8, "unit": unit}

# Class that defines the arguments of a function so Gemini
# knows how it should be called
get_current_weather_func = FunctionDeclaration(
    name="get_current_weather",
    description="Get the current weather in a given location",
    parameters={
        "type_": "OBJECT",
        "properties": {
            "location": {"type_": "STRING", "description": "The city and state, e.g. San Francisco, CA"},
            "unit": {
                "type_": "STRING",
                "enum": [
                    "celsius",
                    "fahrenheit",
                ],
            },
        },
        "required": ["location"],
    },
)
tool = Tool(function_declarations=[get_current_weather_func])

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

gemini_chat = GoogleAIGeminiChatGenerator(model="gemini-pro", tools=[tool])

messages = [
    ChatMessage.from_user(content="What is the temperature in celsius in Berlin?")
]
res = gemini_chat.run(messages=messages)
weather = get_current_weather(**json.loads(res["replies"][0].text))

messages += res["replies"] + [
    ChatMessage.from_function(content=weather, name="get_current_weather")
]

res = gemini_chat.run(messages=messages)
print(res["replies"][0].text)
```

Will output:

```
In Berlin, the weather is sunny with a temperature of 21.8 degrees Celsius.
```

### Code generation

Gemini can also easily generate code, here's an example:

```python
import os
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator

os.environ["GOOGLE_API_KEY"] = "YOUR-GOOGLE-API-KEY"

gemini_generator = GoogleAIGeminiGenerator(model="gemini-pro")
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
