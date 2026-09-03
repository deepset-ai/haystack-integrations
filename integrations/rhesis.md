---
layout: integration
name: Rhesis
description: Trace Haystack pipelines and Agents to Rhesis for structured feedback and evaluation.

authors:
    - name: Rhesis AI
      socials:
        github: rhesis-ai
        linkedin: https://www.linkedin.com/company/rhesis-ai/
pypi: https://pypi.org/project/rhesis-haystack
repo: https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/rhesis
type: Monitoring Tool
report_issue: https://github.com/deepset-ai/haystack-core-integrations/issues
logo: /logos/rhesis.png
version: Haystack 2.0
toc: true
---
### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

`rhesis-haystack` exports Haystack pipeline, component and `Agent` spans to
[Rhesis](https://rhesis.ai) over OpenTelemetry.

Rhesis is an open-source platform for structured feedback and evaluation on LLM agents. Domain
experts review agent responses in a UI; the feedback stays attached to the test case and the agent
version that produced it, and recurring feedback becomes tests and metrics that run on every change.
See the [Rhesis documentation](https://docs.rhesis.ai) for the platform itself.

What this integration adds beyond viewing traces is correlation. Spans carry the identifiers of the
test execution and the conversation turn they belong to:

| Attribute | Purpose |
|---|---|
| `rhesis.test.run_id`, `rhesis.test.id`, `rhesis.test.result_id` | joins a trace to the test execution that produced it |
| `rhesis.conversation.id`, `rhesis.conversation.is_turn_root` | groups a multi-turn conversation into a single trace |

So a Haystack pipeline can run under a Rhesis test run and have reviewer feedback land on the exact
span tree that produced the answer.

### Features

- Traces pipelines, components and `Agent` runs, including the Haystack 3.0 agent loop: per-step
  `ai.llm.invoke` spans, per-tool `ai.tool.invoke` spans, and promotion of a tool span to
  `ai.agent.handoff` when a tool runs another `Agent`
- Model name and token counts extracted from generators and embedders
- Conversation-aware tracing for applications that drive Haystack outside a pipeline
- A `SpanHandler` extension point for attaching your own attributes
- Builds its own OpenTelemetry `TracerProvider` and never installs a global one, so it does not
  interfere with an application's existing APM or OTel pipeline

## Installation

```bash
pip install rhesis-haystack
```

Set the following environment variables before running your application:

| Variable | Required | Description |
|---|---|---|
| `RHESIS_API_KEY` | Yes | API key for trace ingestion |
| `HAYSTACK_CONTENT_TRACING_ENABLED` | Yes | Must be `"true"` **before importing Haystack** |
| `RHESIS_BASE_URL` | No | Backend URL (default `http://localhost:8080`) |
| `RHESIS_PROJECT_ID` | No | Project ID (resolved from the API key when omitted) |
| `RHESIS_ENVIRONMENT` | No | Environment label (default `development`) |
| `RHESIS_FRONTEND_URL` | No | Frontend URL used to build `trace_url` deep links |
| `HAYSTACK_RHESIS_ENFORCE_FLUSH` | No | Default `"true"`; exports once per run |

`HAYSTACK_CONTENT_TRACING_ENABLED` has to be set before any `haystack` import, otherwise
input/output content tags are no-ops. Haystack reads the variable once, when `haystack.tracing` is
first imported, so setting it afterwards has no effect.

## Usage

### Components

This integration introduces one component and one tracer:

- `RhesisConnector` — add it to a pipeline without connecting it to anything else. Constructing it
  installs the tracer. It returns `name`, `trace_url` and `trace_id`.
- `RhesisTracer` / `DefaultSpanHandler` — bridges Haystack spans to OpenTelemetry, with a
  `SpanHandler` extension point.

It also exports `RhesisTracing`, a conversation-aware entry point for applications that drive
Haystack from their own loop rather than through a pipeline.

### Trace a pipeline

```python
import os

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.connectors.rhesis import RhesisConnector

pipe = Pipeline()
pipe.add_component("tracer", RhesisConnector("Chat example"))
pipe.add_component("prompt_builder", ChatPromptBuilder())
pipe.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipe.connect("prompt_builder.prompt", "llm.messages")

messages = [
    ChatMessage.from_system("Always respond in German."),
    ChatMessage.from_user("Tell me about {{location}}"),
]

response = pipe.run(
    data={
        "prompt_builder": {
            "template_variables": {"location": "Berlin"},
            "template": messages,
        },
        "tracer": {"invocation_context": {"session_id": "demo-session"}},
    }
)
print(response["llm"]["replies"][0])
print(response["tracer"]["trace_url"])
print(response["tracer"]["trace_id"])
```

### Trace an Agent, without a pipeline

Constructing `RhesisConnector` is what installs the tracer, so a standalone `Agent` needs nothing
else — build the connector and never mention it again. There is no pipeline to carry the
`invocation_context` input socket, so attach session and test metadata with
`rhesis_invocation_context` instead:

```python
from haystack_integrations.components.connectors.rhesis import RhesisConnector
from haystack_integrations.tracing.rhesis import rhesis_invocation_context

RhesisConnector("Agent example")  # installs the tracer; never added to a pipeline

with rhesis_invocation_context({"session_id": "agent-example", "test_run_id": "tr-1"}):
    result = agent.run(messages=[ChatMessage.from_user("What is the weather in Berlin?")])
```

Every span opened inside the block joins that session, and the context is restored on exit.

The same context manager works around a `pipeline.run()` call, and there it does something the input
socket cannot. Both attach the context to the run's root span, which is what conversation grouping
and the `trace_url` need. But the socket supplies its value from *inside* the run, so a component
whose span closed before the connector executed has already been exported without it. Wrapping the
call instead means no span opens without the context.

Keys the mapping knows — `session_id`, `conversation_id`, `test_run_id`, `test_id`,
`test_result_id`, `test_configuration_id` — become first-class Rhesis attributes. Anything else,
`user_id` and `tags` included, travels as `haystack.invocation.<key>`.

### Trace a multi-turn conversation

An application that owns its own loop — a chat REPL, a batch script, a server handling one turn per
request — needs two things a component inside the pipeline cannot give it: tracing switched on
without a pipeline to attach to, and a span wrapping a whole pipeline run so a conversation turn has
a root of its own. Without that root, the pipeline span claims the turn and reports the serialized
pipeline input and output as the conversation text.

```python
import os

os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

from haystack_integrations.tracing.rhesis import RhesisTracing

tracing = RhesisTracing("My Assistant")  # no-op when RHESIS_API_KEY is unset
tracing.start_conversation("conversation-1")

for message in ["I have a headache", "It started three days ago"]:
    with tracing.turn(message) as turn:
        result = pipeline.run(...)
        turn.output = extract_reply(result)  # what the user actually sees

tracing.flush()
```

Every turn after the first joins the first one's trace, so a conversation reads as one trace rather
than one per exchange. Call `start_conversation` again to begin a new one.

Assign `turn.output` yourself: only the application knows which part of a pipeline result is the
reply — it may be a tool result, or a value held in agent state rather than the last assistant
message.

Pass `enabled=False` to build a no-op instance when your own configuration says tracing should be
off, and `turn_span_name=...` to name the turn spans after your application.

### Flush behavior

By default (`HAYSTACK_RHESIS_ENFORCE_FLUSH=true`) the tracer exports once per pipeline run, when the
root span closes, so everything the run produced is on the backend by the time `run()` returns. That
costs one blocking round trip per run.

Set it to `false` to hand exporting to the `BatchSpanProcessor` instead and pay nothing on the
request path. Spans are then batched and sent in the background, and OpenTelemetry's `atexit` hook
flushes what is left when the process exits normally.

Leave it on when the process can be hard-killed (`os._exit`, `SIGKILL`, a container OOM kill), when
a serverless runtime freezes the sandbox after the response is returned, or when you cannot call
`flush()` yourself at shutdown. Otherwise turn it off and flush explicitly:

```python
import os

os.environ["HAYSTACK_RHESIS_ENFORCE_FLUSH"] = "false"

from haystack.tracing import tracer

try:
    ...
finally:
    tracer.actual_tracer.flush()
```

### Add your own attributes

```python
from haystack_integrations.tracing.rhesis import DefaultSpanHandler, RhesisSpan


class CustomSpanHandler(DefaultSpanHandler):
    def handle(self, span: RhesisSpan, component_type: str | None) -> None:
        super().handle(span, component_type)
        # add custom attributes here


connector = RhesisConnector("My app", span_handler=CustomSpanHandler())
```

### Semantic mapping

| Haystack source | Rhesis target |
|---|---|
| `haystack.pipeline.run` | `function.haystack.pipeline.run` |
| `haystack.async_pipeline.run` | `function.haystack.async_pipeline.run` |
| `haystack.agent.run` (root) | `ai.agent.invoke` |
| `*ChatGenerator` / `*Generator` | `ai.llm.invoke`, plus model name and token counts |
| `*Retriever` | `ai.retrieval` |
| `*Embedder` | `ai.embedding.generate` |
| `ToolInvoker` | `ai.tool.invoke` |
| `haystack.component.input` / `output` | `ai.prompt` / `ai.completion` events (content-gated) |
| `haystack.pipeline.input_data` / `output_data` | `rhesis.conversation.input` / `output` (content-gated) |
| `invocation_context.session_id` | `rhesis.conversation.id` |
| Other Haystack tags | `haystack.*` metadata |

[`mapping.py`](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/rhesis/src/haystack_integrations/tracing/rhesis/mapping.py)
holds the full, authoritative mapping.

### Things to know

- **Content tracing gates the Rhesis attributes, not Haystack's tags.** With
  `HAYSTACK_CONTENT_TRACING_ENABLED` off, no `ai.prompt` or `ai.completion` events are recorded and
  nothing is promoted to `rhesis.conversation.input` / `.output`. Haystack still passes pipeline I/O
  as an ordinary span tag, so `haystack.pipeline.input_data` carries the run payload either way.
- **Content leaves the process verbatim.** With the flag on, prompts, tool arguments and retrieved
  documents are sent to Rhesis as written. There is no redaction hook; use a custom `SpanHandler` if
  you need one.
- **Haystack spans go to Rhesis only.** Because the connector owns its provider rather than
  installing a global one, Haystack spans do not appear in your own collector, and spans your
  instrumentation opens do not appear in Rhesis. Nesting still works across the two, since
  parent-child relationships travel in the OpenTelemetry context rather than in the provider.
- **Conversation grouping needs a `session_id`.** Without one a run is traced but not grouped. Turns
  share a trace only when driven through `RhesisTracing`.
- **`ComponentTool` invocations are flattened.** The tool span is recorded; the component it wraps
  gets no span of its own.
- **Construction fails closed on a missing API key.** `RhesisConnector(...)` raises `ValueError`
  when no key resolves, so `Pipeline.from_dict` on a YAML containing it needs credentials present.
- **Truncation is silent.** Conversation attributes are capped at 10 000 characters and content
  events at 8 000; nothing marks a value as truncated.

Runnable examples for all three shapes live in
[`integrations/rhesis/example/`](https://github.com/deepset-ai/haystack-core-integrations/tree/main/integrations/rhesis/example).

## License

`rhesis-haystack` is distributed under the terms of the
[Apache-2.0](https://github.com/deepset-ai/haystack-core-integrations/blob/main/integrations/rhesis/LICENSE.txt)
license.
