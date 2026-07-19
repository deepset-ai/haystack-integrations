---
layout: integration
name: Rubric Protocol
description: Post-quantum signed, independently verifiable attestations for every Haystack pipeline run — ML-DSA-65 (FIPS 204) signatures anchored to Hedera Consensus Service
authors:
    - name: Echelon Intelligence Group
      socials:
        github: 0xsims
pypi: https://pypi.org/project/autogen-rubric/
repo: https://github.com/0xsims/autogen-rubric
type: Monitoring Tool
report_issue: https://github.com/0xsims/autogen-rubric/issues
logo: /logos/rubric-protocol.png
version: Haystack 2.0
toc: true
---

### Overview

[Rubric Protocol](https://rubric-protocol.com) produces court-grade evidence of what your AI pipelines did and when. Every attestation is signed with ML-DSA-65 (FIPS 204) post-quantum cryptography and anchored to Hedera Consensus Service — a public, neutral ledger — so anyone can independently verify a pipeline's output years later at [rubric-protocol.com/verify](https://rubric-protocol.com/verify), without trusting your logs or your vendor.

This matters wherever two parties need to agree on what an AI system did: regulatory examinations (EU AI Act Annex IV, SR 26-2, Illinois SB 315), insurance claims, vendor disputes, and internal audit. Unlike mutable application logs, an anchored attestation cannot be silently edited after the fact.

### Installation

```bash
pip install autogen-rubric
```

### Usage

Add the component to any pipeline. It attests each run's replies and passes them through unchanged:

```python
from haystack import Pipeline
from autogen_rubric import RubricClient, RubricHaystackComponent

client = RubricClient(api_key="YOUR_RUBRIC_API_KEY")

pipeline = Pipeline()
# ... add your generator, retriever, etc. ...
pipeline.add_component("rubric", RubricHaystackComponent(
    client,
    agent_id="support-rag",
    pipeline_id="prod-v3",
))
pipeline.connect("llm.replies", "rubric.replies")
```

Or attest ad-hoc from anywhere in your app with the callback form:

```python
from autogen_rubric import RubricClient, rubric_haystack_callback

client = RubricClient(api_key="YOUR_RUBRIC_API_KEY")
attest = rubric_haystack_callback(client, agent_id="support-rag")
attest(result)
```

Each attestation returns an ID resolvable on the public verifier, with its Hedera sequence number and ML-DSA-65 signature — evidence that stands on its own.

### License

MIT
