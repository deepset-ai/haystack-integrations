---
layout: integration
name: Court Rules
description: Retrieve U.S. court filing rules, local rules and judge standing orders as Documents, or give an Agent tools to look them up
authors:
    - name: Court Rules
      socials:
        github: foklepoint
repo: https://github.com/foklepoint/court-rules-haystack
type: Tool Integration
report_issue: https://github.com/foklepoint/court-rules-haystack/issues
logo: /logos/court-rules.png
version: Haystack 3.0
toc: true
---

### Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Retriever](#retriever)
  - [RAG pipeline](#rag-pipeline)
  - [Filing-prep agent](#filing-prep-agent)
- [License](#license)

## Overview

[Court Rules](https://www.courtrules.app/) is a free reference for U.S. federal and state court rules, local rules and
judge standing orders. What a filing needs depends on the court and on the judge: page and word limits, courtesy
copies, pre-motion letters, e-filing and service rules differ from one courtroom to the next. The Court Rules
[REST API](https://docs.courtrules.app) returns these rules as structured data, each with a plain-English summary, a
citation and the official source URL.

`court-rules-haystack` connects that API to Haystack:

- **`CourtRulesRetriever`** searches the rules and returns them as `Document`s. The metadata carries the court
  (`district_id`), the judge (`judge_slug`), the rule type (`logic_type`), the citation and the source URL.
- **`CourtRulesToolset`** gives an `Agent` five read-only tools: `list_courts`, `list_judges`, `get_judge_rules`,
  `search_filing_rules` and `list_court_holidays`. Results are shortened before they reach the model.

Both components support asynchronous execution and `to_dict` / `from_dict` serialization. The API key is read through
Haystack's `Secret` from the `COURT_RULES_API_KEY` environment variable.

Use it for filing-prep assistants, paralegal question answering and checklists that must name the rule and the source
they rely on. The rules are reference material for research. They do not replace reading the court's own documents or
legal advice.

## Installation

The package is not on PyPI yet. Install it from GitHub, pinned to a release tag:

```bash
pip install "court-rules-haystack @ git+https://github.com/foklepoint/court-rules-haystack@v0.1.0"
```

It needs Python 3.10 or newer and `haystack-ai` 3.0 or newer. Get a free API key at
[console.courtrules.app](https://console.courtrules.app) (sign in with Google or email) and set it:

```bash
export COURT_RULES_API_KEY="crm_prod_..."
```

## Usage

### Retriever

`query` is a keyword search: every word must appear in the rule, so use one to three specific words. Narrow the search
with `district_id` (the court), `judge_slug` or `logic_type`. Results are ordered newest first.

```python
from haystack_integrations.components.retrievers.court_rules import CourtRulesRetriever

retriever = CourtRulesRetriever(district_id="edny", top_k=3)
result = retriever.run(query="courtesy copy")

for document in result["documents"]:
    print(document.meta["judge_slug"], document.meta["source_url"])
    print(document.content)
```

### RAG pipeline

The retriever takes the keywords and the prompt takes the question. The model answers from the retrieved rules and
names the source:

```python
from haystack import Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

from haystack_integrations.components.retrievers.court_rules import CourtRulesRetriever

template = [
    ChatMessage.from_system(
        "You answer questions about court filing rules. Use only the rules below. "
        "Say which rule you rely on and give its source URL. If the rules do not answer the question, say so."
    ),
    ChatMessage.from_user(
        "Rules:\n"
        "{% for doc in documents %}"
        "[{{ loop.index }}] {{ doc.content }}\nSource: {{ doc.meta.source_url }}\n\n"
        "{% endfor %}"
        "Question: {{ question }}"
    ),
]

pipeline = Pipeline()
pipeline.add_component("retriever", CourtRulesRetriever(district_id="edny", top_k=5))
pipeline.add_component("prompt_builder", ChatPromptBuilder(template=template))
pipeline.add_component("llm", OpenAIChatGenerator(model="gpt-4o-mini"))
pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm.messages")

question = "Do I have to deliver courtesy copies of my motion papers to chambers?"
result = pipeline.run(
    {
        # The query is a keyword search: every word must appear in the rule.
        "retriever": {"query": "courtesy copy"},
        "prompt_builder": {"question": question},
    }
)
print(result["llm"]["replies"][0].text)
```

### Filing-prep agent

A paralegal preparing a motion needs two kinds of information: the firm's own checklists and the rules of the court
and judge. This agent reads the firm's notes with a BM25 retriever and finds the court, the judge and their rules with
`CourtRulesToolset`:

```python
from haystack import Document
from haystack.components.agents import Agent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.dataclasses import ChatMessage
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.tools import ComponentTool

from haystack_integrations.tools.court_rules import CourtRulesToolset

store = InMemoryDocumentStore()
store.write_documents(
    [
        Document(content="Checklist: order courtesy copies from the print vendor by noon the day before filing."),
        Document(
            content="Checklist: a motion needs a proof of service and a word count certificate before it is sent."
        ),
    ]
)


def notes_to_text(documents: list[Document]) -> str:
    return "\n".join(f"- {document.content}" for document in documents)


firm_notes = ComponentTool(
    component=InMemoryBM25Retriever(document_store=store, top_k=3),
    name="search_firm_checklists",
    description="Search the firm's internal filing checklists.",
    outputs_to_string={"source": "documents", "handler": notes_to_text},
)

agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    tools=[firm_notes, CourtRulesToolset()],
    system_prompt=(
        "You help a paralegal prepare a filing. Find the court and the judge with the court rules tools, "
        "then read the judge's rules and search the filing rules for the topics that matter. "
        "Combine them with the firm's checklists. Cite each court rule with its source URL. "
        "Say when a rule could not be found instead of guessing."
    ),
)

result = agent.run(
    messages=[
        ChatMessage.from_user(
            "I am filing a motion for summary judgment before Judge Garaufis in the Eastern District of New York. "
            "What do I need to prepare beyond the brief itself?"
        )
    ]
)
print(result["last_message"].text)
```

`CourtRulesToolset(tool_names=["list_courts", "search_filing_rules"])` keeps only the named tools. See the
[integration repository](https://github.com/foklepoint/court-rules-haystack) for the full tool list and the
[Court Rules API documentation](https://docs.courtrules.app) for the endpoints behind them.

## License

`court-rules-haystack` is distributed under the terms of the MIT license.
