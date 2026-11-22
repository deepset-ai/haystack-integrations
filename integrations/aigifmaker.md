---
layout: integration
name: AI GIF Maker
description: Generate looping animated GIFs directly from text prompts inside Haystack pipelines using AI GIF Maker
authors:
    - name: AI GIF Maker
      socials:
        github: hanshs474
pypi: https://pypi.org/project/aigifmaker-haystack/
repo: https://github.com/hanshs474/aigifmaker-haystack
type: Model Provider
report_issue: https://github.com/hanshs474/aigifmaker-haystack/issues
logo: /logos/aigifmaker.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

Turn text into animated GIFs with AI GIF Maker. Native GIF generation — no video conversion. Type what you want and download your GIF in about a minute.

[AI GIF Maker](https://aigifmaker.ai/?utm_source=haystack&utm_medium=docs) renders looping GIF animations directly from text prompts without an intermediate video transcoding step. The `aigifmaker-haystack` package provides an `AigifmakerGifGenerator` component that connects prompt builders and LLM chains straight to GIF output inside Haystack 2.0 pipelines.

For API key management and credit packs, see [AI GIF Maker API Keys](https://aigifmaker.ai/settings/apikeys) and [AI GIF Maker Pricing](https://aigifmaker.ai/pricing).

## Installation

```bash
pip install aigifmaker-haystack
```

Create an API key at [aigifmaker.ai/settings/apikeys](https://aigifmaker.ai/settings/apikeys) and export it:

```bash
export AIGIFMAKER_API_KEY="sk-..."
```

## Usage

### Standalone GIF generation

```python
from aigifmaker_haystack import AigifmakerGifGenerator

generator = AigifmakerGifGenerator()
result = generator.run(prompt="a corgi in sunglasses dancing on a beach, looping")
print(result["gifs"])
```

### Prompt-to-GIF pipeline

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from aigifmaker_haystack import AigifmakerGifGenerator

pipe = Pipeline()
pipe.add_component(
    "brief",
    PromptBuilder("Write one short GIF prompt reacting to: {{message}}. Specify what moves and that it loops."),
)
pipe.add_component("llm", OpenAIGenerator())
pipe.add_component("gif", AigifmakerGifGenerator())
pipe.connect("brief", "llm")
```
