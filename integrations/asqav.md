---
layout: integration
name: Asqav
description: Signed audit trails for Haystack pipelines - tamper-evident governance records for every pipeline run
authors:
  - name: Jag Marques
    socials:
      github: jagmarques
      linkedin: https://www.linkedin.com/in/jagmarques
pypi: https://pypi.org/project/asqav/
repo: https://github.com/jagmarques/asqav-sdk
type: Monitoring Tool
report_issue: https://github.com/jagmarques/asqav-sdk/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

Asqav is an AI governance SDK that provides cryptographically signed audit trails for AI agent actions. The Haystack integration adds an `AsqavComponent` that you drop into any pipeline to sign data flowing through it with ML-DSA-65 post-quantum signatures.

Key features:
- Tamper-evident, cryptographically signed records for every pipeline run
- Fail-open design - signing failures are logged but never break your pipeline
- Works as a native Haystack component with typed inputs and outputs

## Installation

```bash
pip install asqav[haystack]
```

## Usage

### Adding AsqavComponent to a Pipeline

`AsqavComponent` is a standard Haystack component. Add it to your pipeline like any other component. It accepts a `data` string and optional `metadata` dict, signs the action through asqav, and passes everything through with a `signature_id` attached.

```python
import asqav
from asqav.extras.haystack import AsqavComponent
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder

# Initialize asqav with your API key
asqav.init("sk_live_...")

# Build a standard Haystack pipeline
prompt_template = "Answer the following question: {{question}}"
pipe = Pipeline()
pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
pipe.add_component("llm", OpenAIGenerator())
pipe.add_component("asqav", AsqavComponent(agent_name="my-rag-pipeline"))
pipe.connect("prompt_builder", "llm")
```

### Running and Inspecting Signatures

Each call to the `AsqavComponent` returns the original data, metadata, and a `signature_id` that links to the signed audit record.

```python
result = pipe.run(
    {
        "prompt_builder": {"question": "What is Haystack?"},
        "asqav": {"data": "What is Haystack?", "metadata": {"source": "user"}},
    }
)

# The asqav component output includes the signature reference
print(result["asqav"]["signature_id"])  # e.g. "sig_a1b2c3"
print(result["asqav"]["data"])          # original data passed through
print(result["asqav"]["metadata"])      # original metadata passed through
```

### Using an Existing Agent

If you already have an agent registered in asqav, pass its ID instead of creating a new one:

```python
governance = AsqavComponent(agent_id="agt_x7y8z9")
pipe.add_component("asqav", governance)
```

### License

`asqav` is licensed under MIT. See the [GitHub repository](https://github.com/jagmarques/asqav-sdk) for details.
