---
layout: integration
name: OrcaReplay
description: Record a Haystack run at the model-provider boundary and replay it offline, with no provider call and no tokens spent.

authors:
    - name: Continuum AI
      socials:
        github: Continuum-AI-Corp
repo: https://github.com/Continuum-AI-Corp/OrcaReplay
type: Monitoring Tool
report_issue: https://github.com/Continuum-AI-Corp/OrcaReplay/issues
logo: /logos/orcareplay.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Limits](#limits)
- [License](#license)

## Overview

[OrcaReplay](https://github.com/Continuum-AI-Corp/OrcaReplay) records a Haystack run from **outside the process** — at the HTTP boundary between your pipeline and its model provider — and can serve that recording back so the same run happens again with **no provider contacted and no API key needed**.

Nothing is installed into your pipeline. `orca record` launches your script as a child process with the provider origin redirected for that process only, so the code that runs is the code you wrote rather than an instrumented variant of it. There is no tracer to register and no component to add.

### Features

- **A run becomes a file.** A colleague, or a maintainer on an issue, can re-run the pipeline session that misbehaved without your key and without spending tokens.
- **Free regression tests.** Replay needs no network and costs nothing, so a recorded run can guard `ChatPromptBuilder` templates, component wiring or generator parameters on every commit — the part of testing an LLM pipeline that is otherwise awkward, because real calls cost money and do not answer the same way twice.
- **Byte-exact comparison.** A replayed request that differs from the recording is reported as a divergence with its size, rather than normalized until it passes.
- **Evidence instead of recall.** The trace holds the verbatim requests and responses, every tool call with its arguments, shell exit codes, and the files the run changed.

### Why it needs no configuration

`OpenAIChatGenerator` takes `api_base_url` defaulting to `None` and passes it straight through as the client's `base_url`. When that is `None`, the OpenAI SDK falls back to `OPENAI_BASE_URL` from the environment — which is exactly the variable `orca record` sets for the child process it launches, and only for that process. Your shell and your other pipelines are untouched.

## Installation

```bash
npm install -g orcareplay
```

Node 20+ is required. The installed command is `orca`. Nothing is installed into your Python environment.

## Usage

An ordinary pipeline, unchanged:

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat.openai import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

pipe = Pipeline()
pipe.add_component("prompt", ChatPromptBuilder(
    template=[ChatMessage.from_user("{{question}}")], required_variables=["question"]))
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipe.connect("prompt.prompt", "llm.messages")
pipe.run({"prompt": {"question": "Say hello in three words."}})
```

Record it:

```bash
orca record generic-openai -- python pipeline.py
```

```text
info recorded run=run_5381c38c5274 events=6 exit=0
```

Then replay it, with no provider reachable:

```bash
orca replay last
```

```text
info replaying exchanges=1 egress=blocked
info replay.done reused=1/1 exact=1 divergences=0 unmatched=0 exit=0
```

`exact=1` means the replayed request matched the recording **byte for byte** — prompt rendering, message assembly and parameters all reproduced. Your components, your connections and your own code run for real; only the model's answer comes from the trace.

To read a run rather than re-run it:

```bash
orca show last      # the timeline: model turns, tool calls, exit codes, files changed
orca graph last     # which event caused which
```

**Embeddings replay too.** An earlier draft of this page said they did not — that `/v1/embeddings` was passed through to the live provider and absent from the recording. That was wrong, and the check written to confirm it disproved it instead. The ordinary RAG shape — `OpenAIDocumentEmbedder` to build the store, `OpenAITextEmbedder` on the query, `InMemoryEmbeddingRetriever`, then the generator — records and replays completely offline:

```text
info replay.done reused=1/1 exact=1 divergences=0 unmatched=0 retrieval=2/2 exit=0
```

`retrieval=2/2` is the part that matters, and it is reported separately for a reason: embeddings are not model exchanges, so `exact=1` says nothing about them. A replay that served the chat turn and refused both embedding calls would print the same `exact=1`. Both embedder components reach the proxy exactly as the generator does, because both leave `api_base_url` to the OpenAI client.

Verified against `haystack-ai` 3.1.1 on Python 3.12, for both a standalone `OpenAIChatGenerator` and the full `Pipeline` above, using a deterministic local origin standing in for a provider so that "byte for byte" is a real comparison rather than a model happening to repeat itself.

One version note: `OpenAIGenerator` (the non-chat one) no longer exists in 3.1.x — `haystack.components.generators.chat.openai.OpenAIChatGenerator` is the path that does.

## Limits

Stated up front rather than discovered later.

- **`egress=blocked` means model-provider egress, not network isolation.** Replay serves the model's answers from the trace and calls no provider, but the rest of the pipeline still runs for real — a retriever still hits your document store, a custom component still makes its own calls. It is not a sandbox; run it inside one if that matters.
- **A matching replay is not a determinism result.** The model is not being re-asked — its recorded answers are served back. Whether a *fresh* run would behave the same way is a different question that replay cannot answer.
- **A trace is a full transcript.** It holds whatever the run held, including anything pasted into a prompt. Scrubbing is best-effort — it matches known key shapes and high-entropy strings, and cannot know that a particular hostname or customer name is confidential — so review a trace before sharing it.

## License

Apache-2.0.
