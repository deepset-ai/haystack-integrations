---
layout: integration
name: Kavel
description: Generate and edit images in Haystack pipelines with Kavel AI, with no API key needed to start
authors:
    - name: Kavel
      socials:
        github: hanshs474
pypi: https://pypi.org/project/kavel-haystack
repo: https://github.com/hanshs474/kavel-haystack
type: Custom Component
report_issue: https://github.com/hanshs474/kavel-haystack/issues
logo: /logos/kavel.png
version: Haystack 2.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Kavel](https://www.kavel.ai/?utm_source=haystack&utm_medium=integration) is an online AI image and video studio. The `KavelImageGenerator` component turns a prompt into an image, or edits an existing image, and returns a permanent URL to the result.

Without an API key the component runs on Kavel's free anonymous tier, so a pipeline works on a machine with nothing configured. Free output is 1K and watermarked, with a small daily allowance per machine. With a key from [kavel.ai/settings/apikeys](https://www.kavel.ai/settings/apikeys?utm_source=haystack&utm_medium=integration) it runs on your account, can edit images, and can use any image model on your plan.

## Installation

```bash
pip install kavel-haystack
```

## Usage

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from kavel_haystack import KavelImageGenerator

pipe = Pipeline()
pipe.add_component("prompt", PromptBuilder(template="A cover image for an article about {{topic}}, editorial photo, soft light"))
pipe.add_component("image", KavelImageGenerator(aspect_ratio="16:9"))
pipe.connect("prompt.prompt", "image.prompt")

result = pipe.run({"prompt": {"topic": "sourdough baking"}})
print(result["image"]["images"][0])
```

To run on your account, set the `KAVEL_API_KEY` environment variable or pass `api_key=Secret.from_token("...")`. Pass `image_url=` to `run()` to edit an existing image (requires an API key).

## License

`kavel-haystack` is distributed under the terms of the [MIT](https://github.com/hanshs474/kavel-haystack/blob/main/LICENSE) license.
