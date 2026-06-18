---
layout: integration
name: Whisper
description: Transcribe audio files with OpenAI's Whisper, locally or via the OpenAI API
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: deepset_ai
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/whisper-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations
type: Custom Component
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

The `whisper-haystack` integration provides two components that transcribe audio files into Haystack documents using OpenAI's [Whisper](https://github.com/openai/whisper) model:

- [`LocalWhisperTranscriber`](https://docs.haystack.deepset.ai/docs/localwhispertranscriber): runs Whisper on your own machine. The audio is never sent to a third party.
- [`RemoteWhisperTranscriber`](https://docs.haystack.deepset.ai/docs/remotewhispertranscriber): transcribes audio with the OpenAI Whisper API (and other OpenAI-compatible providers).

Both components are typically used as the first step of an indexing pipeline. They were previously part of Haystack core and now live in the `whisper-haystack` integration package, maintained in [haystack-core-integrations](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/whisper).

## Installation

```bash
pip install whisper-haystack
```

This is all you need for `RemoteWhisperTranscriber`, which uses the OpenAI Whisper API (set the `OPENAI_API_KEY` environment variable).

To use `LocalWhisperTranscriber`, also install the optional `openai-whisper` dependency and make sure [`ffmpeg`](https://ffmpeg.org/) is available on your system:

```bash
pip install -U openai-whisper
```

## Usage

### RemoteWhisperTranscriber

`RemoteWhisperTranscriber` transcribes audio with the OpenAI Whisper API. Set your `OPENAI_API_KEY` and pass the audio sources to transcribe:

```python
import os
from haystack_integrations.components.audio.whisper import RemoteWhisperTranscriber

os.environ["OPENAI_API_KEY"] = "your-api-key"

transcriber = RemoteWhisperTranscriber()
result = transcriber.run(sources=["path/to/audio/file.mp3"])

print(result["documents"][0].content)
```

### LocalWhisperTranscriber

`LocalWhisperTranscriber` runs the Whisper model on your machine. Choose a model size (for example `tiny`, `base`, or `small`) and transcribe your audio files:

```python
from haystack_integrations.components.audio.whisper import LocalWhisperTranscriber

transcriber = LocalWhisperTranscriber(model="small")
transcriber.warm_up()
result = transcriber.run(sources=["path/to/audio/file.mp3"])

print(result["documents"][0].content)
```

### In a pipeline

The pipeline below fetches an audio file from a URL with `LinkContentFetcher` and transcribes it with `LocalWhisperTranscriber`:

```python
from haystack import Pipeline
from haystack.components.fetchers import LinkContentFetcher
from haystack_integrations.components.audio.whisper import LocalWhisperTranscriber

pipe = Pipeline()
pipe.add_component("fetcher", LinkContentFetcher())
pipe.add_component("transcriber", LocalWhisperTranscriber(model="tiny"))
pipe.connect("fetcher", "transcriber")

result = pipe.run(
    data={
        "fetcher": {
            "urls": [
                "https://github.com/deepset-ai/haystack/raw/refs/heads/main/test/test_files/audio/MLK_Something_happening.mp3"
            ]
        }
    }
)
print(result["transcriber"]["documents"][0].content)
```

## License

`whisper-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
