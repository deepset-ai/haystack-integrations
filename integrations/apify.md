---
layout: integration
name: Apify
description: Extract data from the web and automate web tasks using Apify-Haystack integration.
authors:
  - name: apify
    socials:
      github: apify
      twitter: apify
      linkedin: apifytech
pypi: https://pypi.org/project/apify-haystack
repo: https://github.com/apify/apify-haystack
type: Data Ingestion
report_issue:  https://github.com/apify/apify-haystack/issues
logo: /logos/apify.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
    - [ApifyDatasetFromActorCall on its own](#apifydatasetfromactorcall-on-its-own)
    - [ApifyDatasetFromActorCall in a RAG pipeline](#apifydatasetfromactorcall-in-a-rag-pipeline)
- [License](#license)

## Overview

[Apify](https://apify.com) is a web scraping and data extraction platform. 
It helps automate web tasks and extract content from e-commerce websites, social media (Facebook, Instagram, TikTok), search engines, online maps, and more. 
Apify provides more than two thousand ready-made cloud solutions called Actors.

## Installation

Install the Apify-haystack integration:
```bash
pip install apify-haystack
```

## Usage

Once installed, you will have access to more than two thousand ready-made apps called Actors at [Apify Store](https://apify.com/store)

- Load a dataset from Apify and convert it to a Haystack Document
- Extract data from Facebook/Instagram and save it in the InMemoryDocumentStore
- Crawl websites, scrape text content, and store it in the InMemoryDocumentStore
- Retrieval-Augmented Generation (RAG): Extracting text from a website & question answering

The integration implements the following components (you can find their usage in these [examples](https://github.com/apify/apify-haystack/tree/main/src/apify_haystack/examples)):
- `ApifyDatasetLoader`: Load a dataset created by an Apify Actor
- `ApifyDatasetFromActorCall`: Call an Apify Actor, load the dataset, and convert it to Haystack Documents
- `ApifyDatasetFromTaskCall`: Call an Apify task, load the dataset, and convert it to Haystack Documents

You need to have an Apify account and an Apify API token to run this example.
You can start with a free account at [Apify](https://apify.com/) and get your [Apify API token](https://docs.apify.com/platform/integrations/api#api-token).

In the examples below, specify `apify_api_token` and run the script.


### ApifyDatasetFromActorCall on its own


Use Apify's [Website Content Crawler](https://apify.com/apify/website-content-crawler) to crawl a website, scrape text content, and convert it to Haystack Documents. You can browse other Actors in [Apify Store](https://apify.com/store)

In the example below, the text content is extracted from https://haystack.deepset.ai/. 
You can control the number of crawled pages using `maxCrawlPages` parameter. For a detailed overview of the parameters, please refer to [Website Content Crawler](https://apify.com/apify/website-content-crawler/input-schema).

The script should produce the following output (truncated to a single Document):
```text
Document(id=a617d376*****, content: 'Introduction to Haystack 2.x)
Haystack is an open-source framework fo...', meta: {'url': 'https://docs.haystack.deepset.ai/docs/intro'}
```

```python
from dotenv import load_dotenv
import os
from haystack import Document

from apify_haystack import ApifyDatasetFromActorCall

# Use APIFY_API_TOKEN from .env file or set it
load_dotenv()
os.environ["APIFY_API_TOKEN"] = "YOUR APIFY_API_TOKEN"

actor_id = "apify/website-content-crawler"
run_input = {
    "maxCrawlPages": 3,  # limit the number of pages to crawl
    "startUrls": [{"url": "https://haystack.deepset.ai/"}],
}


def dataset_mapping_function(dataset_item: dict) -> Document:
    """Convert an Apify dataset item to a Haystack Document
    
   Website Content Crawler returns a dataset with the following output fields:
    {
        "url": "https://haystack.deepset.ai",
        "text": "Haystack is an open-source framework for building production-ready LLM applications",
    }
    """
    return Document(content=dataset_item.get("text"), meta={"url": dataset_item.get("url")})


actor = ApifyDatasetFromActorCall(
    actor_id=actor_id,
    run_input=run_input,
    dataset_mapping_function=dataset_mapping_function
)
print(f"Calling the Apify Actor {actor_id} ... crawling will take some time ...")
print("You can monitor the progress at: https://console.apify.com/actors/runs")

dataset = actor.run().get("documents")

print(f"Loaded {len(dataset)} documents from the Apify Actor {actor_id}:")
for d in dataset:
    print(d)
```

### ApifyDatasetFromActorCall in a RAG pipeline

> Follow 🧑‍🍳 [Cookbook: Extract and use website content for question answering with Apify-Haystack integration](https://github.com/deepset-ai/haystack-cookbook/blob/main/notebooks/apify_haystack_rag.ipynb) for the full runnable example.

*Retrieval-Augmented Generation (RAG):* Extracting text content from a website and using it for question answering.
Answer questions about the https://haystack.deepset.ai website using the extracted text content.

Expected output:
```text
question: "What is haystack?"
answer: Haystack is an open-source framework for building production-ready LLM applications
``````

In addition to the `APIFY_API_TOKEN`, you also need to specify `OPENAI_API_KEY` to run this example.

```python

import os

from dotenv import load_dotenv
from haystack import Document, Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.utils.auth import Secret

from apify_haystack import ApifyDatasetFromActorCall

# Set APIFY_API_TOKEN and OPENAI_API_KEY here or use it from .env file
load_dotenv()
os.environ["APIFY_API_TOKEN"] = getpass("Enter YOUR APIFY_API_TOKEN")
os.environ["OPENAI_API_KEY"] = getpass("Enter YOUR OPENAI_API_KEY")

actor_id = "apify/website-content-crawler"
run_input = {
    "maxCrawlPages": 1,  # limit the number of pages to crawl
    "startUrls": [{"url": "https://haystack.deepset.ai/"}],
}


def dataset_mapping_function(dataset_item: dict) -> Document:
    """Convert an Apify dataset item to a Haystack Document
    
   Website Content Crawler returns a dataset with the following output fields:
    {
        "url": "https://haystack.deepset.ai",
        "text": "Haystack is an open-source framework for building production-ready LLM applications",
    }
    """
    return Document(content=dataset_item.get("text"), meta={"url": dataset_item.get("url")})


apify_dataset_loader = ApifyDatasetFromActorCall(
    actor_id=actor_id,
    run_input=run_input,
    dataset_mapping_function=dataset_mapping_function
)

# Components
print("Initializing components...")
document_store = InMemoryDocumentStore()

docs_embedder = OpenAIDocumentEmbedder()
text_embedder = OpenAITextEmbedder()
retriever = InMemoryEmbeddingRetriever(document_store)
generator = OpenAIGenerator(model="gpt-3.5-turbo")

# Load documents from Apify
print("Crawling and indexing documents...")
print("You can visit https://console.apify.com/actors/runs to monitor the progress")
docs = apify_dataset_loader.run()
embeddings = docs_embedder.run(docs.get("documents"))
document_store.write_documents(embeddings["documents"])

template = """
Given the following information, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""

prompt_builder = PromptBuilder(template=template)

# Add components to your pipeline
print("Initializing pipeline...")
pipe = Pipeline()
pipe.add_component("embedder", text_embedder)
pipe.add_component("retriever", retriever)
pipe.add_component("prompt_builder", prompt_builder)
pipe.add_component("llm", generator)

# Now, connect the components to each other
pipe.connect("embedder.embedding", "retriever.query_embedding")
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

question = "What is haystack?"

print("Running pipeline ... ")
response = pipe.run({"embedder": {"text": question}, "prompt_builder": {"question": question}})

print(f"question: {question}")
print(f"answer: {response['llm']['replies'][0]}")

# Other questions
examples = [
    "Who created Haystack?",
    "Are there any upcoming events or community talks?",
]

for example in examples:
    response = pipe.run({"embedder": {"text": example}, "prompt_builder": {"question": example}})
    print(f"question: {question}")
    print(f"answer: {response['llm']['replies'][0]}")
```


### License
`apify-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
