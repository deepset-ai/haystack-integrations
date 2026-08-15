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

## Overview

[Rubric Protocol](https://rubric-protocol.com) produces independently verifiable evidence of what your AI pipelines did and when. Every attestation is signed with ML-DSA-65 (FIPS 204) post-quantum cryptography and anchored to Hedera Consensus Service — a public, neutral ledger — so anyone can verify a pipeline's output years later at [rubric-protocol.com/verify](https://rubric-protocol.com/verify), without trusting your logs or your vendor.

This matters wherever two parties need to agree on what an AI system did: regulatory examinations (EU AI Act Annex IV, SR 26-2, Illinois SB 315), insurance claims, vendor disputes, and internal audit. Unlike mutable application logs, an anchored attestation cannot be silently edited after the fact.

## Installation

```bash
pip install autogen-rubric
```

The package instruments several agent frameworks, Haystack among them — the name predates the others.

## Usage

Add the component to any pipeline. It attests each run's replies and passes them through unchanged:

```python
import os
from haystack import Pipeline
from autogen_rubric import RubricClient, RubricHaystackComponent

client = RubricClient(
    api_key=os.environ["RUBRIC_API_KEY"],
    background_queue=True,          # keeps attestation off the pipeline's critical path
)

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
import os
from autogen_rubric import RubricClient, rubric_haystack_callback

client = RubricClient(api_key=os.environ["RUBRIC_API_KEY"], background_queue=True)
attest = rubric_haystack_callback(client, agent_id="support-rag")

result = pipeline.run({"prompt_builder": {"query": query}})
attest(result)
```

The callback accepts the dict returned by `Pipeline.run()`, and also a
`PipelineSnapshot` or `PipelineState` if you use
[pipeline breakpoints](https://docs.haystack.deepset.ai/docs/pipeline-breakpoints).
If it cannot resolve the pipeline outputs it logs at ERROR and writes **no**
attestation rather than anchoring an empty one - check your logs for
`[RubricHaystack] no attestation written` if a run you expected is missing from
the verifier.

Requires `autogen-rubric >= 1.10.3`. Earlier versions resolved outputs only from
an object exposing `.pipeline_outputs` directly, so passing the `Pipeline.run()`
dict silently attested an empty payload.


Each attestation returns an ID resolvable on the public verifier, with its Hedera sequence number and ML-DSA-65 signature — evidence that stands on its own.

## Latency and failure behaviour

`background_queue=True` hands each attestation to a background sender, so your pipeline is never waiting on network I/O. It is **off by default**: a client constructed as `RubricClient(api_key=...)` submits synchronously inside the component's `run()`, and will block that pipeline run for up to `timeout` seconds (default 15) if the API is slow to respond. Set it explicitly in production.

Attestation never breaks a pipeline. Any failure — network, authentication, or API error — is caught, logged at `WARNING`, and the replies are returned unchanged. The corollary is worth stating plainly for an audit tool: when attestation fails the pipeline still succeeds, and the evidence for that run is simply absent. Pass `on_dead_letter=` to be notified which attestations were dropped, rather than discovering the gap when someone asks for the record.

Attestations marked `risk="high"` are always sent synchronously, queue or not, so a high-risk decision is not lost to an abrupt process exit.

## What is attested

The component attests the **first** reply of each run, truncated to 2000 characters, and records the total reply count in metadata. Pipelines that return several replies, or replies longer than 2000 characters, are therefore attested in part rather than in full — worth knowing before relying on an attestation as a complete record of a run.

The reply text is transmitted to the Rubric API over HTTPS; it is not reduced to a hash on the client. Treat the attested output as leaving your network.

## Verifying an attestation

Verification needs neither this package, nor an account, nor Rubric's cooperation — which is the point:

```bash
npx @rubric-protocol/verify <attestationId>
```

The attestation can equally be checked directly against its Hedera Consensus Service record by sequence number, or looked up at [rubric-protocol.com/verify](https://rubric-protocol.com/verify).

## License

MIT
