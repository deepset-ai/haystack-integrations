---
layout: integration
name: Gandr
description: Gandr Text-to-Speech component for Haystack.
authors:
    - name: Gandr
      socials:
        github: Gandr-AI
pypi: https://pypi.org/project/gandr-haystack/
repo: https://github.com/Gandr-AI/gandr-haystack
type: Model Provider
report_issue: https://github.com/Gandr-AI/gandr-haystack/issues
logo: /logos/gandr.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Parameters](#parameters)
- [Loading a saved pipeline](#loading-a-saved-pipeline)
- [License](#license)

## Overview

[Gandr](https://gandr.ai) is a text-to-speech API. This integration adds a
`GandrTTS` component that turns text into WAV audio inside a Haystack pipeline,
and optionally writes it to disk.

Six stock voices, output at 8 kHz to 24 kHz, and every render is watermarked.

## Installation

```bash
pip install gandr-haystack
```

## Usage

Set `GANDR_API_KEY` in your environment. Keys start with `gnd_`, and a free key
with 100,000 characters is available at [gandr.ai](https://gandr.ai) without a
card.

```python
from gandr_haystack import GandrTTS

tts = GandrTTS(voice="gandr-mia")
result = tts.run(text="Your appointment is confirmed for Tuesday at two fifteen.",
                 path="out.wav")
result["audio"]   # WAV bytes
```

In a pipeline:

```python
from haystack import Pipeline
from gandr_haystack import GandrTTS

pipe = Pipeline()
pipe.add_component("tts", GandrTTS())
pipe.run({"tts": {"text": "Hello from Haystack."}})
```

## Parameters

| Parameter | Default | Notes |
|---|---|---|
| `api_key` | `Secret.from_env_var("GANDR_API_KEY")` | Keys start with `gnd_` |
| `voice` | `gandr-mia` | Also `gandr-ava`, `gandr-jenny`, `gandr-dane`, `gandr-leo`, `gandr-lewis` |
| `language` | `en` | ISO language code |
| `sample_rate` | `24000` | One of 8000, 16000, 22050, 24000 |
| `url` | `https://tts.gandr.ai/v1/tts/bytes` | Override to pin a region |
| `timeout` | `60.0` | Seconds |

`run()` returns `{"audio": bytes, "path": str | None}`.

The API key is held as a Haystack `Secret` read from the environment, so a
serialized pipeline never carries the token. An HTTP failure raises
`RuntimeError` carrying the API's own status and message, so an authentication
error and a quota error are distinguishable.

## Loading a saved pipeline

Haystack does not deserialize a third-party component unless its module is
allowlisted:

```python
from haystack.core.serialization import allow_deserialization_module

allow_deserialization_module("gandr_haystack.tts")
```

Or set `HAYSTACK_DESERIALIZATION_ALLOWLIST=gandr_haystack.tts`. Saving with
`to_dict()` requires nothing.

## License

MIT.
