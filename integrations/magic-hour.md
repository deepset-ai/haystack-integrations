---
layout: integration
name: Magic Hour
description: Generate images, recover accepted jobs, and download outputs in Haystack pipelines.
authors:
  - name: Magic Hour
    socials:
      github: magichourhq
repo: https://github.com/magichourhq/magic-hour-haystack
report_issue: https://github.com/magichourhq/magic-hour-haystack/issues
type: Custom Component
version: Haystack 3.4
toc: true
---

## Overview

Magic Hour provides three native Haystack components for one recoverable image workflow:

- `MagicHourImageGenerator`: submit one Z-Image Turbo generation and return its accepted project ID and charged credits.
- `MagicHourImageWaiter`: poll that existing image project through completion without submitting another generation.
- `MagicHourImageDownloader`: return completed images as Haystack `ByteStream` objects.

The initial integration creates one square image at up to 640 pixels. It does not require an LLM provider. Generation consumes Magic Hour credits.

## Installation

Requires Python 3.11+ and Haystack 3.4. Install from the versioned source repository:

```bash
python -m pip install "git+https://github.com/magichourhq/magic-hour-haystack.git@8fe6474d48da71b5ef9d32b5c2c05ad8ed453ad5"
```

Create a Magic Hour API key in the [Developer Hub](https://magichour.ai/developer) and provide it through your secret manager as `MAGIC_HOUR_API_KEY`. Keys use Haystack's environment-backed `Secret`; serialized pipelines contain the variable name, not its value.

## Usage

Persist the accepted ID before polling so a stopped workflow can resume without another paid submission:

```python
import json
from pathlib import Path

from haystack import Pipeline
from magic_hour_haystack import (
    MagicHourImageGenerator,
    MagicHourImageWaiter,
    MagicHourImageDownloader,
)

receipt_path = Path("magic-hour-project.json")
if receipt_path.exists():
    receipt = json.loads(receipt_path.read_text())
else:
    create = Pipeline()
    create.add_component("generate", MagicHourImageGenerator())
    receipt = create.run({
        "generate": {"prompt": "An orange paper bird on a plain blue background"}
    })["generate"]
    with receipt_path.open("x") as file:
        json.dump(receipt, file)

recover = Pipeline()
recover.add_component("wait", MagicHourImageWaiter())
recover.add_component("download", MagicHourImageDownloader())
recover.connect("wait.project", "download.project")
result = recover.run({"wait": {"project_id": receipt["project_id"]}})
image_bytes = result["download"]["images"][0].data
```

The repository's [runnable example](https://github.com/magichourhq/magic-hour-haystack/blob/8fe6474d48da71b5ef9d32b5c2c05ad8ed453ad5/examples/image_pipeline.py) saves downloaded images and safe receipts with sizes and hashes. Its `--submit-only` option stops after ID persistence; rerunning without the flag resumes the same project.

If submission loses its response, the API may already have accepted it. Inspect the Developer Hub before creating another job. A polling timeout does not cancel the accepted job. Keep its ID and resume. Temporary media URLs are refreshed through another project lookup.

Authenticated API requests use the fixed Magic Hour HTTPS origin. Downloads never receive the API key, accept the observed Magic Hour media host only, and reject redirects. Prompts and generated content are processed by Magic Hour; see the [privacy policy](https://magichour.ai/privacy-policy). Haystack telemetry can be disabled with `HAYSTACK_TELEMETRY_ENABLED=false`.

## License

MIT. This integration is maintained by Magic Hour, independently of deepset.

