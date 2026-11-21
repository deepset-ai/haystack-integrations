---
layout: integration
name: Movoa
description: Generate AI video clips with synchronized sound from text or reference photos inside Haystack pipelines using Movoa
authors:
    - name: Movoa
      socials:
        github: hanshs474
pypi: https://pypi.org/project/movoa-haystack/
repo: https://github.com/hanshs474/movoa-haystack
type: Model Provider
report_issue: https://github.com/hanshs474/movoa-haystack/issues
logo: /logos/movoa.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

Unlimited AI video generator with sound: on paid plans the tenth take of a shot costs what the first did, and your first clip is free to make right now.

[Movoa](https://movoa.ai/) generates video clips with synchronized speech, sound effects, and background music from text prompts or reference frames. The `movoa-haystack` package provides a `MovoaVideoGenerator` component that integrates text-to-video and photo-to-video generation directly into Haystack pipelines.

For API documentation and pricing details, see the [Movoa Developer Docs](https://movoa.readthedocs.io/en/latest/) and [Movoa Pricing](https://movoa.ai/pricing).

## Installation

```bash
pip install movoa-haystack
```

Create an API key at [movoa.ai/settings/apikeys](https://movoa.ai/settings/apikeys) and export it:

```bash
export MOVOA_API_KEY="your-api-key"
```

## Usage

### Text to video

```python
from movoa_haystack import MovoaVideoGenerator

generator = MovoaVideoGenerator(duration=6, aspect_ratio="16:9")
result = generator.run(prompt="a paper boat drifting down a rain gutter, low angle")
print(result["videos"])
```

### Photo to video

```python
from movoa_haystack import MovoaVideoGenerator

generator = MovoaVideoGenerator(duration=6, aspect_ratio="16:9")
result = generator.run(
    prompt="the camera slowly orbits the statue while soft light sweeps across it",
    image_url="https://example.com/statue.jpg",
)
print(result["videos"])
```
