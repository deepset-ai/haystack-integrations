---
layout: integration
name: Vaultak
description: Runtime security monitoring for Haystack pipelines — risk-score inputs, enforce policies, and mask PII before responses reach your users
authors:
    - name: Vaultak
      socials:
        github: samueloladji-beep
        twitter: VaultakAI
        linkedin: https://www.linkedin.com/company/vaultak/
pypi: https://pypi.org/project/haystack-vaultak/
repo: https://github.com/samueloladji-beep/haystack-vaultak
type: Monitoring Tool
report_issue: https://github.com/samueloladji-beep/haystack-vaultak/issues
version: Haystack 2.0
toc: true
---

### **Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
    - [VaultakSecurityChecker](#vaultaksecuritychecker)
    - [VaultakPIIMasker](#vaultakpiimasker)
    - [Full RAG pipeline example](#full-rag-pipeline-example)
- [License](#license)

## Overview

[Vaultak](https://vaultak.com) is a runtime security platform for AI pipelines. It intercepts
inputs and outputs in real time — scoring risk on a 0–10 scale, enforcing policy rules, and masking
PII — so that dangerous or sensitive content never reaches your LLM or your users.

This integration ships two Haystack components that can be dropped into any pipeline:

| Component | Position in pipeline | What it does |
|---|---|---|
| `VaultakSecurityChecker` | Before the LLM / retriever | Risk-scores the input; raises `RuntimeError` if above threshold; checks against policy rules |
| `VaultakPIIMasker` | After the LLM | Scans LLM replies for PII (names, emails, phone numbers, etc.) and masks them before they reach your users |

## Installation

```bash
pip install haystack-vaultak
```

Sign up at [vaultak.com](https://vaultak.com) to get your API key.

## Usage

### VaultakSecurityChecker

Insert `VaultakSecurityChecker` before your retriever or LLM to intercept and score every user
query before it enters your pipeline. Queries whose risk score exceeds your threshold raise a
`RuntimeError` so the pipeline halts cleanly.

```python
from haystack_vaultak import VaultakSecurityChecker

checker = VaultakSecurityChecker(
    api_key="YOUR_VAULTAK_API_KEY",
    threshold=7.0,
    verbose=True,
)

pipeline.add_component("security", checker)
pipeline.connect("security.query", "retriever.query")
```

### VaultakPIIMasker

Insert `VaultakPIIMasker` after your LLM generator to scan and redact PII from every reply
before it reaches your users.

```python
from haystack_vaultak import VaultakPIIMasker

masker = VaultakPIIMasker(api_key="YOUR_VAULTAK_API_KEY")

pipeline.add_component("pii_masker", masker)
pipeline.connect("llm.replies", "pii_masker.replies")
```

### Full RAG pipeline example

The example below adds both components to a standard RAG pipeline. `VaultakSecurityChecker`
gates every incoming query; `VaultakPIIMasker` cleans every outgoing reply.

```python
import os
from haystack import Pipeline, Document
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack_vaultak import VaultakSecurityChecker, VaultakPIIMasker

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
VAULTAK_API_KEY = "YOUR_VAULTAK_API_KEY"

# --- Build the document store ---
document_store = InMemoryDocumentStore()
document_store.write_documents([
    Document(content="Acme Corp Q3 revenue was $4.2M with 312 active customers."),
    Document(content="Support contact: support@acme.com, phone 555-867-5309."),
])

prompt_template = """
Answer the question using the provided documents only.
Documents:
{% for doc in documents %}
    {{ doc.content }}
{% endfor %}
Question: {{ query }}
Answer:
"""

# --- Assemble the pipeline with Vaultak components ---
pipeline = Pipeline()
pipeline.add_component("security_checker", VaultakSecurityChecker(api_key=VAULTAK_API_KEY))
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=document_store))
pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
pipeline.add_component("llm", OpenAIGenerator())
pipeline.add_component("pii_masker", VaultakPIIMasker(api_key=VAULTAK_API_KEY))

pipeline.connect("security_checker.query", "retriever.query")
pipeline.connect("security_checker.query", "prompt_builder.query")
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm.prompt")
pipeline.connect("llm.replies", "pii_masker.replies")

# --- Run ---
result = pipeline.run({"security_checker": {"query": "What is the support email?"}})
print(result["pii_masker"]["replies"])
# Email addresses and phone numbers are masked in the output
```

Every scored query and masked reply is visible in your [Vaultak dashboard](https://app.vaultak.com).

## License

`haystack-vaultak` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
