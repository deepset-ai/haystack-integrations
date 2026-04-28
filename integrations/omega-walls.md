---
layout: integration
name: Omega Walls
description: Runtime trust boundary for Haystack RAG and agent pipelines that ingest untrusted content.
authors:
  - name: Synqra Tech
    socials:
      github: synqratech
pypi: https://pypi.org/project/omega-walls/
repo: https://github.com/synqratech/omega-walls
type: Custom Component
report_issue: https://github.com/synqratech/omega-walls/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [When to use it](#when-to-use-it)
- [License](#license)

## Overview

[Omega Walls](https://github.com/synqratech/omega-walls) is an open-source runtime trust boundary for RAG and AI agent pipelines.

It is designed for Haystack applications that ingest external or semi-trusted content such as documents, PDFs, web pages, support tickets, knowledge base articles, or tool outputs.

In LLM-powered workflows, retrieved content is usually meant to be data. However, once it enters the model context, it can start behaving like instructions. This can make RAG and agent pipelines less predictable when they move from clean demo data to real-world inputs.

Omega Walls adds a boundary between:

- untrusted content
- model context
- memory
- tools and actions

The Haystack adapter provides a guard layer that can wrap a Haystack pipeline and tool calls before execution.

## Installation

Install Omega Walls with framework integrations:

```bash
pip install "omega-walls[integrations]"
````

## Usage

### Components

This integration introduces the `OmegaHaystackGuard`, which can be used to wrap a Haystack pipeline and guard tool calls.

* `OmegaHaystackGuard.wrap_pipeline(...)`: wraps a Haystack pipeline with an Omega guard component.
* `OmegaHaystackGuard.wrap_tool(...)`: wraps tool functions so tool calls can be checked before execution.

### Use Omega Walls with a Haystack pipeline

```python
from omega.integrations import OmegaHaystackGuard

guard = OmegaHaystackGuard(profile="quickstart")

pipeline = guard.wrap_pipeline(
    pipeline,
    component_name="omega_guard_component",
)

safe_tool = guard.wrap_tool("network_post", network_post_fn)
```

### What it checks

Omega Walls is designed to check:

* model/input flow
* tool calls before execution
* memory-write candidates
* cross-document or cross-step prompt-injection pressure
* secret-exfiltration pressure
* tool/action abuse

When a risky input or tool call is detected, the guard can block the step with typed exceptions instead of letting the pipeline continue blindly.

## When to use it

Omega Walls is useful for Haystack users building RAG or agentic workflows over real-world content, especially when the pipeline reads from:

* external documents
* PDFs
* web pages
* support tickets
* user-provided files
* internal knowledge bases
* tool outputs

Typical use cases include:

* internal document assistants
* support-ticket summarizers
* agentic RAG workflows
* pipelines with tool calls
* pipelines that read untrusted or user-provided documents

The goal is to keep retrieved content as data, rather than letting it silently become part of the agent’s control flow.

## License

Omega Walls is distributed under the terms of the [Apache-2.0 license](https://github.com/synqratech/omega-walls/blob/main/LICENSE).
