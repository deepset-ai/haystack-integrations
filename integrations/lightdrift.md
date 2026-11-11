---
layout: integration
name: Lightdrift Image Review
description: Build a bounded stock-image candidate review queue in a Haystack pipeline while preserving provenance and rights metadata.
authors:
    - name: Lightdrift
repo: https://github.com/JacksonHolland/lightdrift-claude-plugin/tree/main/examples/haystack-image-review
report_issue: https://github.com/JacksonHolland/lightdrift-claude-plugin/issues
type: Custom Component
version: Haystack 3.2.0
toc: true
---

## Overview

`LightdriftImageReview` turns a visual brief into a bounded queue for human review. It preserves the query ID, asset IDs, complete rights objects, source and provenance, and the original response envelope. It does not download images or approve candidates. This community-maintained example is tested with Haystack 3.2.0 on Python 3.13; other versions are not claimed.

## Installation

Clone the published example in an isolated environment:

```bash
git clone https://github.com/JacksonHolland/lightdrift-claude-plugin.git
cd lightdrift-claude-plugin
git checkout fc056d6c7317bb1ad8c6b557e7ad44c0acd64821
cd examples/haystack-image-review
python -m venv .venv
. .venv/bin/activate
python -m pip install .
export HAYSTACK_TELEMETRY_ENABLED=false
python -m unittest discover -s tests -v
python demo.py
```

The default demo runs a real Haystack Pipeline using synthetic fixtures. It makes no API calls, needs no API key, and is not a retrieval-quality benchmark. No PyPI package is claimed.

## Explicit backend use

Live use requires a Lightdrift account, available search credit and a backend `LIGHTDRIFT_API_KEY` environment variable. Review [pricing](https://lightdrift.ai/#pricing) and account usage first. Do not put the key in browser code or pipeline inputs.

```python
from haystack import Pipeline
from lightdrift_haystack import LightdriftImageReview

pipeline = Pipeline()
pipeline.add_component("images", LightdriftImageReview(live=True))
result = pipeline.run({"images": {
    "visual_brief": "A quiet coastal walking trail with open sky",
    "candidate_count": 5,
}})["images"]
for candidate in result["review_queue"]:
    print(candidate["asset_id"], candidate["provenance_url"], candidate["review_state"])
```

Each live invocation makes one search request, accepts 1–20 candidates, refuses redirects and does not automatically retry. Live authentication, relevance and billing were not tested in the offline test suite. An HTTP timeout can follow a billed request; inspect usage before retrying.

## Review and maintenance

Outputs include `review_queue`, `query_id`, `response` and `status`. Missing rights or provenance produce warnings, not permission. Empty and degraded responses remain explicit. Keep the full response and inspect source/license requirements before choosing an image; the component does not grant publishing rights.

See the [workflow guide](https://docs.lightdrift.ai/guides/haystack-image-review), [source and tests](https://github.com/JacksonHolland/lightdrift-claude-plugin/tree/main/examples/haystack-image-review), and [issue tracker](https://github.com/JacksonHolland/lightdrift-claude-plugin/issues). Content & Distribution maintains this example. No endorsement by deepset is implied.
