---
layout: integration
name: Lazybird
description: Turn text into natural AI speech in your pipelines and agents with Lazybird text to speech
authors:
    - name: Lazybird
      socials:
        github: lazybirdai
        twitter: lazybirdstudio
pypi: https://pypi.org/project/lazybird-haystack/
repo: https://github.com/lazybirdai/lazybird-haystack
type: Model Provider
report_issue: https://github.com/lazybirdai/lazybird-haystack/issues
logo: /logos/lazybird.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Lazybird](https://www.lazybird.app) is an AI voiceover generator with 500+ voices in 150+ languages and accents, voice cloning and voice design. This integration brings the [Lazybird text to speech API](https://www.lazybird.app/text-to-speech-api) to Haystack.

The `LazybirdTextToSpeech` component turns text or SSML into speech and returns the MP3 as a `ByteStream`, for voiceovers, spoken answers, announcements and anything else that should talk. It works in Haystack 2.12 and later, including Haystack 3, and has an async `run_async` for async pipelines.

## Installation

```bash
pip install lazybird-haystack
```

## Usage

### Components

This integration introduces one component and a helper:

- `LazybirdTextToSpeech`: takes `text` (plain text or SSML) and returns `audio`, a `ByteStream` with the MP3.
- `list_voices`: searches the voices you can use as `voice_id`, your own voices first, then the Lazybird library.

### API key

1. [Sign up for Lazybird](https://www.lazybird.app). The free plan includes 10,000 credits a month, no credit card needed.
2. Open [Studio settings](https://www.lazybird.app/studio/settings) and create an API key.
3. Set it as an environment variable. The component reads it from `LAZYBIRD_API_KEY`.

```bash
export LAZYBIRD_API_KEY="your-api-key"
```

### Text to speech

```python
from lazybird_haystack import LazybirdTextToSpeech

tts = LazybirdTextToSpeech()
result = tts.run(text="Welcome back. Your report is ready.")
result["audio"].to_file("welcome.mp3")
```

Text that starts with `<speak>` is sent as SSML, for pauses and pronunciation:

```python
from lazybird_haystack import LazybirdTextToSpeech

tts = LazybirdTextToSpeech()
result = tts.run(text='<speak>Good morning. <break time="500ms"/> The front door is open.</speak>')
result["audio"].to_file("morning.mp3")
```

### Voices, languages and settings

Any voice can speak other languages and accents. Pick one with `list_voices`, then set the language with `locale`:

```python
from lazybird_haystack import LazybirdTextToSpeech, list_voices

for voice in list_voices("british narrator")[:5]:
    print(voice["id"], voice["displayName"], voice["language"])

tts = LazybirdTextToSpeech(
    voice_id="tgJ2Hes6DauwTg8kFrRPLN",  # Elyssia, the default voice
    locale="es-ES",
    speed=1.1,  # 1 is normal (0.5 to 2)
    settings={"pitch": 1.0, "volume": 1.0},
)
result = tts.run(text="Hola, tu pedido ya está en camino.")
result["audio"].to_file("pedido.mp3")
```

`run` also takes `voice_id` and `settings` to override them per call.

### In a pipeline

`PromptBuilder` fills in a template and `LazybirdTextToSpeech` speaks it:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from lazybird_haystack import LazybirdTextToSpeech

pipeline = Pipeline()
pipeline.add_component("template", PromptBuilder(template="Hi {{ name }}, your order {{ order }} has shipped."))
pipeline.add_component("tts", LazybirdTextToSpeech())
pipeline.connect("template.prompt", "tts.text")

result = pipeline.run({"template": {"name": "Maya", "order": "1042"}})
result["tts"]["audio"].to_file("order.mp3")
```

The component serializes with the pipeline and keeps the API key out of the YAML. To load a saved pipeline in Haystack 3, add the package to the trusted modules: `Pipeline.loads(yaml, allowed_modules=["lazybird_haystack"])`.

### Spoken answers from an LLM

This pipeline answers a question with `OpenAIChatGenerator` (it needs `OPENAI_API_KEY`) and reads the answer aloud:

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.converters import OutputAdapter
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from lazybird_haystack import LazybirdTextToSpeech

template = [ChatMessage.from_user("Answer in two short sentences: {{ question }}")]

pipeline = Pipeline()
pipeline.add_component("prompt", ChatPromptBuilder(template=template, required_variables=["question"]))
pipeline.add_component("llm", OpenAIChatGenerator())
pipeline.add_component("answer", OutputAdapter(template="{{ replies[0].text }}", output_type=str))
pipeline.add_component("tts", LazybirdTextToSpeech())
pipeline.connect("prompt.prompt", "llm.messages")
pipeline.connect("llm.replies", "answer.replies")
pipeline.connect("answer.output", "tts.text")

result = pipeline.run({"prompt": {"question": "Why is the sky blue?"}})
result["tts"]["audio"].to_file("answer.mp3")
```

An invalid API key, missing credits or another failed request raises `LazybirdError` with a message that says what to fix. See the [Lazybird docs](https://www.lazybird.app/docs) and [API reference](https://www.lazybird.app/docs/api-reference) for more.

## License

`lazybird-haystack` is distributed under the terms of the [MIT](https://github.com/lazybirdai/lazybird-haystack/blob/main/LICENSE) license.
