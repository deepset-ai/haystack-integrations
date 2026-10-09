---
layout: integration
name: NovaFabric
description: Capture each Haystack pipeline run as a portable Run Capsule you can replay, diff and verify, self-hosted.
authors:
    - name: Mohsen Seyedkazemi Ardebili
      socials:
        github: MSKazemi
        linkedin: https://www.linkedin.com/in/mskazemi/
pypi: https://pypi.org/project/novafabric/
repo: https://github.com/MSKazemi/novafabric
type: Monitoring Tool
report_issue: https://github.com/MSKazemi/novafabric/issues
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[NovaFabric](https://novafabric.ai) is open-source, self-hosted replay and evidence infrastructure for AI agents. Its Haystack adapter wraps a `Pipeline` (or `AsyncPipeline`) so that each run is written as a **Run Capsule**: a directory on your machine with the run's manifest, trace, the model calls capture can see, the environment and a secret-scan record. Afterwards you can:

- replay the run with `nova replay` (five modes; `forensic` reads the capsule and runs nothing, `mocked` re-runs the pipeline against the recorded synchronous OpenAI/Anthropic chat replies while tools run live);
- compare two runs structurally with `nova diff`;
- optionally seal a capsule with your own key and verify it offline with `nova verify`.

The adapter is **experimental**. No account and no telemetry: everything stays on your machine.

## Installation

```bash
pip install novafabric haystack-ai
```

## Usage

```python
from haystack import Pipeline
from novafabric.adapters.haystack import wrap_pipeline

pipe = Pipeline()
# ... add components and connections ...
pipe = wrap_pipeline(pipe, run_name="rag-qa")  # patches run() in place
result = pipe.run({"retriever": {"query": "What is a run capsule?"}})
```

Each run writes a capsule under `.novafabric/runs/<run-id>/` in the working directory. From a shell:

```bash
nova validate .novafabric/runs/<run-id>                    # check the capsule against its schema
nova replay .novafabric/runs/<run-id> --mode forensic      # read-only report of the recorded run
nova diff .novafabric/runs/<run-a> .novafabric/runs/<run-b> # what changed between two runs
```

Docs: [getting started](https://novafabric.ai/docs/getting-started/) · [replay modes](https://novafabric.ai/docs/architecture/replay-modes/) · [what is a Run Capsule](https://novafabric.ai/docs/architecture/run-capsule/)

## License

Apache-2.0
