---
layout: integration
name: Free Image to Video
description: Generate AI video clips with synchronized sound from text prompts or reference photos inside Haystack pipelines using Free Image to Video
authors:
    - name: Free Image to Video
      socials:
        github: hanshs474
pypi: https://pypi.org/project/freeimagetovideo-haystack/
repo: https://github.com/hanshs474/fitv-haystack
type: Model Provider
report_issue: https://github.com/hanshs474/fitv-haystack/issues
logo: /logos/freeimagetovideo.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)

## Overview

Free image to video AI with no daily cap: start with no sign-up, keep going on a free account. Every video comes with sound and no watermark.

[Free Image to Video](https://freeimagetovideo.ai/) generates 4–15 second AI video clips with synchronized sound from text prompts or public photo URLs using MiniMax H3. The `freeimagetovideo-haystack` package provides a `FreeImageToVideoGenerator` component that integrates text-to-video and image-to-video generation directly into Haystack pipelines.

For API documentation and plan details, see the [Free Image to Video Documentation](https://freeimagetovideo.readthedocs.io/en/latest/) and [Pricing](https://freeimagetovideo.ai/pricing).

## Installation

```bash
pip install freeimagetovideo-haystack
```

Create an API key at [freeimagetovideo.ai/settings/apikeys](https://freeimagetovideo.ai/settings/apikeys) and export it:

```bash
export FREEIMAGETOVIDEO_API_KEY="your-api-key"
```

## Usage

```python
from freeimagetovideo_haystack import FreeImageToVideoGenerator

generator = FreeImageToVideoGenerator(duration=6, resolution="480p", aspect_ratio="16:9")
result = generator.run(
    prompt="a paper lantern drifting over a calm river at dusk",
    image_url="https://example.com/lantern.jpg",
)
print(result["url"])
```
