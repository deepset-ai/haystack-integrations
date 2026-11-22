---
layout: integration
name: Polias
description: Search the web, news, official sources and law with Polias, a search engine with its own EU-hosted index
authors:
    - name: Polias
      socials:
        github: Polias-Team
pypi: https://pypi.org/project/polias-haystack
repo: https://github.com/Polias-Team/polias-haystack
type: Custom Component
report_issue: https://github.com/Polias-Team/polias-haystack/issues
logo: /logos/polias.png
version: Haystack 2.0
toc: true
---

### **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

[Polias](https://api.polias.eu/) is a search engine with its own index, hosted in the EU. This integration provides two components:

- `PoliasWebSearch` returns snippets and URLs from the web, news from the last 30 days, court decisions and legislation, or websites of public authorities.
- `PoliasAISearch` returns documents for AI answers. Each document has licence details. Where the licence allows, it holds a longer excerpt, and for legal results the full text.

You need an API key from [api.polias.eu/account](https://api.polias.eu/account).

## Installation

```bash
pip install polias-haystack
```

## Usage

```python
from haystack_integrations.components.websearch.polias import PoliasWebSearch

websearch = PoliasWebSearch(top_k=5, areas=["web", "legal"])  # reads POLIAS_API_KEY
result = websearch.run(query="Kündigung Eigenbedarf")
print(result["links"])
```

In a RAG pipeline:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.websearch.polias import PoliasAISearch

pipe = Pipeline()
pipe.add_component("search", PoliasAISearch(top_k=3, areas=["web", "legal"]))
pipe.add_component("prompt", PromptBuilder(template="""
Answer the question using the documents and cite their source notices.
{% for doc in documents %}{{ doc.meta.title }}: {{ doc.content }} ({{ doc.meta.notice }})
{% endfor %}
Question: {{ query }}
"""))
pipe.connect("search.documents", "prompt.documents")
# connect "prompt" to any chat generator
```

## License

`polias-haystack` is distributed under the terms of the [MIT](https://opensource.org/license/mit) license.
