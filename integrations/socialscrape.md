---
layout: integration
name: SocialScrape
description: Social media transcripts, profiles, posts, comments and search results as Haystack Documents and agent tools.
authors:
  - name: SocialScrape
    socials:
      github: SocialScraper
pypi: https://pypi.org/project/socialscrape-haystack
repo: https://github.com/SocialScraper/socialscrape-haystack
type: Data Ingestion
report_issue: https://github.com/SocialScraper/socialscrape-haystack/issues
logo: /logos/socialscrape.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[SocialScrape](https://socialscrape.dev) is a social media data API: profiles, posts, comments, search results, ad libraries and video transcripts from 29 platforms, including YouTube, TikTok, Instagram, X, Facebook, LinkedIn and Reddit. Every platform answers in the same JSON shape, with one API key.

The `socialscrape-haystack` integration turns that data into Haystack `Document`s for indexing and RAG pipelines, and gives a Haystack `Agent` tools to look things up on its own. It is built on the official SocialScrape Python SDK, so retries, timeouts and long transcription jobs are handled for you. Full documentation is at [socialscrape.dev/docs/haystack](https://socialscrape.dev/docs/haystack).

Create an API key in the [SocialScrape dashboard](https://socialscrape.dev/app). A new account starts with free credits, and a request that fails costs nothing.

## Installation

```bash
pip install socialscrape-haystack
```

Python 3.11 or newer and Haystack 2.14 or newer. Set your API key in the `SOCIALSCRAPE_API_KEY` environment variable:

```bash
export SOCIALSCRAPE_API_KEY="ss_live_..."
```

## Usage

### Components

This integration introduces three components:

- The `SocialScrapeTranscriptFetcher`: takes a list of video URLs (YouTube, TikTok, Instagram and other video links) and returns one `Document` per URL with the transcript as its content, and the title, platform, language and duration in `meta` where the API returns them. A URL that fails is reported in the `errors` output and does not fail the batch.
- The `SocialScrapeFetcher`: runs any SocialScrape endpoint by id with its parameters and returns `Document`s, one per item for list endpoints (a profile's posts, a video's comments, a search) and one otherwise.
- The `SocialScrapeToolset`: a Haystack `Toolset` for `Agent`, with eight tools: profile, posts, one post, comments, transcript, search, endpoint lookup and call-any-endpoint.

The API key is a Haystack `Secret`, read from `SOCIALSCRAPE_API_KEY` by default, and all of them serialize with `to_dict` and `from_dict` without storing the key.

### Index video transcripts

This pipeline fetches transcripts, splits them and writes them to an in-memory document store.

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

from socialscrape_haystack import SocialScrapeTranscriptFetcher

store = InMemoryDocumentStore()

pipeline = Pipeline()
pipeline.add_component("fetcher", SocialScrapeTranscriptFetcher())
pipeline.add_component("splitter", DocumentSplitter(split_by="word", split_length=300, split_overlap=30))
pipeline.add_component("writer", DocumentWriter(document_store=store))
pipeline.connect("fetcher.documents", "splitter.documents")
pipeline.connect("splitter.documents", "writer.documents")

result = pipeline.run({"fetcher": {"urls": [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.tiktok.com/@nasa/video/7665075736742530317",
]}})

print(store.count_documents(), "chunks stored")
print(result["fetcher"]["errors"])  # URLs that could not be fetched, if any
```

To search the chunks, add a `SentenceTransformersDocumentEmbedder` between the splitter and the writer and query the store with a retriever, as in any Haystack indexing pipeline.

### Summarize videos with a prompt builder

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from socialscrape_haystack import SocialScrapeTranscriptFetcher

template = [ChatMessage.from_user(
    "Summarize the main points of each video.\n"
    "{% for doc in documents %}\n[{{ doc.meta.url }}]\n{{ doc.content }}\n{% endfor %}"
)]

pipeline = Pipeline()
pipeline.add_component("fetcher", SocialScrapeTranscriptFetcher())
pipeline.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["documents"]))
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipeline.connect("fetcher.documents", "prompt.documents")
pipeline.connect("prompt.prompt", "llm.messages")

result = pipeline.run({"fetcher": {"urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]}})
print(result["llm"]["replies"][0].text)
```

### Load comments, posts or profiles from any endpoint

```python
from socialscrape_haystack import SocialScrapeFetcher

fetcher = SocialScrapeFetcher(max_pages=3)

comments = fetcher.run(
    endpoint="youtube.video.comments",
    params={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
)["documents"]
print(len(comments), comments[0].content, comments[0].meta)

profile = fetcher.run(endpoint="tiktok.profile", params={"handle": "nasa"})["documents"][0]
print(profile.content, profile.meta)
```

### Give an Agent social media tools

```python
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from socialscrape_haystack import SocialScrapeToolset

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=SocialScrapeToolset(),
    system_prompt="You answer questions about social media accounts and videos. Use the tools, do not guess.",
)

result = agent.run(messages=[ChatMessage.from_user(
    "How many followers does @nasa have on TikTok, and what is their latest video about?"
)])
print(result["last_message"].text)
```

### License

`socialscrape-haystack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
