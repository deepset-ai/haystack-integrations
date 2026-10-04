---
layout: integration
name: GetYouTubeTranscript
description: Fetch YouTube video transcripts, optionally with timestamps, as Haystack Documents
authors:
    - name: GetYouTubeTranscript
      socials:
        github: tubeagentkit
pypi: https://pypi.org/project/getyoutubetranscript-haystack
repo: https://github.com/tubeagentkit/getyoutubetranscript-haystack
type: Data Ingestion
report_issue: https://github.com/tubeagentkit/getyoutubetranscript-haystack/issues
logo: /logos/getyoutubetranscript.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[GetYouTubeTranscript](https://getyoutubetranscript.com) is an API for YouTube video transcripts. This integration provides the `GetYouTubeTranscriptFetcher` component, which takes YouTube video URLs or IDs and returns one Haystack `Document` per video, with the title, channel and language in `meta`.

Transcripts are fetched by the API on its own servers, so the component works from cloud servers and serverless functions, where direct requests to YouTube are often blocked.

You need a GetYouTubeTranscript API key, which you can create at [getyoutubetranscript.com/dashboard](https://getyoutubetranscript.com/dashboard). By default the component reads it from the `GETYOUTUBETRANSCRIPT_API_KEY` environment variable.

## Installation

```bash
pip install getyoutubetranscript-haystack
```

## Usage

### Components

This integration introduces one component:

- `GetYouTubeTranscriptFetcher`: fetches transcripts for a list of videos and outputs `documents`. Parameters: `api_key` (a `Secret`, defaults to the `GETYOUTUBETRANSCRIPT_API_KEY` env var), `language` (caption language code), `timestamps` (when `True`, `content` is one `[m:ss] text` line per caption and `meta["segments"]` holds `{start, duration, text}` per line), and `raise_on_failure` (when `False`, videos without captions are logged and skipped).

### Fetch transcripts

```python
from haystack_integrations.components.fetchers.getyoutubetranscript import GetYouTubeTranscriptFetcher

fetcher = GetYouTubeTranscriptFetcher()
documents = fetcher.run(videos=["https://youtu.be/jNQXAC9IVRw"])["documents"]

print(documents[0].meta["title"])
print(documents[0].content)
```

### Index transcripts in a pipeline

```python
from haystack import Pipeline
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_integrations.components.fetchers.getyoutubetranscript import GetYouTubeTranscriptFetcher

store = InMemoryDocumentStore()
indexing = Pipeline()
indexing.add_component("fetcher", GetYouTubeTranscriptFetcher())
indexing.add_component("splitter", DocumentSplitter(split_by="word", split_length=200))
indexing.add_component("writer", DocumentWriter(document_store=store))
indexing.connect("fetcher.documents", "splitter.documents")
indexing.connect("splitter.documents", "writer.documents")

indexing.run({"fetcher": {"videos": ["https://youtu.be/5e37ZT3SQbk"]}})
print(store.count_documents())
```

### Use it as an agent tool

```python
from haystack.tools import ComponentTool
from haystack_integrations.components.fetchers.getyoutubetranscript import GetYouTubeTranscriptFetcher

youtube_tool = ComponentTool(
    component=GetYouTubeTranscriptFetcher(timestamps=True),
    name="youtube_transcript",
    description="Get the transcripts of YouTube videos from their URLs or IDs.",
)
```

### License

`getyoutubetranscript-haystack` is distributed under the terms of the [MIT](https://github.com/tubeagentkit/getyoutubetranscript-haystack/blob/main/LICENSE) license.
