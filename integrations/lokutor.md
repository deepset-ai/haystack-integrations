---
layout: integration
name: Lokutor
description: Text-to-speech and speech-to-text components for Haystack, powered by Lokutor's own speech models
authors:
    - name: Lokutor AI
      socials:
        github: lokutor-ai
repo: https://github.com/lokutor-ai/lokutor-haystack
type: Model Provider
report_issue: https://github.com/lokutor-ai/lokutor-haystack/issues
logo: /logos/lokutor.svg
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Text to speech](#text-to-speech)
  - [Speech to text](#speech-to-text)
  - [In a pipeline](#in-a-pipeline)
- [License](#license)

## Overview

[Lokutor](https://lokutor.com) runs its own speech models: Versa 2.0 for text to speech and Conv 2.0 for speech to text, in nine languages (English, Spanish, Catalan, Galician, Basque, Portuguese, French, Italian and German).

This integration adds two components:

- `LokutorTextToSpeech`: turns text into a WAV `ByteStream`. Ten stock voices (`F1`-`F5`, `M1`-`M5`) plus your cloned voices; expression tags such as `[laugh]` or `[happy]` in the text are performed by the voice.
- `LokutorSpeechToText`: turns WAV files (paths or `ByteStream`s) into `Document`s, with optional speaker diarization and per-word timings.

Get an API key at [app.lokutor.com](https://app.lokutor.com). API documentation: [docs.lokutor.com](https://docs.lokutor.com).

## Installation

```bash
pip install git+https://github.com/lokutor-ai/lokutor-haystack.git
```

Set your key in the `LOKUTOR_API_KEY` environment variable. The components take it as a Haystack `Secret`, so it is never written into a serialized pipeline.

## Usage

### Text to speech

```python
from pathlib import Path

from haystack_integrations.components.audio.lokutor import LokutorTextToSpeech

tts = LokutorTextToSpeech(voice="F1", language="en")
audio = tts.run(text="Hello from Lokutor.")["audio"]  # ByteStream, mime_type "audio/wav"
audio.to_file(Path("hello.wav"))
```

The audio is 16-bit PCM, 44.1 kHz, mono WAV, up to 5,000 characters per call. `voice` and `language` can also be passed to `run`, and `run_async` is available.

### Speech to text

```python
from haystack_integrations.components.audio.lokutor import LokutorSpeechToText

stt = LokutorSpeechToText(language="en", diarize=True)
docs = stt.run(sources=["meeting.wav"])["documents"]
print(docs[0].content, docs[0].meta["speakers"])
```

Lokutor decodes WAV only (PCM 8 or 16 bit, 8-48 kHz): convert MP3 or M4A files first. Set `language=None` to detect the language.

### In a pipeline

Transcribe recordings and index them for retrieval:

```python
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore

from haystack_integrations.components.audio.lokutor import LokutorSpeechToText

store = InMemoryDocumentStore()
indexing = Pipeline()
indexing.add_component("stt", LokutorSpeechToText(language="en"))
indexing.add_component("writer", DocumentWriter(document_store=store))
indexing.connect("stt.documents", "writer.documents")
indexing.run({"stt": {"sources": ["call.wav"]}})
```

### License

`lokutor-haystack` is distributed under the terms of the [Apache-2.0](https://github.com/lokutor-ai/lokutor-haystack/blob/main/LICENSE) license.
