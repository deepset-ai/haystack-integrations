---
layout: integration
name: Asyntai AI Chatbot
description: Answer from a whole website, feed its knowledge base, and read its chats and leads with the Asyntai AI chat agent.
authors:
    - name: Asyntai
      socials:
        github: asyntai
pypi: https://pypi.org/project/asyntai-haystack
repo: https://github.com/asyntai/asyntai-haystack
type: Tool Integration
report_issue: https://github.com/asyntai/asyntai-haystack/issues
logo: /logos/asyntai.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Components](#components)
  - [Ask a website a question](#ask-a-website-a-question)
  - [Teach the website agent from your files](#teach-the-website-agent-from-your-files)
  - [Give an agent the Asyntai tools](#give-an-agent-the-asyntai-tools)
- [License](#license)

## Overview

[Asyntai](https://asyntai.com) is an AI chat agent for websites. Point it at a domain and it reads the pages, the product feed and the documents, and keeps them current.

This integration brings that agent into Haystack. Your pipelines ask the website a question and get the answer a visitor would get, built from the real pages and the real prices. Your indexing pipelines can feed the website agent new documents, and a Haystack `Agent` can read the chats visitors had and the leads they left.

You need an Asyntai API key, created under **Settings → API** on the Starter plan or higher. Full documentation: [asyntai.com/documentation/integrations/haystack](https://asyntai.com/documentation/integrations/haystack/).

## Installation

```bash
pip install asyntai-haystack
```

Set the key:

```bash
export ASYNTAI_API_KEY="your-key"
```

## Usage

### Components

This integration introduces five components:

- `AsyntaiGenerator`: answers a prompt from the website's pages, products and knowledge base.
- `AsyntaiChatGenerator`: the same, with `ChatMessage` objects in and out.
- `AsyntaiDocumentWriter`: stores Haystack documents in the website agent's knowledge base.
- `AsyntaiUrlIndexer`: reads web pages into the knowledge base.
- `AsyntaiToolset`: six tools for a Haystack `Agent`: ask the website, add a text, add a page, list the knowledge, read the leads, read a chat.

### Ask a website a question

```python
from haystack_integrations.components.generators.asyntai import AsyntaiGenerator

generator = AsyntaiGenerator()
result = generator.run(prompt="How long does delivery take?")
print(result["replies"][0])
```

### Teach the website agent from your files

```python
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack_integrations.components.writers.asyntai import AsyntaiDocumentWriter

pipeline = Pipeline()
pipeline.add_component("converter", TextFileToDocument())
pipeline.add_component("writer", AsyntaiDocumentWriter())
pipeline.connect("converter.documents", "writer.documents")

pipeline.run({"converter": {"sources": ["faq.txt", "returns.txt"]}})
```

### Give an agent the Asyntai tools

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.tools.asyntai import AsyntaiToolset

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=AsyntaiToolset(),
)
result = agent.run([ChatMessage.from_user("Who asked about delivery this week?")])
print(result["messages"][-1].text)
```

### License

`asyntai-haystack` is distributed under the terms of the [MIT](https://github.com/asyntai/asyntai-haystack/blob/main/LICENSE) license.
