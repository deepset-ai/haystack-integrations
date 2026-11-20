---
layout: integration
name: SAEF
description: Estimate the carbon, energy and water of LLM calls in a Haystack pipeline from token usage, by model class and cloud region
authors:
    - name: Guillermo Llopis
      socials:
        github: guillermollopis
        linkedin: https://www.linkedin.com/in/guillermollopis
pypi: https://pypi.org/project/saef/
repo: https://github.com/guillermollopis/soma-ai-emission-factors
report_issue: https://github.com/guillermollopis/soma-ai-emission-factors/issues
type: Monitoring Tool
toc: true
version: Haystack 2.0
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`saef` estimates the carbon (kg CO2e), energy (kWh) and water (litres) behind LLM API calls from their token usage. It applies open per-token emission factors by model class and cloud region (SAEF, CC BY 4.0, [doi 10.5281/zenodo.24160409](https://doi.org/10.5281/zenodo.24160409)), with a low and high case for each estimate. Cached input tokens are credited separately from fresh input and output. The method is published in Sustainable Production and Consumption 70 (2026) 320-347, [doi 10.1016/j.spc.2026.11.003](https://doi.org/10.1016/j.spc.2026.11.003).

`SaefTracker` is a pass-through component. Place it after a Generator or ChatGenerator. It reads the model and token usage from each reply's `meta`, returns the replies unchanged plus a `saef` list with one estimate per reply, and keeps running totals for the pipeline.

All figures are estimates from token counts, not measurements. Providers do not publish energy per request.

## Installation

```bash
pip install "saef[haystack]"
```

## Usage

```python
from haystack import Pipeline
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from saef.integrations.haystack import SaefTracker

pipe = Pipeline()
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o"))
pipe.add_component("saef", SaefTracker(region="eu-west-1"))
pipe.connect("llm.replies", "saef.replies")

result = pipe.run({"llm": {"messages": [ChatMessage.from_user("Summarise the GHG Protocol in one line")]}})
print(result["saef"]["saef"][0]["kg_co2e"])

totals = pipe.get_component("saef").totals()
print(totals["calls"], totals["kg_co2e"], totals["kg_co2e_high_case"])
```

For a text Generator such as `OpenAIGenerator`, also connect its `meta` output: `pipe.connect("llm.meta", "saef.meta")`.

`region` takes a cloud region id such as `us-east-1`, `eu-west-1` or `europe-west1`, or `global-average` (the default, also settable with the `SAEF_REGION` environment variable). `log_path` writes one JSON line per call.

## License

`saef` is MIT licensed. The SAEF emission factor dataset is CC BY 4.0.
