---
layout: integration
name: FunASR
description: Transcribe audio files to Documents using FunASR — an open-source, self-hosted speech recognition toolkit supporting 50+ languages.
authors:
    - name: deepset
      socials:
        github: deepset-ai
        twitter: Haystack_AI
        linkedin: https://www.linkedin.com/company/deepset-ai/
pypi: https://pypi.org/project/funasr-haystack/
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/funasr
type: Model Provider
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
version: Haystack 2.0
toc: true
---

[![PyPI - Version](https://img.shields.io/pypi/v/funasr-haystack.svg)](https://pypi.org/project/funasr-haystack/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/funasr-haystack.svg)](https://pypi.org/project/funasr-haystack/)
[![test](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/funasr.yml/badge.svg)](https://github.com/deepset-ai/haystack-core-integrations/actions/workflows/funasr.yml)

---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [FunASRTranscriber](#funasrtranscriber)
- [License](#license)

## Overview

[FunASR](https://github.com/modelscope/FunASR) is an open-source speech recognition toolkit from Alibaba DAMO Academy that runs entirely locally — no API key required. It supports 50+ languages, speaker diarization, and timestamp extraction.

This integration provides:

- [`FunASRTranscriber`](https://docs.haystack.deepset.ai/docs/funasrtranscriber): Transcribes audio files to Haystack `Document` objects. Accepts file paths, `Path` objects, and `ByteStream` inputs.

## Installation

```bash
pip install funasr-haystack
```

## Usage

### FunASRTranscriber

`FunASRTranscriber` transcribes audio files to Haystack `Document` objects using FunASR models. Models are downloaded from ModelScope on first use and cached in `~/.cache/modelscope`.

#### Basic Example

```python
from haystack_integrations.components.audio.funasr import FunASRTranscriber

transcriber = FunASRTranscriber()

result = transcriber.run(sources=["speech.wav", "interview.mp3"])
for doc in result["documents"]:
    print(doc.content)
```

#### In a Pipeline

```python
from haystack import Pipeline
from haystack.components.fetchers import LinkContentFetcher
from haystack_integrations.components.audio.funasr import FunASRTranscriber

pipe = Pipeline()
pipe.add_component("fetcher", LinkContentFetcher())
pipe.add_component("transcriber", FunASRTranscriber())

pipe.connect("fetcher", "transcriber")

result = pipe.run(
    data={
        "fetcher": {
            "urls": ["https://example.com/speech.wav"],
        },
    }
)
print(result["transcriber"]["documents"][0].content)
```

#### Speaker Diarization

```python
from haystack.utils import ComponentDevice
from haystack_integrations.components.audio.funasr import FunASRTranscriber

transcriber = FunASRTranscriber(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
    spk_model="cam++",
    device=ComponentDevice.from_str("cuda"),
)

result = transcriber.run(sources=["meeting.wav"])
doc = result["documents"][0]
print(doc.content)
print("Speakers:", doc.meta.get("speakers"))
```

## License

`funasr-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.
