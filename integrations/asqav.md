---
layout: integration
name: Asqav
description: Governance and audit trails for Haystack pipelines - policy enforcement, compliance logging, and signed execution records
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

## Overview

Asqav is an AI governance library that provides audit trails, policy enforcement, and compliance logging for AI pipelines. It records signed execution logs for every pipeline run, making it possible to answer who ran what, when, and with what inputs and outputs.

Key features:
- Tamper-evident audit logs for every pipeline run
- Policy rules that can block or flag non-compliant outputs before they are returned
- Structured compliance reports exportable to JSON or CSV
- No external service required - works fully offline or with your own storage backend

## Installation

```bash
pip install asqav
```

## Usage

### Wrapping a Pipeline

Wrap any Haystack `Pipeline` with `AsqavPipeline` to automatically log every run. The wrapper is a drop-in replacement - it accepts the same `.run()` call and returns the same output.

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
import asqav

# Build a standard Haystack pipeline
prompt_template = "Answer the following question: {{question}}"
pipeline = Pipeline()
pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
pipeline.add_component("llm", OpenAIGenerator())
pipeline.connect("prompt_builder", "llm")

# Wrap it with Asqav governance
governed = asqav.wrap(pipeline, pipeline_id="my-rag-pipeline")

# Run as normal - execution is automatically logged
result = governed.run({"prompt_builder": {"question": "What is Haystack?"}})
print(result["llm"]["replies"])
```

### Viewing Audit Logs

Asqav writes structured audit records for each run. You can retrieve them programmatically or export them for compliance review.

```python
import asqav

# List recent runs for a pipeline
logs = asqav.get_logs(pipeline_id="my-rag-pipeline", limit=10)
for entry in logs:
    print(entry["run_id"], entry["timestamp"], entry["status"])

# Export to JSON
asqav.export_logs(pipeline_id="my-rag-pipeline", format="json", path="audit.json")
```

### Enforcing Policies

Define policies as Python callables. Asqav evaluates them after each run and can raise an error or emit a warning depending on the enforcement mode.

```python
import asqav

def no_pii_in_output(inputs, outputs):
    # Return True to allow, False to flag/block
    for reply in outputs.get("llm", {}).get("replies", []):
        if "@" in reply:
            return False
    return True

governed = asqav.wrap(
    pipeline,
    pipeline_id="my-rag-pipeline",
    policies=[no_pii_in_output],
    enforcement="block",  # or "warn"
)
```

For full documentation and configuration options, see [asqav.com/docs](https://asqav.com/docs).
