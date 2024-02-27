---
layout: integration
name: Titan Takeoff Inference Server
description: Use Titan Takeoff to run local open-source LLMs with Haystack. Titan Takeoff allows you to run the latest models from Meta, Mistral and Alphabet directly in your laptop.
authors:
    - name: Fergus Finn
      socials:
        github: fergusbarratt
        twitter: BarrattFergus
        linkedin: https://www.linkedin.com/in/fergusfinn/
    - name: Rod Rivera
      socials:
        github: rorcde
        twitter: rorcde
        linkedin: https://www.linkedin.com/in/aiengineer/
pypi: https://pypi.org/project/your-project
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/titanml-takeoff
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/titanml.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview
You can use the Takeoff inference server to deploy local models efficiently in your Haystack 2.0 pipelines. Takeoff is a state-of-the art inference server focused on deploying openly available language models at scale. It can run LLMs on local machines with consumer GPUs, and on cloud infrastructure. 

The TakeoffGenerator component in Haystack 2.0 is a wrapper around the Takeoff server API, and can be used to serve takeoff-deployed models efficiently in Haystack pipelines.

## Installation

```bash
pip install takeoff_haystack
```

## Usage
You can interact with takeoff deployed models using the `TakeoffGenerator` component in Haystack. To do so, you must have a takeoff model deployed. For information on how to do so, please read the takeoff docs [here](https://docs.titanml.co/docs/Docs/launching/).

The following example deploys a Llama-2-7B-Chat-AWQ model using takeoff locally on port 3000.

```bash
docker run --gpus all -e TAKEOFF_MODEL_NAME=TheBloke/Llama-2-7B-Chat-AWQ \
                      -e TAKEOFF_DEVICE=cuda \
                      -e TAKEOFF_MAX_SEQUENCE_LENGTH=256 \
                      -it \
                      -p 3000:3000 tytn/takeoff-pro:0.11.0-gpu
```

## TextGeneration

Below is an example of using takeoff models in a Haystack RAG pipeline. It summarizes headlines from popular news sites in technology.

```bash
from typing import Dict, List
from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder  
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
import feedparser
from takeoff_haystack import TakeoffGenerator

# Dict of website RSS feeds  
urls = {
  'theverge': 'https://www.theverge.com/rss/frontpage/',
  'techcrunch': 'https://techcrunch.com/feed',
  'mashable': 'https://mashable.com/feeds/rss/all',
  'cnet': 'https://cnet.com/rss/news',
  'engadget': 'https://engadget.com/rss.xml',
  'zdnet': 'https://zdnet.com/news/rss.xml',
  'venturebeat': 'https://feeds.feedburner.com/venturebeat/SZYF',
  'readwrite': 'https://readwrite.com/feed/',    
  'wired': 'https://wired.com/feed/rss',
  'gizmodo': 'https://gizmodo.com/rss',
}

# Configurable parameters
NUM_WEBSITES = 3  
NUM_TITLES = 1

def get_titles(urls: Dict[str, str], num_sites: int, num_titles: int) -> List[str]:
  titles: List[str] = []
  sites = list(urls.keys())[:num_sites]
  
  for site in sites:
    feed = feedparser.parse(urls[site])  
    entries = feed.entries[:num_titles]
    
    for entry in entries:
      titles.append(entry.title)
      
  return titles
  
titles = get_titles(urls, NUM_WEBSITES, NUM_TITLES)

document_store = InMemoryDocumentStore()
document_store.write_documents([Document(content=title) for title in titles])

template = """
HEADLINES:  
{% for document in documents %}
  {{ document.content }}  
{% endfor %}
REQUEST: {{ query }}
"""

pipe = Pipeline()
pipe.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", TakeoffGenerator(base_url="http://localhost", port="3000"))
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query = f"Summarize each of the {NUM_WEBSITES * NUM_TITLES} provided headlines in three words."
response = pipe.run({"prompt_builder": {"query": query}, "retriever": {"query": query}})
print(response["llm"]["replies"])
```

You should see a response like the following
```
['\n\n\nANSWER:\n\n1. Poker Roguelike - Exciting gameplay\n2. AI-powered news reader - Personalized feed\n3. Best laptops MWC 2024 - Powerful devices']
```

### License

Info about your integration license
