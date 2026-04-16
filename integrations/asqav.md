---
layout: integration
name: Asqav
description: Signed audit trails for Haystack pipelines - tamper-evident governance records for every pipeline run
authors:
  - name: João Marques
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

AI agents running in production need more than observability. When a pipeline makes a decision, calls a tool, or generates output, you need tamper-evident proof of what happened, not just a log entry someone could edit later. This matters for regulatory compliance (EU AI Act Article 12 requires automatic, verifiable event recording for high-risk systems), incident investigation (reconstructing exactly what an agent did and why), and accountability across teams that share pipelines.

Asqav provides cryptographic governance for AI agent actions. Every action gets signed server-side with ML-DSA-65 (NIST FIPS 204), hash-chained to the previous action, and stored as a verifiable receipt the agent can't forge. The signing key never touches the agent's runtime.

The Haystack integration adds `AsqavComponent`, a native Haystack component that signs data flowing through your pipeline. Drop it in, and every run produces a signed, tamper-evident audit record.

- Tamper-evident records for every pipeline run, signed with quantum-safe cryptography
- Fail-open design: signing failures are logged but never break your pipeline
- Native Haystack component with typed inputs and outputs
- Compliance bundle export for EU AI Act, DORA, and SOC 2 audits
- Public verification endpoint: anyone can verify a signature without an API key

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
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.builders import ChatPromptBuilder

# Initialize asqav with your API key
asqav.init("sk_live_...")

# Build a standard Haystack pipeline
prompt_template = "Answer the following question: {{question}}"
pipe = Pipeline()
pipe.add_component("prompt_builder", ChatPromptBuilder(template=prompt_template))
pipe.add_component("llm", OpenAIChatGenerator())
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
